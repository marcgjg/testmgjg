import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

st.set_page_config(page_title="Industry Matching Game", layout="wide")

# ---------- data load ----------
CSV = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.csv"
FALLBACK = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.34,9.22,20.76
Aerospace/Defense,0.90,7.68,18.56
Air Transport,1.24,7.29,51.65
Apparel,0.99,7.44,31.45
Auto & Truck,1.62,10.34,18.3
Auto Parts,1.23,8.09,32.36
Bank (Money Center),0.88,5.64,64.69
Banks (Regional),0.52,5.69,37.62
Beverage (Alcoholic),0.61,6.55,23.35
Beverage (Soft),0.57,6.59,16.48
Broadcasting,0.92,6.03,59.93
Brokerage & Investment Banking,0.95,5.74,65.11
Building Materials,1.36,9.46,15.95
Business & Consumer Services,1.00,8.27,14.37
Cable TV,0.96,6.28,55.82
Chemical (Basic),1.15,7.63,36.81
Chemical (Diversified),0.99,6.47,53.08
Chemical (Specialty),0.92,7.67,21.34
Coal & Related Energy,1.18,9.23,8.65
Computer Services,1.23,8.72,20.84
Computers/Peripherals,1.14,9.29,4.6
Construction Supplies,1.29,9.14,17.74
Diversified,1.09,8.61,13.86
Drugs (Biotechnology),1.25,9.37,14.6
Drugs (Pharmaceutical),1.07,8.72,14.45
Education,0.98,8.1,16.28
Electrical Equipment,1.27,9.4,12.93
Electronics (Consumer & Office),0.92,8.12,11.75
Electronics (General),1.06,8.55,12.6
Engineering/Construction,0.99,8.17,15.2
Entertainment,1.04,8.28,16.9
Environmental & Waste Services,0.92,7.88,16.19
Farming/Agriculture,0.98,7.43,34.78
Financial Svcs. (Non-bank & Insurance),1.07,5.46,74.14
Food Processing,0.47,6.02,26.75
Food Wholesalers,0.72,6.64,30.21
Furn/Home Furnishings,0.87,7.15,29.54
Green & Renewable Energy,1.13,6.5,63.79
Healthcare Products,1.01,8.5,11.34
Healthcare Support Services,0.94,7.6,24.36
Heathcare Information and Technology,1.22,9.1,13.94
Homebuilding,1.43,9.78,14.89
Hospitals/Healthcare Facilities,0.86,6.57,43.55
Hotel/Gaming,1.19,8.12,30.17
Household Products,0.90,7.91,13.21
Information Services,0.98,7.62,26.13
Insurance (General),0.76,7.35,14.79
Insurance (Life),0.73,6.36,38.55
Insurance (Prop/Cas.),0.61,6.79,13.39
Investments & Asset Management,0.57,6.2,25.95
Machinery,1.07,8.54,13.57
Metals & Mining,1.02,8.4,14.35
Office Equipment & Services,1.20,8.05,31.74
Oil/Gas (Integrated),0.48,6.33,12.06
Oil/Gas (Production and Exploration),0.88,7.52,21.04
Oil/Gas Distribution,0.75,6.59,34.01
Oilfield Svcs/Equip.,0.94,7.44,27.81
Packaging & Container,0.98,7.2,34.6
Paper/Forest Products,1.07,8.32,18.41
Power,0.54,5.54,44.55
Precious Metals,1.23,9.09,15.89
Publishing & Newspapers,0.64,6.63,22.3
R.E.I.T.,0.95,6.62,45.5
Real Estate (Development),1.03,6.58,52.09
Real Estate (General/Diversified),0.86,6.99,29.55
Real Estate (Operations & Services),1.08,8.14,22.35
Recreation,1.33,7.97,39.43
Reinsurance,0.54,6.08,26.78
Restaurant/Dining,1.01,8.05,18.79
Retail (Automotive),1.35,8.39,33.51
Retail (Building Supply),1.79,11,16.8
Retail (Distributors),1.12,8.16,23.82
Retail (General),1.06,8.79,8.03
Retail (Grocery and Food),0.58,5.96,34.32
Retail (REITs),0.95,6.96,35.39
Retail (Special Lines),1.22,8.64,22.44
Rubber& Tires,0.65,5.33,79.47
Semiconductor,1.49,10.76,3.75
Semiconductor Equip,1.48,10.51,7.56
Shipbuilding & Marine,0.58,6.64,16.05
Shoe,1.42,10.15,9.29
Software (Entertainment),1.18,9.58,2.43
Software (Internet),1.69,11.1,10.35
Software (System & Application),1.24,9.69,4.67
Steel,1.06,8.17,20.57
Telecom (Wireless),0.77,6.92,32.25
Telecom. Equipment,1.00,8.39,11.35
Telecom. Services,0.89,6.37,50.04
Tobacco,0.98,7.95,21.85
Transportation,1.03,7.72,27.91
Transportation (Railroads),0.99,7.75,22.11
Trucking,1.10,8.39,18.64
Utility (General),0.39,5.2,43.84
Utility (Water),0.68,6.15,36.96%"""

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV)
        df = df[["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]]
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
        df["WACC"] = df["WACC"].str.rstrip("%").astype(float)
        df["Debt"] = df["Debt"].str.rstrip("%").astype(float)
    except Exception:
        df = pd.read_csv(StringIO(FALLBACK))
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
        df["WACC"] = df["WACC"].astype(str).str.rstrip("%").astype(float)
        df["Debt"] = df["Debt"].astype(str).str.rstrip("%").astype(float)
    return df

df_all = load_data()

# Add a description
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown("""
    This tool helps you visualize the **Net Present Value (NPV)** and **Internal Rate of Return (IRR)** for a series of cash flows.
    
    - **NPV (Net Present Value)**: Calculates the present value of future cash flows minus the initial investment
    - **IRR (Internal Rate of Return)**: The discount rate at which the NPV equals zero
    
    Enter your cash flows as comma-separated values, with the initial investment as a negative number.
    """)


# ---------- session init ----------
ss = st.session_state
for k, v in [
    ("game_active", False),
    ("game_submitted", False),
    ("df", None),
    ("letters", []),
    ("metrics_opts", []),
    ("true_map", {}),
    ("answers", {}),
    ("results", []),
    ("score", 0.0),
]:
    if k not in ss:
        ss[k] = v

# ---------- sidebar ----------
with st.sidebar:
    if not ss.game_active:
        st.markdown("### 🎮 Game Setup")
        n = st.slider("Number of industries", 2, 10, 5)
        st.markdown(f"*Selected: {n} industries*")
        
        if st.button("🚀 Start Game", type="primary", use_container_width=True):
            sample   = df_all.sample(n).reset_index(drop=True)
            letters  = list(string.ascii_uppercase[:n])

            # metric strings in TRUE order
            metrics = []
            for _, r in sample.iterrows():
                beta  = float(r["Beta"])
                wacc  = float(r["WACC"])
                debt  = float(r["Debt"])
                if debt <= 1:          # convert 0–1 ratio to 0–100 %
                    debt *= 100
                metrics.append(
                    f"Beta: {beta:.2f}, Debt%: {debt:.2f}%, WACC: {wacc:.2f}%"
                )

            metrics_opts = metrics.copy()
            random.shuffle(metrics_opts)

            ss.df          = sample
            ss.letters     = letters
            ss.metrics_opts = metrics_opts
            ss.true_map    = {L: metrics[i] for i, L in enumerate(letters)}
            ss.answers     = {L: "Select..." for L in letters}

            ss.game_active    = True
            ss.game_submitted = False
            ss.balloons_shown = False  # Reset balloons flag for new game
            
        st.markdown("---")
        st.markdown("### 📖 How to Play")
        st.markdown("""
        1. **Observe** the 3D scatter plot
        2. **Match** each lettered point to its correct financial metrics
        3. **Submit** your answers to see results
        
        **Scoring**: +1 for correct, -0.5 for incorrect
        """)
        
        if ss.game_submitted:
            st.markdown("### 🎯 Latest Score")
            st.metric("Score", f"{ss.score:.1f}/{len(ss.letters)}")
    else:
        st.markdown("### 🎮 Game in Progress")
        completed = sum(1 for v in ss.answers.values() if v != "Select...")
        st.progress(completed / len(ss.letters))
        st.markdown(f"**Progress**: {completed}/{len(ss.letters)} completed")

# ---------- main ----------
st.title("🎯 Industry Matching Game")
st.markdown("---")

if ss.game_active:
    df      = ss.df
    letters = ss.letters

    # Add a progress indicator
    progress_text = f"📊 **Round in Progress** | Industries: {len(letters)} | Click points in the 3D chart and match them to metrics!"
    st.markdown(f"<div style='text-align: center; padding: 10px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;'>{progress_text}</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="medium")

    # graph (left)
    with col_left:
        # Create color scheme based on WACC values
        colors = ['#FF6B6B' if wacc > 9 else '#4ECDC4' if wacc < 7 else '#45B7D1' 
                  for wacc in df["WACC"]]
        
        fig = go.Figure(go.Scatter3d(
            x=df["Beta"], y=df["Debt"], z=df["WACC"],
            text=letters, mode="markers+text", textposition="top center",
            marker=dict(
                size=12,
                color=colors,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            textfont=dict(size=14, color='white', family="Arial Black")
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title="Beta", 
                yaxis_title="Debt %", 
                zaxis_title="WACC %",
                xaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                ),
                yaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                ),
                zaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                )
            ),
            height=600, 
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # dropdowns (right)
    with col_right:
        if not ss.game_submitted:
            st.markdown("### 🎲 Match each industry to its metrics")
            st.markdown("*Select the correct Beta, Debt%, and WACC combination for each lettered point.*")
            
            for i, L in enumerate(letters):
                industry = df.at[i, "Industry"]
                current  = ss.answers[L]
                used     = {v for k, v in ss.answers.items() if k != L}
                opts     = ["Select..."] + [
                    m for m in ss.metrics_opts if m not in used or m == current
                ]
                
                # Add emoji indicators based on selection status only
                status_emoji = "🔵" if current != "Select..." else "⚪"
                
                sel = st.selectbox(
                    f"{status_emoji} **Point {L}**: {industry}",
                    opts,
                    index=opts.index(current) if current in opts else 0,
                    key=f"sel_{L}"
                )
                ss.answers[L] = sel

            # submit with improved styling
            st.markdown("---")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 Submit Answers", type="primary", use_container_width=True):
                    if "Select..." in ss.answers.values():
                        st.error("⚠️ Complete all selections first.")
                    elif len(set(ss.answers.values())) < len(letters):
                        st.error("⚠️ Each metric combo can be chosen only once.")
                    else:
                        correct = 0
                        results = []
                        for i, L in enumerate(letters):
                            g = ss.answers[L]
                            a = ss.true_map[L]
                            mark = "✅" if g == a else "❌"
                            if mark == "✅":
                                correct += 1
                            results.append((L, df.at[i, "Industry"], a, mark))
                        ss.score   = correct - 0.5 * (len(letters) - correct)
                        ss.results = results
                        ss.game_submitted = True
                        ss.game_active = False  # unlock sidebar immediately
                        st.rerun()

# ---------- results (centered) ----------
if ss.game_submitted:
    st.markdown("---")
    lft, ctr, rgt = st.columns([1, 2, 1])
    with ctr:
        # Score display with visual styling
        score_color = "#28a745" if ss.score >= len(ss.letters) * 0.8 else "#ffc107" if ss.score >= 0 else "#dc3545"
        st.markdown(f"<div style='text-align: center; padding: 20px; background-color: {score_color}; color: white; border-radius: 15px; margin-bottom: 20px;'><h2>🎯 Final Score: {ss.score:.1f}/{len(ss.letters)}</h2></div>", unsafe_allow_html=True)
        
        if ss.results and len(ss.results) == len(ss.letters) \
           and all(r[3] == "✅" for r in ss.results):
            if not hasattr(ss, 'balloons_shown') or not ss.balloons_shown:
                st.balloons()
                ss.balloons_shown = True
            st.markdown("### 🎉 Perfect Round! Outstanding!")

        st.markdown("### 📋 Detailed Results")
        for L, industry, metrics, mark in ss.results:
            color = "#d4edda" if mark == "✅" else "#f8d7da"
            border_color = "#28a745" if mark == "✅" else "#dc3545"
            st.markdown(f"""
            <div style='padding: 10px; margin: 5px 0; background-color: {color}; 
                        border-left: 4px solid {border_color}; border-radius: 5px;'>
                <strong>{mark} Point {L}</strong> ({industry})<br>
                <small>{metrics}</small>
            </div>
            """, unsafe_allow_html=True)

# ---------- footer ----------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px; padding: 20px;'>"
    "Industry Matching Game | Developed by Prof. Marc Goergen with the help of ChatGPT and Claude"
    "</div>", 
    unsafe_allow_html=True
)
