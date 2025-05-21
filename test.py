import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, random, requests

# ── PAGE CONFIG ──  (must be first Streamlit call)
st.set_page_config(page_title="Industry WACC Guess", page_icon="🏭", layout="wide")

# ── DATA LOADING ───────────────────────────────────────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
FALLBACK = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22%,20.76%
Aerospace/Defense,0.90,7.68%,18.56%
Air Transport,1.24,7.29%,51.65%
Apparel,0.99,7.44%,31.45%
Auto & Truck,1.62,10.34%,18.30%
Auto Parts,1.23,8.09%,32.36%
Bank (Money Center),0.88,5.64%,64.69%
Banks (Regional),0.52,5.69%,37.62%
Beverage (Alcoholic),0.61,6.55%,23.35%
Beverage (Soft),0.57,6.59%,16.48%
Building Materials,1.36,9.46%,15.95%
Business & Consumer Services,1.00,8.27%,14.37%
Cable TV,0.96,6.28%,55.82%
Chemical (Basic),1.15,7.63%,36.81%
Computer Services,1.23,8.72%,20.84%
Drugs (Biotechnology),1.25,9.37%,14.60%
Entertainment,1.04,8.28%,16.90%
Food Processing,0.47,6.02%,26.75%
Green & Renewable Energy,1.13,6.50%,63.79%
Healthcare Products,1.01,8.50%,11.34%
Homebuilding,1.43,9.78%,14.89%
Hotel/Gaming,1.19,8.12%,30.17%
Household Products,0.90,7.91%,13.21%
Information Services,0.98,7.62%,26.13%
Insurance (General),0.76,7.35%,14.79%
Machinery,1.07,8.54%,13.57%
Metals & Mining,1.02,8.40%,14.35%
Oil/Gas (Integrated),0.48,6.33%,12.06%
Packaging & Container,0.98,7.20%,34.60%
Paper/Forest Products,1.07,8.32%,18.41%
Power,0.54,5.54%,44.55%
Precious Metals,1.23,9.09%,15.89%
R.E.I.T.,0.95,6.62%,45.50%
Retail (Automotive),1.35,8.39%,33.51%
Semiconductor,1.49,10.76%,3.75%
Steel,1.06,8.17%,20.57%
Telecom. Services,0.89,6.37%,50.04%
Utility (General),0.39,5.20%,43.84%"""

@st.cache_data
def load_wacc() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_URL)
    except Exception:
        df = pd.read_csv(io.StringIO(FALLBACK))
    df = df[~df["Industry Name"].str.startswith("Total Market")]
    df["Cost of Capital"] = (
        df["Cost of Capital"].astype(str).str.rstrip("%").astype(float) / 100
    )
    df["D/(D+E)"] = df["D/(D+E)"].astype(str).str.rstrip("%").astype(float) / 100
    return df

df_full = load_wacc()

# ── HELPERS ───────────────────────────────────────────────── #
def new_round(n: int):
    subset = df_full.sample(n).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n)]
    st.session_state.round = {
        "df": subset,
        "letters": letters,
        "guesses": {L: None for L in letters},
        "finished": False,
        "score": 0.0,
    }

def plot_3d(df, letters):
    fig = go.Figure(
        go.Scatter3d(
            x=df["Beta"],
            y=df["D/(D+E)"],
            z=df["Cost of Capital"],
            mode="markers+text",
            text=letters,
            textposition="top center",
            marker=dict(size=6, color="#1f77b4"),
            hovertemplate="Beta %{x:.2f}<br>Debt %{y:.2%}<br>WACC %{z:.2%}"
        )
    )
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=20, b=0),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt ratio",
            zaxis_title="WACC",
        )
    )
    return fig

# ── INIT SESSION ─────────────────────────────────────────── #
if "round" not in st.session_state:
    new_round(5)

round_state = st.session_state.round
letters = round_state["letters"]
df_sub = round_state["df"]

# ── SIDEBAR ──────────────────────────────────────────────── #
with st.sidebar:
    st.header("New round")
    n_sel = st.slider("Industries", 2, 10, len(letters))
    if st.button("Restart"):
        new_round(n_sel)

# ── MAIN UI ──────────────────────────────────────────────── #
st.title("🏭 Industry WACC guessing game")
st.write("Match each letter-labelled point to its industry. "
         "Duplicates are blocked. Scoring: **+1** correct, **−0.5** wrong.")

# Show plot
st.plotly_chart(plot_3d(df_sub, letters), use_container_width=True)

# ------------ Form ------------
if not round_state["finished"]:
    with st.form("guess_form"):
        placeholder = "— pick —"
        for idx, L in enumerate(letters):
            current = round_state["guesses"][L]
            chosen = {v for k, v in round_state["guesses"].items() if k != L and v}
            available = [ind for ind in df_sub["Industry Name"] if ind not in chosen or ind == current]
            opts = [placeholder] + sorted(available)
            if current and current not in opts:
                opts.append(current)
            idx_default = opts.index(current) if current else 0
            beta = df_sub.at[idx, "Beta"]
            debt = df_sub.at[idx, "D/(D+E)"] * 100
            wacc = df_sub.at[idx, "Cost of Capital"] * 100
            label = f"Point {L}: β {beta:.2f}, Debt {debt:.2f} %, WACC {wacc:.2f} %"
            sel = st.selectbox(label, opts, index=idx_default)
            round_state["guesses"][L] = sel if sel != placeholder else None
        submitted = st.form_submit_button("Submit guesses")

    # Evaluate if submitted
    if submitted:
        guesses = round_state["guesses"]
        if None in guesses.values():
            st.warning("Pick an industry for every point.")
        elif len(set(guesses.values())) < len(guesses):
            st.warning("No duplicates allowed.")
        else:
            correct = sum(
                guesses[L] == df_sub.at[i, "Industry Name"]
                for i, L in enumerate(letters)
            )
            wrong = len(letters) - correct
            round_state["score"] = correct - 0.5 * wrong
            round_state["finished"] = True

# ------------ Results ------------
if round_state["finished"]:
    st.subheader(f"Round score: {round_state['score']:.2f}")
    if round_state["score"] == len(letters):
        st.success("Perfect round! 🎉")
    elif round_state["score"] < 0:
        st.error("Score below zero — game over.")
    else:
        st.info("Round complete.")

    st.table(pd.DataFrame({
        "Letter": letters,
        "Industry": df_sub["Industry Name"]
    }).set_index("Letter"))
