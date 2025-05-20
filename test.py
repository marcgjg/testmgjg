import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import io

st.set_page_config(page_title="Industry Matching Game", page_icon="🔢", layout="wide")

st.title("🔢 Industry WACC Matching Game")
st.markdown("Match each 3D point (industry financial metrics) to the correct industry name. "
            "Choose your answers from the dropdowns below the chart. Try to get them all right "
            "before your score goes below zero!")

# --- Data Loading ---
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
# Attempt to load remote data (with caching to avoid repeated fetch)
@st.cache_data(show_spinner=False)
def load_data():
    try:
        response = requests.get(CSV_URL, timeout=5)
        if response.status_code == 200:
            csv_data = response.content
            df = pd.read_csv(io.BytesIO(csv_data))
            return df
    except Exception as e:
        return None

df = load_data()
# If remote fetch failed, allow user to upload data or use fallback sample
if df is None:
    st.warning("⚠️ Using fallback data. (Upload a CSV/XLSX file to use custom/full dataset.)")
    uploaded_file = st.sidebar.file_uploader("Upload industry WACC data", type=['csv', 'xlsx'])
    if uploaded_file:
        # Read user-provided file
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    else:
        # Hardcoded small sample (few industries):contentReference[oaicite:11]{index=11}
        SAMPLE_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
Apparel,1.36,9.68%,12.11%
Auto Parts,1.76,11.94%,19.59%
"""
        df = pd.read_csv(io.StringIO(SAMPLE_CSV))
# Clean and prepare data
# Strip '%' and convert to float for relevant columns
if 'Cost of Capital' in df.columns:
    df['Cost of Capital'] = df['Cost of Capital'].astype(str).str.rstrip('%').astype(float)
if 'D/(D+E)' in df.columns:
    df['D/(D+E)'] = df['D/(D+E)'].astype(str).str.rstrip('%').astype(float)
# Ensure correct column names and types
df.rename(columns=lambda x: x.strip(), inplace=True)
# (At this point, df has the needed columns ready.)

# --- Sidebar: Game Controls ---
st.sidebar.header("Game Setup")
max_n = min(10, len(df))
num_industries = st.sidebar.slider("Number of industries to match", min_value=1, max_value=max_n, value=min(5, max_n))
if st.sidebar.button("🔄 Start New Game"):
    # Randomly select industries for the game
    chosen = df.sample(num_industries).reset_index(drop=True)
    labels = [chr(65+i) for i in range(num_industries)]  # e.g. ['A','B',...]
    # Store mapping of label to industry name
    st.session_state.correct_mapping = {labels[i]: chosen.at[i, "Industry Name"] for i in range(num_industries)}
    # Store list of industry names (options for guessing), shuffled to avoid order clues
    names_list = list(chosen["Industry Name"])
    np.random.shuffle(names_list)
    st.session_state.labels_list = names_list
    # Store the numeric coordinates for plotting (as numpy array for convenience)
    st.session_state.coords = chosen[["D/(D+E)", "Beta", "Cost of Capital"]].values
    st.session_state.labels = labels
    # Initialize game state variables
    st.session_state.score = 0
    st.session_state.correct_guesses = set()
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.last_feedback = ""
    # Reset any old guess inputs (clear selectbox states from previous game)
    for letter in labels:
        key = f"sel_{letter}"
        if key in st.session_state:
            del st.session_state[key]

# If a game has been started, proceed with display
if "labels" in st.session_state:
    # --- Display 3D Scatter Plot ---
    coords = st.session_state.coords
    fig = go.Figure(data=[go.Scatter3d(
        x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
        mode='markers+text',
        text=st.session_state.labels,
        textposition='top center',
        marker=dict(size=6, color='royalblue')
    )])
    fig.update_layout(scene=dict(
        xaxis_title="Debt/(Debt+Equity) (%)",
        yaxis_title="Beta",
        zaxis_title="WACC (%)"
    ))
    st.plotly_chart(fig, use_container_width=True)
    
    # Show current score and feedback from last guess (if any)
    if st.session_state.last_feedback:
        st.info(st.session_state.last_feedback)
    else:
        st.info(f"**Score:** {st.session_state.score} (Start guessing the industries below)")
    
    # --- Guessing Form ---
    if not st.session_state.game_over and not st.session_state.victory:
        with st.form("guess_form"):
            selections = {}
            # Create a selectbox for each point that is not yet correctly guessed
            for letter in st.session_state.labels:
                if letter in st.session_state.correct_guesses:
                    # Already correct: show as fixed
                    st.write(f"**Point {letter}: {st.session_state.correct_mapping[letter]}** ✓")
                else:
                    selections[letter] = st.selectbox(f"Industry for point {letter}",
                                                      options=st.session_state.labels_list,
                                                      index=None,  # no pre-selection
                                                      format_func=lambda x: "Select industry..." if x == "" else x,
                                                      key=f"sel_{letter}")
            submitted = st.form_submit_button("Submit Guesses")
        if submitted:
            # Validate all selections made
            if None in selections.values() or "" in selections.values():
                st.warning("Please select an industry for *every* point before submitting.")
            else:
                correct_count = wrong_count = 0
                # Evaluate each guess
                for letter, guess_name in selections.items():
                    if guess_name == st.session_state.correct_mapping[letter]:
                        correct_count += 1
                        st.session_state.correct_guesses.add(letter)
                    else:
                        wrong_count += 1
                # Update score
                st.session_state.score += (correct_count - wrong_count)
                # Prepare feedback message
                feedback = f"✅ **Correct this round:** {correct_count} &nbsp;&nbsp; ❌ **Wrong:** {wrong_count} &nbsp;&nbsp; " \
                           f"🔔 **Score:** {st.session_state.score}"
                st.session_state.last_feedback = feedback
                # Check for win/lose conditions
                if st.session_state.score < 0:
                    st.session_state.game_over = True
                elif len(st.session_state.correct_guesses) == len(st.session_state.labels):
                    st.session_state.victory = True
                # Trigger a rerun to update the UI (show/hide form or end game message)
                st.experimental_rerun()
    # --- End of Game Messages ---
    if st.session_state.victory:
        st.success(f"🎉 Congratulations, you matched all industries correctly! Final Score: {st.session_state.score}")
        # Reveal all matches
        answer_list = [f"{label} = {name}" for label, name in st.session_state.correct_mapping.items()]
        st.write("**Correct matches:** " + ", ".join(answer_list))
    if st.session_state.game_over:
        st.error(f"💥 Game over! Your score fell below 0. Better luck next time.")
        # Show the correct answers
        answer_list = [f"{label} = {name}" for label, name in st.session_state.correct_mapping.items()]
        st.write("**The correct matches were:** " + ", ".join(answer_list))
else:
    st.sidebar.info("Choose the number of industries and click **Start New Game** to begin.")
    st.write("*No game in progress. Use the sidebar to start a new game.*")
