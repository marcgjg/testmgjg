import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

# Data source and fallback
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
Chemicals (Basic),1.03,8.12%,16.53%
Chemicals (Diversified),1.12,9.03%,12.85%
Chemicals (Specialty),1.13,8.08%,29.06%
Coal & Related Energy,0.93,6.22%,54.14%
Computer Services,1.06,8.07%,17.17%
Computer Software (Entertainment),1.06,8.83%,9.60%
Computer Software (System & Application),1.07,8.19%,16.51%
Computer/Peripherals,1.16,8.46%,15.38%
Construction Materials,0.98,7.65%,28.10%
Construction,0.85,6.81%,32.77%
Consumer Financial Services,0.51,5.37%,44.02%
Consumer Products,0.98,7.44%,29.72%
Containers & Packaging,0.93,6.85%,26.50%
Drugs (Biotechnology),1.19,9.21%,9.98%
Drugs (Pharmaceutical),0.80,6.96%,11.06%
Education,1.01,6.91%,45.79%
Electrical Equipment,1.13,8.30%,22.51%
Electronics (Consumer & Office),1.30,8.12%,33.45%
Engineering/Construction,1.01,7.61%,20.55%
Entertainment,1.21,7.72%,31.48%
Environmental & Waste Services,0.84,6.75%,27.26%
Farming/Agriculture,0.97,6.84%,32.97%
Financial Svcs. (Non-bank & Insurance),1.04,6.60%,47.60%
Food Processing,0.56,5.96%,21.05%
Healthcare Products,0.90,6.98%,20.91%
Healthcare Support Services,0.87,6.26%,32.45%
Healthcare Information and Technology,0.90,6.60%,25.09%
Homebuilding,1.37,8.72%,20.61%
Hospitals/Healthcare Facilities,1.07,6.69%,52.92%
Hotel/Gaming,1.20,7.26%,47.58%
Household Products,0.67,6.67%,15.35%
Information Services,0.87,7.36%,17.30%
Insurance (General),1.21,7.92%,23.13%
Insurance (Life),1.18,8.58%,15.46%
Insurance (Prop/Cas.),0.71,5.84%,34.85%
Investments & Asset Management,1.08,6.32%,57.26%
Machinery,1.20,8.61%,14.53%
Metals & Mining,1.35,8.10%,32.27%
Office Equipment & Services,1.32,9.20%,14.08%
Oil/Gas (Integrated),1.35,8.97%,21.32%
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
Retail (Grocery and Food),0.69,6.37%,23.56%
Retail (Online),1.02,8.73%,9.04%
Retail (Special Lines),1.47,9.62%,25.49%
Rubber& Tires,1.30,9.06%,24.71%
Semiconductor,1.35,9.27%,13.32%
Semiconductor Equip,1.21,8.72%,17.47%
Shipbuilding & Marine,1.30,7.36%,40.16%
Shoe,0.96,7.21%,31.34%
Software (Internet),0.97,7.91%,14.80%
Steel,1.06,6.87%,41.39%
Telecom (Wireless),0.57,5.95%,24.46%
Telecom. Equipment,1.16,8.57%,17.80%
Telecom. Services,0.79,6.41%,24.46%
Tobacco,0.58,7.09%,11.45%
Transportation,1.06,7.12%,41.86%
Trucking,1.05,6.62%,44.77%
Utility (General),0.59,5.45%,40.69%
Utility (Water),0.57,5.11%,44.52%
Warehouse/Storage,0.88,6.02%,51.34%
"""

# Load data (with fallback)
try:
    df_full = pd.read_csv(CSV_URL)
except Exception:
    df_full = pd.read_csv(StringIO(SAMPLE_CSV))
# Ensure consistent types
if df_full["Cost of Capital"].dtype == object:
    df_full["Cost of Capital"] = df_full["Cost of Capital"].str.rstrip("%").astype(float)
if df_full["D/(D+E)"].dtype == object:
    df_full["D/(D+E)"] = df_full["D/(D+E)"].str.rstrip("%").astype(float)

# Initialize session state variables
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "game_submitted" not in st.session_state:
    st.session_state.game_submitted = False
if "chosen_df" not in st.session_state:
    st.session_state.chosen_df = None
if "metrics_mapping" not in st.session_state:
    st.session_state.metrics_mapping = {}
if "letters_list" not in st.session_state:
    st.session_state.letters_list = []

# Sidebar UI
num_points = st.sidebar.slider("Number of industries (points)", 2, 26, 5, disabled=st.session_state.game_active)
start_clicked = st.sidebar.button("Start Game", disabled=st.session_state.game_active)
if start_clicked:
    # Start a new game
    # Reset previous selections and state
    for letter in list(st.session_state.letters_list):
        key = f"sel_{letter}"
        if key in st.session_state:
            st.session_state.pop(key)
    st.session_state.game_active = True
    st.session_state.game_submitted = False
    # Choose random industries
    N = num_points
    if N > len(df_full):
        N = len(df_full)
    chosen_indices = random.sample(range(len(df_full)), N)
    chosen_df = df_full.iloc[chosen_indices].copy().reset_index(drop=True)
    st.session_state.chosen_df = chosen_df
    st.session_state.letters_list = list(string.ascii_uppercase[:N])
    # Prepare metric triples and mapping
    metrics_options = []
    st.session_state.metrics_mapping = {}
    for i, row in chosen_df.iterrows():
        letter = st.session_state.letters_list[i]
        beta_val = row["Beta"]
        wacc_val = row["Cost of Capital"]
        debt_val = row["D/(D+E)"]
        beta_str = f"{beta_val:.2f}"
        wacc_str = f"{wacc_val:.2f}%"
        debt_str = f"{debt_val:.2f}%"
        triple_str = f"Beta: {beta_str}, Debt%: {debt_str}, WACC: {wacc_str}"
        metrics_options.append(triple_str)
        st.session_state.metrics_mapping[letter] = triple_str
    # Randomize options order for dropdowns
    random.shuffle(metrics_options)
    st.session_state.metrics_options = metrics_options

# Main area
if not st.session_state.game_active:
    if st.session_state.game_submitted and st.session_state.chosen_df is not None:
        # Round finished: show scatterplot and score
        st.subheader("Results")
        score = 0.0
        N = len(st.session_state.letters_list)
        # Score should have been computed at submit time and stored, but compute again to be safe
        for letter in st.session_state.letters_list:
            user_val = st.session_state.get(f"sel_{letter}")
            if not user_val or user_val == "Select metrics...":
                # not answered
                continue
            correct_val = st.session_state.metrics_mapping.get(letter)
            if user_val == correct_val:
                score += 1.0
            else:
                score -= 0.5
        # Display score
        if abs(score - round(score)) < 1e-9:
            score_display = str(int(round(score)))
        else:
            score_display = f"{score:.1f}"
        st.write(f"Score: **{score_display}**")
        if score == len(st.session_state.letters_list):
            st.success("Perfect score! All matches are correct.")
        # Show 3D scatter from last game
        if st.session_state.chosen_df is not None:
            df_plot = st.session_state.chosen_df
            letters = st.session_state.letters_list
            fig = go.Figure(data=[go.Scatter3d(
                x=df_plot["Beta"],
                y=df_plot["D/(D+E)"],
                z=df_plot["Cost of Capital"],
                mode="markers+text",
                text=letters,
                textposition="top center",
                textfont=dict(size=12)
            )])
            fig.update_traces(marker=dict(size=5, color="blue"))
            fig.update_layout(scene=dict(
                xaxis_title="Beta", 
                yaxis_title="Debt %", 
                zaxis_title="WACC"
            ), margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig)
        st.info("Adjust the number of industries and press **Start Game** to play again.")
    else:
        st.write("Select the number of industries and press **Start Game** in the sidebar to begin.")
else:
    # Game in progress
    # Display 3D scatterplot with letter-labeled points
    df_plot = st.session_state.chosen_df
    letters = st.session_state.letters_list
    fig = go.Figure(data=[go.Scatter3d(
        x=df_plot["Beta"],
        y=df_plot["D/(D+E)"],
        z=df_plot["Cost of Capital"],
        mode="markers+text",
        text=letters,
        textposition="top center",
        textfont=dict(size=12)
    )])
    fig.update_traces(marker=dict(size=5, color="blue"))
    fig.update_layout(scene=dict(
        xaxis_title="Beta", 
        yaxis_title="Debt %", 
        zaxis_title="WACC"
    ), margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig)
    # Dropdowns for each letter
    all_options = ["Select metrics..."] + st.session_state.metrics_options
    for letter in st.session_state.letters_list:
        current_selection = st.session_state.get(f"sel_{letter}", "Select metrics...")
        # Compute options excluding selections of other dropdowns
        taken_options = set()
        for other in st.session_state.letters_list:
            if other == letter:
                continue
            val = st.session_state.get(f"sel_{other}")
            if val and val != "Select metrics...":
                taken_options.add(val)
        # Build options list for this dropdown
        opts = ["Select metrics..."] + [opt for opt in st.session_state.metrics_options if opt not in taken_options]
        st.selectbox(f"Point {letter}: {st.session_state.chosen_df.iloc[st.session_state.letters_list.index(letter)]['Industry Name']}",
                     options=opts, index=opts.index(current_selection) if current_selection in opts else 0, key=f"sel_{letter}")
    # Submit button
    submit_clicked = st.button("Submit")
    if submit_clicked:
        # Ensure all points have a selection
        incomplete = False
        for letter in st.session_state.letters_list:
            if st.session_state.get(f"sel_{letter}") == "Select metrics...":
                incomplete = True
                break
        if incomplete:
            st.warning("Please assign all points before submitting.")
        else:
            # Calculate score
            score = 0.0
            for letter in st.session_state.letters_list:
                user_val = st.session_state[f"sel_{letter}"]
                correct_val = st.session_state.metrics_mapping.get(letter)
                if user_val == correct_val:
                    score += 1.0
                else:
                    score -= 0.5
            # Display score and success if perfect
            if abs(score - round(score)) < 1e-9:
                score_display = str(int(round(score)))
            else:
                score_display = f"{score:.1f}"
            st.write(f"Score: **{score_display}**")
            if score == len(st.session_state.letters_list):
                st.success("Perfect score! All matches are correct.")
            # Mark game as submitted/over
            st.session_state.game_submitted = True
            st.session_state.game_active = False
            st.info("Use the sidebar to start a new game.")
