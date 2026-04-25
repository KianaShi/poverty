import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IE6600 Dashboard", layout="wide")

# load data
df_2015 = pd.read_csv("acs2015_county_data.csv")
df_2017 = pd.read_csv("acs2017_county_data.csv")

df_2015["Year"] = 2015
df_2017["Year"] = 2017

df = pd.concat([df_2015, df_2017], ignore_index=True)
df.columns = df.columns.str.strip()

numeric_cols = [
    "Income", "IncomePerCap", "Poverty", "ChildPoverty",
    "Professional", "Service", "Office", "Construction", "Production",
    "Unemployment"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["State", "County", "Income", "Poverty"])

# title
st.title("Industry, Household & Children: A Multi-Perspective Analysis of U.S. Poverty")
st.markdown(
    "This dashboard compares county-level data from **2015** and **2017** to explore "
    "how occupational structure relates to **poverty** and **income** across U.S. counties."
)

# Feature Selection
f1, f2, f3 = st.columns(3)

with f1:
    year = st.selectbox("Year", [2015, 2017])

with f2:
    selected_state = st.selectbox(
        "State",
        ["All"] + sorted(df["State"].dropna().unique().tolist())
    )

with f3:
    poverty_range = st.slider(
        "Poverty Range",
        float(df["Poverty"].min()),
        float(df["Poverty"].max()),
        (float(df["Poverty"].min()), float(df["Poverty"].max()))
    )

# filter
filtered_df = df[df["Year"] == year].copy()

if selected_state != "All":
    filtered_df = filtered_df[filtered_df["State"] == selected_state]

filtered_df = filtered_df[
    (filtered_df["Poverty"] >= poverty_range[0]) &
    (filtered_df["Poverty"] <= poverty_range[1])
]

# KPI
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Counties Shown", f"{filtered_df.shape[0]:,}")
with k2:
    st.metric("Average Poverty", f"{filtered_df['Poverty'].mean():.1f}%")
with k3:
    st.metric("Average Income", f"${filtered_df['Income'].mean():,.0f}")

st.markdown("---")

state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}


# ===== section 1: State-Level Map =====
st.subheader(f"State-Level Poverty and Dominant Occupation ({year})")

occupation_cols = ["Professional", "Service", "Office", "Construction", "Production"]

# statesummary
state_summary = (
    filtered_df.groupby("State", as_index=False)
    .agg({
        "Poverty": "mean",
        "Income": "mean",
        **{col: "mean" for col in occupation_cols}
    })
)

# dominant occupation
national_avg = filtered_df[occupation_cols].mean()

for col in occupation_cols:
    state_summary[col + "_diff"] = state_summary[col] - national_avg[col]

diff_cols = [col + "_diff" for col in occupation_cols]

state_summary["Dominant Occupation"] = (
    state_summary[diff_cols]
    .idxmax(axis=1)
    .str.replace("_diff", "", regex=False)
)

# Short
occ_short = {
    "Professional": "Prof",
    "Service": "Serv",
    "Office": "Off",
    "Construction": "Const",
    "Production": "Prod"
}
state_summary["Occ Short"] = state_summary["Dominant Occupation"].map(occ_short)

# abbrev
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}
state_summary["State Code"] = state_summary["State"].map(state_abbrev)
state_summary = state_summary.dropna(subset=["State Code"])

# show name
state_summary["Label"] = state_summary["State Code"] + "<br>" + state_summary["Occ Short"]

# mid point
state_centers = {
    "AL": (32.8, -86.8), "AK": (64.0, -152.0), "AZ": (34.2, -111.7), "AR": (34.8, -92.2),
    "CA": (37.2, -119.5), "CO": (39.0, -105.5), "CT": (41.6, -72.7), "DE": (39.0, -75.5),
    "FL": (28.4, -82.4), "GA": (32.7, -83.3), "HI": (20.8, -157.5), "ID": (44.2, -114.0),
    "IL": (40.0, -89.2), "IN": (40.0, -86.1), "IA": (42.1, -93.5), "KS": (38.5, -98.0),
    "KY": (37.5, -85.3), "LA": (31.0, -92.0), "ME": (45.3, -69.0), "MD": (39.0, -76.7),
    "MA": (42.3, -71.8), "MI": (44.3, -85.4), "MN": (46.3, -94.2), "MS": (32.7, -89.7),
    "MO": (38.5, -92.5), "MT": (46.9, -110.4), "NE": (41.5, -99.7), "NV": (39.3, -116.6),
    "NH": (43.7, -71.6), "NJ": (40.1, -74.7), "NM": (34.4, -106.1), "NY": (42.9, -75.0),
    "NC": (35.5, -79.4), "ND": (47.5, -100.5), "OH": (40.4, -82.8), "OK": (35.6, -97.5),
    "OR": (43.9, -120.6), "PA": (41.0, -77.6), "RI": (41.7, -71.5), "SC": (33.8, -80.9),
    "SD": (44.4, -100.2), "TN": (35.8, -86.4), "TX": (31.5, -99.3), "UT": (39.3, -111.7),
    "VT": (44.1, -72.7), "VA": (37.5, -78.7), "WA": (47.4, -120.7), "WV": (38.6, -80.6),
    "WI": (44.5, -89.5), "WY": (43.0, -107.6), "DC": (38.9, -77.0)
}

