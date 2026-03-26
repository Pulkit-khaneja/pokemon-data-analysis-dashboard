from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Pokemon Dashboard", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parents[1] / "nootebook" / "pokemon_cleaned.csv"
    df = pd.read_csv(data_path)
    df["Legendary"] = df["Legendary"].astype(str).str.strip().str.lower().eq("true")
    return df


df = load_data()

st.title("Pokemon Analytics Dashboard")
st.caption("Interactive overview of Pokemon stats, roles, and top performers")

st.sidebar.header("Filters")

type_options = sorted(df["Type1"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "Select Type",
    options=type_options,
    default=type_options,
)

selected_legendary = st.sidebar.multiselect(
    "Legendary",
    options=[True, False],
    default=[True, False],
    format_func=lambda value: "Legendary" if value else "Non-Legendary",
)

role_options = sorted(df["Role"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect(
    "Role",
    options=role_options,
    default=role_options,
)

generation_options = sorted(df["Generation"].dropna().unique().tolist())
selected_generations = st.sidebar.multiselect(
    "Generation",
    options=generation_options,
    default=generation_options,
)

df_filtered = df[
    df["Type1"].isin(selected_types)
    & df["Legendary"].isin(selected_legendary)
    & df["Role"].isin(selected_roles)
    & df["Generation"].isin(selected_generations)
].copy()

if df_filtered.empty:
    st.warning("No Pokemon match the current filters. Adjust the sidebar selections.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pokemon", f"{len(df_filtered):,}")
col2.metric("Avg Total", f"{df_filtered['Total'].mean():.0f}")
col3.metric("Max Total", f"{df_filtered['Total'].max():.0f}")
col4.metric("Legendary %", f"{df_filtered['Legendary'].mean() * 100:.1f}%")

chart_col1, chart_col2 = st.columns(2)

type_counts = df_filtered["Type1"].value_counts().reset_index()
type_counts.columns = ["Type", "Count"]

fig1 = px.bar(
    type_counts,
    x="Type",
    y="Count",
    color="Type",
    title="Type Distribution",
)
chart_col1.plotly_chart(fig1, use_container_width=True)

fig2 = px.scatter(
    df_filtered,
    x="Attack",
    y="Defense",
    color="Legendary",
    size="Total",
    hover_name="Pokemon",
    title="Attack vs Defense",
)
chart_col2.plotly_chart(fig2, use_container_width=True)

bottom_col1, bottom_col2 = st.columns(2)

fig3 = px.pie(df_filtered, names="Role", title="Role Distribution")
bottom_col1.plotly_chart(fig3, use_container_width=True)

top10 = df_filtered.sort_values(by="Total", ascending=False).head(10)
fig4 = px.bar(
    top10.sort_values(by="Total", ascending=True),
    x="Total",
    y="Pokemon",
    color="Type1",
    orientation="h",
    title="Top 10 Strongest Pokemon",
)
bottom_col2.plotly_chart(fig4, use_container_width=True)

st.subheader("Dataset Preview")
preview_columns = [
    "Pokemon",
    "Type1",
    "Type2",
    "Generation",
    "Legendary",
    "Total",
    "HP",
    "Attack",
    "Defense",
    "Speed",
    "Role",
]
st.dataframe(df_filtered[preview_columns], use_container_width=True)
