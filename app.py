from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="TN Mandi Price Intelligence", page_icon="🍅", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
.reco {padding: 1rem 1.25rem; border-radius: 12px; background: #0f3d2e;
       border-left: 6px solid #22c55e; color: #e8fff3; font-size: 1.05rem; margin: 0.5rem 0 1rem 0;}
.reco b {color: #86efac;}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent
DB = (ROOT / "data" / "mandi.duckdb").as_posix()


@st.cache_data(ttl=3600)
def load_data():
    con = duckdb.connect(DB, read_only=True)
    df = con.execute("SELECT * FROM clean_prices").df()
    con.close()
    df["arrival_date"] = pd.to_datetime(df["arrival_date"])
    return df


def price_chart(data):
    fig = px.bar(
        data, x="modal_kg", y="market", orientation="h",
        color="modal_kg", color_continuous_scale="RdYlGn_r",
        text=data["modal_kg"].round(1), hover_data=["district"],
    )
    fig.update_layout(
        height=36 * len(data) + 100, coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", title=None),
        xaxis_title="Rs per kg", margin=dict(l=0, r=0, t=10, b=0),
    )
    return fig


df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
commodities = sorted(df["commodity"].unique())
default = commodities.index("Tomato") if "Tomato" in commodities else 0
commodity = st.sidebar.selectbox("Commodity", commodities, index=default)

districts = sorted(df["district"].dropna().unique())
picked = st.sidebar.multiselect("District (empty = all)", districts)
top_n = st.sidebar.slider("Markets to show", 5, 20, 10)

# ---------- Data for selection ----------
d = df[df["commodity"] == commodity]
if picked:
    d = d[d["district"].isin(picked)]

st.title("🍅 Tamil Nadu Mandi Price Intelligence")
st.caption("Where is it cheapest to buy? Source: Agmarknet via data.gov.in")

if d.empty:
    st.warning("No data for this selection. Try another commodity or district.")
    st.stop()

latest = d["arrival_date"].max()
today = d[d["arrival_date"] == latest]
by_market = (
    today.groupby(["market", "district"], as_index=False)["modal_kg"]
    .mean().sort_values("modal_kg")
)

if len(by_market) < 2:
    st.info("Only one market reporting for this selection, so no comparison is possible.")
    st.dataframe(by_market)
    st.stop()

cheap, dear = by_market.iloc[0], by_market.iloc[-1]
avg = by_market["modal_kg"].mean()
gap = (dear["modal_kg"] - cheap["modal_kg"]) / dear["modal_kg"] * 100

# ---------- Answer first ----------
st.markdown(
    f'<div class="reco">✅ <b>Best buy today:</b> {cheap["market"]} ({cheap["district"]}) '
    f'at <b>Rs {cheap["modal_kg"]:.1f}/kg</b>. '
    f'Buying here instead of {dear["market"]} saves up to <b>{gap:.0f}%</b>.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cheapest", f"Rs {cheap['modal_kg']:.1f}/kg")
c2.metric("Average", f"Rs {avg:.1f}/kg")
c3.metric("Most expensive", f"Rs {dear['modal_kg']:.1f}/kg")
c4.metric("Markets reporting", len(by_market))
st.caption(f"Data date: {latest.date()}")

# ---------- Tabs ----------
t1, t2, t3, t4 = st.tabs(["💰 Cheapest vs Dearest", "🗺️ By district", "📈 Trend", "📋 Data"])

with t1:
    a, b = st.columns(2)
    with a:
        st.subheader(f"{top_n} cheapest")
        st.plotly_chart(price_chart(by_market.head(top_n)), use_container_width=True)
    with b:
        st.subheader(f"{top_n} most expensive")
        st.plotly_chart(price_chart(by_market.tail(top_n).iloc[::-1]), use_container_width=True)

with t2:
    dist = (
        by_market.groupby("district", as_index=False)["modal_kg"].mean()
        .sort_values("modal_kg").rename(columns={"district": "market"})
    )
    dist["district"] = dist["market"]
    st.subheader("Average price by district")
    st.plotly_chart(price_chart(dist.head(15)), use_container_width=True)

with t3:
    daily = d.groupby("arrival_date")["modal_kg"].mean().reset_index()
    if len(daily) > 1:
        fig = px.line(daily, x="arrival_date", y="modal_kg", markers=True)
        fig.update_layout(yaxis_title="Rs per kg", xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Only one day of data so far. A daily collector and forecast are planned for Phase 2.")

with t4:
    show = by_market.rename(columns={"modal_kg": "Rs/kg"}).round(2)
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", show.to_csv(index=False), f"{commodity}_prices.csv", "text/csv")