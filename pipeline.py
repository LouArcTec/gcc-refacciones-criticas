# %%
import matplotlib.pyplot as plt
from datetime import timedelta
from sksurv.ensemble import RandomSurvivalForest
from sklearn.model_selection import StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import gc
import numpy as np
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


# =====================================================================
# STEP 1: LOAD AND CLEAN DATA
# =====================================================================
# Note: Outlier capping logic has been explicitly removed. Extreme
# machine failures are vital for the survival curve to learn properly.
RAW_FILE = "infotec.xlsx"  # Ensure this path matches your environment

print("Loading raw files...")
df_equipos = pd.read_excel(RAW_FILE, sheet_name="Equipos")
df_ordenes = pd.read_excel(RAW_FILE, sheet_name="Ordenes de trabajo", parse_dates=[
                           'Created On', 'Changed On'])
df_refacciones = pd.read_excel(RAW_FILE, sheet_name="Refacciones", parse_dates=[
                               'Document Date', 'Posting Date'])

# Standardize IDs (Prevents joining errors where '123' doesn't match '123.0')


def clean_id_column(series):
    return series.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()


df_refacciones['Order'] = clean_id_column(df_refacciones['Order'])
df_ordenes['Order'] = clean_id_column(df_ordenes['Order'])
df_equipos['EQUIPO'] = clean_id_column(df_equipos['EQUIPO'])
df_ordenes['Equipment'] = clean_id_column(df_ordenes['Equipment'])

# =====================================================================
# STEP 2: BRAND-AWARE + OPERATIONAL BEHAVIORAL CLUSTERING
# =====================================================================
print("Intelligently Clustering Spare Parts Catalog via Brand Distributions & Behavior...")

# 1. Synthesize a pristine, unique Part DNA Key
df_refacciones['Material_Cleaned'] = df_refacciones['Material'].fillna(
    '').astype(str).str.strip()
df_refacciones['Description_Cleaned'] = df_refacciones['Description'].fillna(
    'UNKNOWN').astype(str).str.upper().str.strip()

# ---------------------------------------------------------------------
# NEW ENHANCEMENT: BULK CONSUMABLES ELIMINATION FILTER
# ---------------------------------------------------------------------
print("Filtering out bulk purchase consumables...")
# Load the consumables reference list (handling it as an Excel file per your modification)
df_consumibles = pd.read_excel(
    "consumibles.xlsx",
    sheet_name="Sheet1",
    header=None,
    names=["Consumable_Description"]
)

# Clean strings identically to match perfectly (Uppercase, stripped)
consumibles_set = set(df_consumibles['Consumable_Description'].fillna(
    '').astype(str).str.upper().str.strip())

# Count records before drop
total_before_filter = len(df_refacciones)

# Execute exclusion filter
df_refacciones = df_refacciones[~df_refacciones['Description_Cleaned'].isin(
    consumibles_set)]

total_after_filter = len(df_refacciones)
print(
    f"• Successfully removed {total_before_filter - total_after_filter} bulk consumable transaction lines.")
print(
    f"• Transaction ledger size reduced from {total_before_filter:,} to {total_after_filter:,} rows.")
# ---------------------------------------------------------------------

df_refacciones['Part_Key'] = np.where(
    df_refacciones['Material_Cleaned'].isin(['', 'nan', '0', '0.0']),
    df_refacciones['Description_Cleaned'],
    df_refacciones['Material_Cleaned']
)

# 2. Build full-context relational logs to extract brand and behavioral metrics
df_ref_merged = df_refacciones.merge(
    df_ordenes[['Order', 'Equipment']], on='Order', how='inner')
df_ref_merged = df_ref_merged.merge(
    df_equipos[['EQUIPO', 'MARCA']], left_on='Equipment', right_on='EQUIPO', how='inner')

# 3. Dynamically unpack brand allocation metrics using one-hot footprints
brand_dummies = pd.get_dummies(df_ref_merged['MARCA'], prefix='Prop')
# Captures Kenworth, International, Scania, Foton, etc.
brand_cols = brand_dummies.columns.tolist()
df_ref_merged = pd.concat([df_ref_merged, brand_dummies], axis=1)

