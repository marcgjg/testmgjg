# streamlit_app.py  –  drag-and-drop guessing game
# requires: streamlit-sortables>=0.3.1
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random, io, requests
from streamlit_sortables import sort_items     # ← new import

# ───────────── constants ───────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SAMPLE_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
Alcoholic Beverages,0.74,6.14%,16.24%
Auto & Truck,1.19,7.83%,26.49%
Bank (Money Center),1.33,8.38%,86.93%"""
AXES = dict(debt_pct=(0, 100), beta=(0.0, 3.0), wacc=(0.0, 20.0))

# ───────────── helpers ───────────── #
def tidy(df):
    df = df[["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]].copy()
    df["DebtPct"] = df["D/(D+E)"].str.rstrip("%").str.replace(",", "").astype(float)
    df["Beta"]    = pd.to_numeric(df["Beta"], errors="coerce")
    df["WACC"]    = df["Cost of Capital"].str.rstrip("%").str.replace(",", "").astype(float)
    df = df.dropna(subset=["DebtPct", "Beta", "WACC"])
    df.rename(columns={"Industry Name": "Industry"}, inplace=True)
    return df

@st.cache_data(ttl=24*3600, show_spinner="Downloading Damodaran CSV …")
def remote_csv():
    try:
        r = requests.get(CSV_URL, timeout=10)
        r.raise_for_status()
        return tidy(pd.read_csv(io.StringIO(r.text)))
    except Exception:
        return None

def load_data(upload):
    df = remote_csv()
    if df is not None:
        return df, "remote CSV"
    if upload is not None:
        if upload.name.lower().endswith(".csv"):
            return tidy(pd.read_csv(upload)), "uploaded CSV"
        return tidy(pd.read_excel(upload)), "uploaded Excel"
    return tidy(pd.read_csv(io.StringIO(SAMPLE_CSV))), "built-in sample"

# ───────────── UI & state ───────────── #
st.set_page_config("Industry drag-and-drop", "🎯", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">🎯 Drag the industry names onto the points</h1>',
            unsafe_allow_html=True)

upload = st.sidebar.file_uploader("Upload Damodaran CSV/XLS (optional)",
                                  type=["csv", "xls", "xlsx"])
data, src = load_data(upload)
st.sidebar.caption(f"Data source: {src}")

n_points = st.sidebar.slider("Number of random industries", 1, 10, 3)

# initialise / reset game
if st.sidebar.button("🚀 Start new game"):
    st.session_state.targets = random.sample(list(data["Industry"]), k=n_points)
    st.session_state.score = 0
    st.session_state.finished = False
    # containers: Available + Point 1..n
    st.session_state.containers = (
        [{"header": "Available", "items": st.session_state.targets.copy()}] +
        [{"header": f"Point {i+1}", "items": []} for i in range(n_points)]
    )

# first load sentinel
if "containers" not in st.session_state:
    st.session_state.targets = random.sample(list(data["Industry"]), k=n_points)
    st.session_state.score = 0
    st.session_state.finished = False
    st.session_state.containers = (
        [{"header": "Available", "items": st.session_state.targets.copy()}] +
        [{"header": f"Point {i+1}", "items": []} for i in range(n_points)]
    )

targets   = st.session_state.targets
score     = st.session_state.score
finished  = st.session_state.finished
containers = st.session_state.containers

subset = data[data["Industry"].isin(targets)].reset_index(drop=True)

# ───────────── layout ───────────── #
left, right = st.columns([2, 1])

with left:
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=subset["DebtPct"], y=subset["Beta"], z=subset["WACC"],
        mode="markers+text",
        marker=dict(size=6, color="#9ca3af"),
        text=[str(i+1) for i in range(len(subset))],
        textposition="top center",
        hovertemplate="Point %{text}<br>Debt %% %{x:.1f}<br>Beta %{y:.2f}<br>WACC %% %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Debt %", range=list(AXES["debt_pct"])),
            yaxis=dict(title="Beta",  range=list(AXES["beta"])),
            zaxis=dict(title="WACC %",range=list(AXES["wacc"])),
        ),
        margin=dict(l=0, r=0, t=0, b=0), height=650, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Drag the names")
    sorted_containers = sort_items(containers, multi_containers=True,
                                   direction="vertical")
    st.session_state.containers = sorted_containers   # keep updates

    if st.button("✅ Submit answers", disabled=finished):
        correct, wrong = 0, 0
        for i in range(1, len(sorted_containers)):          # skip “Available”
            box_items = sorted_containers[i]["items"]
            if not box_items:
                continue
            guess = box_items[0]
            actual = subset.loc[i-1, "Industry"]
            if guess == actual:
                correct += 1
            else:
                wrong += 1
        score += correct - wrong
        st.session_state.score = score

        if wrong == 0 and correct == n_points:
            st.success(f"🎉 Perfect!  Score {score}")
            st.session_state.finished = True
        elif score < 0:
            st.error("💥 Score below zero – Game over.")
            st.session_state.finished = True
        else:
            st.info(f"+{correct} / –{wrong} → score {score}")

    st.markdown(f"### Current score : **{score}**")
    if finished:
        st.markdown("---")
        st.markdown("#### Solution")
        for i in range(len(subset)):
            st.write(f"Point {i+1} → {subset.loc[i,'Industry']}")

st.markdown(
    '<div style="text-align:center; color:#6B7280; padding-top:1rem;">'
    'Damodaran dataset · Component: streamlit-sortables · App by ChatGPT</div>',
    unsafe_allow_html=True,
)
