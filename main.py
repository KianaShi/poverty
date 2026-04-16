import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IE6600 Dashboard", layout="wide")

# 读数据
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

# 标题区
st.title("U.S. County Poverty and Occupational Structure Dashboard")
st.markdown(
    "This dashboard compares county-level data from **2015** and **2017** to explore "
    "how occupational structure relates to **poverty** and **income** across U.S. counties."
)

# 顶部筛选区
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

# 过滤
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

# ===== Section 1: Poverty Distribution =====
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


st.markdown("---")

# ===== Section 2: Top 10 Counties by Poverty =====
st.subheader(f"Top 10 Counties by Poverty ({year})")

left2, right2 = st.columns([3, 1])

top_counties = (
    filtered_df[["County", "State", "Poverty"]]
    .sort_values("Poverty", ascending=False)
    .head(10)
    .copy()
)

top_counties["CountyLabel"] = top_counties["County"] + ", " + top_counties["State"]

with left2:
    fig2 = px.bar(
        top_counties,
        x="CountyLabel",
        y="Poverty",
        color="Poverty",
        color_continuous_scale="OrRd"
    )
    fig2.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="County",
        yaxis_title="Poverty Rate",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with right2:
    st.markdown("### Quick Analysis")

    if len(top_counties) > 0:
        top1 = top_counties.iloc[0]
        avg_top10 = top_counties["Poverty"].mean()
        gap = top1["Poverty"] - avg_poverty

        st.write(f"Highest-poverty county: **{top1['County']}, {top1['State']}**")
        st.write(f"Top county poverty rate: **{top1['Poverty']:.1f}%**")
        st.write(f"Average among top 10 counties: **{avg_top10:.1f}%**")
        st.write(f"Gap from overall average: **{gap:.1f} percentage points**")

        if gap > 10:
            st.info("The highest-poverty counties are far above the overall level, suggesting strong inequality across counties.")
        else:
            st.info("The highest-poverty counties are only moderately above the overall level.")
    else:
        st.write("No data available for the current selection.")

st.caption("This chart highlights the counties with the highest poverty rates in the selected data.")




# 图3：Income vs Poverty
st.markdown("---")

st.subheader(f"Income vs Poverty ({year})")

left3, right3 = st.columns([3, 1])

with left3:
    fig3 = px.scatter(
        filtered_df,
        x="Income",
        y="Poverty",
        hover_name="County",
        hover_data=["State"],
        trendline="ols",   # ⭐ 加趋势线
        color_discrete_sequence=["#4C78A8"]
    )

    fig3.update_traces(marker=dict(size=5, opacity=0.5))

    fig3.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Income",
        yaxis_title="Poverty Rate"
    )

    st.plotly_chart(fig3, use_container_width=True)


with right3:
    import numpy as np

    st.markdown("### Trend Analysis")

    if len(filtered_df) > 0:
        corr = filtered_df["Income"].corr(filtered_df["Poverty"])
        avg_income = filtered_df["Income"].mean()
        avg_poverty = filtered_df["Poverty"].mean()

        st.write(f"Average income: **${avg_income:,.0f}**")
        st.write(f"Average poverty: **{avg_poverty:.1f}%**")
        st.write(f"Correlation: **{corr:.2f}**")

        # 自动解释强弱
        if corr < -0.7:
            st.success("Strong negative relationship")
            st.write("Counties with higher income tend to have significantly lower poverty rates.")
        elif corr < -0.4:
            st.info("Moderate negative relationship")
            st.write("Higher income is associated with lower poverty, but with some variation.")
        else:
            st.warning("Weak relationship")
            st.write("Income does not strongly explain poverty in this selection.")

    else:
        st.write("No data available.")

st.caption("Higher-income counties generally tend to have lower poverty rates.")


#选职业

st.markdown("---")

st.subheader("Select Occupation for Analysis")

occupation_col = st.selectbox(
    "Occupation",
    ["Professional", "Service", "Office", "Construction", "Production"]
)

# 图4：Occupation vs Poverty
st.markdown("---")

st.subheader(f"{occupation_col} vs Poverty ({year})")

left4, right4 = st.columns([3, 1])

# ===== 左边：图 =====
with left4:
    fig4 = px.scatter(
        filtered_df,
        x=occupation_col,
        y="Poverty",
        hover_name="County",
        hover_data=["State"],
        trendline="ols",   # ⭐ 加趋势线
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


# ===== 右边：分析 =====
with right4:
    st.markdown("### Trend Analysis")

    if len(filtered_df) > 0:
        corr = filtered_df[occupation_col].corr(filtered_df["Poverty"])
        avg_occ = filtered_df[occupation_col].mean()
        avg_poverty = filtered_df["Poverty"].mean()

        st.write(f"Average {occupation_col}: **{avg_occ:.1f}%**")
        st.write(f"Average poverty: **{avg_poverty:.1f}%**")
        st.write(f"Correlation: **{corr:.2f}**")

        # 自动解释
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

# 可展开数据表
with st.expander("Show Sample Data"):
    st.dataframe(filtered_df[[
        "Year", "State", "County", "Income", "IncomePerCap", "Poverty",
        "Professional", "Service", "Office", "Construction", "Production",
        "Unemployment"
    ]].head(20))

# Insights
st.subheader("Key Insights")
st.write(
    "This dashboard suggests that poverty is not evenly distributed across counties. "
    "Income tends to be negatively associated with poverty, while occupational composition "
    "shows potentially meaningful structural relationships with county-level economic outcomes."
)