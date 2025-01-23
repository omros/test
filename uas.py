import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="YouTube Channel Dashboard", layout="wide")

# Helper functions
@st.cache_data
def load_data():
    data = pd.read_excel("Tabel Harga Berdasarkan Daerah.xlsx", sheet_name="Sheet")
    data = data.rename(columns={'Komoditas (Rp)': 'Komoditas'})
    data = data.set_index('Komoditas').T
    data.index = pd.to_datetime(data.index.str.strip(), format='%d/ %m/ %Y')
    data = data.apply(lambda x: x.str.replace(',', '').astype(float))
    return data

def custom_quarter(date):
    month = date.month
    year = date.year
    if month in [2, 3, 4]:
        return pd.Period(year=year, quarter=1, freq='Q')
    elif month in [5, 6, 7]:
        return pd.Period(year=year, quarter=2, freq='Q')
    elif month in [8, 9, 10]:
        return pd.Period(year=year, quarter=3, freq='Q')
    else:  # month in [11, 12, 1]
        return pd.Period(year=year if month != 1 else year-1, quarter=4, freq='Q')

def aggregate_data(df, freq):
    if freq == 'Q':
        return df.resample('Q').mean()
    elif freq == 'M':
        return df.resample('M').mean()
    elif freq == 'W':
        return df.resample('W').mean()
    else:
        return df

def get_weekly_data(df):
    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'M')

def get_quarterly_data(df):
    return aggregate_data(df, 'Q')

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, chart_type, height=150, time_frame='Daily'):
    chart_data = df[[column]].copy()
    if time_frame == 'Kuartalan':
        chart_data.index = chart_data.index.strftime('%Y Q%q')
    if chart_type == 'Bar':
        st.bar_chart(chart_data, y=column, color=color, height=height)
    elif chart_type == 'Area':
        st.area_chart(chart_data, y=column, color=color, height=height)


def is_period_complete(date, freq):
    today = datetime.now()
    if freq == 'D':
        return date.date() < today.date()
    elif freq == 'W':
        return date + timedelta(days=6) < today
    elif freq == 'M':
        next_month = date.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1) <= today
    elif freq == 'Q':
        current_quarter = custom_quarter(today)
        return date < current_quarter

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

def display_metric(col, title, value, df, column, color, time_frame):
    with col:
        with st.container(border=True):
            delta, delta_percent = calculate_delta(df, column)
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric(title, format_with_commas(value), delta=delta_str)
            create_metric_chart(df, selected_komoditas[0], "#FF9F36", chart_selection, height=150, time_frame=time_frame)

            
            last_period = df.index[-1]
            freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q'}[time_frame]
            if not is_period_complete(last_period, freq):
                st.caption(f"Note: The last {time_frame.lower()[:-2] if time_frame != 'Daily' else 'day'} is incomplete.")

# Load data
df = load_data()

# Set up input widgets
st.logo(image="images/streamlit-logo-primary-colormark-lighttext.png", 
        icon_image="images/streamlit-mark-color.png")

with st.sidebar.title("Dashboard Harga Komoditas"):

    max_date = df['DATE'].max().date()
    default_start_date = df.index.min()
    default_end_date = df.index.max()
    start_date, end_date = st.date_input("Pilih Rentang Tanggal", [default_start_date, default_end_date])
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    time_frame = st.selectbox("Pilih Rentang Waktu", ("Harian", "Mingguan", "Bulanan", "Kuartalan"))
    selected_komoditas = st.sidebar.multiselect("Pilih Komoditas", df.columns.tolist(), default=df.columns.tolist()[:1])
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))

# Prepare data based on selected time frame
if time_frame == 'Daily':
    df_display = df.set_index('DATE')
elif time_frame == 'Weekly':
    df_display = get_weekly_data(df)
elif time_frame == 'Monthly':
    df_display = get_monthly_data(df)
elif time_frame == 'Quarterly':
    df_display = get_quarterly_data(df)

# Display Key Metrics
st.subheader("All-Time Statistics")

metrics = [
    ("Harga Rata-rata", "Beras Kualitas Medium I", '#29b5e8'),
    ("Harga Tertinggi", "Beras Kualitas Medium II", '#FF9F36'),
]


cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    total_value = df[column].sum()
    display_metric(col, title, total_value, df_display, column, color, time_frame)

st.subheader("Selected Duration")

if time_frame == 'Quarterly':
    start_quarter = custom_quarter(start_date)
    end_quarter = custom_quarter(end_date)
    mask = (df_display.index >= start_quarter) & (df_display.index <= end_quarter)
else:
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color, time_frame)

# DataFrame display
with st.expander('Lihat Data Harga Komoditas'):
    st.dataframe(df_filtered.style.format("{:,.0f}"))