state_summary["lat"] = state_summary["State Code"].map(lambda x: state_centers[x][0])
state_summary["lon"] = state_summary["State Code"].map(lambda x: state_centers[x][1])

map_left, map_right = st.columns([4, 1.4])

with map_left:
    fig_map = px.choropleth(
        state_summary,
        locations="State Code",
        locationmode="USA-states",
        color="Poverty",
        scope="usa",
        hover_name="State",
        hover_data={
            "State Code": False,
            "Poverty": ':.1f',
            "Income": ':,.0f',
            "Dominant Occupation": True,
            "Occ Short": False,
            "lat": False,
            "lon": False,
            "Label": False
        },
        color_continuous_scale="OrRd",
        labels={
            "Poverty": "Avg Poverty Rate (%)",
            "Income": "Avg Income",
            "Dominant Occupation": "Dominant Occupation"
        }
    )

    # add name+occupation
    fig_map.add_scattergeo(
        locations=state_summary["State Code"],
        locationmode="USA-states",
        text=state_summary["Label"],
        mode="text",
        textfont=dict(size=9, color="black"),
        hoverinfo="skip"
    )

    fig_map.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        height=560,
        geo=dict(bgcolor="rgba(0,0,0,0)")
    )

    st.plotly_chart(fig_map, use_container_width=True)

with map_right:
    st.markdown("### Map Insight")

    if len(state_summary) > 0:
        top_state = state_summary.sort_values("Poverty", ascending=False).iloc[0]
        low_state = state_summary.sort_values("Poverty", ascending=True).iloc[0]

        occ_counts = (
            state_summary["Dominant Occupation"]
            .value_counts()
            .reset_index()
        )
        occ_counts.columns = ["Occupation", "State Count"]

        st.write(f"States shown: **{len(state_summary)}**")
        st.write(f"Highest avg poverty: **{top_state['State']} ({top_state['Poverty']:.1f}%)**")
        st.write(f"Lowest avg poverty: **{low_state['State']} ({low_state['Poverty']:.1f}%)**")

        st.markdown("**Dominant occupation across states:**")
        for _, row in occ_counts.iterrows():
            st.write(f"- {row['Occupation']}: **{row['State Count']} states**")

        st.info("Color shows average poverty by state. Text shows state abbreviation and dominant occupation.")
    else:
        st.write("No state-level data available for the current selection.")

st.caption("Color indicates average poverty rate. Each state label shows the state abbreviation and dominant occupation.")

st.markdown("---")

# ===== Section 2: Poverty Distribution =====
st.subheader(f"Poverty Distribution ({year})")

left1, right1 = st.columns([3, 1])

with left1:
    fig1 = px.histogram(
        filtered_df,
        x="Poverty",
        nbins=20,
        color_discrete_sequence=["#E45756"]
    )
    fig1.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Poverty Rate",
        yaxis_title="Number of Counties"
    )
    st.plotly_chart(fig1, use_container_width=True)