# Ensure chronological ordering for Mean Time Between Repairs (MTBR) calculations
df_ref_merged['Posting Date'] = pd.to_datetime(df_ref_merged['Posting Date'])
df_ref_merged = df_ref_merged.sort_values(
    by=['Equipment', 'Part_Key', 'Posting Date'])

# Calculate MTBR for the same component type on the same exact truck
df_ref_merged['Days_Between_Repairs'] = df_ref_merged.groupby(
    ['Equipment', 'Part_Key'])['Posting Date'].diff().dt.days

# 4. Aggregate transaction lines into a detailed Brand Profile Catalog
agg_config = {
    'Description': ('Description_Cleaned', 'first'),
    'Total_Uses': ('Order', 'count'),
    'Avg_Quantity': ('Quantity', 'mean'),
    'Avg_Days_Between_Repairs': ('Days_Between_Repairs', 'mean'),
}
for col in brand_cols:
    agg_config[col] = (col, 'mean')

part_profiles = df_ref_merged.groupby(
    'Part_Key').agg(**agg_config).reset_index()

# 5. Handle sparse instances (items replaced only once on an asset) safely
part_profiles['Avg_Days_Between_Repairs_Cleaned'] = part_profiles['Avg_Days_Between_Repairs'].fillna(
    -1)
part_profiles['Has_Repeated_Repairs'] = np.where(
    part_profiles['Avg_Days_Between_Repairs'].isna(), 0, 1)

# Create log-transformed versions of highly skewed counts
part_profiles['Log_Total_Uses'] = np.log1p(part_profiles['Total_Uses'])
part_profiles['Log_Avg_Quantity'] = np.log1p(part_profiles['Avg_Quantity'])

# 6. Build Enriched Multimodal Feature Matrix for ALL parts
# NOTE: We process the whole catalog together so TF-IDF text vectors can associate rare items with common items
numerical_features = ['Log_Total_Uses', 'Log_Avg_Quantity',
                      'Avg_Days_Between_Repairs_Cleaned', 'Has_Repeated_Repairs'] + brand_cols

preprocessor = ColumnTransformer(
    transformers=[
        # Text/Semantic patterns (Preserved your modified value of max_features=100)
        ('text', TfidfVectorizer(max_features=300, stop_words=[
         'DE', 'PARA', 'Y', 'CON', 'EL', 'LA']), 'Description'),
        # Wear profiles combined with exact multi-brand usage signatures
        ('num', StandardScaler(), numerical_features)
    ]
)

# Fit and transform the entire matrix together
X_features = preprocessor.fit_transform(part_profiles)

# Get clustering elbow over the complete matrix
wcss = []
cluster_range = range(10, 61, 5)

for k in cluster_range:
    km = KMeans(n_clusters=k, random_state=42, n_init='auto')
    km.fit(X_features)
    wcss.append(km.inertia_)

# Plot the Elbow
plt.plot(cluster_range, wcss, 'bx-')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('WCSS / Inertia')
plt.title('The Elbow Method showing the Optimal K')
plt.show()

# 7. Apply K-Means grouping over the hybrid space for all parts
# Preserved your modified target of 25 clusters
kmeans = KMeans(n_clusters=25, random_state=42, n_init='auto')
part_profiles['Raw_Cluster'] = 'CLUSTER_' + \
    kmeans.fit_predict(X_features).astype(str)

# ---------------------------------------------------------------------
# POST-CLUSTERING CONSOLIDATION SCRIPT
# ---------------------------------------------------------------------
print("Consolidating tiny outlier clusters into catch-all safety bucket...")
# Count how many parts landed in each generated cluster
cluster_counts = part_profiles['Raw_Cluster'].value_counts()

# Identify true micro-clusters (e.g., failed groupings containing fewer than 10 unique descriptions)
micro_clusters = cluster_counts[cluster_counts < 10].index.tolist()

