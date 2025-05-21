import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# --- Load Data from Damodaran WACC table, with fallback to Jan 2025 snapshot ---
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
# Hardcoded snapshot of Damodaran's January 2025 WACC data (Industry, Beta, WACC%, Debt%)
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
try:
    # Try to read directly from the online CSV
    df = pd.read_csv(CSV_URL)
except Exception:
    # Fallback to the hardcoded snapshot
    df = pd.read_csv(io.StringIO(SAMPLE_CSV))

# Convert percentage strings to numeric floats (e.g., "9.22%" -> 9.22)
df["Cost of Capital"] = df["Cost of Capital"].str.rstrip("%").astype(float)
df["D/(D+E)"] = df["D/(D+E)"].str.rstrip("%").astype(float)

# --- Streamlit page configuration ---
st.set_page_config(page_title="Industry Match Game (WACC)", page_icon=":bar_chart:", layout="wide")
st.title("Industry WACC Matching Game")

# Initialize session state for game stage
if "game_stage" not in st.session_state:
    st.session_state.game_stage = "setup"

# Sidebar: New round setup form
with st.sidebar.form("setup_form"):
    num_industries = st.slider("Select number of industries for this round", min_value=2, max_value=10, value=5)
    start_button = st.form_submit_button("Start New Round")
    if start_button:
        # Start a new round: sample industries and assign letters
        # Clear any old guesses from previous rounds
        for letter_key in [f"guess_{chr(ord('A')+i)}" for i in range(10)]:  # keys for A-J
            if letter_key in st.session_state:
                del st.session_state[letter_key]
        # Randomly sample the specified number of industries
        df_round = df.sample(n=num_industries, random_state=None).reset_index(drop=True)
        letters = [chr(ord('A') + i) for i in range(num_industries)]
        df_round["Letter"] = letters  # assign letters to sampled industries
        # Store round data and state
        st.session_state.df_round = df_round
        st.session_state.game_stage = "playing"
        st.session_state.score = 0.0
        st.session_state.correct_count = 0
        st.session_state.wrong_count = 0

# Main app logic based on game stage
if st.session_state.game_stage == "setup":
    st.write("Choose the number of industries from the sidebar to start a new round.")