with right1:
    avg_poverty = filtered_df["Poverty"].mean()
    median_poverty = filtered_df["Poverty"].median()
    max_poverty = filtered_df["Poverty"].max()
    min_poverty = filtered_df["Poverty"].min()

    high_poverty_count = (filtered_df["Poverty"] >= 20).sum()
    high_poverty_pct = high_poverty_count / len(filtered_df) * 100 if len(filtered_df) > 0 else 0

    st.markdown("### Quick Analysis")
    st.write(f"Average poverty rate: **{avg_poverty:.1f}%**")
    st.write(f"Median poverty rate: **{median_poverty:.1f}%**")
    st.write(f"Range: **{min_poverty:.1f}% – {max_poverty:.1f}%**")
    st.write(f"Counties with poverty ≥ 20%: **{high_poverty_count}**")
    st.write(f"Share of high-poverty counties: **{high_poverty_pct:.1f}%**")

    if avg_poverty >= 20:
        st.info("Poverty is relatively high in the current selection.")
    elif avg_poverty >= 12:
        st.info("Poverty is moderate in the current selection.")
    else:
        st.info("Poverty is relatively low in the current selection.")

st.caption("This chart shows how poverty rates are distributed across counties in the selected data.")

#occupation

st.markdown("---")

st.subheader("Select Occupation for Analysis")

occupation_col = st.selectbox(
    "Occupation",
    ["Professional", "Service", "Office", "Construction", "Production"]
)
st.markdown("---")

# ===== Section 3: Poverty vs Occupation =====

st.subheader(f"{occupation_col} vs Poverty ({year})")

left4, right4 = st.columns([3, 1])

# ===== left =====
with left4:
    fig4 = px.scatter(
        filtered_df,
        x=occupation_col,
        y="Poverty",
        hover_name="County",
        hover_data=["State"],
        trendline="ols",
        color_discrete_sequence=["#2A9D8F"]
    )

    fig4.update_traces(marker=dict(size=5, opacity=0.5))

    fig4.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title=occupation_col,
        yaxis_title="Poverty Rate"
    )

    st.plotly_chart(fig4, use_container_width=True)


# ===== right =====
with right4:
    st.markdown("### Trend Analysis")

    if len(filtered_df) > 0:
        corr = filtered_df[occupation_col].corr(filtered_df["Poverty"])
        avg_occ = filtered_df[occupation_col].mean()
        avg_poverty = filtered_df["Poverty"].mean()

        st.write(f"Average {occupation_col}: **{avg_occ:.1f}%**")
        st.write(f"Average poverty: **{avg_poverty:.1f}%**")
        st.write(f"Correlation: **{corr:.2f}**")

        # auto explain
        if corr > 0.4:
            st.warning("Positive relationship")
            st.write(f"Higher {occupation_col.lower()} share is associated with higher poverty.")
        elif corr < -0.4:
            st.success("Negative relationship")
            st.write(f"Higher {occupation_col.lower()} share is associated with lower poverty.")
        else:
            st.info("Weak relationship")
            st.write(f"{occupation_col} does not strongly explain poverty variation.")

    else:
        st.write("No data available.")

st.caption("The share of this occupational group may be associated with different poverty patterns.")

st.markdown("---")

# ===== Section 4: Top 10 Counties by Child Poverty =====
st.subheader(f"Top 10 Counties by Child Poverty ({year})")

left2, right2 = st.columns([3, 1])
top_counties["Rank"] = range(len(top_counties), 0, -1)
top_counties = (
    filtered_df[["County", "State", "ChildPoverty"]]
    .sort_values("ChildPoverty", ascending=False)
    .head(10)
    .copy()
)

top_counties["CountyLabel"] = top_counties["County"] + ", " + top_counties["State"]

with left2:
    fig2 = px.bar(
        top_counties,
        x="CountyLabel",
        y="ChildPoverty",
        color="Rank",
        color_continuous_scale="OrRd"
    )
    fig2.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="County",
        yaxis_title="Child Poverty Rate",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with right2:
    st.markdown("### Quick Analysis")

    if len(top_counties) > 0:
        top1 = top_counties.iloc[0]
        avg_top10 = top_counties["ChildPoverty"].mean()

        overall_avg = filtered_df["ChildPoverty"].mean()
        gap = top1["ChildPoverty"] - overall_avg

        st.write(f"Highest child-poverty county: **{top1['County']}, {top1['State']}**")
        st.write(f"Top child poverty rate: **{top1['ChildPoverty']:.1f}%**")
        st.write(f"Average among top 10 counties: **{avg_top10:.1f}%**")
        st.write(f"Gap from overall average: **{gap:.1f} percentage points**")

        if gap > 10:
            st.info("Child poverty is highly concentrated in the top counties, indicating strong inequality.")
        else:
            st.info("Child poverty levels are moderately higher in top counties.")
    else:
        st.write("No data available for the current selection.")

st.caption("This chart highlights counties with the highest child poverty rates.")

st.markdown("---")
