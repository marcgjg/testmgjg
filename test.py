import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# Optional: set wide layout and title
st.set_page_config(page_title="Industry Matching Game", page_icon="🎲", layout="wide")
st.title("🔀 Industry Matching Game")
st.write("Match each letter-labeled data point to the correct industry. Choose the number of industries and data source below to begin:")

# --- Data loading function with caching ---
@st.cache_data
def load_damodaran_wacc():
    """Load Damodaran's latest WACC data (US) into a DataFrame, or return None on failure."""
    url = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"
    try:
        tables = pd.read_html(url)  # parse HTML tables on the page
        df = tables[0]
        # Ensure expected columns exist
        if "Industry Name" in df.columns:
            # Clean percentage columns by removing '%' and converting to float
            for col in ["Cost of Capital", "D/(D+E)"]:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.rstrip('%').astype(float)
            return df
    except Exception as e:
        st.warning("Could not load live WACC data, will use fallback sample.")
    return None

# Fallback sample data (in case online data isn't available)
fallback_data = {
    "Industry Name": [
        "Advertising", "Aerospace/Defense", "Air Transport", "Apparel", "Auto & Truck", 
        "Auto Parts", "Bank (Money Center)", "Banks (Regional)", "Beverage (Alcoholic)", "Beverage (Soft)"
    ],
    "Beta": [1.34, 0.90, 1.24, 0.99, 1.62, 1.23, 0.88, 0.52, 0.61, 0.57],
    "Cost of Capital": [9.22, 7.68, 7.29, 7.44, 10.34, 8.09, 5.64, 5.69, 6.55, 6.59],  # WACC percentages
    "D/(D+E)": [20.76, 18.56, 51.65, 31.45, 18.30, 32.36, 64.69, 37.62, 23.35, 16.48]   # Debt ratio percentages
}
fallback_df = pd.DataFrame(fallback_data)

# --- Initialize session state variables if not already set ---
if "game_active" not in st.session_state:
    st.session_state.game_active = False
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.answers = {}   # mapping of letters to industry names
    st.session_state.letters = []   # list of letters for current game

# --- Game Setup Form (shown if no game is active or after a game ends) ---
if not st.session_state.game_active or st.session_state.game_over:
    with st.form("setup_form", clear_on_submit=True):
        num_options = st.slider("Number of industries to match:", min_value=1, max_value=10, value=5)
        data_source = st.radio("Data source:", ["Use Damodaran WACC data (latest)", "Upload my own dataset"])
        uploaded_file = None
        if data_source == "Upload my own dataset":
            uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])
        start = st.form_submit_button("Start Game")
    if start:
        # Determine which dataset to use
        if uploaded_file is not None:
            # User provided a file
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file, engine="openpyxl")
            except Exception as e:
                st.error("Error reading file. Falling back to sample data.")
                df = fallback_df.copy()
        else:
            # Use Damodaran data if possible, otherwise fallback
            df = load_damodaran_wacc()
            if df is None:
                df = fallback_df.copy()
        
        # Ensure the important columns are present
        required_cols = {"Industry Name", "Beta", "Cost of Capital", "D/(D+E)"}
        if not required_cols.issubset(df.columns):
            st.warning("Uploaded data is missing required columns. Using fallback sample data.")
            df = fallback_df.copy()
        
        # Clean percentage columns in uploaded data if needed
        for col in ["Cost of Capital", "D/(D+E)"]:
            if col in df.columns and df[col].dtype == object:
                # Remove '%' if present and convert to float
                df[col] = df[col].astype(str).str.rstrip('%').astype(float)
        
        # Randomly sample the specified number of industries
        try:
            df_selection = df.sample(num_options, random_state=42)  # fixed seed for reproducibility (optional)
        except ValueError:
            df_selection = df.copy()  # if df has fewer rows than num_options, just take all
        df_selection = df_selection.reset_index(drop=True)
        N = len(df_selection)
        letters = [chr(65 + i) for i in range(N)]  # List of labels: 'A', 'B', 'C', ...
        
        # Map letters to industry names
        mapping = {letters[i]: df_selection.loc[i, "Industry Name"] for i in range(N)}
        
        # Reset any old game state and set new game state
        st.session_state.game_active = True
        st.session_state.game_over = False
        st.session_state.score = 0
        st.session_state.letters = letters
        st.session_state.answers = mapping
        st.session_state.selected_data = df_selection  # store the selected subset for reuse
        
        # Clear any old guess selections from session_state
        for key in list(st.session_state.keys()):
            if key.startswith("guess_"):
                del st.session_state[key]
        
        st.experimental_rerun()  # rerun to refresh the UI for the game (since we changed state)
        
