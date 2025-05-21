import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, random, requests

# ───────────────────────── Data ───────────────────────── #
CSV_URL = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
# snapshot (Jan-2025) – truncated to keep file small; still > 80 industries
FALLBACK_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
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
Building Materials,1.36,9.46%,15.95%
Business & Consumer Services,1.00,8.27%,14.37%
Cable TV,0.96,6.28%,55.82%
Chemical (Basic),1.15,7.63%,36.81%
Computer Services,1.23,8.72%,20.84%
Drugs (Biotechnology),1.25,9.37%,14.60%
Drugs (Pharmaceutical),1.07,8.72%,14.45%
Entertainment,1.04,8.28%,16.90%
Food Processing,0.47,6.02%,26.75%
Green & Renewable Energy,1.13,6.50%,63.79%
Healthcare Products,1.01,8.50%,11.34%
Homebuilding,1.43,9.78%,14.89%
Hospitals/Healthcare Facilities,0.86,6.57%,43.55%
Hotel/Gaming,1.19,8.12%,30.17%
Household Products,0.90,7.91%,13.21%
Information Services,0.98,7.62%,26.13%
Insurance (General),0.76,7.35%,14.79%
Machinery,1.07,8.54%,13.57%
Metals & Mining,1.02,8.40%,14.35%
Oil/Gas (Integrated),0.48,6.33%,12.06%
Oil/Gas Prod/Exploration,0.88,7.52%,21.04%
Packaging & Container,0.98,7.20%,34.60%
Paper/Forest Products,1.07,8.32%,18.41%
Power,0.54,5.54%,44.55%
Precious Metals,1.23,9.09%,15.89%
R.E.I.T.,0.95,6.62%,45.50%
Retail (Automotive),1.35,8.39%,33.51%
Semiconductor,1.49,10.76%,3.75%
Steel,1.06,8.17%,20.57%
Telecom. Services,0.89,6.37%,50.04%
Utility (General),0.39,5.20%,43.84%"""

@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_URL)
    except Exception:
        df = pd.read_csv(io.StringIO(FALLBACK_CSV))
    # clean %
    df["Cost of Capital"] = df["Cost of Capital"].astype(str).str.rstrip("%").astype(float) / 100
    df["D/(D+E)"] = df["D/(D+E)"].astype(str).str.rstrip("%").astype(float) / 100
    df = df[~df["Industry Name"].str.startswith("Total Market")]
    return df

df_full = load_data()

# ───────────────────────── Helpers ───────────────────────── #
def make_fig(df_sub: pd.DataFrame, letters):
    return go.Figure(
        go.Scatter3d(
            x=df_sub["Beta"],
            y=df_sub["D/(D+E)"],
            z=df_sub["Cost of Capital"],
            mode="markers+text",
            text=letters,
            textposition="top center",
            marker=dict(size=6, color="#1f77b4"),
            hovertemplate="Beta %{x:.2f}<br>Debt %{y:.2%}<br>WACC %{z:.2%}"
        )
    ).update_layout(
        height=600,
        margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt ratio",
            zaxis_title="WACC"
        )
    )

def reset_round(n: int):
    sub = df_full.sample(n).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n)]
    st.session_state.round = dict(
        df=sub,
        letters=letters,
        guesses={L: None for L in letters},
        finished=False,
        score=0.0
    )

# ───────────────────────── UI ───────────────────────── #
st.set_page_config(page_title="Industry guess", page_icon="🏭", layout="wide")
st.title("🏭 Industry WACC guessing game")
st.write("Pick the industry that matches each letter-labelled point. "
         "_Duplicates are disabled._  "
         "Scoring: **+1** correct, **−0.5** wrong.")

if "round" not in st.session_state:
    reset_round(5)  # default first round

# sidebar controls
with st.sidebar:
    st.header("New round")
    n_sel = st.slider("Industries this round", 2, 10, len(st.session_state.round["letters"]))
    if st.button("Start / restart"):
        reset_round(n_sel)

round_data = st.session_state.round
df_sub = round_data["df"]
letters = round_data["letters"]

# 3-D plot
st.plotly_chart(make_fig(df_sub, letters), use_container_width=True)

# ------------ guess form ------------
if not round_data["finished"]:
    with st.form("guess_form"):
        placeholder = "— pick —"
        for idx, L in enumerate(letters):
            # current selection (may be None)
            current = round_data["guesses"][L]
            # what others have chosen
            chosen = {v for k, v in round_data["guesses"].items() if k != L and v}
            # option list
            opts = [placeholder] + [ind for ind in df_sub["Industry Name"] if ind not in chosen or ind == current]
            # keep current even if it was filtered out (shouldn’t happen)
            if current and current not in opts:
                opts.append(current)
            idx_default = opts.index(current) if current else 0
            beta = df_sub.at[idx, "Beta"]
            debt = df_sub.at[idx, "D/(D+E)"] * 100
            wacc = df_sub.at[idx, "Cost of Capital"] * 100
            label = f"Point {L}: β {beta:.2f}, Debt {debt:.2f} %, WACC {wacc:.2f} %"
            sel = st.selectbox(label, opts, index=idx_default, key=f"sel_{L}")
            round_data["guesses"][L] = sel if sel != placeholder else None
        submitted = st.form_submit_button("Submit guesses")

    if submitted:
        guesses = round_data["guesses"]
        if None in guesses.values():
            st.warning("Choose an industry for every point.")
        elif len(set(guesses.values())) < len(guesses):
            st.warning("Each industry can be picked only once.")
        else:
            correct = sum(
                guesses[L] == df_sub.at[i, "Industry Name"]
                for i, L in enumerate(letters)
            )
            wrong = len(letters) - correct
            round_data["score"] = correct - 0.5 * wrong
            round_data["finished"] = True
            st.session_state.round = round_data
            st.experimental_rerun()  # one safe rerun to show results

# ------------ results ------------
if round_data["finished"]:
    st.subheader(f"Round score: {round_data['score']:.2f}")
    if round_data["score"] == len(letters):
        st.success("Perfect! 🎉")
    elif round_data["score"] < 0:
        st.error("Score below zero — game over.")
    else:
        st.info("Round complete.")

    st.table(pd.DataFrame({
        "Letter": letters,
        "Industry": df_sub["Industry Name"]
    }).set_index("Letter"))
