import pandas as pd

# 1. Load full dataset
df = pd.read_csv('sales data.csv', encoding='latin1')
print(f"Initial rows loaded: {len(df)}")

# 2. Safe Date Conversion & Turnaround Time
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True, errors='coerce')

# Convert sales to numeric cleanly
df['Sales'] = pd.to_numeric(df['Sales'].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')

# Drop only rows missing Customer ID or Sales
df = df.dropna(subset=['Customer ID', 'Sales'])
df = df[df['Sales'] > 0]
df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days.fillna(0).astype(int)

# 3. RFM Metrics Calculation
snapshot = df['Order Date'].max()
rfm = df.groupby('Customer ID').agg(
    Recency=('Order Date', lambda x: (snapshot - x.max()).days if pd.notnull(x.max()) else 999),
    Frequency=('Order ID', 'nunique'),
    Monetary=('Sales', 'sum')
)

# 4. Behavioral Customer Segmentation
med_r, med_f = rfm['Recency'].median(), rfm['Frequency'].median()

def assign_tier(row):
    if row['Recency'] <= med_r and row['Frequency'] >= med_f:
        return 'Champions & Loyalists'
    elif row['Recency'] <= med_r:
        return 'Recent / Potential Growth'
    elif row['Frequency'] >= med_f:
        return 'At Risk (High Value, Slipping)'
    return 'Hibernating / Lost'

rfm['Customer_Segment'] = rfm.apply(assign_tier, axis=1)

# 5. Merge and Export
final_df = df.merge(rfm[['Customer_Segment']], on='Customer ID', how='left')
final_df.to_csv('cleaned_sales_rfm.csv', index=False)
print(f"Success! Exported {len(final_df)} rows to 'cleaned_sales_rfm.csv'")