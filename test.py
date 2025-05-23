import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, requests

st.set_page_config(page_title="Industry WACC Guess", page_icon="🏭", layout="wide")

LIVE_CSV = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
SNAPSHOT_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22%,20.76%
Aerospace/Defense,0.90,7.68%,18.56%
Air Transport,1.24,7.29%,51.65%
Apparel,0.99,7.44%,31.45%
Auto & Truck,1.62,10.34%,18.30%
... (snapshot continues with full list from previous message) ...
Utility (Water),0.68,6.15%,36.96%
"""

@st.cache_data
def load_table():
    try:
        df = pd.read_csv(LIVE_CSV)
    except Exception:
        df = pd.read_csv(io.StringIO(SNAPSHOT_CSV))
    df = df[~df["Industry Name"].str.startswith("Total Market")]
    df["Cost of Capital"] = df["Cost of Capital"].str.rstrip("%").astype(float)/100
    df["D/(D+E)"] = df["D/(D+E)"].str.rstrip("%").astype(float)/100
    return df

df_all = load_table()

# --------------- helpers ----------------
def start_round(n):
    sample = df_all.sample(n).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n)]
    st.session_state.stage   = "playing"
    st.session_state.df      = sample
    st.session_state.letters = letters
    st.session_state.guess   = {L: None for L in letters}
    st.session_state.score   = None   # not yet scored

def reset_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def plot(df, letters):
    fig = go.Figure(go.Scatter3d(
        x=df["Beta"], y=df["D/(D+E)"], z=df["Cost of Capital"],
        mode="markers+text", text=letters, textposition="top center",
        marker=dict(size=6,color="#1f77b4"),
        hovertemplate="β %{x:.2f}<br>Debt %{y:.2%}<br>WACC %{z:.2%}"
    ))
    fig.update_layout(height=600, margin=dict(l=0,r=0,t=20,b=0),
                      scene=dict(xaxis_title="Beta",
                                 yaxis_title="Debt ratio",
                                 zaxis_title="WACC"))
    return fig

# --------------- initial session vars ---------------
if "stage" not in st.session_state:
    st.session_state.stage = "setup"       # setup | playing | finished

# --------------- sidebar ----------------------------
with st.sidebar:
    st.header("Controls")
    if st.button("Reset everything", type="secondary"):
        reset_all()
        st.experimental_rerun()

    if st.session_state.stage in ("setup","finished"):
        n_val = st.slider("Industries in round", 2, 10, 5,
                          key="slider_n")
        if st.button("Start round"):
            start_round(n_val)
    else:
        st.write("🔒 Round in progress…")

# --------------- main area --------------------------
st.title("🏭 Industry WACC guessing game")
st.write("Match each point to its industry. Duplicates blocked. "
         "Scoring: +1 correct, −0.5 wrong.")

stage = st.session_state.stage

if stage == "setup":
    st.info("Use the slider in the sidebar then click **Start round**.")

elif stage == "playing":
    df   = st.session_state.df
    lets = st.session_state.letters
    st.plotly_chart(plot(df, lets), use_container_width=True)

    with st.form("guess_form"):
        placeholder = "— pick —"
        taken = set()
        for i,L in enumerate(lets):
            current = st.session_state.guess[L]
            choices = [ind for ind in df["Industry Name"]
                       if ind not in taken or ind==current]
            opts = [placeholder] + sorted(choices)
            beta, debt, wacc = df.at[i,"Beta"], df.at[i,"D/(D+E)"]*100, df.at[i,"Cost of Capital"]*100
            prompt = f"Point {L}: β {beta:.2f}, Debt {debt:.2f}%, WACC {wacc:.2f}%"
            sel = st.selectbox(prompt, opts,
                               index = opts.index(current) if current else 0)
            st.session_state.guess[L] = None if sel==placeholder else sel
            if sel!=placeholder: taken.add(sel)
        submit = st.form_submit_button("Submit")

    if submit:
        guesses = st.session_state.guess
        if None in guesses.values():
            st.warning("Choose an industry for every point.")
        elif len(set(guesses.values())) < len(guesses):
            st.warning("Duplicate industries selected.")
        else:
            corr  = sum(guesses[L]==df.at[i,"Industry Name"]
                        for i,L in enumerate(lets))
            wrong = len(lets)-corr
            st.session_state.score = corr - 0.5*wrong
            st.session_state.stage = "finished"
            st.experimental_rerun()

elif stage == "finished":
    df   = st.session_state.df
    lets = st.session_state.letters
    st.plotly_chart(plot(df, lets), use_container_width=True)
    score = st.session_state.score
    st.subheader(f"Round score: {score:.2f}")
    if score == len(lets):
        st.success("Perfect round! 🎉")
    elif score < 0:
        st.error("Score below zero — game over.")
    else:
        st.info("Round complete.")

    st.table(pd.DataFrame({"Letter": lets, "Industry": df["Industry Name"]})
             .set_index("Letter"))
    st.markdown("Start another round from the sidebar when ready.")
