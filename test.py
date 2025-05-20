import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import io
import requests

# ─────────────────────  DATA SOURCES  ───────────────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SAMPLE_CSV = """
Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
Alcoholic Beverages,0.74,6.14%,16.24%
Auto & Truck,1.19,7.83%,26.49%
Bank (Money Center),1.33,8.38%,86.93%
"""  # ← extend/replace with full table if desired

AXES = dict(debt_pct=(0, 100), beta=(0, 3), wacc=(0, 20))

# ─────────────────────  HELPERS  ───────────────────── #
def clean(df_raw: pd.DataFrame) -> pd.DataFrame:
    req = ["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]
    df = df_raw.loc[:, req].copy()
    df["DebtPct"] = (
        df["D/(D+E)"].astype(str).str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False).astype(float)
    )
    df["Beta"] = pd.to_numeric(df["Beta"], errors="coerce")
    df["WACC"] = (
        df["Cost of Capital"].astype(str).str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False).astype(float)
    )
    df = df.dropna(subset=["DebtPct", "Beta", "WACC"])
    df.rename(columns={"Industry Name": "Industry"}, inplace=True)
    return df

@st.cache_data(show_spinner="Fetching Damodaran CSV …", ttl=24*3600)
def try_remote_csv() -> pd.DataFrame | None:
    try:
        r = requests.get(CSV_URL, timeout=10)
        r.raise_for_status()
        return clean(pd.read_csv(io.StringIO(r.text)))
    except Exception:
        return None

def load_industry_data(uploaded_file) -> pd.DataFrame:
    # 1️⃣ remote if available
    df = try_remote_csv()
    if df is not None:
        return df, "remote CSV"

    # 2️⃣ user-supplied file
    if uploaded_file is not None:
        ext = uploaded_file.name.lower()
        if ext.endswith(".csv"):
            df_up = pd.read_csv(uploaded_file)
        elif ext.endswith((".xls", ".xlsx")):
            df_up = pd.read_excel(uploaded_file, sheet_name=0)
        else:
            st.error("Unsupported file type. Please upload CSV or Excel.")
            st.stop()
        return clean(df_up), "uploaded file"

    # 3️⃣ built-in mini sample
    df_sample = pd.read_csv(io.StringIO(SAMPLE_CSV))
    return clean(df_sample), "built-in sample"

# ─────────────────────  UI LAYOUT  ───────────────────── #
st.set_page_config("Industry WACC Guess", "🎯", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">🎯 Guess the Industry’s Capital-Market Coordinates</h1>',
    unsafe_allow_html=True,
)

uploaded = st.sidebar.file_uploader(
    "⬆️ Upload Damodaran CSV/XLS (optional)", type=["csv", "xls", "xlsx"]
)
data, source_note = load_industry_data(uploaded)

st.sidebar.caption(f"Data source: {source_note}")

# ────── game state ──────
all_inds = data["Industry"].tolist()
if "current" not in st.session_state:
    st.session_state.current = random.choice(all_inds)
if "revealed" not in st.session_state:
    st.session_state.revealed = False


def choose_new():
    st.session_state.current = random.choice(all_inds)
    st.session_state.revealed = False


st.sidebar.button("🎲 New random industry", on_click=choose_new)
picked = st.sidebar.selectbox(
    "…or choose one yourself",
    all_inds,
    index=all_inds.index(st.session_state.current),
    key="ind_sel",
)
st.session_state.current = picked

st.sidebar.markdown("---")
st.sidebar.markdown("### Your guess")
g_debt = st.sidebar.slider("Debt / (Debt + Equity) %", *AXES["debt_pct"], 50)
g_beta = st.sidebar.slider("Beta", *AXES["beta"], 1.0, 0.01)
g_wacc = st.sidebar.slider("Cost of Capital %", *AXES["wacc"], 8.0, 0.05)

if st.sidebar.button("Check guess"):
    st.session_state.revealed = True

# ─────────── 3-D plot ───────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("3-D Industry Map")
    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=data["DebtPct"],
            y=data["Beta"],
            z=data["WACC"],
            mode="markers",
            marker=dict(size=4, color="#d1d5db"),
            text=data["Industry"],
            hovertemplate=(
                "<b>%{text}</b><br>Debt %%: %{x:.1f}<br>"
                "Beta: %{y:.2f}<br>WACC %%: %{z:.2f}"
            ),
            name="All industries",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[g_debt], y=[g_beta], z=[g_wacc],
            mode="markers+text",
            marker=dict(size=6, symbol="diamond", color="#3b82f6"),
            text=["Your guess"], textposition="top center",
            name="Your guess",
        )
    )
    if st.session_state.revealed:
        act = data.set_index("Industry").loc[st.session_state.current]
        fig.add_trace(
            go.Scatter3d(
                x=[act["DebtPct"]], y=[act["Beta"]], z=[act["WACC"]],
                mode="markers+text",
                marker=dict(size=6, symbol="circle", color="#ef4444"),
                text=["Actual"], textposition="bottom center",
                name="Actual",
            )
        )
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Debt / (Debt + Equity) %", range=list(AXES["debt_pct"])),
            yaxis=dict(title="Beta", range=list(AXES["beta"])),
            zaxis=dict(title="Cost of Capital %", range=list(AX
