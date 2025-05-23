import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, requests

# ───────────────────────── PAGE CONFIG (must be first) ─────────────────────────
st.set_page_config(page_title="Industry WACC Guess", page_icon="🏭", layout="wide")

# ───────────────────────── DATA (live + snapshot fallback) ────────────────────
LIVE_CSV = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"

SNAPSHOT_CSV = """Industry Name,Beta,Cost of Capital,D/(D+E)
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
Broadcasting,0.92,6.03%,59.93%
Brokerage & Investment Banking,0.95,5.74%,65.11%
Building Materials,1.36,9.46%,15.95%
Business & Consumer Services,1.00,8.27%,14.37%
Cable TV,0.96,6.28%,55.82%
Chemical (Basic),1.15,7.63%,36.81%
Chemical (Diversified),0.99,6.47%,53.08%
Chemical (Specialty),0.92,7.67%,21.34%
Coal & Related Energy,1.18,9.23%,8.65%
Computer Services,1.23,8.72%,20.84%
Computers/Peripherals,1.14,9.29%,4.60%
Construction Supplies,1.29,9.14%,17.74%
Diversified,1.09,8.61%,13.86%
Drugs (Biotechnology),1.25,9.37%,14.60%
Drugs (Pharmaceutical),1.07,8.72%,14.45%
Education,0.98,8.10%,16.28%
Electrical Equipment,1.27,9.40%,12.93%
Electronics (Consumer & Office),0.92,8.12%,11.75%
Electronics (General),1.06,8.55%,12.60%
Engineering/Construction,0.99,8.17%,15.20%
Entertainment,1.04,8.28%,16.90%
Environmental & Waste Services,0.92,7.88%,16.19%
Farming/Agriculture,0.98,7.43%,34.78%
Financial Svcs. (Non-bank & Insurance),1.07,5.46%,74.14%
Food Processing,0.47,6.02%,26.75%
Food Wholesalers,0.72,6.64%,30.21%
Furn/Home Furnishings,0.87,7.15%,29.54%
Green & Renewable Energy,1.13,6.50%,63.79%
Healthcare Products,1.01,8.50%,11.34%
Healthcare Support Services,0.94,7.60%,24.36%
Heathcare Information and Technology,1.22,9.10%,13.94%
Homebuilding,1.43,9.78%,14.89%
Hospitals/Healthcare Facilities,0.86,6.57%,43.55%
Hotel/Gaming,1.19,8.12%,30.17%
Household Products,0.90,7.91%,13.21%
Information Services,0.98,7.62%,26.13%
Insurance (General),0.76,7.35%,14.79%
Insurance (Life),0.73,6.36%,38.55%
Insurance (Prop/Cas.),0.61,6.79%,13.39%
Investments & Asset Management,0.57,6.20%,25.95%
Machinery,1.07,8.54%,13.57%
Metals & Mining,1.02,8.40%,14.35%
Office Equipment & Services,1.20,8.05%,31.74%
Oil/Gas (Integrated),0.48,6.33%,12.06%
Oil/Gas (Production and Exploration),0.88,7.52%,21.04%
Oil/Gas Distribution,0.75,6.59%,34.01%
Oilfield Svcs/Equip.,0.94,7.44%,27.81%
Packaging & Container,0.98,7.20%,34.60%
Paper/Forest Products,1.07,8.32%,18.41%
Power,0.54,5.54%,44.55%
Precious Metals,1.23,9.09%,15.89%
Publishing & Newspapers,0.64,6.63%,22.30%
R.E.I.T.,0.95,6.62%,45.50%
Real Estate (Development),1.03,6.58%,52.09%
Real Estate (General/Diversified),0.86,6.99%,29.55%
Real Estate (Operations & Services),1.08,8.14%,22.35%
Recreation,1.33,7.97%,39.43%
Reinsurance,0.54,6.08%,26.78%
Restaurant/Dining,1.01,8.05%,18.79%
Retail (Automotive),1.35,8.39%,33.51%
Retail (Building Supply),1.79,11.00%,16.80%
Retail (Distributors),1.12,8.16%,23.82%
Retail (General),1.06,8.79%,8.03%
Retail (Grocery and Food),0.58,5.96%,34.32%
Retail (REITs),0.95,6.96%,35.39%
Retail (Special Lines),1.22,8.64%,22.44%
Rubber& Tires,0.65,5.33%,79.47%
Semiconductor,1.49,10.76%,3.75%
Semiconductor Equip,1.48,10.51%,7.56%
Shipbuilding & Marine,0.58,6.64%,16.05%
Shoe,1.42,10.15%,9.29%
Software (Entertainment),1.18,9.58%,2.43%
Software (Internet),1.69,11.10%,10.35%
Software (System & Application),1.24,9.69%,4.67%
Steel,1.06,8.17%,20.57%
Telecom (Wireless),0.77,6.92%,32.25%
Telecom. Equipment,1.00,8.39%,11.35%
Telecom. Services,0.89,6.37%,50.04%
Tobacco,0.98,7.95%,21.85%
Transportation,1.03,7.72%,27.91%
Transportation (Railroads),0.99,7.75%,22.11%
Trucking,1.10,8.39%,18.64%
Utility (General),0.39,5.20%,43.84%
Utility (Water),0.68,6.15%,36.96%
"""

