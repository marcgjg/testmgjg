import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Data source URL and fallback dataset (snapshot as of Jan 2025)
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SAMPLE_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
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
Broadcasting,0.92,6.03%,59.93%
Brokerage & Investment Banking,0.95,5.74%,65.11%
Building Materials,1.36,9.46%,15.95%
Business & Consumer Services,1.00,8.27%,14.37%
Cable TV,0.96,6.28%,55.82%
Chemical (Basic),1.15,7.63%,36.81%
Chemical (Diversified),0.99,6.47%,53.08%
Chemical (Specialty),0.92,7.67%,21.34%
Coal & Related Energy,1.18,9.23%,8.65%
Computer Services,1.23,8.72%,20.84%
Computers/Peripherals,1.14,9.29%,4.60%
Construction Supplies,1.29,9.14%,17.74%
Diversified,1.09,8.61%,13.86%
Drugs (Biotechnology),1.25,9.37%,14.60%
Drugs (Pharmaceutical),1.07,8.72%,14.45%
Education,0.98,8.10%,16.28%
Electrical Equipment,1.27,9.40%,12.93%
Electronics (Consumer & Office),0.92,8.12%,11.75%
Electronics (General),1.06,8.55%,12.60%
Engineering/Construction,0.99,8.17%,15.20%
Entertainment,1.04,8.28%,16.90%
Environmental & Waste Services,0.92,7.88%,16.19%
Farming/Agriculture,0.98,7.43%,34.78%
Financial Svcs. (Non-bank & Insurance),1.07,5.46%,74.14%
Food Processing,0.47,6.02%,26.75%
Food Wholesalers,0.72,6.64%,30.21%
Furn/Home Furnishings,0.87,7.15%,29.54%
Green & Renewable Energy,1.13,6.50%,63.79%
Healthcare Products,1.01,8.50%,11.34%
Healthcare Support Services,0.94,7.60%,24.36%
Heathcare Information and Technology,1.22,9.10%,13.94%
Homebuilding,1.43,9.78%,14.89%
Hospitals/Healthcare Facilities,0.86,6.57%,43.55%
Hotel/Gaming,1.19,8.12%,30.17%
Household Products,0.90,7.91%,13.21%
Information Services,0.98,7.62%,26.13%
Insurance (General),0.76,7.35%,14.79%
Insurance (Life),0.73,6.36%,38.55%
Insurance (Prop/Cas.),0.61,6.79%,13.39%
Investments & Asset Management,0.57,6.20%,25.95%
Machinery,1.07,8.54%,13.57%
Metals & Mining,1.02,8.40%,14.35%
Office Equipment & Services,1.20,8.05%,31.74%
Oil/Gas (Integrated),0.48,6.33%,12.06%
Oil/Gas (Production and Exploration),0.88,7.52%,21.04%
Oil/Gas Distribution,0.75,6.59%,34.01%
Oilfield Svcs/Equip.,0.94,7.44%,27.81%
Packaging & Container,0.98,7.20%,34.60%
Paper/Forest Products,1.07,8.32%,18.41%
Power,0.54,5.54%,44.55%
Precious Metals,1.23,9.09%,15.89%
Publishing & Newspapers,0.64,6.63%,22.30%
R.E.I.T.,0.95,6.62%,45.50%
Real Estate (Development),1.03,6.58%,52.09%
Real Estate (General/Diversified),0.86,6.99%,29.55%
Real Estate (Operations & Services),1.08,8.14%,22.35%
Recreation,1.33,7.97%,39.43%
Reinsurance,0.54,6.08%,26.78%
Restaurant/Dining,1.01,8.05%,18.79%
Retail (Automotive),1.35,8.39%,33.51%
Retail (Building Supply),1.79,11.00%,16.80%
Retail (Distributors),1.12,8.16%,23.82%
Retail (General),1.06,8.79%,8.03%
Retail (Grocery and Food),0.58,5.96%,34.32%
Retail (REITs),0.95,6.96%,35.39%
Retail (Special Lines),1.22,8.64%,22.44%
Rubber& Tires,0.65,5.33%,79.47%
Semiconductor,1.49,10.76%,3.75%
Semiconductor Equip,1.48,10.51%,7.56%
Shipbuilding & Marine,0.58,6.64%,16.05%
Shoe,1.42,10.15%,9.29%
Software (Entertainment),1.18,9.58%,2.43%
Software (Internet),1.69,11.10%,10.35%
Software (System & Application),1.24,9.69%,4.67%
Steel,1.06,8.17%,20.57%
Telecom (Wireless),0.77,6.92%,32.25%
Telecom. Equipment,1.00,8.39%,11.35%
Telecom. Services,0.89,6.37%,50.04%
Tobacco,0.98,7.95%,21.85%
Transportation,1.03,7.72%,27.91%
Transportation (Railroads),0.99,7.75%,22.11%
Trucking,1.10,8.39%,18.64%
Utility (General),0.39,5.20%,43.84%
Utility (Water),0.68,6.15%,36.96%"""

@st.cache_data
def load_wacc_data():
    try:
        res = requests.get(CSV_URL, timeout=5)
        if res.status_code == 200:
            content = res.text
            if not content.startswith("Industry Name"):
                raise Exception("Unexpected content")
        else:
            raise Exception("Fetch failed")
    except Exception:
        content = SAMPLE_CSV
    import io
    df = pd.read_csv(io.StringIO(content))
    # Convert percentage columns to numeric for plotting
    df["Cost of Capital"] = df["Cost of Capital"].str.rstrip("%").astype(float)
    df["D/(D+E)"] = df["D/(D+E)"].str.rstrip("%").astype(float)
    return df

# Initialize data
df = load_wacc_data()

# Session state initialization
if "round_active" not in st.session_state:
    st.session_state.round_active = False
if "finished" not in st.session_state:
    st.session_state.finished = False
if "round_data" not in st.session_state:
    st.session_state.round_data = None
if "letters" not in st.session_state:
    st.session_state.letters = []
if "combo_options" not in st.session_state:
    st.session_state.combo_options = []

# Placeholder text for dropdowns
placeholder_text = "(Select metrics)"

# Start a new round
import random, string
def start_round():
    n = st.session_state.n_points
    if n > len(df):
        n = len(df)
    selection = df.sample(n, random_state=random.randint(0, 10000)).reset_index(drop=True)
    letters = list(string.ascii_uppercase)
    selection["Letter"] = letters[:n]
    st.session_state.round_data = selection
    st.session_state.letters = list(selection["Letter"])
    # Prepare combo options for dropdowns and shuffle once
    combos = [
        f"Beta {row['Beta']:.2f}, Debt {row['D/(D+E)']:.2f}%, WACC {row['Cost of Capital']:.2f}%"
        for _, row in selection.iterrows()
    ]
    random.shuffle(combos)
    st.session_state.combo_options = combos
    # Reset selections from any previous round
    for key in list(st.session_state.keys()):
        if key.startswith("guess_"):
            st.session_state[key] = placeholder_text
    st.session_state.round_active = True
    st.session_state.finished = False
    # Clear old score data
    for key in ["score", "correct_count", "wrong_count", "perfect"]:
        if key in st.session_state:
            del st.session_state[key]

# Finish round and score answers
def finish_round():
    correct = 0
    wrong = 0
    if st.session_state.round_data is not None:
        for _, row in st.session_state.round_data.iterrows():
            letter = row["Letter"]
            correct_str = f"Beta {row['Beta']:.2f}, Debt {row['D/(D+E)']:.2f}%, WACC {row['Cost of Capital']:.2f}%"
            chosen = st.session_state.get(f"guess_{letter}", placeholder_text)
            if chosen == correct_str:
                correct += 1
            else:
                wrong += 1
    st.session_state.score = correct * 1.0 + wrong * -0.5
    st.session_state.correct_count = correct
    st.session_state.wrong_count = wrong
    st.session_state.perfect = (wrong == 0 and correct == len(st.session_state.letters))
    st.session_state.finished = True

# Sidebar controls
st.sidebar.title("Industry WACC Matching Game")
st.sidebar.markdown("Match each letter-labeled point to the correct industry metrics:")
st.sidebar.slider("Number of industries to match", 3, 10, 5, key="n_points",
                  disabled=(st.session_state.round_active and not st.session_state.finished))
st.sidebar.button("Start New Round", on_click=start_round,
                  disabled=(st.session_state.round_active and not st.session_state.finished))

# Main game interface
if st.session_state.round_active:
    data_df = st.session_state.round_data
    # 3D scatter plot of Beta vs Debt vs WACC with letter labels
    fig = go.Figure(data=[go.Scatter3d(
        x=data_df["Beta"],
        y=data_df["D/(D+E)"],
        z=data_df["Cost of Capital"],
        mode="markers+text",
        text=data_df["Letter"],
        textposition="top center",
        marker=dict(size=5, color="blue"),
        hoverinfo="none"
    )])
    fig.update_layout(
        scene=dict(xaxis_title="Beta", yaxis_title="Debt (%)", zaxis_title="WACC (%)"),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig)
    # Dropdowns for each letter
    combos = st.session_state.combo_options
    for letter in st.session_state.letters:
        taken = {
            st.session_state.get(f"guess_{other}", "")
            for other in st.session_state.letters if other != letter
        }
        taken.discard(placeholder_text)
        current = st.session_state.get(f"guess_{letter}", placeholder_text)
        available = [opt for opt in combos if opt not in taken]
        options = [placeholder_text] + available
        if current != placeholder_text and current not in options:
            options.append(current)
        st.selectbox(f"Letter {letter}", options, key=f"guess_{letter}", disabled=st.session_state.finished)
    # Check answers or display results
    if not st.session_state.finished:
        st.button("Check Answers", on_click=finish_round)
    else:
        st.markdown(f"**Score:** {st.session_state.score}")
        if st.session_state.perfect:
            st.success("Perfect round! 🎉")
