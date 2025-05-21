import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, random
from io import StringIO

# ---------- Config ----------
st.set_page_config(page_title="Industry Guessing Game",
                   page_icon="🏭", layout="wide")
st.title("🏭 Industry WACC Guessing Game")
st.write(
    "Match each letter-labelled point to its **industry name**. "
    "Scoring: **+1** correct, **−0.5** wrong. "
    "Each industry can be chosen only once per round."
)

# ---------- Data ----------
URL = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"
@st.cache_data(ttl=86_400)
def fetch_table():
    try:
        t = requests.get(URL, timeout=10).text
        df = pd.read_html(t)[0]
        df = df[~df["Industry Name"].str.contains("Total Market", na=False)]
        for c in ["Cost of Capital", "D/(D+E)"]:
            df[c] = df[c].astype(str).str.rstrip("%").astype(float)
        return df
    except Exception:
        return None

FALLBACK = pd.read_csv(StringIO("""Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22,20.76
Aerospace/Defense,0.90,7.68,18.56
Air Transport,1.24,7.29,51.65
Apparel,0.99,7.44,31.45
Auto & Truck,1.62,10.34,18.30
Auto Parts,1.23,8.09,32.36
Bank (Money Center),0.88,5.64,64.69
Banks (Regional),0.52,5.69,37.62
Beverage (Alcoholic),0.61,6.55,23.35
Beverage (Soft),0.57,6.59,16.48
"""))
df = fetch_table() or FALLBACK

# ---------- Sidebar ----------
st.sidebar.header("Settings")
max_n = min(10, len(df))
n_ind = st.sidebar.slider("Industries per round", 2, max_n, 5)
if st.sidebar.button("Start / Restart round"):
    subset = df.sample(n_ind, random_state=random.randint(0, 1_000_000)).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n_ind)]
    mapping = {letters[i]: subset.at[i, "Industry Name"] for i in range(n_ind)}
    st.session_state.update(
        active=True, finished=False, letters=letters, subset=subset,
        mapping=mapping
    )
    # clear old guesses
    for k in list(st.session_state.keys()):
        if k.startswith("guess_"):
            del st.session_state[k]
    if "score" not in st.session_state:
        st.session_state.score = 0.0

# ---------- Game ----------
if st.session_state.get("active"):
    letters = st.session_state.letters
    sub = st.session_state.subset
    st.subheader(f"Score: {st.session_state.score:.2f}")

    # 3-D scatter
    fig = go.Figure(go.Scatter3d(
        x=sub["Beta"], y=sub["D/(D+E)"], z=sub["Cost of Capital"],
        mode="markers+text", text=letters, textposition="top center",
        marker=dict(size=6, color="#1f77b4")
    ))
    fig.update_layout(scene=dict(xaxis_title="Beta",
                                 yaxis_title="Debt ratio (%)",
                                 zaxis_title="WACC (%)"),
                      margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    placeholder = "— pick —"
    if not st.session_state.get("finished"):
        with st.form("match"):
            taken = set()                           # grows as we go
            for L, row in zip(letters, sub.itertuples()):
                current = st.session_state.get(f"guess_{L}", placeholder)
                # available names = not taken OR already chosen for this box
                avail = [name for name in sub["Industry Name"]
                         if name not in taken or name == current]
                opts = [placeholder] + sorted(avail)
                if current not in opts:
                    current = placeholder            # reset if illegal
                idx = opts.index(current)
                choice = st.selectbox(
                    f"{L}: {row._1}",  # row._1 is Industry Name via itertuples
                    opts, index=idx, key=f"guess_{L}"
                )
                taken.add(choice)
            submitted = st.form_submit_button("Submit guesses")

        if submitted:
            guesses = {L: st.session_state[f"guess_{L}"] for L in letters}
            # Validation
            if placeholder in guesses.values():
                st.warning("Select an industry for **every** letter.")
            elif len(set(guesses.values())) < len(guesses):
                st.warning("Duplicate industries selected. Each name can be used only once.")
            else:
                correct = sum(guesses[L] == st.session_state.mapping[L] for L in letters)
                wrong = len(letters) - correct
                st.session_state.score += correct - 0.5 * wrong
                if correct == len(letters):
                    st.success(f"🎉 All correct! Total score {st.session_state.score:.2f}")
                    st.session_state.finished = True
                elif st.session_state.score < 0:
                    st.error(f"💀 Score below zero. Game over! "
                             f"Final score {st.session_state.score:.2f}")
                    st.session_state.finished = True
                else:
                    st.info(f"Correct {correct} · Wrong {wrong} → "
                            f"Score {st.session_state.score:.2f}. Try again!")

    # ---- answers after finish ----
    if st.session_state.get("finished"):
        st.subheader("Correct answers")
        st.table(pd.DataFrame({
            "Letter": letters,
            "Industry": [st.session_state.mapping[L] for L in letters]
        }).set_index("Letter"))
        st.info("Start a new round from the sidebar when ready.")
else:
    st.info("Set the number of industries and click **Start / Restart round** to play.")
