import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

st.set_page_config(page_title="WACC Matching Game", layout="wide")

# Load data from Damodaran or fallback
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
FALLBACK_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22%,20.76%
Aerospace/Defense,0.90,7.68%,18.56%
Air Transport,1.24,7.29%,51.65%
Apparel,0.99,7.44%,31.45%
Auto & Truck,1.62,10.34%,18.30%
Banks (Regional),0.52,5.69%,37.62%
Beverage (Soft),0.57,6.59%,16.48%
Computer Services,1.23,8.72%,20.84%
Entertainment,1.04,8.28%,16.90%
Green & Renewable Energy,1.13,6.50%,63.79%
Steel,1.06,8.17%,20.57%
Utility (General),0.39,5.20%,43.84%"""

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
    except Exception:
        df = pd.read_csv(StringIO(FALLBACK_CSV))
    df = df[["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]].copy()
    df.columns = ["Industry", "Beta", "WACC", "Debt"]
    df["WACC"] = df["WACC"].astype(str).str.rstrip("%").astype(float)
    df["Debt"] = df["Debt"].astype(str).str.rstrip("%").astype(float)
    return df

df_full = load_data()

# Initialize session state
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "game_submitted" not in st.session_state:
    st.session_state.game_submitted = False

st.title("🎯 Industry WACC Matching Game")

# Sidebar
with st.sidebar:
    if not st.session_state.game_active:
        num_points = st.slider("Number of industries", 2, 10, 5)
        if st.button("Start Game"):
            sample = df_full.sample(num_points).reset_index(drop=True)
            letters = list(string.ascii_uppercase[:num_points])
            metrics = [
                f"Beta: {r['Beta']:.2f}, Debt%: {r['Debt']:.2f}%, WACC: {r['WACC']:.2f}%"
                for _, r in sample.iterrows()
            ]
            random.shuffle(metrics)
            st.session_state.df = sample
            st.session_state.letters = letters
            st.session_state.metrics = metrics
            st.session_state.mapping = {
                letters[i]: metrics[i] for i in range(num_points)
            }
            st.session_state.answers = {
                L: "Select metrics..." for L in letters
            }
            st.session_state.game_active = True
            st.session_state.game_submitted = False
    elif st.session_state.game_submitted:
        if st.button("Start New Round"):
            st.session_state.game_active = False
            st.session_state.game_submitted = False

# Game UI
if st.session_state.get("game_active"):
    df = st.session_state.df
    letters = st.session_state.letters
    st.plotly_chart(go.Figure(go.Scatter3d(
        x=df["Beta"], y=df["Debt"], z=df["WACC"],
        text=letters, mode="markers+text", textposition="top center",
        marker=dict(size=6, color="blue")
    )).update_layout(
        scene=dict(xaxis_title="Beta", yaxis_title="Debt %", zaxis_title="WACC %"),
        height=600, margin=dict(l=0, r=0, t=20, b=0)
    ), use_container_width=True)

    if not st.session_state.game_submitted:
        st.subheader("Match each industry to its correct metrics")
        taken = set()
        for i, L in enumerate(letters):
            ind = df.at[i, "Industry"]
            current = st.session_state.answers.get(L, "Select metrics...")
            others = set(v for k, v in st.session_state.answers.items() if k != L)
            available = [m for m in st.session_state.metrics if m not in others or m == current]
            options = ["Select metrics..."] + available
            sel = st.selectbox(f"Point {L}: {ind}", options, index=options.index(current), key=f"sel_{L}")
            st.session_state.answers[L] = sel

        if st.button("Submit Answers"):
            if "Select metrics..." in st.session_state.answers.values():
                st.warning("Please assign all metrics before submitting.")
            elif len(set(st.session_state.answers.values())) < len(letters):
                st.warning("Each metric can be used only once.")
            else:
                score = 0
                results = []
                for i, L in enumerate(letters):
                    correct = st.session_state.mapping[L]
                    guess = st.session_state.answers[L]
                    if guess == correct:
                        score += 1
                        results.append((L, "✅", correct))
                    else:
                        score -= 0.5
                        results.append((L, "❌", correct))
                st.session_state.score = score
                st.session_state.results = results
                st.session_state.game_submitted = True

    else:
        score = st.session_state.score
        results = st.session_state.results
        st.subheader(f"Score: {score:.2f}")
        if all(r[1] == "✅" for r in results):
            st.success("Perfect score! 🎉")
        st.subheader("Correct Answers:")
        for L, mark, val in results:
            st.write(f"{mark} Point {L} → {val}")
