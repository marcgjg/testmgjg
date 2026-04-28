import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Sidebar for user input
st.sidebar.header("Input Parameters")
debt_ratio = st.sidebar.slider("Debt Ratio (%)", 0, 100, 40)
cost_of_debt = st.sidebar.number_input("Cost of Debt (%)", min_value=0.0, max_value=20.0, value=5.0)
cost_of_equity = st.sidebar.number_input("Cost of Equity (%)", min_value=0.0, max_value=20.0, value=10.0)
tax_rate = st.sidebar.number_input("Corporate Tax Rate (%)", min_value=0.0, max_value=100.0, value=30.0)

# Header and description
st.markdown("<h1 style='color:#003366;'>Capital Structure Visualizer</h1>", unsafe_allow_html=True)
st.markdown("""
A simple tool to illustrate the trade-off between debt and equity in corporate finance.
""")

# Calculation
debt_ratio_decimal = debt_ratio / 100
tax_rate_decimal = tax_rate / 100
wacc = debt_ratio_decimal * cost_of_debt * (1 - tax_rate_decimal) + (1 - debt_ratio_decimal) * cost_of_equity

# Data for plot
ratios = np.linspace(0, 1, 101)
waccs = ratios * cost_of_debt * (1 - tax_rate_decimal) + (1 - ratios) * cost_of_equity

# Plotly Chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=ratios * 100,
    y=waccs,
    mode='lines',
    name='WACC',
    line=dict(color='#008080', width=3)
))
fig.add_trace(go.Scatter(
    x=[debt_ratio],
    y=[wacc],
    mode='markers+text',
    name='Your Selection',
    marker=dict(color='#FF5733', size=12),
    text=[f"WACC: {wacc:.2f}%"],
    textposition="top center"
))
fig.update_layout(
    title="Weighted Average Cost of Capital (WACC) vs. Debt Ratio",
    xaxis_title="Debt Ratio (%)",
    yaxis_title="WACC (%)",
    font=dict(family="Open Sans", size=14),
    plot_bgcolor='#f9f9f9',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# Explanations and key takeaways
st.markdown("""
**Key Takeaways:**  
- WACC decreases as debt increases (due to tax shield), but excessive debt can increase financial risk.
- Optimal capital structure minimizes WACC.
- Your selected debt ratio gives a WACC of **{:.2f}%**.
""".format(wacc))

# Data table in expander
with st.expander("Show Calculation Table"):
    data = pd.DataFrame({
        "Debt Ratio (%)": ratios * 100,
        "WACC (%)": waccs
    })
    st.dataframe(data.style.highlight_max(axis=0), use_container_width=True)

# Footer
st.markdown("<hr><small>© 2026 Prof. Marc Goergen | finance.profmarcgoergen.com</small>", unsafe_allow_html=True)
