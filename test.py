import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Data source URLs and fallback snapshot (January 2025)
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

# Cache data loading to avoid repeated fetches
@st.cache_data
def load_industry_data():
    try:
        df = pd.read_csv(CSV_URL)
    except Exception:
        df = pd.read_csv(io.StringIO(SAMPLE_CSV))
    # Drop aggregate rows if present
    df = df[~df["Industry Name"].str.startswith("Total Market")]
    # Ensure numeric columns (remove % and convert to float)
    if df["Cost of Capital"].dtype == object:
        df["Cost of Capital"] = df["Cost of Capital"].str.rstrip("%").astype(float) / 100.0
        df["D/(D+E)"] = df["D/(D+E)"].str.rstrip("%").astype(float) / 100.0
    return df

df = load_industry_data()

# Utility to create 3D scatter plot figure
def make_scatter_3d(dataframe, letters):
    fig = go.Figure(data=[go.Scatter3d(
        x=dataframe["Beta"], 
        y=dataframe["D/(D+E)"], 
        z=dataframe["Cost of Capital"],
        mode='markers+text',
        text=letters,
        textposition='top center',
        marker=dict(size=6),
        hovertemplate="Beta: %{x:.2f}<br>Debt Ratio: %{y:.2%}<br>WACC: %{z:.2%}<extra></extra>"
    )])
    fig.update_layout(scene=dict(
        xaxis_title="Beta", 
        yaxis_title="Debt Ratio (D/(D+E))", 
        zaxis_title="Cost of Capital (WACC)"
    ))
    return fig

# Initialize session state variables
if "game_active" not in st.session_state:
    st.session_state.game_active = False
    st.session_state.submitted = False

# Main app logic
st.title("🌀 Industry WACC Guessing Game")
st.write("Match each anonymous industry data point (Beta, Debt%, WACC) to the correct industry.")

# If game not started, show setup controls
if not st.session_state.game_active:
    # Select number of industries for this round
    num_options = st.slider("How many industries do you want to guess?", 2, 10, 5)
    if st.button("Start Round"):
        # Begin a new round with the chosen number of industries
        selected_df = df.sample(num_options, random_state=None).reset_index(drop=True)
        st.session_state.selected_df = selected_df
        st.session_state.n = num_options
        st.session_state.game_active = True
        st.session_state.submitted = False
        # Clear any old guesses in session state
        for key in list(st.session_state.keys()):
            if key.startswith("guess_"):
                st.session_state.pop(key)
        # Prepare letters for points and create scatter plot
        letters = [chr(65 + i) for i in range(num_options)]
        fig = make_scatter_3d(selected_df, letters)
        # Display scatter plot and input form for guesses
        st.plotly_chart(fig)
        with st.form("guesses_form"):
            # Create a dropdown for each data point
            for idx, letter in enumerate(letters):
                beta_val = selected_df.loc[idx, "Beta"]
                debt_pct = selected_df.loc[idx, "D/(D+E)"] * 100
                wacc_pct = selected_df.loc[idx, "Cost of Capital"] * 100
                # Prepare dropdown options excluding already chosen industries
                current_guess = st.session_state.get(f"guess_{letter}", None)
                chosen = [st.session_state.get(f"guess_{L}") for L in letters if L != letter]
                chosen = [c for c in chosen if c]  # remove None
                all_inds = list(selected_df["Industry Name"])
                available_options = [ind for ind in all_inds if ind not in chosen or ind == current_guess]
                st.selectbox(
                    f"Point {letter}: Beta {beta_val:.2f}, Debt {debt_pct:.2f}%, WACC {wacc_pct:.2f}%", 
                    options=available_options, 
                    index=(available_options.index(current_guess) if current_guess else 0 if available_options else 0),
                    key=f"guess_{letter}"
                )
            submit_guesses = st.form_submit_button("Submit Guesses")
        if submit_guesses:
            # Ensure all points have a selection
            guesses = [st.session_state.get(f"guess_{L}") for L in letters]
            if None in guesses or any(g == "" for g in guesses):
                st.error("Please select an industry for each data point before submitting.")
            else:
                # Calculate score
                actual = list(selected_df["Industry Name"])
                score = 0.0
                for guess, correct in zip(guesses, actual):
                    if guess == correct:
                        score += 1.0
                    else:
                        score -= 0.5
                # Show results
                st.session_state.submitted = True
                st.markdown(f"**Score:** {score:.2f}")
                results_df = pd.DataFrame({"Point": letters, "Actual Industry": actual})
                st.table(results_df)
                # New round options
                st.markdown("### Play Another Round")
                new_count = st.slider("Number of industries for new round:", 2, 10, st.session_state.n, key="new_round_count")
                if st.button("New Round"):
                    # Set up a new round with the chosen number of industries
                    new_df = df.sample(new_count, random_state=None).reset_index(drop=True)
                    st.session_state.selected_df = new_df
                    st.session_state.n = new_count
                    st.session_state.submitted = False
                    # Clear old guesses
                    for key in list(st.session_state.keys()):
                        if key.startswith("guess_"):
                            st.session_state.pop(key)
                    # Display new round scatter plot and guess form
                    letters_new = [chr(65 + i) for i in range(new_count)]
                    fig_new = make_scatter_3d(new_df, letters_new)
                    st.plotly_chart(fig_new)
                    with st.form("guesses_form_new"):
                        for idx, letter in enumerate(letters_new):
                            beta_val = new_df.loc[idx, "Beta"]
                            debt_pct = new_df.loc[idx, "D/(D+E)"] * 100
                            wacc_pct = new_df.loc[idx, "Cost of Capital"] * 100
                            current_guess = st.session_state.get(f"guess_{letter}", None)
                            chosen = [st.session_state.get(f"guess_{L}") for L in letters_new if L != letter]
                            chosen = [c for c in chosen if c]
                            all_inds = list(new_df["Industry Name"])
                            available_options = [ind for ind in all_inds if ind not in chosen or ind == current_guess]
                            st.selectbox(
                                f"Point {letter}: Beta {beta_val:.2f}, Debt {debt_pct:.2f}%, WACC {wacc_pct:.2f}%", 
                                options=available_options,
                                index=(available_options.index(current_guess) if current_guess else 0 if available_options else 0),
                                key=f"guess_{letter}"
                            )
                        submit_new = st.form_submit_button("Submit Guesses")
                    if submit_new:
                        # (The submission handling for the new round will be captured on the next app rerun)
                        st.experimental_rerun()

