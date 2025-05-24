import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

st.set_page_config(page_title="WACC Matching Game", layout="wide")

# ---------- Data loading ----------
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
FALLBACK = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22,20.76
Aerospace/Defense,0.90,7.68,18.56
Air Transport,1.24,7.29,51.65
Apparel,0.99,7.44,31.45
Auto & Truck,1.62,10.34,18.30
Banks (Regional),0.52,5.69,37.62
Beverage (Soft),0.57,6.59,16.48
Computer Services,1.23,8.72,20.84
Entertainment,1.04,8.28,16.90
Green & Renewable Energy,1.13,6.50,63.79
Steel,1.06,8.17,20.57
Utility (General),0.39,5.20,43.84"""

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df = df[["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]]
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
        df["WACC"] = df["WACC"].str.rstrip("%").astype(float)
        df["Debt"] = df["Debt"].str.rstrip("%").astype(float)
    except Exception:
        df = pd.read_csv(StringIO(FALLBACK))
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
    return df

df_all = load_data()

# ---------- Session state ----------
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "game_submitted" not in st.session_state:
    st.session_state.game_submitted = False

# ---------- Sidebar ----------
with st.sidebar:
    if not st.session_state.game_active:
        n = st.slider("Number of industries", 2, 10, 5)
        if st.button("Start Game"):
            sample = df_all.sample(n).reset_index(drop=True)
            letters = list(string.ascii_uppercase[:n])

            # TRUE metric strings (kept in order)
            metrics_true = [
                f"Beta: {r['Beta']:.2f}, Debt%: {r['Debt']:.2f}%, WACC: {r['WACC']:.2f}%"
                for _, r in sample.iterrows()
            ]
            # Shuffled copy for dropdowns
            metrics_opts = metrics_true.copy()
            random.shuffle(metrics_opts)

            st.session_state.df = sample
            st.session_state.letters = letters
            st.session_state.metrics_opts = metrics_opts
            st.session_state.true_map = {L: metrics_true[i] for i, L in enumerate(letters)}
            st.session_state.answers = {L: "Select..." for L in letters}

            st.session_state.game_active = True
            st.session_state.game_submitted = False
    elif st.session_state.game_submitted:
        if st.button("Start New Round"):
            st.session_state.game_active = False
            st.session_state.game_submitted = False

# ---------- Main UI ----------
st.title("🎯 Industry WACC Matching Game")

if st.session_state.game_active:
    df = st.session_state.df
    letters = st.session_state.letters

    col_left, col_right = st.columns(2)

    with col_left:
        fig = go.Figure(go.Scatter3d(
            x=df["Beta"], y=df["Debt"], z=df["WACC"],
            text=letters, mode="markers+text", textposition="top center",
            marker=dict(size=6, color="blue")
        ))
        fig.update_layout(scene=dict(
            xaxis_title="Beta", yaxis_title="Debt %", zaxis_title="WACC %"
        ), height=600, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        if not st.session_state.game_submitted:
            st.subheader("Match industries to metrics")
            for i, L in enumerate(letters):
                industry = df.at[i, "Industry"]
                current = st.session_state.answers[L]
                others = {v for k, v in st.session_state.answers.items() if k != L}
                opts = ["Select..."] + [
                    m for m in st.session_state.metrics_opts if m not in others or m == current
                ]
                choice = st.selectbox(f"Point {L}: {industry}", opts,
                                      index=opts.index(current) if current in opts else 0,
                                      key=f"sel_{L}")
                st.session_state.answers[L] = choice

            if st.button("Submit Answers"):
                if "Select..." in st.session_state.answers.values():
                    st.warning("Complete all selections first.")
                elif len(set(st.session_state.answers.values())) < len(letters):
                    st.warning("Each metric can be chosen only once.")
                else:
                    correct = 0
                    results = []
                    for i, L in enumerate(letters):
                        guess = st.session_state.answers[L]
                        actual = st.session_state.true_map[L]
                        mark = "✅" if guess == actual else "❌"
                        if mark == "✅":
                            correct += 1
                        results.append((L, df.at[i, "Industry"], actual, mark))
                    score = correct - 0.5 * (len(letters) - correct)
                    st.session_state.score = score
                    st.session_state.results = results
                    st.session_state.game_submitted = True
                    st.session_state.game_active = False  # unlock sidebar immediately

# ---------- Results ----------
if st.session_state.game_submitted:
    st.subheader(f"Score: {st.session_state.score:.2f}")
    if all(r[3] == "✅" for r in st.session_state.results):
        st.success("Perfect round! 🎉")

    st.subheader("Correct Answers")
    for L, name, metrics, mark in st.session_state.results:
        st.write(f"{mark} Point {L} ({name}) → {metrics}")
