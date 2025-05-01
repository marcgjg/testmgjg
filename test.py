import streamlit as st
import plotly.graph_objects as go

# Page configuration with wide layout and title
st.set_page_config(page_title="PV and FV Calculator", layout="wide")

# Theme toggle in sidebar
st.sidebar.title("Settings")
theme = st.sidebar.radio("Select Theme", options=["Light", "Dark"])

# Apply theme colors
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

# Use session state to store inputs and results
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# Calculate Present Value (PV) and Future Value (FV)
def calculate_values(principal, rate, years):
    fv = principal * (1 + rate / 100) ** years
    pv = principal / ((1 + rate / 100) ** years)
    return pv, fv

pv, fv = calculate_values(principal, rate, years)

# Organize main page content in columns
col1, col2 = st.columns(2)

with col1:
    st.header("Present Value (PV) 💰")
    st.markdown(f"<div style='color:{text_color}; font-size:24px;'>${pv:,.2f}</div>", unsafe_allow_html=True)
    st.caption("The current worth of a future sum of money or stream of cash flows given a specified rate of return.")

with col2:
    st.header("Future Value (FV) 🚀")
    st.markdown(f"<div style='color:{text_color}; font-size:24px;'>${fv:,.2f}</div>", unsafe_allow_html=True)
    st.caption("The value of a current asset at a specified date in the future based on an assumed rate of growth.")

# Interactive plot of value growth over years
years_range = list(range(1, years + 1))
fv_values = [principal * (1 + rate / 100) ** y for y in years_range]

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

# Feedback message
st.success("Calculation complete! Adjust inputs in the sidebar to update values.")

# Footer with external links
st.markdown(
    """
    ---
    Developed by Your Name | [GitHub](https://github.com/yourrepo) | [Documentation](https://yourdocslink)
    """,
    unsafe_allow_html=True
)
