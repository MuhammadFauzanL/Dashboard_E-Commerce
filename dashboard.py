import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    main_data = pd.read_csv(os.path.join(data_dir, "main_data.csv"))
    
    datetime_cols = ['order_purchase_timestamp', 'order_approved_at', 
                     'order_delivered_carrier_date', 'order_delivered_customer_date',
                     'order_estimated_delivery_date']
    for col in datetime_cols:
        if col in main_data.columns:
            main_data[col] = pd.to_datetime(main_data[col])
    
    return main_data

main_data = load_data()

st.sidebar.title("E-Commerce Dashboard")
st.sidebar.markdown("---")

min_date = main_data['order_purchase_timestamp'].min().date()
max_date = main_data['order_purchase_timestamp'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

filtered_data = main_data[
    (main_data['order_purchase_timestamp'].dt.date >= start_date) & 
    (main_data['order_purchase_timestamp'].dt.date <= end_date)
]

st.title("E-Commerce Public Dataset Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered_data['order_id'].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    total_customers = filtered_data['customer_id'].nunique()
    st.metric("Total Customers", f"{total_customers:,}")

with col3:
    total_revenue = filtered_data['price'].sum()
    st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")

with col4:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.metric("Avg Order Value", f"R$ {avg_order_value:,.2f}")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Tren Pesanan Bulanan")
    
    monthly_orders = filtered_data.groupby(
        filtered_data['order_purchase_timestamp'].dt.to_period('M')
    )['order_id'].nunique().reset_index(name='order_count')
    monthly_orders['order_purchase_timestamp'] = monthly_orders['order_purchase_timestamp'].astype(str)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_orders['order_purchase_timestamp'], monthly_orders['order_count'], 
            marker='o', linewidth=2, color='#1f77b4')
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Pesanan")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("Distribusi Pelanggan per Kota (Top 10)")
    
    customer_city = filtered_data.groupby('customer_city')['customer_id'].nunique().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("Blues_r", len(customer_city))
    ax.barh(customer_city.index, customer_city.values, color=colors)
    ax.set_xlabel("Jumlah Pelanggan")
    ax.set_ylabel("Kota")
    ax.invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Metode Pembayaran")
    
    payment_methods = filtered_data['payment_type'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#ff99cc']
    ax.pie(payment_methods.values, labels=payment_methods.index, autopct='%1.1f%%',
           colors=colors, startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

with col2:
    st.subheader("Status Pesanan")
    
    order_status = filtered_data['order_status'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("Set2", len(order_status))
    ax.bar(order_status.index, order_status.values, color=colors)
    ax.set_xlabel("Status")
    ax.set_ylabel("Jumlah")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

st.subheader("Distribusi Penjual per Kota (Top 10)")

seller_city = filtered_data.groupby('seller_city')['seller_id'].nunique().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 5))
colors = sns.color_palette("Greens_r", len(seller_city))
ax.bar(seller_city.index, seller_city.values, color=colors)
ax.set_xlabel("Kota")
ax.set_ylabel("Jumlah Penjual")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig)