# Dynamically map only the tiny anomalies to CLUSTER_RARE, keeping everything else stable
part_profiles['Component_Category'] = np.where(
    part_profiles['Raw_Cluster'].isin(micro_clusters),
    'CLUSTER_RARE',
    part_profiles['Raw_Cluster']
)

# Drop intermediate tracking column
part_profiles.drop(columns=['Raw_Cluster'], inplace=True)
# ---------------------------------------------------------------------

# 8. Map these brand-isolated groupings back to the active transactions table
df_refacciones = df_refacciones.merge(
    part_profiles[['Part_Key', 'Component_Category']], on='Part_Key', how='left')

# Drop helper transformations to clean memory footprint
df_refacciones.drop(columns=['Material_Cleaned',
                    'Description_Cleaned', 'Part_Key'], inplace=True)
print("✅ Brand-Aware Behavioral Clustering completed successfully.")

# 1. Total Unique Parts in the whole catalog
print(f"Total Unique Spare Parts (Profiles): {len(part_profiles)}")

# 2. Part profile distribution (How many items belong to each cluster)
print("\n--- Unique Spare Parts Count Per Cluster ---")
print(part_profiles['Component_Category'].value_counts().sort_index())

# =====================================================================
# STEP 3: BUILD TARGET TIMELINE LIFECYCLES
# =====================================================================
print("Building mathematical survival lifecycles...")
merged_history = df_refacciones.merge(
    df_ordenes[['Order', 'Equipment', 'Order Type']], on='Order', how='inner')

global_start_date = df_ordenes['Created On'].min()
global_end_date = df_ordenes['Created On'].max()

# Clean up Truck Feature Names
df_equipos.columns = df_equipos.columns.str.strip()
if len(df_equipos.columns) >= 4 and df_equipos.columns[3] == '':
    df_equipos.rename(columns={df_equipos.columns[3]: 'Origin'}, inplace=True)
df_equipos.rename(columns={'EQUIPO': 'Equipment', 'MARCA': 'Brand',
                  'MODELO': 'ModelYear', 'ORIGEN': 'Origin'}, inplace=True)

lifecycles = []
unique_categories = df_refacciones['Component_Category'].unique()
grouped_history = {truck_id: grp for truck_id,
                   grp in merged_history.groupby('Equipment')}

for truck_id in df_equipos['Equipment'].unique():
    truck_data = grouped_history.get(truck_id, pd.DataFrame())

    for category in unique_categories:
        if truck_data.empty:
            truck_replacements = pd.DataFrame()
        else:
            truck_replacements = truck_data[truck_data['Component_Category'] == category].sort_values(
                'Posting Date')

        if truck_replacements.empty:
            total_days = (global_end_date - global_start_date).days
            if total_days > 0:
                lifecycles.append({'Equipment': truck_id, 'Component_Category': category,
                                  'Time_to_Event': total_days, 'Event_Observed': 0})
        else:
            dates = truck_replacements['Posting Date'].tolist()
            first_delta = (dates[0] - global_start_date).days
            if first_delta > 0:
                lifecycles.append({'Equipment': truck_id, 'Component_Category': category,
                                  'Time_to_Event': first_delta, 'Event_Observed': 1})
            for i in range(len(dates) - 1):
                delta = (dates[i+1] - dates[i]).days
                if delta > 0:
                    lifecycles.append(
                        {'Equipment': truck_id, 'Component_Category': category, 'Time_to_Event': delta, 'Event_Observed': 1})
            last_delta = (global_end_date - dates[-1]).days
            if last_delta > 0:
                lifecycles.append({'Equipment': truck_id, 'Component_Category': category,
                                  'Time_to_Event': last_delta, 'Event_Observed': 0})

df_lifecycle = pd.DataFrame(lifecycles)

# =====================================================================
# STEP 4: MASTER FEATURE ENGINEERING & MATRIX ENCODING
# =====================================================================
dataset = df_lifecycle.merge(df_equipos, on='Equipment', how='inner')
dataset['Truck_Age'] = 2026 - dataset['ModelYear']

