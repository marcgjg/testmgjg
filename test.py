import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# Set wide layout for better display (optional)
st.set_page_config(layout="wide")

# Session state initialization
if "game_active" not in st.session_state:
    st.session_state.game_active = False
    st.session_state.submitted = False
    st.session_state.round = 0
    st.session_state.game_data = []

# Title
st.title("🎯 Industry WACC Matching Game")

# Sidebar controls
if not st.session_state.game_active or st.session_state.submitted:
    # Only show controls if no game running or round finished
    num_points = st.sidebar.slider("Number of industries (points)", min_value=3, max_value=26, value=5, step=1)
    start_label = "Start New Round" if st.session_state.game_active and st.session_state.submitted else "Start Game"
    if st.sidebar.button(start_label):
        # Start a new game round
        # Load data (if not already loaded)
        try:
            # Try fetching latest data
            df = pd.read_csv("https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv")
        except Exception:
            # Fallback to hardcoded snapshot (Jan 2025 data)
            data_snapshot = [
                # Industry, Beta, Debt%, WACC (Jan 2025 snapshot)
                ("Advertising", 1.34, 20.76, 9.22),
                ("Aerospace/Defense", 0.90, 18.56, 7.68),
                ("Air Transport", 1.24, 51.65, 7.29),
                ("Apparel", 0.99, 31.45, 7.44),
                ("Auto & Truck", 1.62, 18.30, 10.34),
                ("Auto Parts", 1.23, 32.36, 8.09),
                ("Bank (Money Center)", 0.88, 64.69, 5.64),
                ("Banks (Regional)", 0.52, 37.62, 5.69),
                ("Beverage (Alcoholic)", 0.61, 23.35, 6.55),
                ("Beverage (Soft)", 0.57, 16.48, 6.59),
                ("Broadcasting", 0.92, 59.93, 6.03),
                ("Brokerage & Investment Banking", 0.95, 65.11, 5.74),
                ("Building Materials", 1.36, 15.95, 9.46),
                ("Business & Consumer Services", 1.00, 14.37, 8.27),
                ("Cable TV", 0.96, 55.82, 6.28),
                ("Chemical (Basic)", 1.15, 36.81, 7.63),
                ("Chemical (Diversified)", 0.99, 53.08, 6.47),
                ("Chemical (Specialty)", 0.92, 21.34, 7.67),
                ("Coal & Related Energy", 1.18, 8.65, 9.23),
                ("Computer Services", 1.23, 20.84, 8.72),
                ("Computers/Peripherals", 1.14, 4.60, 9.29),
                ("Construction Supplies", 1.29, 17.74, 9.14),
                ("Diversified", 1.09, 13.86, 8.61),
                ("Drugs (Biotechnology)", 1.25, 14.60, 9.37),
                ("Drugs (Pharmaceutical)", 1.07, 14.45, 8.72),
                ("Education", 0.98, 16.28, 8.10),
                ("Electrical Equipment", 1.27, 12.93, 9.40),
                ("Electronics (Consumer & Office)", 0.92, 11.75, 8.12),
                ("Electronics (General)", 1.06, 12.60, 8.55),
                ("Engineering/Construction", 0.99, 15.20, 8.17),
                ("Entertainment", 1.04, 16.90, 8.28),
                ("Environmental & Waste Services", 0.92, 16.19, 7.88),
                ("Farming/Agriculture", 0.98, 34.78, 7.43),
                ("Financial Svcs. (Non-bank & Insurance)", 1.07, 74.14, 5.46),
                ("Food Processing", 0.47, 26.75, 6.02),
                ("Food Wholesalers", 0.72, 30.21, 6.64),
                ("Furn/Home Furnishings", 0.87, 29.54, 7.15),
                ("Green & Renewable Energy", 1.13, 63.79, 6.50),
                ("Healthcare Products", 1.01, 11.34, 8.50),
                ("Healthcare Support Services", 0.94, 24.36, 7.60),
                ("Healthcare Information and Technology", 1.22, 13.94, 9.10),
                ("Homebuilding", 1.43, 14.89, 9.78),
                ("Hospitals/Healthcare Facilities", 0.86, 43.55, 6.57),
                ("Hotel/Gaming", 1.19, 30.17, 8.12),
                ("Household Products", 0.90, 13.21, 7.91),
                ("Information Services", 0.98, 26.13, 7.62),
                ("Insurance (General)", 0.76, 14.79, 7.35),
                ("Insurance (Life)", 0.73, 38.55, 6.36),
                ("Insurance (Prop/Cas.)", 0.61, 13.39, 6.79),
                ("Investments & Asset Management", 0.57, 25.95, 6.20),
                ("Machinery", 1.07, 13.57, 8.54),
                ("Metals & Mining", 1.02, 14.35, 8.40),
                ("Office Equipment & Services", 1.20, 31.74, 8.05),
                ("Oil/Gas (Integrated)", 0.48, 12.06, 6.33),
                ("Oil/Gas (Production and Exploration)", 0.88, 21.04, 7.52),
                ("Oil/Gas Distribution", 0.75, 34.01, 6.59),
                ("Oilfield Svcs/Equip.", 0.94, 27.81, 7.44),
                ("Packaging & Container", 0.98, 34.60, 7.20),
                ("Paper/Forest Products", 1.07, 18.41, 8.32),
                ("Power", 0.54, 44.55, 5.54),
                ("Precious Metals", 1.23, 15.89, 9.09),
                ("Publishing & Newspapers", 0.64, 22.30, 6.63),
                ("R.E.I.T.", 0.95, 45.50, 6.62),
                ("Real Estate (Development)", 1.03, 52.09, 6.58),
                ("Real Estate (General/Diversified)", 0.86, 29.55, 6.99),
                ("Real Estate (Operations & Services)", 1.08, 22.35, 8.14),
                ("Recreation", 1.33, 39.43, 7.97),
                ("Reinsurance", 0.54, 26.78, 6.08),
                ("Restaurant/Dining", 1.01, 18.79, 8.05),
                ("Retail (Automotive)", 1.35, 33.51, 8.39),
                ("Retail (Building Supply)", 1.79, 16.80, 11.00),
                ("Retail (Distributors)", 1.12, 23.82, 8.16),
                ("Retail (General)", 1.06, 8.03, 8.79),
                ("Retail (Grocery and Food)", 0.58, 34.32, 5.96),
                ("Retail (REITs)", 0.95, 35.39, 6.96),
                ("Retail (Special Lines)", 1.22, 22.44, 8.64),
                ("Rubber & Tires", 0.65, 79.47, 5.33),
                ("Semiconductor", 1.49, 3.75, 10.76),
                ("Semiconductor Equip", 1.48, 7.56, 10.51),
                ("Shipbuilding & Marine", 0.58, 16.05, 6.64),
                ("Shoe", 1.42, 9.29, 10.15),
                ("Software (Entertainment)", 1.18, 2.43, 9.58),
                ("Software (Internet)", 1.69, 10.35, 11.10),
                ("Software (System & Application)", 1.24, 4.67, 9.69),
                ("Steel", 1.06, 20.57, 8.17),
                ("Telecom (Wireless)", 0.77, 32.25, 6.92),
                ("Telecom. Equipment", 1.00, 11.35, 8.39),
                ("Telecom. Services", 0.89, 50.04, 6.37),
                ("Tobacco", 0.98, 21.85, 7.95),
                ("Transportation", 1.03, 27.91, 7.72),
                ("Transportation (Railroads)", 0.99, 22.11, 7.75),
                ("Trucking", 1.10, 18.64, 8.39),
                ("Utility (General)", 0.39, 43.84, 5.20),
                ("Utility (Water)", 0.68, 36.96, 6.15)
            ]
            df = pd.DataFrame(data_snapshot, columns=["Industry", "Beta", "Debt%", "WACC"])
        else:
            # If CSV loaded, filter columns and rename for consistency
            df = df[["Industry Name", "Beta", "D/(D+E)", "Cost of Capital"]].copy()
            df.columns = ["Industry", "Beta", "Debt%", "WACC"]
        # If data was loaded successfully above, df is ready
        # Randomly sample the desired number of industries
        selected = df.sample(n=num_points, random_state=None).reset_index(drop=True)
        # Prepare game data and letters
        letters = [chr(65 + i) for i in range(len(selected))]
        game_data = []  # list of dicts for each point
        for i, row in selected.iterrows():
            ind_name = row["Industry"]
            beta_val = row["Beta"]
            debt_val = row["Debt%"] * (100 if row["Debt%"] <= 1 else 1)  # ensure percent (if in 0-1 form, convert)
            wacc_val = row["WACC"] * (100 if row["WACC"] <= 1 else 1)
            # Format to two decimals for consistency
            beta_val = float(f"{beta_val:.2f}")
            debt_val = float(f"{debt_val:.2f}")
            wacc_val = float(f"{wacc_val:.2f}")
            game_data.append({
                "letter": letters[i],
                "industry": ind_name,
                "beta": beta_val,
                "debt": debt_val,
                "wacc": wacc_val
            })
        # Shuffle the list of metric combinations for options
        combos = [
            f"Beta: {d['beta']:.2f}, Debt%: {d['debt']:.2f}%, WACC: {d['wacc']:.2f}%"
            for d in game_data
        ]
        random.shuffle(combos)
        # Store in session state
        st.session_state.game_data = game_data
        st.session_state.options = combos
        st.session_state.game_active = True
        st.session_state.submitted = False
        # Increment round counter for unique keys
        st.session_state.round += 1

