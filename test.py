import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from io import BytesIO
from urllib.request import urlopen

# ─────────────────────  CONSTANTS  ───────────────────── #
HTML_URL  = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html"
XLSX_URL  = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.xls"
AXES_RANGES = dict(
    debt_pct=(0, 100),
    beta=(0, 3),
    wacc=(0, 20),
)

# ─────────────────────  PAGE CONFIG  ─────────────────── #
st.set_page_config(page_title="Industry WACC Guessing Game",
                   page_icon="🎯", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">🎯 Guess the Industry’s Capital-Market Coordinates</h1>',
    unsafe_allow_html=True,
)

# ─────────────────────  LOAD DATA  ───────────────────── #
@st.cache_data(show_spinner="Fetching Damodaran table …")
def load_industry_data() -> pd.DataFrame:
    """Return a clean DF with columns: Industry, DebtPct, Beta, WACC."""
    try:
        # try the small XLS first – quicker & cleaner
        df_raw = pd.read_excel(XLSX_URL, sheet_name=0, header=0)
    except Exception:
        # fall back to the HTML if the XLS fetch fails
        df_raw = pd.read_html(HTML_URL, header=0)[0]

    # keep only rows with needed columns present
    req_cols = ["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]
    df = df_raw.loc[:, req_cols].copy()

    # numeric cleaning – strip %, convert to float
    df["DebtPct"] = pd.to_numeric(
        df["D/(D+E)"].str.replace("%", "", regex=False), errors="coerce"
    )
    df["Beta"] = pd.to_numeric(df["Beta"], errors="coerce")
    df["WACC"] = pd.to_numeric(
        df["Cost of Capital"].str.replace("%", "", regex=False), errors="coerce"
    )

    df = df.dropna(subset=["DebtPct", "Beta", "WACC"])
    df.rename(columns={"Industry Name": "Industry"}, inplace=True)
    return df

data = load_industry_data()   # ~100 ms after first cache

# ─────────────────────  SIDEBAR  ─────────────────────── #
sb = st.sidebar
sb.header("Pick an industry")
all_industries = data["Industry"].tolist()

if "current_ind" not in st.session_state:
    st.session_state.current_ind = random.choice(all_industries)
if "revealed" not in st.session_state:
    st.session_state.revealed = False

def new_industry():
    st.session_state.current_ind = random.choice(all_industries)
    st.session_state.revealed = False

sb.button("🎲 New random industry", on_click=new_industry)
chosen_industry = sb.selectbox("…or choose one yourself",
                               all_industries,
                               index=all_industries.index(st.session_state.current_ind),
                               key="ind_select")
st.session_state.current_ind = chosen_industry

sb.markdown("---")
sb.markdown("### Your guess")

guess_debt = sb.slider("Debt / (Debt + Equity) %", *AXES_RANGES["debt_pct"], 50)
guess_beta = sb.slider("Beta", *AXES_RANGES["beta"], 1.0, 0.01)
guess_wacc = sb.slider("Cost of Capital %", *AXES_RANGES["wacc"], 8.0, 0.05)

if sb.button("Check guess"):
    st.session_state.revealed = True

# ─────────────────────  MAIN PANEL  ─────────────────── #
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("3-D Industry Map")
    fig = go.Figure()

    # grey markers for all industries
    fig.add_trace(
        go.Scatter3d(
            x=data["DebtPct"],
            y=data["Beta"],
            z=data["WACC"],
            mode="markers",
            marker=dict(size=4, color="#d1d5db"),   # Tailwind slate-300
            name="All industries",
            hovertemplate=(
                "<b>%{text}</b><br>Debt %%: %{x:.1f}<br>"
                "Beta: %{y:.2f}<br>WACC %%: %{z:.2f}"
            ),
            text=data["Industry"],
        )
    )

    # student guess (always plotted)
    fig.add_trace(
        go.Scatter3d(
            x=[guess_debt], y=[guess_beta], z=[guess_wacc],
            mode="markers+text",
            marker=dict(size=6, symbol="diamond", color="#3b82f6"),  # Tailwind blue-500
            text=["Your guess"],
            textposition="top center",
            name="Your guess",
        )
    )

    # actual point (only if revealed)
    if st.session_state.revealed:
        actual = data.set_index("Industry").loc[st.session_state.current_ind]
        fig.add_trace(
            go.Scatter3d(
                x=[actual["DebtPct"]], y=[actual["Beta"]], z=[actual["WACC"]],
                mode="markers+text",
                marker=dict(size=6, symbol="circle", color="#ef4444"),  # red-500
                text=["Actual"],
                textposition="bottom center",
                name="Actual",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis_title="Debt / (Debt + Equity) %",
            yaxis_title="Beta",
            zaxis_title="Cost of Capital %",
            xaxis=dict(range=list(AXES_RANGES["debt_pct"])),
            yaxis=dict(range=list(AXES_RANGES["beta"])),
            zaxis=dict(range=list(AXES_RANGES["wacc"])),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        legend=dict(orientation="h", y=-0.1),
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Your task")
    st.write(f"**Target industry:** **{st.session_state.current_ind}**")

    if not st.session_state.revealed:
        st.info(
            "Pick the three slider values you believe best describe this industry "
            "and click **Check guess** when ready."
        )
    else:
        actual = data.set_index("Industry").loc[st.session_state.current_ind]
        # Euclidean distance in normalised space
        dx = guess_debt - actual["DebtPct"]
        dy = guess_beta - actual["Beta"]
        dz = guess_wacc - actual["WACC"]
        dist = np.sqrt(
            (dx / (AXES_RANGES["debt_pct"][1]))**2 +
            (dy / (AXES_RANGES["beta"][1]))**2 +
            (dz / (AXES_RANGES["wacc"][1]))**2
        )
        st.success(
            f"**Actual values**\n\n"
            f"* Debt ratio: **{actual['DebtPct']:.1f}%**\n"
            f"* Beta: **{actual['Beta']:.2f}**\n"
            f"* WACC: **{actual['WACC']:.2f}%**"
        )
        st.write(f"Your absolute errors: ")
        st.write(f"* Debt ratio error = {abs(dx):.1f} pp")
        st.write(f"* Beta error = {abs(dy):.2f}")
        st.write(f"* WACC error = {abs(dz):.2f} pp")
        st.write(f"Overall normalised distance ≈ **{dist:.3f}**")

        st.button("Try another industry →", on_click=new_industry)

# ─────────────────────  FOOTER  ─────────────────────── #
st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Dataset: Prof. Aswath Damodaran, NYU Stern (Jan 2025) '
    '| App by ChatGPT</div>',
    unsafe_allow_html=True,
)
