import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
file_path = 'Tabel Harga Berdasarkan Daerah.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet')

# Data preprocessing
df = df.rename(columns={'Komoditas (Rp)': 'Komoditas'})
df = df.set_index('Komoditas').T

# Convert index to datetime
df.index = pd.to_datetime(df.index.str.strip(), format='%d/ %m/ %Y')
df = df.apply(lambda x: x.str.replace(',', '').astype(float))

# Streamlit app
st.title("Dashboard Harga Komoditas")

# Sidebar filters
komoditas_list = df.columns.tolist()
selected_komoditas = st.sidebar.multiselect("Pilih Komoditas:", komoditas_list, default=komoditas_list[:1])

date_range = st.sidebar.date_input("Pilih Rentang Tanggal:", [df.index.min(), df.index.max()])

# Filter data
filtered_df = df[selected_komoditas]
filtered_df = filtered_df.loc[date_range[0]:date_range[1]]

# Line chart
st.subheader("Tren Harga Komoditas")
plt.figure(figsize=(10, 5))
for komoditas in selected_komoditas:
    plt.plot(filtered_df.index, filtered_df[komoditas], label=komoditas)
plt.xlabel("Tanggal")
plt.ylabel("Harga (Rp)")
plt.legend()
st.pyplot(plt)

# Show statistics
st.subheader("Statistik Harga")
st.dataframe(filtered_df.describe())

# Bar chart for average price
st.subheader("Perbandingan Harga Rata-rata")
avg_price = filtered_df.mean()
st.bar_chart(avg_price)

# Show raw data
if st.checkbox("Tampilkan Data Mentah"):
    st.dataframe(filtered_df)