# If a game is active, display the game interface
if st.session_state.game_active:
    game_data = st.session_state.game_data
    # During an active round, hide sidebar controls (already handled above).
    if not st.session_state.submitted:
        st.sidebar.write("🔒 Round in progress...")
    # Create 3D scatter plot with Plotly
    letters = [d["letter"] for d in game_data]
    x_vals = [d["beta"] for d in game_data]
    y_vals = [d["debt"] for d in game_data]
    z_vals = [d["wacc"] for d in game_data]
    fig = go.Figure(data=[go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals,
        mode='markers+text',
        text=letters,
        textposition='top center',
        marker=dict(size=6, color='blue'),
        hovertext=[f"{d['industry']}" for d in game_data],
        hovertemplate="<b>%{hovertext}</b><br>Beta: %{x}<br>Debt%%: %{y}<br>WACC: %{z}<extra></extra>"
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt (%)",
            zaxis_title="WACC (%)"
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    # If round not yet submitted, show dropdowns for answers
    if not st.session_state.submitted:
        st.markdown("**Match each industry to its Beta, Debt%, and WACC:**")
        # For each industry, show a dropdown of metric combinations
        answers = {}
        for d in game_data:
            letter = d["letter"]
            ind_name = d["industry"]
            prompt = f"Point {letter}: {ind_name}"
            # Unique key per round+letter to avoid reuse
            key = f"answer_{letter}_{st.session_state.round}"
            answers[letter] = st.selectbox(prompt, options=st.session_state.options, key=key)
        # Submit button
        if st.button("Submit Answers"):
            # Check for duplicate selections
            selections = list(answers.values())
            if len(set(selections)) < len(selections):
                st.error("❗ Each metrics combination must be used only once. Please adjust duplicate selections.")
                st.stop()
            # Calculate score
            score = 0.0
            correct_count = 0
            for d in game_data:
                letter = d["letter"]
                correct_combo = f"Beta: {d['beta']:.2f}, Debt%: {d['debt']:.2f}%, WACC: {d['wacc']:.2f}%"
                if answers[letter] == correct_combo:
                    score += 1.0
                    correct_count += 1
                else:
                    score -= 0.5
            # Round is finished
            st.session_state.submitted = True
            # Display score and feedback
            total = len(game_data)
            # Ensure at least one decimal place for score
            score_display = f"{score:.1f}" if abs(score - int(score)) > 1e-9 else f"{int(score)}"
            st.subheader(f"Results: {correct_count} out of {total} correct")
            st.write(f"**Score:** {score_display}")
            if correct_count == total:
                st.success("🎉 Perfect! You matched all industries correctly.")
    else:
        # Round submitted: show score results and enable new round in sidebar
        # (The score was calculated when submitted was set to True)
        # This block can display results if needed after rerun, but we handle results immediately above.
        pass
