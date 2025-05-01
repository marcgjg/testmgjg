import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Original Code (with minimal modifications for compatibility)
@st.cache_data
def calculate_pv_and_fv(initial_investment, interest_rate, years, contribution_amount, contribution_frequency):
    # Convert interest rate to decimal
    interest_rate = interest_rate / 100

    # Calculate future value
    if contribution_frequency == "Yearly":
        future_value = initial_investment * (1 + interest_rate)**years + \
                       contribution_amount * ((1 + interest_rate)**years - 1) / interest_rate
    elif contribution_frequency == "Monthly":
        monthly_interest_rate = interest_rate / 12
        future_value = initial_investment * (1 + monthly_interest_rate)**(years*12) + \
                       contribution_amount * ((1 + monthly_interest_rate)**(years*12) - 1) / monthly_interest_rate
    else: # One time
        future_value = initial_investment * (1 + interest_rate)**years

    # Calculate present value
    if contribution_frequency == "Yearly":
        present_value = initial_investment / (1 + interest_rate)**years + \
                       contribution_amount * (1 - (1 + interest_rate)**-years) / interest_rate
    elif contribution_frequency == "Monthly":
        monthly_interest_rate = interest_rate / 12
        present_value = initial_investment / (1 + monthly_interest_rate)**(years*12) + \
                        contribution_amount * (1 - (1 + monthly_interest_rate)**-(years*12)) / monthly_interest_rate
    else: # One time
        present_value = initial_investment / (1 + interest_rate)**years

    return present_value, future_value

# --- Streamlit App ---
st.set_page_config(page_title="PV and FV Calculator", layout="wide")

# Sidebar for Inputs
with st.sidebar:
    st.header("Calculator Inputs")
    initial_investment = st.number_input("Initial Investment", value=1000.0, step=100.0)
    interest_rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    years = st.slider("Number of Years", min_value=1, max_value=50, value=10)
    contribution_amount = st.number_input("Yearly Contribution Amount", value=100.0, step=50.0)
    contribution_frequency = st.selectbox("Contribution Frequency", ["Yearly", "Monthly", "One time"])

# Main Panel Calculations
present_value, future_value = calculate_pv_and_fv(initial_investment, interest_rate, years, contribution_amount, contribution_frequency)

# Display Results using Columns
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Present Value", value=f"${present_value:,.2f}")
with col2:
    st.metric(label="Future Value", value=f"${future_value:,.2f}")

# --- Visualization ---
# Generate data for a line chart of investment growth over time
def generate_growth_data(initial_investment, interest_rate, years, contribution_amount, contribution_frequency):
    interest_rate = interest_rate / 100
    data = []
    investment = initial_investment
    for year in range(years + 1):
        data.append(investment)
        if contribution_frequency == "Yearly" and year > 0:
            investment += contribution_amount
        elif contribution_frequency == "Monthly" and year > 0:
            monthly_interest_rate = interest_rate / 12
            investment += contribution_amount
        investment *= (1 + interest_rate) if contribution_frequency == "Yearly" else (1 + interest_rate/12)**12 if contribution_frequency == "Monthly" else (1 + interest_rate)
    return data

growth_data = generate_growth_data(initial_investment, interest_rate, years, contribution_amount, contribution_frequency)

# Create DataFrame for Plotly
df = pd.DataFrame({'Year': range(years + 1), 'Investment Value': growth_data})

# Create the Plotly line chart
fig = px.line(df, x='Year', y='Investment Value', title='Investment Growth Over Time',
              labels={'Investment Value': 'Investment Value ($)'})
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Investment Value ($)",
    plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
    paper_bgcolor="rgba(0,0,0,0)", # Transparent background
)

st.plotly_chart(fig, use_container_width=True)