@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(LIVE_CSV)
    except Exception:
        df = pd.read_csv(io.StringIO(SNAPSHOT_CSV))
    df = df[~df["Industry Name"].str.startswith("Total Market")]
    df["Cost of Capital"] = df["Cost of Capital"].str.rstrip("%").astype(float) / 100
    df["D/(D+E)"] = df["D/(D+E)"].str.rstrip("%").astype(float) / 100
    return df

df_all = load_data()

# ───────────────────────── ROUND helpers ───────────────────────────────
def new_round(n: int):
    sample = df_all.sample(n).reset_index(drop=True)
    letters = [chr(65+i) for i in range(n)]
    st.session_state.round = {
        "df": sample,
        "letters": letters,
        "guesses": {},
        "finished": False,
        "score": 0.0,
    }

def plot_3d(df, letters):
    fig = go.Figure(go.Scatter3d(
        x=df["Beta"],
        y=df["D/(D+E)"],
        z=df["Cost of Capital"],
        mode="markers+text",
        text=letters,
        textposition="top center",
        marker=dict(size=6, color="#1f77b4"),
        hovertemplate="β %{x:.2f}<br>Debt %{y:.2%}<br>WACC %{z:.2%}<extra></extra>"
    ))
    fig.update_layout(
        height=600, margin=dict(l=0, r=0, t=20, b=0),
        scene=dict(
            xaxis_title="Beta",
            yaxis_title="Debt ratio",
            zaxis_title="WACC"
        )
    )
    return fig

# ───────────────────────── INIT session ────────────────────────────────
if "round" not in st.session_state:
    new_round(5)

R = st.session_state.round
df = R["df"]
letters = R["letters"]

# ───────────────────────── SIDEBAR (locked during play) ────────────────
with st.sidebar:
    st.header("New round")
    if R["finished"]:
        n_slider = st.slider("Industries", 2, 10, len(letters))
        if st.button("Restart"):
            new_round(n_slider)
    else:
        st.write("🔒 *Round in progress…*")

# ───────────────────────── MAIN UI ─────────────────────────────────────
st.title("🏭 Industry WACC guessing game")
st.write("Match each point to the correct industry. Each industry can be chosen only once.  "
         "Scoring: **+1** correct, **−0.5** wrong.")

st.plotly_chart(plot_3d(df, letters), use_container_width=True)

placeholder = "— pick —"

if not R["finished"]:
    with st.form("guess_form"):
        taken = set()
        for idx, L in enumerate(letters):
            current = R["guesses"].get(L)
            # build options excluding already-taken industries
            opts = [ind for ind in df["Industry Name"] if ind not in taken or ind == current]
            opts = [placeholder] + sorted(opts)
            beta = df.at[idx, "Beta"]
            debt = df.at[idx, "D/(D+E)"] * 100
            wacc = df.at[idx, "Cost of Capital"] * 100
            prompt = f"Point {L}: β {beta:.2f}, Debt {debt:.2f} %, WACC {wacc:.2f} %"
            sel = st.selectbox(prompt, opts, index=opts.index(current) if current else 0)
            R["guesses"][L] = None if sel == placeholder else sel
            if sel != placeholder:
                taken.add(sel)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if None in R["guesses"].values():
            st.warning("Choose an industry for every point.")
        elif len(set(R["guesses"].values())) < len(R["guesses"]):
            st.warning("Duplicate industries selected.")
        else:
            correct = sum(
                R["guesses"][L] == df.at[i, "Industry Name"]
                for i, L in enumerate(letters)
            )
            wrong = len(letters) - correct
            R["score"] = correct - 0.5 * wrong
            R["finished"] = True
            st.experimental_rerun()  # refresh to show results

# ───────────────────────── RESULTS ─────────────────────────────────────
if R["finished"]:
    st.subheader(f"Round score: {R['score']:.2f}")
    if R["score"] == len(letters):
        st.success("Perfect round! 🎉")
    elif R["score"] < 0:
        st.error("Score below zero — game over.")
    else:
        st.info("Round complete.")

    st.table(pd.DataFrame({
        "Letter": letters,
        "Industry": df["Industry Name"]
    }).set_index("Letter"))
