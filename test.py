import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

st.set_page_config(page_title="WACC Matching Game", layout="wide")

# Load data from Damodaran or fallback
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
FALLBACK_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22,20.76
Aerospace/Defense,0.90,7.68,18.56
Air Transport,1.24,7.29,51.65
Apparel,0.99,7.44,31.45
Auto & Truck,1.62,10.34,18.3
Auto Parts,1.23,8.09,32.36
Bank (Money Center),0.88,5.64,64.69
Banks (Regional),0.52,5.69,37.62
Beverage (Alcoholic),0.61,6.55,23.35
Beverage (Soft),0.57,6.59,16.48
Broadcasting,0.92,6.03,59.93
Brokerage & Investment Banking,0.95,5.74,65.11
Building Materials,1.36,9.46,15.95
Business & Consumer Services,1.00,8.27,14.37
Cable TV,0.96,6.28,55.82
Chemical (Basic),1.15,7.63,36.81
Chemical (Diversified),0.99,6.47,53.08
Chemical (Specialty),0.92,7.67,21.34
Coal & Related Energy,1.18,9.23,8.65
Computer Services,1.23,8.72,20.84
Computers/Peripherals,1.14,9.29,4.6
Construction Supplies,1.29,9.14,17.74
Diversified,1.09,8.61,13.86
Drugs (Biotechnology),1.25,9.37,14.6
Drugs (Pharmaceutical),1.07,8.72,14.45
Education,0.98,8.1,16.28
Electrical Equipment,1.27,9.4,12.93
Electronics (Consumer & Office),0.92,8.12,11.75
Electronics (General),1.06,8.55,12.6
Engineering/Construction,0.99,8.17,15.2
Entertainment,1.04,8.28,16.9
Environmental & Waste Services,0.92,7.88,16.19
Farming/Agriculture,0.98,7.43,34.78
Financial Svcs. (Non-bank & Insurance),1.07,5.46,74.14
Food Processing,0.47,6.02,26.75
Food Wholesalers,0.72,6.64,30.21
Furn/Home Furnishings,0.87,7.15,29.54
Green & Renewable Energy,1.13,6.5,63.79
Healthcare Products,1.01,8.5,11.34
Healthcare Support Services,0.94,7.6,24.36
Heathcare Information and Technology,1.22,9.1,13.94
Homebuilding,1.43,9.78,14.89
Hospitals/Healthcare Facilities,0.86,6.57,43.55
Hotel/Gaming,1.19,8.12,30.17
Household Products,0.90,7.91,13.21
Information Services,0.98,7.62,26.13
Insurance (General),0.76,7.35,14.79
Insurance (Life),0.73,6.36,38.55
Insurance (Prop/Cas.),0.61,6.79,13.39
Investments & Asset Management,0.57,6.2,25.95
Machinery,1.07,8.54,13.57
Metals & Mining,1.02,8.4,14.35
Office Equipment & Services,1.20,8.05,31.74
Oil/Gas (Integrated),0.48,6.33,12.06
Oil/Gas (Production and Exploration),0.88,7.52,21.04
Oil/Gas Distribution,0.75,6.59,34.01
Oilfield Svcs/Equip.,0.94,7.44,27.81
Packaging & Container,0.98,7.2,34.6
Paper/Forest Products,1.07,8.32,18.41
Power,0.54,5.54,44.55
Precious Metals,1.23,9.09,15.89
Publishing & Newspapers,0.64,6.63,22.3
R.E.I.T.,0.95,6.62,45.5
Real Estate (Development),1.03,6.58,52.09
Real Estate (General/Diversified),0.86,6.99,29.55
Real Estate (Operations & Services),1.08,8.14,22.35
Recreation,1.33,7.97,39.43
Reinsurance,0.54,6.08,26.78
Restaurant/Dining,1.01,8.05,18.79
Retail (Automotive),1.35,8.39,33.51
Retail (Building Supply),1.79,11,16.8
Retail (Distributors),1.12,8.16,23.82
Retail (General),1.06,8.79,8.03
Retail (Grocery and Food),0.58,5.96,34.32
Retail (REITs),0.95,6.96,35.39
Retail (Special Lines),1.22,8.64,22.44
Rubber& Tires,0.65,5.33,79.47
Semiconductor,1.49,10.76,3.75
Semiconductor Equip,1.48,10.51,7.56
Shipbuilding & Marine,0.58,6.64,16.05
Shoe,1.42,10.15,9.29
Software (Entertainment),1.18,9.58,2.43
Software (Internet),1.69,11.1,10.35
Software (System & Application),1.24,9.69,4.67
Steel,1.06,8.17,20.57
Telecom (Wireless),0.77,6.92,32.25
Telecom. Equipment,1.00,8.39,11.35
Telecom. Services,0.89,6.37,50.04
Tobacco,0.98,7.95,21.85
Transportation,1.03,7.72,27.91
Transportation (Railroads),0.99,7.75,22.11
Trucking,1.10,8.39,18.64
Utility (General),0.39,5.2,43.84
Utility (Water),0.68,6.15,36.96%"""

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

st.title("🎯 Industry Matching Game")

# Add a description
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown("""
    This tool gives you a feeling about how the beta, cost of capital and leverage (D/(D+E)) vary across industries. Choose the number of industries and then guess their metrics. You obtain 1 point for a correct guess and you lose 0.5 points for a wrong guess. Good luck!

    The data are sourced from Professor Damodaran's website.
    """)

# Sidebar controls
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

    # During an active round: scatterplot on left, dropdowns on right
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(
            go.Figure(
                go.Scatter3d(
                    x=df["Beta"], y=df["Debt"], z=df["WACC"],
                    text=letters, mode="markers+text", textposition="top center",
                    marker=dict(size=6, color="blue")
                )
            ).update_layout(
                scene=dict(xaxis_title="Beta", yaxis_title="Debt %", zaxis_title="WACC %"),
                height=600, margin=dict(l=0, r=0, t=20, b=0)
            ),
            use_container_width=True
        )
    with col_right:
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
            st.write("")  # empty placeholder in right column after submission

    # After round submission: score and answers centered below both columns
    if st.session_state.game_submitted:
        score = st.session_state.score
        results = st.session_state.results
        col_space_left, col_center, col_space_right = st.columns([1, 2, 1])
        with col_center:
            st.subheader(f"Score: {score:.2f}")
            if all(r[1] == "✅" for r in results):
                st.success("Perfect score! 🎉")
            st.subheader("Correct Answers:")
            for i, (L, mark, val) in enumerate(results):
                industry = st.session_state.df.at[i, "Industry"]
                st.write(f"{mark} Point {L} ({industry}) → {val}")