order_counts = df_ordenes.groupby('Equipment').size().rename('Total_Orders')
dataset = dataset.join(order_counts, on='Equipment')

plant_mapping = df_ordenes.groupby('Equipment')['MaintPlant'].agg(
    lambda x: x.value_counts().index[0] if not x.empty else 'UNKNOWN').rename('Primary_Plant')
dataset = dataset.join(plant_mapping, on='Equipment')

order_type_ratio = df_ordenes.groupby('Equipment')['Order Type'].apply(lambda x: (
    x == 'WPM2').sum() / len(x) if len(x) > 0 else 0).rename('Order_Type_Ratio')
dataset = dataset.join(order_type_ratio, on='Equipment')

df_orders_sorted = df_ordenes.sort_values(by=['Equipment', 'Created On'])
df_orders_sorted['Days_Between_Orders'] = df_orders_sorted.groupby('Equipment')[
    'Created On'].diff().dt.days
avg_days_between = df_orders_sorted.groupby(
    'Equipment')['Days_Between_Orders'].mean().rename('Avg_Days_Between_Orders')
dataset = dataset.join(avg_days_between, on='Equipment')

dataset['Total_Orders'] = dataset['Total_Orders'].fillna(0)
dataset['Order_Type_Ratio'] = dataset['Order_Type_Ratio'].fillna(0.0)
dataset['Avg_Days_Between_Orders'] = dataset['Avg_Days_Between_Orders'].fillna(
    dataset['Avg_Days_Between_Orders'].mean())

features = ['Truck_Age', 'Total_Orders', 'Origin', 'Avg_Days_Between_Orders',
            'Brand', 'Primary_Plant', 'Order_Type_Ratio', 'Component_Category']
X = dataset[features].copy()
X_encoded = pd.get_dummies(X, columns=[
                           'Origin', 'Brand', 'Primary_Plant', 'Component_Category']).astype(float)
training_columns = X_encoded.columns.tolist()

# Apply RAM-Fix: Coarsen event time into 5-day buckets
binned_days = (
    np.round(dataset['Time_to_Event'].astype(float) / 5) * 5).astype(float)
y_structured = np.empty(len(dataset), dtype=[(
    'Status', '?'), ('Survival_in_days', '<f8')])
y_structured['Status'] = dataset['Event_Observed'].astype(bool)
y_structured['Survival_in_days'] = binned_days

# =====================================================================
# STEP 5: TRAIN UNIFIED HYBRID RANDOM SURVIVAL FOREST
# =====================================================================
print("Training the Random Survival Forest Matrix (Optimized for RAM)...")
rsf_master = RandomSurvivalForest(
    n_estimators=150,
    min_samples_split=60,
    min_samples_leaf=20,
    n_jobs=2,
    random_state=42
)

n_splits = 3
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

cv_c_indices = []
cv_c_indices_train = []

for fold, (train_idx, test_idx) in enumerate(skf.split(X_encoded, y_structured['Status'])):
    X_tr, X_te = X_encoded.iloc[train_idx], X_encoded.iloc[test_idx]
    y_tr, y_te = y_structured[train_idx], y_structured[test_idx]

    rsf_master.fit(X_tr, y_tr)

    train_score = rsf_master.score(X_tr, y_tr)
    cv_c_indices_train.append(train_score)
    print(f"  • Train C-Index: {train_score:.4f}")

    score = rsf_master.score(X_te, y_te)
    cv_c_indices.append(score)
    print(f"  • Cross-Validation Fold {fold + 1} C-Index: {score:.4f}")

    del X_tr, X_te, y_tr, y_te
    gc.collect()

rsf_master.fit(X_encoded, y_structured)
print("✅ Master Model Trained.")

# =====================================================================
# STEP 6: FLEET-WIDE PROCUREMENT LEDGER (PREDICTING ALL TRUCKS)
# =====================================================================
print("Processing final evaluation for the full fleet...")


