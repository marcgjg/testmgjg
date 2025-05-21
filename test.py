import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
from io import StringIO

# ───────────────────────────── App setup ────────────────────────────── #
st.set_page_config(page_title="Industry WACC Matching Game",
                   page_icon="🎲",
                   layout="wide")
st.title("🎲 Industry WACC Matching Game")
st.write(
    "Match each letter-labelled point to the correct industry name. "
    "Score **+1** for every correct match and **−0.5** for every wrong one. "
    "If your score drops below zero, you lose; if you match them all, you win!"
)

# ─────────────────────────── Data functions ─────────────────────────── #
DAMODARAN_URL = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"

@st.cache_data(show_spinner="Fetching Damodaran data …", ttl=24*3600)
def load_damodaran() -> pd.DataFrame | None:
    try:
        html = requests.get(DAMODARAN_URL, timeout=10)
        html.raise_for_status()
        tables = pd.read_html(html.text)
        df = tables[0]
        df = df[~df["Industry Name"].str.contains("Total Market", na=False)]
        # Clean % signs
        for col in ["Cost of Capital", "D/(D+E)"]:
            df[col] = df[col].astype(str).str.rstrip("%").astype(float)
        return df
    except Exception:
        return None

# Hard-coded fallback (Jan-2025 snapshot — first 50 rows for brevity)
FALLBACK_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22,20.76
Aerospace/Defense,0.90,7.68,18.56
Air Transport,1.24,7.29,51.65
Apparel,0.99,7.44,31.45
Auto & Truck,1.62,10.34,18.30
Auto Parts,1.23,8.09,32.36
Bank (Money Center),0.88,5.64,64.69
Banks (Regional),0.52,5.69,37.62
Beverage (Alcoholic),0.61,6.55,23.35
Beverage (Soft),0.57,6.59,16.48
Building Materials,1.36,9.46,15.95
Business & Consumer Services,1.00,8.27,14.37
Cable TV,0.96,6.28,55.82
Chemical (Basic),1.15,7.63,36.81
Chemical (Specialty),0.92,7.67,21.34
Coal & Related Energy,1.18,9.23,8.65
Computer Services,1.23,8.72,20.84
Computers/Peripherals,1.14,9.29,4.60
Construction Supplies,1.29,9.14,17.74
Drugs (Biotechnology),1.25,9.37,14.60
Drugs (Pharmaceutical),1.07,8.72,14.45
Electrical Equipment,1.27,9.40,12.93
Electronics (Consumer & Office),0.92,8.12,11.75
Electronics (General),1.06,8.55,12.60
Engineering/Construction,0.99,8.17,15.20
Entertainment,1.04,8.28,16.90
Environmental & Waste Services,0.92,7.88,16.19
Farming/Agriculture,0.98,7.43,34.78
Food Processing,0.47,6.02,26.75
Green & Renewable Energy,1.13,6.50,63.79
Healthcare Products,1.01,8.50,11.34
Heathcare Information and Technology,1.22,9.10,13.94
Homebuilding,1.43,9.78,14.89
Hospitals/Healthcare Facilities,0.86,6.57,43.55
Hotel/Gaming,1.19,8.12,30.17
Household Products,0.90,7.91,13.21
Information Services,0.98,7.62,26.13
Insurance (General),0.76,7.35,14.79
Insurance (Life),0.73,6.36,38.55
Insurance (Prop/Cas.),0.61,6.79,13.39
Investments & Asset Management,0.57,6.20,25.95
Machinery,1.07,8.54,13.57
Metals & Mining,1.02,8.40,14.35
Oil/Gas (Integrated),0.48,6.33,12.06
Oil/Gas (Production and Exploration),0.88,7.52,21.04
Packaging & Container,0.98,7.20,34.60
Paper/Forest Products,1.07,8.32,18.41
Power,0.54,5.54,44.55
Precious Metals,1.23,9.09,15.89
Publishing & Newspapers,0.64,6.63,22.30
R.E.I.T.,0.95,6.62,45.50
Retail (Automotive),1.35,8.39,33.51
"""

df_live = load_damodaran()
df_data = df_live if df_live is not None else pd.read_csv(StringIO(FALLBACK_CSV))

# ─────────────────────────── Sidebar controls ────────────────────────── #
st.sidebar.header("Game settings")
n_max = min(10, len(df_data))
n_choice = st.sidebar.slider("Industries per round", 2, n_max, 5)
start_round = st.sidebar.button("Start new round")

# ─────────────────────────── Session defaults ────────────────────────── #
if "round_active" not in st.session_state:
    st.session_state.round_active = False
    st.session_state.score = 0.0
    st.session_state.letters = []
    st.session_state.mapping = {}
    st.session_state.subset = pd.DataFrame()
    st.session_state.finished = False

# ─────────────────────── Start / reset round logic ───────────────────── #
if start_round:
    subset = df_data.sample(n_choice, random_state=random.randint(0, 999999)).reset_index(drop=True)
    letters = [chr(65+i) for i in range(len(subset))]
    mapping = {letters[i]: subset.at[i, "Industry Name"] for i in range(len(subset))}
    st.session_state.round_active = True
    st.session_state.finished = False
    st.session_state.letters = letters
    st.session_state.mapping = mapping
    st.session_state.subset = subset
    # clear previous guesses
    for k in list(st.session_state.keys()):
        if k.startswith("guess_"):
            del st.session_state[k]

# ───────────────────────────── Active round UI ───────────────────────── #
if st.session_state.round_active and not st.session_state.finished:
    sub = st.session_state.subset
    letters = st.session_state.letters

    st.subheader(f"Current score: {st.session_state.score:.2f}")

    # 3-D scatter plot
    fig = go.Figure(go.Scatter3d(
        x=sub["Beta"],
        y=sub["D/(D+E)"],
        z=sub["Cost of Capital"],
        mode="markers+text",
        text=letters,
        textposition="top center",
        marker=dict(size=6, color="#1f77b4")
    ))
    fig.update_layout(
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt ratio (%)",
            zaxis_title="WACC (%)"
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Build dropdown options (shuffle WACC values)
    wacc_vals = list(sub["Cost of Capital"])
    options = random.sample(wacc_vals, len(wacc_vals))
    opts_display = ["– pick –"] + [f"{v:.2f} %" for v in options]

    with st.form("match_form"):
        st.write("Select the **WACC (%)** for each industry:")
        for i, row in sub.iterrows():
            label = f"{letters[i]} — {row['Industry Name']} " \
                    f"(Beta {row['Beta']:.2f}, Debt {row['D/(D+E)']:.1f}%)"
            st.selectbox(label, opts_display, key=f"guess_{letters[i]}")
        submitted = st.form_submit_button("Submit answers")

    if submitted:
        guesses = {letters[i]: st.session_state[f"guess_{letters[i]}"] for i in range(len(letters))}
        if "– pick –" in guesses.values():
            st.warning("Choose a WACC for every industry before submitting.")
        else:
            correct = wrong = 0
            feedback = []
            for i, L in enumerate(letters):
                true_val = sub.at[i, "Cost of Capital"]
                guess_val = float(guesses[L].split()[0])
                if abs(guess_val - true_val) < 1e-6:
                    correct += 1
                    feedback.append(f"✅ {sub.at[i,'Industry Name']}: correct!")
                else:
                    wrong += 1
                    feedback.append(
                        f"❌ {sub.at[i,'Industry Name']}: you picked {guess_val:.2f} %, "
                        f"true is {true_val:.2f} %"
                    )
            # Scoring: +1 correct, –0.5 wrong
            st.session_state.score += correct - 0.5 * wrong

            if correct == len(letters):
                st.success(f"🎉 All correct! Round complete. "
                           f"Score now {st.session_state.score:.2f}")
                st.session_state.finished = True
            elif st.session_state.score < 0:
                st.error(f"💀 Score below zero. Game over! Final score "
                         f"{st.session_state.score:.2f}")
                st.session_state.finished = True
            else:
                st.info(f"Correct: {correct} · Wrong: {wrong} "
                        f"→ Score {st.session_state.score:.2f}. Try again!")
            with st.expander("See details", expanded=False):
                for line in feedback:
                    st.write(line)

# ───────────────────────── Round finished notice ─────────────────────── #
if st.session_state.round_active and st.session_state.finished:
    st.info("Start a new round from the sidebar when you're ready!")
