import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.patches as mpatches  # Tambahkan impor ini

sns.set(style='dark')

# Helper functions
def create_by_season(df):
    total_casual_users = df.groupby("season").casual.sum().sort_values(ascending=False).reset_index()
    total_registered_users = df.groupby("season").registered.sum().sort_values(ascending=False).reset_index()
    total_users = pd.merge(
        left=total_casual_users,
        right=total_registered_users,
        how="left",
        left_on="season",
        right_on="season"
    )
    total_users_season = total_users.melt(id_vars='season', var_name='tipePengguna', value_name='jumlahPengguna')
    return total_users_season

def create_total_casual_users_df(df):
    total_casual_users_df = df.groupby("season").casual.sum().sort_values(ascending=False).reset_index()
    return total_casual_users_df

def create_total_registered_user_df(df):
    sum_registered_user_df = df.groupby("season").registered.sum().sort_values(ascending=False).reset_index()
    return sum_registered_user_df

def create_total_users_by_weather_df(df):
    total_users_by_weather_df = df.groupby("weathersit").cnt.sum().sort_values(ascending=False).reset_index()
    return total_users_by_weather_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="weekday", as_index=False).agg({
    "dteday": "max",
    "instant": "nunique",
    "cnt": "sum"
    })
    rfm_df.columns = ["weekday", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Prepare dataframe
all_df = pd.read_csv("main_data.csv")

# Ensure the date column are of type datetime
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Create filter components
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Adding a company logo
    st.image("logo.jpg", width=200)

    # Retrieve start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label='Range of Time', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                 (all_df["dteday"] <= str(end_date))]

createSeason = create_by_season(main_df)
total_casual_users_df = create_total_casual_users_df(main_df)
total_registered_user_df = create_total_registered_user_df(main_df)
rfm_df = create_rfm_df(main_df)

# Create dashboard
st.header('Leisurely Ride, Healthy Living :bike:')

# Season Users
st.subheader('Season Users')
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = total_casual_users_df.casual.sum()
    st.metric("Total Casual User", value=f'{total_casual:,}', delta_color="inverse")

with col2:
    total_registered = total_registered_user_df.registered.sum()
    st.metric("Total Registered User", value=f'{total_registered:,}', delta_color="inverse")

with col3:
    total_users = total_casual + total_registered
    st.metric("Total Users", value=f'{total_users:,}', delta_color="inverse")

# Use the "Set2" color palette
new_palette = ["#D3D3D3", "#4682B4"]

plt.figure(figsize=(15, 6))

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="season", y="jumlahPengguna", hue="tipePengguna", data=createSeason, palette=new_palette)
plt.ylabel("Total Users")
plt.xlabel("Season")
plt.title("Comparison of Casual Users and Registered Users by Season")

casual_patch = mpatches.Patch(color=new_palette[0], label='Casual')
registered_patch = mpatches.Patch(color=new_palette[1], label='Registered')
plt.legend(handles=[casual_patch, registered_patch], title="User Type")

plt.tight_layout()
st.pyplot(fig)

# Number of Casual Users and Registered Users by Season
st.subheader("Number of Casual Users and Registered Users by Season")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#4682B4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="casual", y="season", data=total_casual_users_df, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Casual Users", loc="center", fontsize=40)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20, rotation=45)

sns.barplot(x="registered", y="season", data=total_registered_user_df, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Registered Users", loc="center", fontsize=40)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20, rotation=-45)

st.pyplot(fig)

# Productivity Bike Sharing in season
def plot_season_data(df, season_name, season_label):
    season_df = df[df['season'] == season_name]

    if not season_df.empty:
        fig, ax = plt.subplots(figsize=(20, 5))
        sub = f"Bike Sharing productivity based on time during the {season_label} season"
        st.subheader(sub.title())

        # Create a custom color palette
        palette = {"Workingday": "#4682B4", "Holiday": "#D3D3D3"}

        sns.pointplot(data=season_df, x='hr', y='cnt', hue='daystatus', palette=palette, errorbar=None, ax=ax)
        ax.set_title(f'Bike Sharing Productivity Based on Time During the {season_label} Season')
        ax.set_ylabel('Total Users')
        ax.set_xlabel('Hour')

        # Add a legend
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=["Workingday", "Holiday"], title="Day Status")

        st.pyplot(fig)
    else:
        st.write(f"No data available for the {season_label} season.")

# Identifikasi musim yang ada dalam rentang tanggal tersebut
seasons_available = main_df['season'].unique()

# Tampilkan visualisasi untuk setiap musim yang ada
if 'Winter' in seasons_available:
    plot_season_data(main_df, 'Winter', 'Winter')

if 'Fall' in seasons_available:
    plot_season_data(main_df, 'Fall', 'Fall')

if 'Spring' in seasons_available:
    plot_season_data(main_df, 'Spring', 'Spring')

if 'Summer' in seasons_available:
    plot_season_data(main_df, 'Summer', 'Summer')

# Jumlah pengguna berdasarkan kondisi cuaca
st.subheader("Number of Users Based on Weather Conditions")

# Mengelompokkan data berdasarkan kondisi cuaca dan menjumlahkan total pengguna
byweather = main_df.groupby("weathersit")["cnt"].sum().sort_values(ascending=False).reset_index()

level_labels = byweather['weathersit'].tolist()
level_counts = byweather['cnt'].tolist()
cols = st.columns(len(level_labels))

for i in range(len(level_labels)):
    with cols[i]:
        st.metric(label=level_labels[i], value=level_counts[i])

# Highlight the highest value with blue and other values with gray
max_count = byweather['cnt'].max()
colors = ["#4682B4" if count == max_count else "#D3D3D3" for count in byweather['cnt']]
            
# Membuat figure dan plot
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y="cnt", x="weathersit", data=byweather, palette=colors, ax=ax)

# Menambahkan judul dan label
ax.set_title("Jumlah Pengguna Berdasarkan Kondisi Cuaca", loc="center", fontsize=15)
ax.set_ylabel("Total Users")
ax.set_xlabel("Kondisi Cuaca")
ax.ticklabel_format(style='plain', axis='y')  # Mengatur format sumbu y agar tidak dalam notasi ilmiah

# Menampilkan plot di Streamlit
st.pyplot(fig)

# RFM Analysis
st.subheader("Best Customer Based on RFM Parameters (day)")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Avg Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Avg Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale='en_US')
    st.metric("Avg Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

# Menyoroti nilai penting dengan warna biru untuk semua blok grafik RFM
colors = ["#4682B4"] * len(rfm_df)

sns.barplot(y="recency", x="weekday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="frequency", x="weekday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="weekday", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.caption('Copyright © Agistia Ronna Aniqa 2025')