# If game is active and not yet submitted (user in the middle of a round), show the guessing interface
elif st.session_state.game_active and not st.session_state.submitted:
    selected_df = st.session_state.selected_df
    n = st.session_state.n
    letters = [chr(65 + i) for i in range(n)]
    fig = make_scatter_3d(selected_df, letters)
    st.plotly_chart(fig)
    with st.form("guesses_form_active"):
        for idx, letter in enumerate(letters):
            beta_val = selected_df.loc[idx, "Beta"]
            debt_pct = selected_df.loc[idx, "D/(D+E)"] * 100
            wacc_pct = selected_df.loc[idx, "Cost of Capital"] * 100
            current_guess = st.session_state.get(f"guess_{letter}", None)
            chosen = [st.session_state.get(f"guess_{L}") for L in letters if L != letter]
            chosen = [c for c in chosen if c]
            all_inds = list(selected_df["Industry Name"])
            available_options = [ind for ind in all_inds if ind not in chosen or ind == current_guess]
            st.selectbox(
                f"Point {letter}: Beta {beta_val:.2f}, Debt {debt_pct:.2f}%, WACC {wacc_pct:.2f}%",
                options=available_options,
                index=(available_options.index(current_guess) if current_guess else 0 if available_options else 0),
                key=f"guess_{letter}"
            )
        submit_round = st.form_submit_button("Submit Guesses")
    if submit_round:
        guesses = [st.session_state.get(f"guess_{L}") for L in letters]
        if None in guesses or any(g == "" for g in guesses):
            st.error("Please select an industry for each data point before submitting.")
        else:
            score = 0.0
            actual = list(selected_df["Industry Name"])
            for guess, correct in zip(guesses, actual):
                score += 1.0 if guess == correct else -0.5
            st.session_state.score = score
            st.session_state.submitted = True
            st.experimental_rerun()

# If game is active and submitted (round over), display results and option for new round
elif st.session_state.game_active and st.session_state.submitted:
    selected_df = st.session_state.selected_df
    letters = [chr(65 + i) for i in range(len(selected_df))]
    score = st.session_state.get("score", 0.0)
    st.markdown(f"**Score:** {score:.2f}")
    results_df = pd.DataFrame({"Point": letters, "Actual Industry": list(selected_df["Industry Name"])})
    st.table(results_df)
    st.markdown("### Play Another Round")
    new_count = st.slider("Number of industries for new round:", 2, 10, st.session_state.n, key="new_round_count")
    if st.button("New Round"):
        new_df = df.sample(new_count, random_state=None).reset_index(drop=True)
        st.session_state.selected_df = new_df
        st.session_state.n = new_count
        st.session_state.submitted = False
        # Clear old guesses
        for key in list(st.session_state.keys()):
            if key.startswith("guess_"):
                st.session_state.pop(key)
        # Display new round setup
        st.experimental_rerun()
