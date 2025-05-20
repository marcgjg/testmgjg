# streamlit_app.py
# -------------------------------------------------------
#  🎯  Guess the Industry’s Capital-Market Coordinates
# -------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import io
import requests

# ─────────────── CONSTANTS ──────────────── #
CSV_URL   = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
# tiny fallback sample – extend / replace with full table if you like
SAMPLE_CSV = """
Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
Alcoholic Beverages,0.74,6.14%,16.24%
Auto & Truck,1.19,7.83%,26.49%
Bank (Money Center),1.33,8.38%,86.93%
"""

AXES = dict(
    debt_pct=(0, 100),          # x-axis  (int)
    beta=(0.0, 3.0),            # y-axis  (float)
    wacc=(0.0, 20.0),           # z-axis  (float)
)

# ─────────────── DATA HELPERS ─────────────── #
def clean(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Return tidy DataFrame with Industry · DebtPct · Beta · WACC."""
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

@st.cache_data(show_spinner="Downloading Damodaran CSV …", ttl=24 * 3600)
def fetch_remote_csv() -> pd.DataFrame | None:
    """Attempt to download the CSV. Return None on failure."""
    try:
        resp = requests.get(CSV_URL, timeout=10)
        resp.raise_for_status()
        return clean(pd.read_csv(io.StringIO(resp.text)))
    except Exception:
        return None

def load_industry_data(uploaded_file) -> tuple[pd.DataFrame, str]:
    """
    1️⃣ remote CSV if reachable,
    2️⃣ user-uploaded file,
    3️⃣ built-in sample.
    """
    df_remote = fetch_remote_csv()
    if df_remote is not None:
        return df_remote, "remote CSV"

    # user-supplied file
    if uploaded_file is not None:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            df_up = pd.read_csv(uploaded_file)
        elif name.endswith((".xls", ".xlsx")):
            df_up = pd.read_excel(uploaded_file, sheet_name=0)
        else:
            st.error("Please upload CSV or Excel (.xls/.xlsx).")
            st.stop()
        return clean(df_up), "uploaded file"

    # built-in tiny sample
    df_sample = pd.read_csv(io.StringIO(SAMPLE_CSV))
    return clean(df_sample), "built-in sample"


# ─────────────── PAGE CONFIG ─────────────── #
st.set_page_config(page_title="Industry WACC Guessing Game",
                   page_icon="🎯", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">🎯 Guess the Industry’s Capital-Market Coordinates</h1>',
    unsafe_allow_html=True,
)

# ─────────────── DATA LOAD ──────────────── #
uploaded_file = st.sidebar.file_uploader(
    "⬆️ Upload Damodaran CSV/XLS (optional)",
    type=["csv", "xls", "xlsx"]
)
data, data_source = load_industry_data(uploaded_file)
st.sidebar.caption(f"Data source: {data_source}")

# ─────────────── SESSION STATE ───────────── #
all_industries = data["Industry"].tolist()
if "current_ind" not in st.session_state:
    st.session_state.current_ind = random.choice(all_industries)
if "revealed" not in st.session_state:
    st.session_state.revealed = False

def new_random_industry():
    st.session_state.current_ind = random.choice(all_industries)
    st.session_state.revealed = False

# ─────────────── SIDEBAR ─────────────── #
sb = st.sidebar
sb.button("🎲 New random industry", on_click=new_random_industry)

picked = sb.selectbox(
    "…or choose one yourself",
    all_industries,
    index=all_industries.index(st.session_state.current_ind),
    key="ind_select"
)
st.session_state.current_ind = picked

sb.markdown("---")
sb.markdown("### Your guess")

# Debt slider (all int args)
g_debt = sb.slider("Debt / (Debt + Equity) %",
                   AXES["debt_pct"][0], AXES["debt_pct"][1],
                   50, 1)

# Beta slider (all float args)
beta_min, beta_max = AXES["beta"]
g_beta = sb.slider("Beta",
                   float(beta_min), float(beta_max),
                   1.0, 0.01)

# WACC slider (all float args)
wacc_min, wacc_max = AXES["wacc"]
g_wacc = sb.slider("Cost of Capital %",
                   float(wacc_min), float(wacc_max),
                   8.0, 0.05)

if sb.button("Check guess"):
    st.session_state.revealed = True

# ─────────────── MAIN LAYOUT ─────────────── #
left, right = st.columns([2, 1])

# ---------- 3-D Scatter ---------- #
with left:
    st.subheader("3-D Industry Map")
    fig = go.Figure()

    # all industries · grey dots
    fig.add_trace(
        go.Scatter3d(
            x=data["DebtPct"], y=data["Beta"], z=data["WACC"],
            mode="markers",
            marker=dict(size=4, color="#d1d5db"),
            text=data["Industry"],
            hovertemplate="<b>%{text}</b><br>Debt %%: %{x:.1f}<br>"
                          "Beta: %{y:.2f}<br>WACC %%: %{z:.2f}",
            name="All industries",
        )
    )
    # student's guess · blue diamond
    fig.add_trace(
        go.Scatter3d(
            x=[g_debt], y=[g_beta], z=[g_wacc],
            mode="markers+text",
            marker=dict(size=6, symbol="diamond", color="#3b82f6"),
            text=["Your guess"], textposition="top center",
            name="Your guess",
        )
    )
    # actual point · red dot (after reveal)
    if st.session_state.revealed:
        actual = data.set_index("Industry").loc[st.session_state.current_ind]
        fig.add_trace(
            go.Scatter3d(
                x=[actual["DebtPct"]], y=[actual["Beta"]], z=[actual["WACC"]],
                mode="markers+text",
                marker=dict(size=6, symbol="circle", color="#ef4444"),
                text=["Actual"], textposition="bottom center",
                name="Actual",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Debt / (Debt + Equity) %",
                       range=list(AXES["debt_pct"])),
            yaxis=dict(title="Beta",
                       range=list(AXES["beta"])),
            zaxis=dict(title="Cost of Capital %",
                       range=list(AXES["wacc"])),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- Feedback panel ---------- #
with right:
    st.subheader("Your task")
    st.write(f"**Target industry:** **{st.session_state.current_ind}**")

    if not st.session_state.revealed:
        st.info("Adjust the sliders and press **Check guess**.")
    else:
        act = data.set_index("Industry").loc[st.session_state.current_ind]
        dx, dy, dz = (g_debt - act["DebtPct"],
                      g_beta - act["Beta"],
                      g_wacc - act["WACC"])
        dist = np.sqrt(
            (dx / AXES["debt_pct"][1]) ** 2 +
            (dy / AXES["beta"][1]) ** 2 +
            (dz / AXES["wacc"][1]) ** 2
        )
        st.success(
            f"**Actual values**\n\n"
            f"* Debt ratio: **{act['DebtPct']:.1f}%**\n"
            f"* Beta: **{act['Beta']:.2f}**\n"
            f"* WACC: **{act['WACC']:.2f}%**"
        )
        st.write(
            f"Absolute errors → "
            f"Debt {abs(dx):.1f} pp, "
            f"Beta {abs(dy):.2f}, "
            f"WACC {abs(dz):.2f} pp"
        )
        st.write(f"Normalised distance ≈ **{dist:.3f}**")
        st.button("Try another industry →", on_click=new_random_industry)

# ---------- Footer ---------- #
st.markdown(
    '<div style="text-align:center; color:#6B7280; padding-top:1rem;">'
    'Damodaran dataset | App by ChatGPT</div>',
    unsafe_allow_html=True,
)
