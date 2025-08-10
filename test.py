import streamlit as st
import numpy as np
import plotly.graph_objects as go
import uuid
import pandas as pd

# Set a custom theme and page configuration
st.set_page_config(
    page_title="Bond Price vs YTM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #1E3A8A;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
    }
    h2 {
        color: #1E3A8A;
        font-family: 'Segoe UI', sans-serif;
    }
    h3 {
        color: #1E3A8A;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #888;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Define a custom color palette
def get_colors():
    return ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#6366F1', '#EC4899', '#6B7280', '#D946EF', '#14B8A6', '#C084FC']

# Custom header with logo/title
st.markdown('<h1>📈 Bond Price vs Yield to Maturity</h1>', unsafe_allow_html=True)

# Add a description
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown("""
    This tool can be used in two different ways:
    - It can help you visualize the negative or inverse relationship between the **Yield to Maturity (YTM)** of a bond and its **Price**.
    - You can also use this tool to compare the **Interest Rate Risk** or **Duration** of i) bonds with the same coupon rate but different maturities or ii) bonds with the same maturity but different coupon rates.
    """)

if 'curves' not in st.session_state:
    st.session_state.curves = {}
    st.session_state.curve_colors = {}

# All inputs moved to the sidebar
with st.sidebar:
    st.header("Bond Parameters")
    face_value = st.slider("Face Value (€):", 100, 10000, 100, 100)
    coupon_rate = st.slider("Coupon Rate (%):", 0.0, 10.0, 2.0, 0.25)
    coupon_frequency = st.selectbox("Coupon Frequency:", ["Annual", "Semi-Annual"])
    maturity = st.slider("Maturity (Years):", 0.5, 30.0, 10.0, 0.5)
    min_ytm, max_ytm = st.slider("YTM Range (%):", 0.0, 20.0, (0.0, 15.0), 0.1)

    st.header("Chart Controls")
    col_add, col_reset = st.columns(2)
    with col_add:
        add_curve = st.button("➕ Add to Chart", use_container_width=True)
    with col_reset:
        reset_button = st.button("🔄 Reset Chart", use_container_width=True)

    resolution = st.select_slider("Chart Resolution:", ["Low", "Medium", "High", "Very High"], value="Medium")
    resolution_points = {"Low": 100, "Medium": 250, "High": 500, "Very High": 1000}
    num_points = resolution_points[resolution]

    if reset_button:
        st.session_state.curves = {}
        st.session_state.curve_colors = {}
        st.experimental_rerun()

    st.header("Current Bond Analysis")
    periods_per_year = 1 if coupon_frequency == "Annual" else 2
    n_periods = int(maturity * periods_per_year)
    coupon_payment = face_value * (coupon_rate / 100) / periods_per_year
    current_ytm = 5.0

# Define functions for calculations
def calculate_bond_price(yield_rate):
    return sum([coupon_payment / (1 + yield_rate / periods_per_year) ** t for t in range(1, n_periods + 1)]) + \
           face_value / (1 + yield_rate / periods_per_year) ** n_periods

def calculate_duration(yield_rate):
    pv_payments = [coupon_payment / (1 + yield_rate / periods_per_year) ** t for t in range(1, n_periods + 1)]
    pv_payments.append(face_value / (1 + yield_rate / periods_per_year) ** n_periods)
    weighted_times = [t * payment / periods_per_year for t, payment in enumerate(pv_payments, 1)]
    return sum(weighted_times) / sum(pv_payments)

# Main content area
st.subheader("Current Bond Metrics")
current_price = calculate_bond_price(current_ytm / 100)
duration = calculate_duration(current_ytm / 100)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Coupon Payment", f"€{coupon_payment:.2f}")
with col2:
    st.metric("Total Periods", f"{n_periods}")
with col3:
    st.metric(f"Duration @ {current_ytm}% YTM", f"{duration:.2f} years")

st.subheader("Bond Price vs Yield Curve")
yields = np.linspace(min_ytm / 100, max_ytm / 100, num_points)
prices = [calculate_bond_price(ytm) for ytm in yields]

fig = go.Figure()

# Add the current bond curve with a distinct style
fig.add_trace(go.Scatter(
    x=yields * 100,
    y=prices,
    mode='lines',
    name=f"Current ({coupon_rate:.2f}% - {coupon_frequency} - {maturity:.1f}y)",
    line=dict(color='#3B82F6', width=3, dash='dash')
))

# Add all saved curves
for curve_key, (x_vals, y_vals, label) in st.session_state.curves.items():
    color = st.session_state.curve_colors.get(curve_key, "#1f77b4")
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name=label,
        line=dict(color=color, width=3)
    ))

# Add the face value line
fig.add_shape(type="line", x0=min_ytm, y0=face_value, x1=max_ytm, y1=face_value,
    line=dict(color="rgba(128, 128, 128, 0.5)", width=2, dash="dot"))

# Update chart layout for a cleaner look
fig.update_layout(
    title="Bond Price vs Yield to Maturity",
    xaxis_title="Yield to Maturity (%)",
    yaxis_title="Bond Price (€)",
    height=600,
    font=dict(size=14, color="#374151"),
    paper_bgcolor='white',
    plot_bgcolor='white',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    xaxis=dict(showgrid=True, gridcolor='rgba(200, 200, 200, 0.5)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(200, 200, 200, 0.5)')
)

st.plotly_chart(fig, use_container_width=True)

if add_curve:
    curve_label = f"{coupon_rate:.2f}% - {coupon_frequency} - {maturity:.1f}y"
    curve_key = f"{uuid.uuid4().hex[:5]}"
    x_values = (yields * 100).tolist()
    y_values = prices
    st.session_state.curves[curve_key] = (x_values, y_values, curve_label)
    
    # Get a color from the custom palette
    color_idx = len(st.session_state.curve_colors) % len(get_colors())
    st.session_state.curve_colors[curve_key] = get_colors()[color_idx]
    st.success(f"Added bond: {curve_label}")

st.subheader("Bond Prices at Selected Yields")
specific_yields = np.arange(0, 20.5, 0.5) / 100
specific_prices = [calculate_bond_price(ytm) for ytm in specific_yields]
price_data = pd.DataFrame({"Yield to Maturity (%)": specific_yields * 100, "Bond Price (€)": np.round(specific_prices, 2)})
st.dataframe(price_data, use_container_width=True)

st.markdown('<div class="footer">Bond Price vs Yield to Maturity Calculator | Developed by Prof. Marc Goergen with the help of ChatGPT, Perplexity and Claude</div>', unsafe_allow_html=True)
