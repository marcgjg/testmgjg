import streamlit as st
import plotly.graph_objects as go

# Page configuration with wide layout and title
st.set_page_config(page_title="PV and FV Calculator", layout="wide")

# Theme toggle in sidebar
st.sidebar.title("Settings")
theme = st.sidebar.radio("Select Theme", options=["Light", "Dark"])

# Apply theme colors based on selection
if theme == "Dark":
    bg_color = "#0E1117"
    text_color = "#FAFAFA"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"

# Sidebar inputs with tooltips
st.sidebar.header("Input Parameters")

principal = st.sidebar.number_input(
    "Principal Amount ($)", min_value=0.0, value=1000.0, step=100.0,
    help="Initial amount of money invested or loaned."
)

rate = st.sidebar.slider(
    "Interest Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1,
    help="Annual interest rate applied to the principal."
)

years = st.sidebar.slider(
    "Number of Years", min_value=1, max_value=50, value=10,
    help="Duration for which the money is invested or borrowed."
)

compounding = st.sidebar.selectbox(
    "Compounding Frequency",
    options=["Annually", "Semi-Annually", "Quarterly", "Monthly", "Daily"],
    help="How often the interest is compounded per year."
)

# Map compounding frequency to number of compounding periods per year
compounding_map = {
    "Annually": 1,
    "Semi-Annually": 2,
    "Quarterly": 4,
    "Monthly": 12,
    "Daily": 365
}

n = compounding_map[compounding]

payment = st.sidebar.number_input(
    "Additional Payment per Period ($)", min_value=0.0, value=0.0, step=10.0,
    help="Additional payment made at each compounding period."
)

# Calculation function for PV and FV including payments and compounding
def calculate_values(principal, rate, years, n, payment):
    r = rate / 100 / n
    t = years * n
    if r == 0:
        fv = principal + payment * t
        pv = principal + payment * t
    else:
        fv = principal * (1 + r) ** t + payment * (((1 + r) ** t - 1) / r)
        pv = principal / (1 + r) ** t + payment * (1 - (1 + r) ** -t) / r
    return pv, fv

pv, fv = calculate_values(principal, rate, years, n, payment)

# Layout output in two columns
col1, col2 = st.columns(2)

with col1:
    st.header("Present Value (PV) 💰")
    st.markdown(f"<div style='color:{text_color}; font-size:24px;'>${pv:,.2f}</div>", unsafe_allow_html=True)
    st.caption("Current worth of a future sum or stream of cash flows given the rate of return.")

with col2:
    st.header("Future Value (FV) 🚀")
    st.markdown(f"<div style='color:{text_color}; font-size:24px;'>${fv:,.2f}</div>", unsafe_allow_html=True)
    st.caption("Value of the current asset at a future date based on growth assumptions.")

# Plot future value growth over time
years_range = list(range(1, years + 1))
fv_values = [calculate_values(principal, rate, y, n, payment)[1] for y in years_range]

fig = go.Figure()
fig.add_trace(go.Scatter(x=years_range, y=fv_values, mode='lines+markers', name='Future Value'))
fig.update_layout(
    title="Future Value Growth Over Time",
    xaxis_title="Years",
    yaxis_title="Value ($)",
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=text_color)
)

st.plotly_chart(fig, use_container_width=True)

# Success message
st.success("Calculation complete! Adjust inputs in the sidebar to update values.")

# Footer with external links
st.markdown(
    """
    ---
    Developed by Your Name | [GitHub](https://github.com/yourrepo) | [Documentation](https://yourdocslink)
    """,
    unsafe_allow_html=True
)
