import streamlit as st
import pandas as pd
import boto3
import pydeck as pdk
import altair as alt

# Page Configuration
st.set_page_config(page_title="NYC Operations Center", layout="wide")
st.title("NYC 311 Operations Dashboard (Oct–Dec 2025)")
st.caption("Cloud-native analytics dashboard powered by AWS S3 + Streamlit")
st.markdown("""
This dashboard showcases a **cloud-native data pipeline** end-to-end. 
It pulls data live from an **AWS S3 data lake** instead of relying on local files.  

 The source dataset comes from the 
[**NYC Open Data – 311 Service Requests**](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9/about_data) 
and is limited to a subset of records to keep the dashboard fast and responsive.
""")


# --- Connect to AWS S3 ---
# @st.cache_data is CRITICAL. It keeps the data in memory for 1 hour
# so we don't re-download 50k rows every time the user clicks a button.
@st.cache_data(ttl=3600)
def load_data_from_s3():
    # Streamlit Cloud uses st.secrets to securely access keys
    # On your local machine, it looks at .streamlit/secrets.toml
    s3 = boto3.client(
        's3',
        region_name='us-east-1'
    )
    bucket_name = 'jennifer-311-nyc-data'
    file_key = 'nyc_311_2025_cleaned.csv'

    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])

# Load Data with a spinner for UX
try:
    with st.spinner('Establishing connection to AWS S3...'):
        df = load_data_from_s3()
        st.success(f"Connection Established. Loaded {len(df):,} records.")
except Exception as e:
    st.error(f"Failed to connect to AWS: {e}")
    st.stop()


# --- Visualization Section ---

# Chart 1: Key Metrics
st.header("📌 Overview Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Number of Complaints", f"{len(df):,}")
col2.metric("Most Common Issue", df['complaint_type'].mode()[0].title())
col3.metric("Top Borough", df['borough'].mode()[0].title())

# Chart 2: Complaint Volume Over Time
st.header("📈 Complaint Volume Over Time")
st.caption("Daily trend of NYC 311 complaints showing spikes and seasonal patterns")
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
daily_counts = (
    df.dropna(subset=['created_date'])
      .groupby(df['created_date'].dt.date)
      .size()
      .reset_index(name="Count")
)
st.line_chart(daily_counts.set_index("created_date")["Count"])

# Chart 3: Complaints by hour
st.header("⏰ Complaint Patterns by Time of Day")
st.caption("Distribution of complaints across hours of the day")
df['hour'] = df['created_date'].dt.hour
hour_counts = df['hour'].value_counts().sort_index()
st.bar_chart(hour_counts)

st.write("")

# Chart 4: Borough Pie Chart
st.header("🏙️ Complaint Distribution by Borough")
st.caption("Percentage share and volume of complaints across NYC boroughs")
borough_counts = (
    df['borough']
    .str.title()
    .value_counts()
    .reset_index()
)
borough_counts.columns = ["Borough", "Complaint Count"]
total = borough_counts["Complaint Count"].sum()
borough_counts["Percentage"] = borough_counts["Complaint Count"] / total * 100
colors = ["#4C78A8", "#72B7B2", "#F58518", "#E45756", "#54A24B", "#B279A2"]
pie = alt.Chart(borough_counts).mark_arc(innerRadius=70).encode(
    theta=alt.Theta(field="Complaint Count", type="quantitative"),
    color=alt.Color(
        field="Borough",
        type="nominal",
        scale=alt.Scale(range=colors),
        legend=alt.Legend(title="Borough")
    ),
    tooltip=[
        alt.Tooltip("Borough:N", title="Borough"),
        alt.Tooltip("Complaint Count:Q", title="Complaints", format=","),
        alt.Tooltip("Percentage:Q", title="Share (%)", format=".1f")
    ]
).properties(height=380)
st.altair_chart(pie, use_container_width=True)

# Chart 5: Borough Bar Chart
st.header("📊 Complaint Volume by Borough")
st.caption("Total number of complaints reported in each borough")
# st.bar_chart(df['borough'].value_counts())
borough_counts = df['borough'].value_counts().sort_values(ascending=False)
st.bar_chart(borough_counts)

# Chart 6: Complaint Type Table
st.header("📋 Most Common Complaint Types")
st.caption("Top complaint categories reported by NYC residents")
# st.table(df['complaint_type'].value_counts().head(5))
top5 = (
    df["complaint_type"]
    .value_counts()
    .head(5)
    .reset_index()
)
top5.columns = ["COMPLAINT TYPE", "COUNT"]
top5["COMPLAINT TYPE"] = (
    top5["COMPLAINT TYPE"]
    .str.title()
    .str.replace("/", " / ", regex=False)
)
top5["COUNT"] = top5["COUNT"].map("{:,}".format)
st.table(top5)

st.write("")

# Chart 7: Complaint type by borough
st.header("🏢 Top Complaint Types by Borough")
st.caption("Stacked bars show only the top 5 complaint categories — totals do not include all complaint types.")
top_types = df['complaint_type'].value_counts().head(5).index
pivot = (
    df[df['complaint_type'].isin(top_types)]
    .groupby(['borough', 'complaint_type'])
    .size()
    .reset_index(name='count')
)
chart = alt.Chart(pivot).mark_bar().encode(
    x=alt.X("borough:N", title="Borough"),
    y=alt.Y("count:Q", stack="zero", title="Complaints"),
    color=alt.Color("complaint_type:N", title="Complaint Type"),
    tooltip=["borough:N", "complaint_type:N", "count:Q"]
).properties(height=350)
st.altair_chart(chart, use_container_width=True)

# Chart 8: Map
st.header("🗺️ Geographic Distribution of Complaints")
st.caption("Explore complaint locations by month with interactive tooltips")
# Convert created_date to datetime and extract month
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
df['month'] = df['created_date'].dt.month_name()
# Select month from dropdown
selected_month = st.selectbox(
    "Select a month to explore:",
    ["October", "November", "December"]
)
# Filter data for the selected month
map_df = df[
    (df['month'] == selected_month)
].dropna(subset=["latitude", "longitude"])
st.caption(f"Showing {len(map_df):,} complaints for {selected_month}")
# Make tooltip-friendly string columns
map_df['created_date_str'] = map_df['created_date'].dt.strftime("%Y-%m-%d %H:%M")
map_df['complaint_type_str'] = map_df['complaint_type'].str.title()
map_df['borough_str'] = map_df['borough'].str.title()
map_df['status_str'] = map_df['status'].str.title()
# Interactive PyDeck Map
layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[longitude, latitude]',
    get_radius=60,
    get_fill_color='[76, 120, 168, 160]',  # muted blue
    pickable=True,
)
view_state = pdk.ViewState(
    latitude=40.7128,
    longitude=-74.0060,
    zoom=10,
    pitch=0,
)
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>Complaint:</b> {complaint_type_str}<br/>"
                "<b>Borough:</b> {borough_str}<br/>"
                "<b>Status:</b> {status_str}<br/>"
                "<b>Date:</b> {created_date_str}",
        "style": {"color": "white"}
    }
))
