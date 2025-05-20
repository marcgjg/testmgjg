import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from io import StringIO

# ───────────── APP CONFIGURATION ───────────── #
st.set_page_config(page_title="Industry Matching Game", page_icon="🏭", layout="wide")
st.title("🏭 Industry Financials Matching Game")
st.write("Match each letter-labeled data point in the plot to the correct industry.")

# ───────────── LOAD DATA ───────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SAMPLE_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.51,8.79%,18.55%
Aerospace/Defense,1.18,7.77%,22.29%
Air Transport,1.44,8.77%,37.06%
"""

# Load data: try user-uploaded file, then remote CSV, else fallback sample
df = None
user_file = st.sidebar.file_uploader("Upload your own data (CSV or XLSX)", type=['csv', 'xlsx'])
if user_file is not None:
    try:
        if user_file.name.lower().endswith('.csv'):
            df = pd.read_csv(user_file)
        else:
            df = pd.read_excel(user_file, engine='openpyxl')
    except Exception as e:
        st.sidebar.error(f"Failed to read file: {e}")
        df = None

if df is None:
    try:
        res = requests.get(CSV_URL, timeout=5)
        if res.status_code == 200:
            data_str = res.content.decode('utf-8', errors='ignore')
            df = pd.read_csv(StringIO(data_str))
        else:
            df = pd.read_csv(StringIO(SAMPLE_CSV))
            st.sidebar.warning("Could not fetch live data, using sample data.")
    except Exception:
        df = pd.read_csv(StringIO(SAMPLE_CSV))
        st.sidebar.warning("Could not fetch live data, using sample data.")

# Ensure required columns are present
required_cols = ["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]
if not all(col in df.columns for col in required_cols):
    st.error("Dataset must contain 'Industry Name', 'Beta', 'Cost of Capital', 'D/(D+E)' columns.")
    st.stop()

# Clean and prepare data columns
df["Beta"] = pd.to_numeric(df["Beta"], errors='coerce')
df["Cost of Capital"] = df["Cost of Capital"].astype(str).str.rstrip('%')
df["D/(D+E)"] = df["D/(D+E)"].astype(str).str.rstrip('%')
df["Cost of Capital"] = pd.to_numeric(df["Cost of Capital"], errors='coerce')
df["D/(D+E)"] = pd.to_numeric(df["D/(D+E)"], errors='coerce')
df.dropna(subset=required_cols, inplace=True)
df.reset_index(drop=True, inplace=True)

# Sidebar game controls
st.sidebar.markdown("### Game Settings")
max_industries = min(10, len(df))
num_choice = st.sidebar.slider("Number of industries to match", 1, max_industries, value=min(5, max_industries))
start_game = st.sidebar.button("Start New Game")

# Initialize session state
if "game_status" not in st.session_state:
    st.session_state.game_status = "not_started"
if "chosen_df" not in st.session_state:
    st.session_state.chosen_df = pd.DataFrame()
if "options" not in st.session_state:
    st.session_state.options = []

if start_game:
    N = num_choice
    if len(df) < N:
        N = len(df)
        st.sidebar.warning(f"Only {len(df)} industries available; starting game with all.")
    # Pick N random industries for this game
    chosen_df = df.sample(n=N, random_state=None).reset_index(drop=True)
    st.session_state.chosen_df = chosen_df
    # Prepare shuffled list of industry names for dropdowns (with placeholder)
    industries_list = chosen_df["Industry Name"].tolist()
    np.random.shuffle(industries_list)
    st.session_state.options = ["(choose industry)"] + industries_list
    # Reset guess selections for each point
    for i in range(N):
        letter = chr(65 + i)  # 'A', 'B', 'C', ...
        st.session_state[f"guess_{letter}"] = "(choose industry)"
    st.session_state.game_status = "playing"

# ───────────── GAME LOGIC & INTERFACE ───────────── #
if st.session_state.game_status in ["playing", "won", "lost"]:
    if st.session_state.game_status == "playing":
        chosen_df = st.session_state.chosen_df
        N = chosen_df.shape[0]
        letters = [chr(65 + i) for i in range(N)]
        # Plot the data points in 3D with letters A, B, C... as labels
        fig = go.Figure(data=[go.Scatter3d(
            x=chosen_df["D/(D+E)"],
            y=chosen_df["Beta"],
            z=chosen_df["Cost of Capital"],
            mode='markers+text',
            text=letters,
            textposition="top center",
            marker=dict(size=6, color='blue'),
            hovertemplate="Point %{text}: Debt/(D+E) = %{x}%<br>Beta = %{y}<br>Cost of Capital = %{z}%"
        )])
        fig.update_layout(
            scene=dict(
                xaxis_title="Debt/(Debt+Equity) (%)",
                yaxis_title="Beta",
                zaxis_title="Cost of Capital (%)"
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        # Input form for guesses
        with st.form("guess_form"):
            st.markdown("**Select the industry for each point:**")
            for letter in letters:
                st.selectbox(f"Point {letter}:", options=st.session_state.options, key=f"guess_{letter}")
            submit = st.form_submit_button("Submit Guesses")
        if submit:
            guesses = [st.session_state[f"guess_{letter}"] for letter in letters]
            if "(choose industry)" in guesses:
                st.warning("Please select an industry for each point before submitting.")
            else:
                correct = wrong = 0
                for i, letter in enumerate(letters):
                    actual = chosen_df.loc[i, "Industry Name"]
                    if st.session_state[f"guess_{letter}"] == actual:
                        correct += 1
                    else:
                        wrong += 1
                score = correct - wrong
                if score < 0:
                    st.session_state.game_status = "lost"
                    st.experimental_rerun()
                elif correct == N:
                    st.session_state.game_status = "won"
                    st.experimental_rerun()
                else:
                    st.info(f"Score: {score}. Not all matches are correct, try again!")
    elif st.session_state.game_status == "won":
        st.balloons()
        st.markdown("**🎉 You won!** You matched all industries correctly. Use **Start New Game** to play again.")
    elif st.session_state.game_status == "lost":
        st.markdown("**💀 Game over.** You've run out of points. Use **Start New Game** to try again.")
else:
    st.markdown("⚙️ *Adjust the settings in the sidebar and click **Start New Game** to begin.*")