elif st.session_state.game_stage == "playing":
    df_round = st.session_state.df_round
    letters = list(df_round["Letter"])
    # Display 3D plot of the selected industries
    fig = go.Figure(data=[go.Scatter3d(
        x=df_round["Beta"],
        y=df_round["D/(D+E)"],
        z=df_round["Cost of Capital"],
        mode="markers+text",
        text=df_round["Letter"], 
        textposition="top center",
        marker=dict(size=6, color="cornflowerblue"),
        showlegend=False
    )])
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt Ratio (%)",
            zaxis_title="Cost of Capital (%)"
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Guess the Industry for Each Lettered Point")
    placeholder_option = "Select industry"
    # Create a dropdown for each lettered point
    for letter in letters:
        # Retrieve the numeric clues for this point
        row = df_round[df_round["Letter"] == letter].iloc[0]
        beta_val = row["Beta"]
        debt_val = row["D/(D+E)"]
        wacc_val = row["Cost of Capital"]
        dropdown_label = f"**Point {letter}:** Beta {beta_val:.2f}, Debt {debt_val:.2f}%, WACC {wacc_val:.2f}%"
        # Determine which industries have already been chosen in other dropdowns
        chosen_others = set()
        for other in letters:
            if other == letter:
                continue
            guess_key = f"guess_{other}"
            if guess_key in st.session_state:
                chosen_val = st.session_state[guess_key]
                if chosen_val and chosen_val != placeholder_option:
                    chosen_others.add(chosen_val)
        # Available options: placeholder + industries not already chosen by other letters
        available_options = [placeholder_option] + [ind for ind in df_round["Industry Name"] if ind not in chosen_others]
        st.selectbox(dropdown_label, options=available_options, key=f"guess_{letter}")
    # Submit button for guesses
    submitted = st.button("Submit Guesses")
    if submitted:
        # Ensure all dropdowns have a selection
        guesses = {letter: st.session_state[f"guess_{letter}"] for letter in letters}
        if placeholder_option in guesses.values():
            st.warning("Please select an industry for **each** point before submitting your guesses.")
        else:
            # Calculate score
            correct = 0
            wrong = 0
            for letter, guess in guesses.items():
                actual_industry = df_round[df_round["Letter"] == letter]["Industry Name"].iloc[0]
                if guess == actual_industry:
                    correct += 1
                else:
                    wrong += 1
            score = correct - 0.5 * wrong
            # Store results in session state
            st.session_state.score = score
            st.session_state.correct_count = correct
            st.session_state.wrong_count = wrong
            st.session_state.game_stage = "finished"
            # Display outcome messages
            st.write(f"**Score:** {score:.2f}")
            if correct == len(letters):
                st.success("Congratulations! You matched all industries correctly! :tada:")
            else:
                st.error("Game over – some matches were incorrect.")
            # Show correct mappings in a table
            result_df = df_round[["Letter", "Industry Name", "Beta", "D/(D+E)", "Cost of Capital"]].copy()
            # Rename columns for display
            result_df.rename(columns={"D/(D+E)": "Debt (%)", "Cost of Capital": "WACC (%)"}, inplace=True)
            # Format numeric values for display
            result_df["Beta"] = result_df["Beta"].apply(lambda x: f"{x:.2f}")
            result_df["Debt (%)"] = result_df["Debt (%)"].apply(lambda x: f"{x:.2f}%")
            result_df["WACC (%)"] = result_df["WACC (%)"].apply(lambda x: f"{x:.2f}%")
            st.table(result_df)
            st.info("Use the sidebar to start a new round, or click Play Again to choose a new set of industries.")
            # Play Again button
            if st.button("Play Again"):
                # Reset to setup stage for a new game
                st.session_state.game_stage = "setup"
                # Optionally, clear round-specific state
                st.session_state.pop("df_round", None)
                st.session_state.pop("score", None)
                st.session_state.pop("correct_count", None)
                st.session_state.pop("wrong_count", None)
                for letter_key in [f"guess_{chr(ord('A')+i)}" for i in range(10)]:
                    st.session_state.pop(letter_key, None)

elif st.session_state.game_stage == "finished":
    # In case the app is in finished state on a rerun, display the last results
    df_round = st.session_state.df_round
    letters = list(df_round["Letter"])
    fig = go.Figure(data=[go.Scatter3d(
        x=df_round["Beta"], y=df_round["Debt (%)"], z=df_round["WACC (%)"],
        mode="markers+text", text=df_round["Letter"], textposition="top center",
        marker=dict(size=6, color="cornflowerblue"), showlegend=False
    )])
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        scene=dict(xaxis_title="Beta", yaxis_title="Debt Ratio (%)", zaxis_title="Cost of Capital (%)")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**Score:** {st.session_state.score:.2f}")
    if st.session_state.correct_count == len(letters):
        st.success("Congratulations! You matched all industries correctly! :tada:")
    else:
        st.error("Game over – some matches were incorrect.")
    result_df = df_round[["Letter", "Industry Name", "Beta", "D/(D+E)", "Cost of Capital"]].copy()
    result_df.rename(columns={"D/(D+E)": "Debt (%)", "Cost of Capital": "WACC (%)"}, inplace=True)
    result_df["Beta"] = result_df["Beta"].apply(lambda x: f"{x:.2f}")
    result_df["Debt (%)"] = result_df["Debt (%)"].apply(lambda x: f"{x:.2f}%")
    result_df["WACC (%)"] = result_df["WACC (%)"].apply(lambda x: f"{x:.2f}%")
    st.table(result_df)
    st.info("Use the sidebar to start a new round, or click Play Again below.")
    if st.button("Play Again"):
        st.session_state.game_stage = "setup"
        st.session_state.pop("df_round", None)
        st.session_state.pop("score", None)
        st.session_state.pop("correct_count", None)
        st.session_state.pop("wrong_count", None)
        for letter_key in [f"guess_{chr(ord('A')+i)}" for i in range(10)]:
            st.session_state.pop(letter_key, None)