# --- Main Game Interface (shown when a game is active and not over) ---
if st.session_state.game_active and not st.session_state.game_over:
    # Display current score
    st.subheader(f"Current Score: {st.session_state.score}")
    
    # Retrieve selected industries data
    data = st.session_state.selected_data
    letters = st.session_state.letters
    
    # Plotly 3D scatter plot of the selected industries
    fig = go.Figure(data=[go.Scatter3d(
        x=data["Beta"], 
        y=data["D/(D+E)"], 
        z=data["Cost of Capital"],
        mode='markers+text',
        text=letters,
        textposition='top center',
        marker=dict(size=6, color='blue')
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt Ratio (%)",
            zaxis_title="WACC (%)"
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a form for the user's guesses
    with st.form("guess_form"):
        st.write("**Match each letter to an industry:**")
        # Prepare options for dropdowns (shuffle the industry names so order is not alphabetical)
        options = list(data["Industry Name"])
        random.shuffle(options)
        # Add a placeholder option at top
        placeholder = "– Select an industry –"
        options_with_placeholder = [placeholder] + options
        # Create a selectbox for each letter
        for letter in letters:
            st.selectbox(f"**{letter}:**", options_with_placeholder, index=0, key=f"guess_{letter}")
        submit = st.form_submit_button("Submit Guesses")
    
    if submit:
        # Gather the guesses into a dictionary: {letter: chosen_industry}
        guesses = {letter: st.session_state[f"guess_{letter}"] for letter in letters}
        # Check if any placeholder remains
        if placeholder in guesses.values():
            st.error("Please select an industry for each letter before submitting.")
        else:
            # Calculate score changes
            correct_matches = sum(1 for letter in letters if guesses[letter] == st.session_state.answers.get(letter))
            wrong_matches = len(letters) - correct_matches
            # Update cumulative score
            st.session_state.score += (correct_matches - wrong_matches)
            # Check win/lose conditions
            if correct_matches == len(letters):
                # Win condition
                st.session_state.game_over = True
                st.success(f"🎉 You win! You matched all {len(letters)} industries correctly. Final Score: {st.session_state.score}")
                # Reveal the correct answers
                answer_df = pd.DataFrame({
                    "Letter": letters,
                    "Industry": [st.session_state.answers[l] for l in letters]
                })
                st.write("**Correct Matches:**")
                st.table(answer_df)
            elif st.session_state.score < 0:
                # Loss condition
                st.session_state.game_over = True
                st.error(f"💥 Game over! Your score fell below 0 (Score: {st.session_state.score}).")
                # Reveal correct answers
                answer_df = pd.DataFrame({
                    "Letter": letters,
                    "Industry": [st.session_state.answers[l] for l in letters]
                })
                st.write("**Correct Matches were:**")
                st.table(answer_df)
            else:
                # Continue game: provide feedback and allow another attempt
                st.info(f"You got **{correct_matches} / {len(letters)}** correct. Adjust your guesses and submit again!")
                st.experimental_rerun()
                
# --- Option to start a new game after win/lose ---
if st.session_state.game_active and st.session_state.game_over:
    # Offer a button to play again (reset game_active to False to show setup form)
    if st.button("Play Again"):
        st.session_state.game_active = False
        st.session_state.game_over = False
        st.experimental_rerun()
