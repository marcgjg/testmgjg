# streamlit_app.py  –  DRAG-AND-DROP GUESSING GAME
# ----------------------------------------------------
# pip install streamlit-sortable
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import io
import requests

from streamlit_sortable import sortable   # <-- drag-and-drop component

# ─────────────────  CONSTANTS  ───────────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SAMPLE_CSV = """
Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
Alcoholic Beverages,0.74,6.14%,16.24%
Auto & Truck,1.19,7.83%,26.49%
Bank (Money Center),1.33,8.38%,86.93%
"""
AXES = dict(debt_pct=(0, 100), beta=(0.0, 3.0), wacc=(0.0, 20.0))

# ───────────────  DATA HELPERS  ─────────────── #
def clean(raw: pd.DataFrame) -> pd.DataFrame:
    req = ["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]
    df = raw.loc[:, req].copy()
    df["DebtPct"] = df["D/(D+E)"].str.rstrip("%").str.replace(",", "").astype(float)
    df["Beta"]    = pd.to_numeric(df["Beta"], errors="coerce")
    df["WACC"]    = df["Cost of Capital"].str.rstrip("%").str.replace(",", "").astype(float)
    df = df.dropna(subset=["DebtPct", "Beta", "WACC"])
    df.rename(columns={"Industry Name": "Industry"}, inplace=True)
    return df

@st.cache_data(ttl=24 * 3600, show_spinner="Downloading Damodaran CSV …")
def fetch_remote() -> pd.DataFrame | None:
    try:
        r = requests.get(CSV_URL, timeout=10)
        r.raise_for_status()
        return clean(pd.read_csv(io.StringIO(r.text)))
    except Exception:
        return None

def get_data(uploaded) -> tuple[pd.DataFrame, str]:
    """Remote → upload → sample."""
    df = fetch_remote()
    if df is not None:
        return df, "remote CSV"
    if uploaded is not None:
        fn = uploaded.name.lower()
        if fn.endswith(".csv"):
            return clean(pd.read_csv(uploaded)), "uploaded CSV"
        elif fn.endswith((".xls", ".xlsx")):
            return clean(pd.read_excel(uploaded, sheet_name=0)), "uploaded Excel"
        else:
            st.error("Upload CSV or Excel only."); st.stop()
    sample = pd.read_csv(io.StringIO(SAMPLE_CSV))
    return clean(sample), "built-in sample"

# ───────────────  PAGE CONFIG  ─────────────── #
st.set_page_config("Industry WACC Drag-and-Drop", "🎯", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">🎯 Industry Capital-Market Drag-and-Drop</h1>',
    unsafe_allow_html=True,
)

# ───────────────  LOAD DATA  ─────────────── #
uploaded_file = st.sidebar.file_uploader(
    "⬆️ (optional) Upload Damodaran CSV/XLS",
    type=["csv", "xls", "xlsx"],
)
data, src = get_data(uploaded_file)
st.sidebar.caption(f"Data source: {src}")

# ───────────────  GAME CONTROLS  ─────────────── #
st.sidebar.markdown("---")
num_points = st.sidebar.slider("Number of random industries", 1, 10, 3)

# Initialise / reset game
if st.sidebar.button("🎮 Start new game"):
    st.session_state.target_inds = random.sample(list(data["Industry"]), k=num_points)
    st.session_state.score = 0
    st.session_state.revealed = False
    # drag-and-drop groups
    st.session_state.groups = {
        "Available": st.session_state.target_inds.copy(),
    }
    for i in range(num_points):
        st.session_state.groups[f"Point {i+1}"] = []

# Make sure game data exists on first load
if "groups" not in st.session_state:
    st.session_state.target_inds = random.sample(list(data["Industry"]), k=num_points)
    st.session_state.score = 0
    st.session_state.revealed = False
    st.session_state.groups = {
        "Available": st.session_state.target_inds.copy(),
    }
    for i in range(num_points):
        st.session_state.groups[f"Point {i+1}"] = []

target_inds = st.session_state.target_inds
groups      = st.session_state.groups
score       = st.session_state.score
revealed    = st.session_state.revealed
num_points  = len(target_inds)

# ───────────────  SUBSET DATA FOR PLOT  ─────────────── #
subset = data[data["Industry"].isin(target_inds)].reset_index(drop=True)

# ───────────────  PLOT  ─────────────── #
left, right = st.columns([2, 1])

with left:
    st.subheader("Drag these labels onto the numbered points")
    # build numbered labels for points
    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=subset["DebtPct"], y=subset["Beta"], z=subset["WACC"],
            mode="markers+text",
            marker=dict(size=6, color="#9CA3AF"),  # slate-400
            text=[str(i+1) for i in range(num_points)],
            textposition="top center",
            hovertemplate=(
                "Point %{text}<br>Debt %% %{x:.1f}<br>"
                "Beta %{y:.2f}<br>WACC %% %{z:.2f}<extra></extra>"
            ),
            name="Targets",
        )
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Debt / (Debt + Equity) %",
                       range=list(AXES["debt_pct"])),
            yaxis=dict(title="Beta", range=list(AXES["beta"])),
            zaxis=dict(title="Cost of Capital %",
                       range=list(AXES["wacc"])),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# ───────────────  DRAG-AND-DROP UI  ─────────────── #
with right:
    st.subheader("Match the labels")
    st.caption("Drag from **Available** onto the numbered drop-zones, "
               "then press **Submit answers**.")
    groups = sortable(
        groups,
        multi_drag=True,
        direction="vertical",
        key="sortable",
        # style tweaks
        drag_handle="⠿",
        labels_style={
            "background-color": "#e5e7eb",
            "padding": "0.25rem 0.5rem",
            "border-radius": "0.375rem",
        },
        group_title_style={"font-weight": "600", "margin": "0.5rem 0"},
    )
    st.session_state.groups = groups  # keep latest ordering

    if st.button("✅ Submit answers"):
        # evaluate only items in each Point slot (ignore empties)
        correct, wrong = 0, 0
        for i in range(num_points):
            box = groups.get(f"Point {i+1}", [])
            if not box:
                continue  # still empty
            guess = box[0]
            actual = subset.loc[i, "Industry"]
            if guess == actual:
                correct += 1
            else:
                wrong += 1
        # update score
        score += correct - wrong
        st.session_state.score = score

        # feedback
        if wrong == 0 and correct == num_points:
            revealed = True
            st.session_state.revealed = True
            st.success(f"🎉 Perfect! You matched all {num_points} points. "
                       f"Final score: **{score}**")
        elif score < 0:
            st.error("💥 Score went below zero – **Game over**.")
            revealed = True
            st.session_state.revealed = True
        else:
            st.info(f"Correct +{correct} · Wrong –{wrong} → "
                    f"Current score **{score}**")

    st.markdown(f"### Current score: **{score}**")

    if revealed:
        st.markdown("---")
        st.markdown("#### Actual mapping")
        for i in range(num_points):
            st.write(f"Point **{i+1}** → {subset.loc[i, 'Industry']}")

# ───────────────  FOOTER  ─────────────── #
st.markdown(
    '<div style="text-align:center; color:#6B7280; padding-top:1rem;">'
    'Damodaran dataset · Drag-and-drop component by <code>streamlit-sortable</code> '
    '| App by ChatGPT</div>',
    unsafe_allow_html=True,
)
