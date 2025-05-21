import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, random
from io import StringIO

# ─────────── config ─────────── #
st.set_page_config(page_title="Industry Guessing Game", page_icon="🏭", layout="wide")
st.title("🏭 Industry WACC Guessing Game")
st.write(
    "Match each letter-labelled point to its **industry**. "
    "Scoring: **+1** correct · **−0.5** wrong. "
    "Duplicate picks are disabled—each industry can only be used once."
)

# ─────────── load Damodaran data ─────────── #
URL = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"

@st.cache_data(ttl=24*3600, show_spinner="Loading Damodaran table …")
def fetch_wacc():
    try:
        html = requests.get(URL, timeout=10).text
        df = pd.read_html(html)[0]
        df = df[~df["Industry Name"].str.contains("Total Market", na=False)]
        for col in ["Cost of Capital", "D/(D+E)"]:
            df[col] = df[col].astype(str).str.rstrip("%").astype(float)
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
"""))  # first 10 rows shown for brevity

df = fetch_wacc() or FALLBACK

# ─────────── sidebar controls ─────────── #
st.sidebar.header("Settings")
n_max = min(10, len(df))
n_ind = st.sidebar.slider("Industries per round", 2, n_max, 5)
start = st.sidebar.button("Start / Restart round")

# ─────────── session defaults ─────────── #
defaults = dict(active=False, finished=False, score=0.0,
                letters=[], mapping={}, subset=pd.DataFrame())
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ─────────── start new round ─────────── #
if start:
    sub = df.sample(n_ind, random_state=random.randint(0, 1_000_000)).reset_index(drop=True)
    letters = [chr(65+i) for i in range(len(sub))]
    st.session_state.update(
        active=True, finished=False, score=st.session_state.score,  # keep running score
        letters=letters, subset=sub,
        mapping={letters[i]: sub.at[i, "Industry Name"] for i in range(len(sub))}
    )
    for k in list(st.session_state.keys()):
        if k.startswith("guess_"):
            del st.session_state[k]

# ─────────── game UI ─────────── #
if st.session_state.active:
    sub = st.session_state.subset
    letters = st.session_state.letters
    st.subheader(f"Score: {st.session_state.score:.2f}")

    # 3-D plot
    fig = go.Figure(go.Scatter3d(
        x=sub["Beta"], y=sub["D/(D+E)"], z=sub["Cost of Capital"],
        mode="markers+text", text=letters, textposition="top center",
        marker=dict(size=6, color="#1f77b4")
    ))
    fig.update_layout(
        scene=dict(xaxis_title="Beta",
                   yaxis_title="Debt ratio (%)",
                   zaxis_title="WACC (%)"),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------- guessing form ---------- #
    if not st.session_state.finished:
        with st.form("guess_form"):
            st.write("Pick **each industry's name** (no duplicates allowed):")
            industries = sub["Industry Name"].tolist()
            random.shuffle(industries)                      # shuffle option order
            placeholder = "– pick –"

            # gather current selections to filter options live
            current = {L: st.session_state.get(f"guess_{L}", placeholder)
                       for L in letters}

            for L in letters:
                # options = placeholder + industries not picked yet OR this row's current pick
                taken = {v for k, v in current.items() if k != L}
                avail = [i for i in industries if i not in taken]
                opts = [placeholder] + avail
                index = opts.index(current[L]) if current[L] in opts else 0
                current[L] = st.selectbox(
                    f"Point {L}", opts, index=index, key=f"guess_{L}"
                )

            submitted = st.form_submit_button("Submit guesses")

        if submitted:
            if placeholder in current.values():
                st.warning("Choose an industry for every point before submitting.")
            else:
                correct = sum(current[L] == st.session_state.mapping[L] for L in letters)
                wrong = len(letters) - correct
                st.session_state.score += correct - 0.5 * wrong

                if correct == len(letters):
                    st.success(f"🎉 All correct! Round complete. "
                               f"Total score {st.session_state.score:.2f}")
                    st.session_state.finished = True
                elif st.session_state.score < 0:
                    st.error(f"💀 Score below 0. Game over! "
                             f"Final score {st.session_state.score:.2f}")
                    st.session_state.finished = True
                else:
                    st.info(f"Correct {correct} · Wrong {wrong} → "
                            f"Score {st.session_state.score:.2f}. Try again!")

    # ---------- reveal answers when finished ---------- #
    if st.session_state.finished:
        st.subheader("Correct answers")
        st.table(pd.DataFrame({
            "Letter": letters,
            "Industry": [st.session_state.mapping[L] for L in letters]
        }).set_index("Letter"))
        st.info("Start a new round from the sidebar whenever you're ready!")
else:
    st.info("Set the number of industries and click **Start / Restart round** to play.")