def generate_fleet_procurement_ledger(model, dataset_features, train_cols, df_ref_clean, df_ord_clean):
    current_date = pd.to_datetime('2026-06-10')  # Anchored baseline date
    all_records = []

    # Isolate valid usage histories tied to known trucks
    active_history = df_ref_clean.dropna(subset=['Order']).merge(
        df_ord_clean[['Order', 'Equipment']], on='Order', how='inner')

    # Loop over every truck
    for truck_id in df_equipos['Equipment'].unique():
        truck_parts = active_history[active_history['Equipment'] == truck_id]
        if truck_parts.empty:
            continue

        clean_history = truck_parts.sort_values('Posting Date').drop_duplicates(
            subset=['Posting Date', 'Description', 'Order'])
        current_active = clean_history.groupby(
            'Description').last().reset_index()

        # Eliminate inactive "ghost" components installed more than 450 days ago
        max_fresh_date = current_active['Posting Date'].max()
        if pd.isna(max_fresh_date):
            continue
        current_active = current_active[(
            max_fresh_date - current_active['Posting Date']).dt.days < 450]

        truck_meta = dataset_features[dataset_features['Equipment'] == truck_id].tail(
            1)
        if truck_meta.empty:
            continue

        for _, part in current_active.iterrows():
            days_in_service = max(
                0, (current_date - pd.to_datetime(part['Posting Date'])).days)

            # Recreate One-Hot input matrix
            pred_profile = truck_meta.copy()
            pred_profile['Component_Category'] = part['Component_Category']
            X_pred = pd.get_dummies(pred_profile[features], columns=[
                                    'Origin', 'Brand', 'Primary_Plant', 'Component_Category'])
            X_pred = X_pred.reindex(
                columns=train_cols, fill_value=0.0).astype(float)

            surv_fn = model.predict_survival_function(X_pred)[0]

            # Survival reading helper for current health
            def get_health(day):
                if day <= surv_fn.x[0]:
                    return 1.0
                if day >= surv_fn.x[-1]:
                    return surv_fn.y[-1]
                idx = np.searchsorted(surv_fn.x, day, side='right') - 1
                return surv_fn.y[max(0, idx)]

            health_now = get_health(days_in_service)

            # ---------------------------------------------------------------------
            # HIGH-SPEED VECTORIZED HORIZON SEARCH (Past & Future Checked Instantly)
            # ---------------------------------------------------------------------
            predicted_drop_date = 'Exceeds Model Limit'

            # Vectorized look at the survival curve array to find where probability dips below 50%
            under_50_indices = np.where(surv_fn.y <= 0.50)[0]

            if len(under_50_indices) > 0:
                # Extract the exact timeline day matching that index step
                drop_day = surv_fn.x[under_50_indices[0]]

                # Calculate date relative to original installation date (works for past and future)
                drop_off_date = pd.to_datetime(
                    part['Posting Date']) + pd.Timedelta(days=int(np.ceil(drop_day)))
                predicted_drop_date = drop_off_date.strftime('%Y-%m-%d')
            # ---------------------------------------------------------------------

            all_records.append({
                "Truck ID": truck_id,
                "Component Description": part['Description'],
                "Category Group": part['Component_Category'],
                "Installation Date": part['Posting Date'].strftime('%Y-%m-%d'),
                "Age (Days)": days_in_service,
                "Current Health (%)": round(health_now * 100, 1),
                "Projected 50% Date": predicted_drop_date
            })

    return pd.DataFrame(all_records).sort_values(by=["Current Health (%)", "Truck ID"], ascending=[False, True])


final_ledger = generate_fleet_procurement_ledger(
    rsf_master, dataset, training_columns, df_refacciones, df_ordenes)

print("\n" + "="*100)
print("🚀 FLEET DEPLOYMENT SUCCESS: Procurement Ledger Compiled")
print("="*100)
print(final_ledger.head(15).to_string(index=False))

final_ledger.to_csv("Master_Procurement_All_Trucks.csv", index=False)
