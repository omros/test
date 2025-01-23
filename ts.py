import streamlit as st
import pandas as pd
from datetime import timedelta

# Set page config
st.set_page_config(page_title="Dashboard Harga Komoditas", layout="wide")

# Load data
@st.cache_data
def load_data():
    data = pd.read_excel("Tabel Harga Berdasarkan Daerah.xlsx", sheet_name="Sheet")
    data = data.rename(columns={'Komoditas (Rp)': 'Komoditas'})
    data = data.set_index('Komoditas').T
    data.index = pd.to_datetime(data.index.str.strip(), format='%d/ %m/ %Y')
    data = data.apply(lambda x: x.str.replace(',', '').astype(float))
    return data

df = load_data()

# Sidebar configuration
st.sidebar.title("Dashboard Harga Komoditas")
time_frame = st.sidebar.selectbox("Pilih Rentang Waktu", ("Harian", "Mingguan", "Bulanan", "Kuartalan"))
selected_komoditas = st.sidebar.multiselect("Pilih Komoditas", df.columns.tolist(), default=df.columns.tolist()[:1])

# Date range selection
default_start_date = df.index.min()
default_end_date = df.index.max()
start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [default_start_date, default_end_date])

# Resampling data
freq_map = {"Harian": 'D', "Mingguan": 'W', "Bulanan": 'M', "Kuartalan": 'Q'}
df_filtered = df[selected_komoditas].loc[start_date:end_date].resample(freq_map[time_frame]).mean()

# Metrics display
st.subheader("Ringkasan Harga Komoditas")
cols = st.columns(len(selected_komoditas))
for col, komoditas in zip(cols, selected_komoditas):
    avg_price = df_filtered[komoditas].mean()
    col.metric(f"Rata-rata Harga {komoditas}", f"Rp {avg_price:,.0f}")

# Line Chart Visualization
st.subheader("Tren Harga Komoditas")
st.line_chart(df_filtered)

# Bar Chart Visualization
st.subheader("Perbandingan Harga Rata-rata")
st.bar_chart(df_filtered.mean())

# Show raw data
with st.expander('Lihat Data Harga Komoditas'):
    st.dataframe(df_filtered.style.format("{:,.0f}"))
