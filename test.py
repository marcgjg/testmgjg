import streamlit as st
import numpy as np
import plotly.graph_objects as go
import uuid
import pandas as pd

# =========================
# App Config (visuals only)
# =========================
st.set_page_config(
    page_title="Bond YTM Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------- THEME / CSS (visual only, no logic changes) ---------
PRIMARY = "#2563eb"  # Tailwind blue-600
ACCENT = "#0ea5e9"   # cyan-500
SURFACE = "#f8fafc"  # slate-50
BORDER = "#e2e8f0"   # slate-200
TEXT = "#0f172a"     # slate-900
MUTED = "#475569"     # slate-600

st.markdown(
    f"""
    <style>
      /* Global */
      .main {{
        background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
      }}
      .app-title h1 {{
        text-align:center; margin: 0 0 0.25rem 0; font-weight:800;
        letter-spacing:-0.02em; color:{TEXT};
      }}
      .app-subtitle {{
        text-align:center; color:{MUTED}; margin-bottom: 1.25rem;
      }}

      /* Card-ish containers */
      .card {{
        background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,.05);
      }}

      /* Buttons */
      .stButton>button {{
        border-radius:12px; padding:0.5rem 0.9rem; font-weight:600;
        border:1px solid {PRIMARY}20; box-shadow:0 2px 6px rgba(37,99,235,.08);
      }}
      .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow:0 6px 16px rgba(37,99,235,.15);
      }}

      /* Sliders */
      [data-baseweb="slider"]>div>div {{
        background:{PRIMARY}30 !important;
      }}

      /* Metrics */
      div[data-testid="stMetric"] {{
        background:{SURFACE}; border:1px solid {BORDER}; border-radius:14px; padding:12px;
      }}
      div[data-testid="stMetric"] label {{ color:{MUTED}; font-weight:600; }}
      div[data-testid="stMetricValue"] {{ color:{TEXT}; }}

      /* Dataframe chrome */
      [data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:14px; overflow:hidden; }}

      /* Footer */
      .footer {{
        text-align:center; color:{MUTED}; font-size:0.9rem; padding: 6px 0 20px 0;
        border-top:1px dashed {BORDER}; margin-top: 28px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------- Color palette for added curves (unchanged logic) ---------

def get_colors():
    return ['#2563eb', '#f59e0b', '#16a34a', '#ef4444', '#8b5cf6', '#ec4899', '#64748b', '#22d3ee', '#84cc16', '#06b6d4']

# --------- Header ---------
st.markdown('<div class="app-title"><h1>📈 Bond Price vs Yield to Maturity</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Explore the inverse relation between YTM and price, and compare interest rate risk visually.</div>', unsafe_allow_html=True)

# --------- About (same content) ---------
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This tool can be used in two different ways:
        - It can help you visualize the negative or inverse relationship between the **Yield to Maturity (YTM)** of a bond and its **Price**.
        - You can also use this tool to compare the **Interest Rate Risk** or **Duration** of (i) bonds with the same coupon rate but different maturities or (ii) bonds with the same maturity but different coupon rates.
        """
    )

# --------- Session state (unchanged) ---------
if 'curves' not in st.session_state:
    st.session_state.curves = {}
    st.session_state.curve_colors = {}

# --------- Layout ---------
col1, col2 = st.columns([1, 2], gap="large")

# ===================== Left Column: Controls & Metrics =====================
with col1:
    with st.container():
        st.subheader("Bond Parameters")
        params_card = st.container()
        with params_card:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            face_value = st.slider("Face Value (€):", 100, 10000, 100, 100)
            coupon_rate = st.slider("Coupon Rate (%):", 0.0, 10.0, 2.0, 0.25)
            coupon_frequency = st.selectbox("Coupon Frequency:", ["Annual", "Semi-Annual"]) 
            maturity = st.slider("Maturity (Years):", 0.5, 30.0, 10.0, 0.5)
            min_ytm, max_ytm = st.slider("YTM Range (%):", 0.0, 20.0, (0.0, 15.0), 0.1)
            st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Chart Controls")
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    # --------- Current Bond Analysis (unchanged logic) ---------
    st.subheader("Current Bond Analysis")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    periods_per_year = 1 if coupon_frequency == "Annual" else 2
    n_periods = int(maturity * periods_per_year)
    coupon_payment = face_value * (coupon_rate / 100) / periods_per_year
    current_ytm = 5.0

    def calculate_bond_price(yield_rate):
        return sum([coupon_payment / (1 + yield_rate / periods_per_year) ** t for t in range(1, n_periods + 1)]) + \
               face_value / (1 + yield_rate / periods_per_year) ** n_periods

    def calculate_duration(yield_rate):
        pv_payments = [coupon_payment / (1 + yield_rate / periods_per_year) ** t for t in range(1, n_periods + 1)]
        pv_payments.append(face_value / (1 + yield_rate / periods_per_year) ** n_periods)
        weighted_times = [t * payment / periods_per_year for t, payment in enumerate(pv_payments, 1)]
        return sum(weighted_times) / sum(pv_payments)

    current_price = calculate_bond_price(current_ytm / 100)
    duration = calculate_duration(current_ytm / 100)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Coupon Payment", f"€{coupon_payment:.2f}")
    with m2:
        st.metric("Total Periods", f"{n_periods}")
    with m3:
        st.metric("Duration @ 5% YTM", f"{duration:.2f} years")
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== Right Column: Chart & Table =====================
with col2:
    st.subheader("Bond Price vs Yield Curve")

    # Compute curve (unchanged logic)
    yields = np.linspace(min_ytm / 100, max_ytm / 100, num_points)
    prices = [calculate_bond_price(ytm) for ytm in yields]

    # Plotly figure (visual refresh only)
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=yields * 100,
            y=prices,
            mode='lines',
            name=f"Current ({coupon_rate:.2f}% - {coupon_frequency} - {maturity:.1f}y)",
            line=dict(color=PRIMARY, width=3, dash='solid'),
            hovertemplate="YTM: %{x:.2f}%<br>Price: €%{y:.2f}<extra></extra>",
        )
    )

    # Historical added curves (unchanged logic – styled)
    for curve_key, (x_vals, y_vals, label) in st.session_state.curves.items():
        color = st.session_state.curve_colors.get(curve_key, "#1f77b4")
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=label,
                line=dict(color=color, width=2.5),
                hovertemplate="YTM: %{x:.2f}%<br>Price: €%{y:.2f}<extra></extra>",
            )
        )

    # Face value reference line (visual only)
    fig.add_shape(
        type="line",
        x0=min_ytm,
        y0=face_value,
        x1=max_ytm,
        y1=face_value,
        line=dict(color="rgba(100, 116, 139, 0.5)", width=2, dash="dash"),
    )

    fig.update_layout(
        title=dict(text="Bond Price vs Yield to Maturity", x=0.02, xanchor='left', font=dict(size=22, color=TEXT)),
        xaxis_title="Yield to Maturity (%)",
        yaxis_title="Bond Price (€)",
        height=600,
        margin=dict(l=60, r=40, t=60, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor=BORDER,
            borderwidth=1
        ),
        template="simple_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_size=14)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#eef2ff", zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#eef2ff", zeroline=False)

    st.plotly_chart(fig, use_container_width=True, theme=None)

    # Add curve to session (unchanged logic)
    if add_curve:
        curve_label = f"{coupon_rate:.2f}% - {coupon_frequency} - {maturity:.1f}y"
        curve_key = f"{uuid.uuid4().hex[:5]}"
        x_values = (yields * 100).tolist()
        y_values = prices
        st.session_state.curves[curve_key] = (x_values, y_values, curve_label)
        color_idx = len(st.session_state.curve_colors) % len(get_colors())
        st.session_state.curve_colors[curve_key] = get_colors()[color_idx]
        st.success(f"Added bond: {curve_label}")

    # Data Table (unchanged logic; light formatting only)
    st.subheader("Bond Prices at Selected Yields")
    specific_yields = np.arange(0, 20.5, 0.5) / 100
    specific_prices = [calculate_bond_price(ytm) for ytm in specific_yields]
    price_data = pd.DataFrame({
        "Yield to Maturity (%)": np.round(specific_yields * 100, 2),
        "Bond Price (€)": np.round(specific_prices, 2),
    })
    st.dataframe(price_data, use_container_width=True, height=360)

# --------- Footer (visual only) ---------
st.markdown(
    '<div class="footer">Bond Price vs Yield to Maturity Calculator · Developed by Prof. Marc Goergen with the help of ChatGPT, Perplexity and Claude</div>',
    unsafe_allow_html=True,
)
