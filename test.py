import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="Industry Matching Game", page_icon="🎲", layout="wide")
st.title("🔀 Industry Matching Game")
st.write("Match each letter-labelled point to its industry. Pick your settings in the sidebar and start playing!")

# ───────────────────────── Data helpers ────────────────────────── #
@st.cache_data(show_spinner=False)
def load_damodaran_wacc():
    url = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"
    try:
        tables = pd.read_html(url)
        df = tables[0]
        for col in ["Cost of Capital", "D/(D+E)"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.rstrip("%").astype(float)
        return df
    except Exception:
        return None

FALLBACK = pd.DataFrame({
    "Industry Name": ["Advertising", "Aerospace/Defense", "Air Transport",
                      "Auto & Truck", "Beverages (Soft)"],
    "Beta": [1.34, 0.90, 1.24, 1.62, 0.57],
    "Cost of Capital": [9.22, 7.68, 7.29, 10.34, 6.59],
    "D/(D+E)": [20.8, 18.6, 51.7, 18.3, 16.5]
})

# ───────────────────────── Session defaults ────────────────────── #
default_state = dict(
    game_active=False, game_over=False,
    score=0, letters=[], mapping={}, data=pd.DataFrame()
)
for k, v in default_state.items():
    st.session_state.setdefault(k, v)

# ───────────────────────── Sidebar – setup ─────────────────────── #
st.sidebar.header("Game setup")
n_max = 10
n_choice = st.sidebar.slider("Number of industries", 1, n_max, 5)
data_source = st.sidebar.radio("Data source", ["Damodaran online", "Upload file"])
upload = None
if data_source == "Upload file":
    upload = st.sidebar.file_uploader("CSV or XLSX", type=["csv", "xlsx"])
start = st.sidebar.button("Start new game")

if start:
    # -- choose dataset ---------------------------------------------------- #
    if upload is not None:
        try:
            if upload.name.endswith(".csv"):
                df_raw = pd.read_csv(upload)
            else:
                df_raw = pd.read_excel(upload, engine="openpyxl")
        except Exception:
            st.sidebar.error("File read failed – using fallback sample.")
            df_raw = FALLBACK.copy()
    else:
        df_raw = load_damodaran_wacc() or FALLBACK.copy()

    needed = {"Industry Name", "Beta", "Cost of Capital", "D/(D+E)"}
    if not needed.issubset(df_raw.columns):
        st.sidebar.error("Dataset missing required columns – using fallback sample.")
        df_raw = FALLBACK.copy()

    # random selection
    n = min(n_choice, len(df_raw))
    subset = df_raw.sample(n, random_state=random.randint(0, 999999)).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n)]
    mapping = {letters[i]: subset.at[i, "Industry Name"] for i in range(n)}

    # store in session
    st.session_state.update({
        "game_active": True,
        "game_over": False,
        "score": 0,
        "letters": letters,
        "mapping": mapping,
        "data": subset
    })
    # clear old guesses
    for k in list(st.session_state.keys()):
        if k.startswith("guess_"):
            del st.session_state[k]

# ───────────────────────── Game play UI ─────────────────────────── #
if st.session_state.game_active:
    letters = st.session_state.letters
    data = st.session_state.data

    st.subheader(f"Current score: {st.session_state.score}")

    # 3-D plot
    fig = go.Figure(go.Scatter3d(
        x=data["Beta"], y=data["D/(D+E)"], z=data["Cost of Capital"],
        mode="markers+text",
        text=letters, textposition="top center",
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

    if not st.session_state.game_over:
        with st.form("guesses"):
            st.write("Select an industry for each point:")
            opts = data["Industry Name"].tolist()
            random.shuffle(opts)
            opts_placeholder = ["– pick –"] + opts
            for L in letters:
                st.selectbox(L, opts_placeholder, key=f"guess_{L}")
            submitted = st.form_submit_button("Submit")

        # process guesses
        if submitted:
            guesses = {L: st.session_state[f"guess_{L}"] for L in letters}
            if "– pick –" in guesses.values():
                st.warning("Make a selection for every point.")
            else:
                correct = sum(guesses[L] == st.session_state.mapping[L] for L in letters)
                wrong = len(letters) - correct
                st.session_state.score += (correct - wrong)

                if correct == len(letters):
                    st.session_state.game_over = True
                    st.success(f"🎉 All correct! Final score: {st.session_state.score}")
                    st.table(pd.DataFrame({
                        "Letter": letters,
                        "Industry": [st.session_state.mapping[L] for L in letters]
                    }))
                elif st.session_state.score < 0:
                    st.session_state.game_over = True
                    st.error(f"💀 Score below zero. Game over.")
                    st.table(pd.DataFrame({
                        "Letter": letters,
                        "Industry": [st.session_state.mapping[L] for L in letters]
                    }))
                else:
                    st.info(f"Correct: {correct} · Wrong: {wrong} → Score {st.session_state.score}. Try again!")

# fallback message if no game yet
if not st.session_state.game_active:
    st.info("Configure the game in the sidebar and click **Start new game** to begin.")
