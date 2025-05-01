import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import cm
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Advanced Time Value of Money Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
    }
    .description {
        font-size: 1rem;
        color: #424242;
        margin-bottom: 1.5rem;
    }
    .calculator-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .result-card {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.8rem;
        color: #757575;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .tab-content {
        padding: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Advanced Time Value of Money Calculator</h1>", unsafe_allow_html=True)

st.markdown("<p class='description'>Calculate the time value of money with this comprehensive financial calculator. Understand how money grows over time and make informed financial decisions.</p>", unsafe_allow_html=True)

# Create tabs for different calculators
tab1, tab2, tab3, tab4 = st.tabs(["📈 PV & FV Calculator", "📊 Visualization", "📝 Comparison Tool", "ℹ️ Learn More"])

with tab1:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    
    # Create two columns for PV and FV calculators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header'>Present Value (PV) Calculator</h2>", unsafe_allow_html=True)
        st.markdown("<p>Calculate what a future sum of money is worth today.</p>", unsafe_allow_html=True)
        
        # PV Calculator inputs
        pv_future_value = st.number_input("Future Value ($)", min_value=0.0, value=10000.0, step=100.0, key="pv_fv")
        pv_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1, key="pv_rate")
        pv_years = st.number_input("Time Period (Years)", min_value=0, value=5, step=1, key="pv_years")
        
        # Compounding frequency selection
        pv_compounding = st.selectbox(
            "Compounding Frequency",
            options=["Annually", "Semi-annually", "Quarterly", "Monthly", "Daily"],
            index=0,
            key="pv_compounding"
        )
        
        # Map selection to number of periods per year
        compounding_map = {
            "Annually": 1,
            "Semi-annually": 2,
            "Quarterly": 4,
            "Monthly": 12,
            "Daily": 365
        }
        
        pv_periods = pv_years * compounding_map[pv_compounding]
        pv_rate_per_period = pv_rate / (100 * compounding_map[pv_compounding])
        
        # Calculate Present Value
        if st.button("Calculate Present Value", key="calc_pv"):
            present_value = pv_future_value / ((1 + pv_rate_per_period) ** pv_periods)
            
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            st.markdown("<h3>Results:</h3>", unsafe_allow_html=True)
            
            # Display the result with more context
            st.metric(
                label="Present Value",
                value=f"${present_value:.2f}",
                delta=f"-${pv_future_value - present_value:.2f} from future value"
            )
            
            st.markdown(f"""
            <p>A future amount of <b>${pv_future_value:.2f}</b> in <b>{pv_years}</b> years with 
            an annual interest rate of <b>{pv_rate:.2f}%</b> compounded <b>{pv_compounding.lower()}</b> 
            has a present value of <b>${present_value:.2f}</b>.</p>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header'>Future Value (FV) Calculator</h2>", unsafe_allow_html=True)
        st.markdown("<p>Calculate what a current sum of money will be worth in the future.</p>", unsafe_allow_html=True)
        
        # FV Calculator inputs
        fv_present_value = st.number_input("Present Value ($)", min_value=0.0, value=10000.0, step=100.0, key="fv_pv")
        fv_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1, key="fv_rate")
        fv_years = st.number_input("Time Period (Years)", min_value=0, value=5, step=1, key="fv_years")
        
        # Compounding frequency selection
        fv_compounding = st.selectbox(
            "Compounding Frequency",
            options=["Annually", "Semi-annually", "Quarterly", "Monthly", "Daily"],
            index=0,
            key="fv_compounding"
        )
        
        fv_periods = fv_years * compounding_map[fv_compounding]
        fv_rate_per_period = fv_rate / (100 * compounding_map[fv_compounding])
        
        # Calculate Future Value
        if st.button("Calculate Future Value", key="calc_fv"):
            future_value = fv_present_value * ((1 + fv_rate_per_period) ** fv_periods)
            
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            st.markdown("<h3>Results:</h3>", unsafe_allow_html=True)
            
            # Display the result with more context
            st.metric(
                label="Future Value",
                value=f"${future_value:.2f}",
                delta=f"+${future_value - fv_present_value:.2f} from present value"
            )
            
            # Calculate the interest earned
            interest_earned = future_value - fv_present_value
            interest_percentage = (interest_earned / fv_present_value) * 100
            
            st.markdown(f"""
            <p>A present amount of <b>${fv_present_value:.2f}</b> will grow to <b>${future_value:.2f}</b> 
            in <b>{fv_years}</b> years with an annual interest rate of <b>{fv_rate:.2f}%</b> 
            compounded <b>{fv_compounding.lower()}</b>.</p>
            <p>Total interest earned: <b>${interest_earned:.2f}</b> ({interest_percentage:.2f}%)</p>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Visualize Time Value of Money</h2>", unsafe_allow_html=True)
    
    viz_col1, viz_col2 = st.columns([1, 2])
    
    with viz_col1:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        
        # Visualization inputs
        viz_initial = st.number_input("Initial Amount ($)", min_value=100.0, value=10000.0, step=100.0)
        viz_rate = st.slider("Annual Interest Rate (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
        viz_years = st.slider("Time Period (Years)", min_value=1, max_value=30, value=10)
        
        viz_compounding = st.selectbox(
            "Compounding Frequency",
            options=["Annually", "Semi-annually", "Quarterly", "Monthly", "Daily"],
            index=0
        )
        
        # Option to add additional rates for comparison
        compare_rates = st.checkbox("Compare different interest rates")
        
        if compare_rates:
            viz_rate2 = st.slider("Second Annual Interest Rate (%)", min_value=1.0, max_value=20.0, value=7.0, step=0.5)
            viz_rate3 = st.slider("Third Annual Interest Rate (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with viz_col2:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        
        # Prepare data for visualization
        years = list(range(viz_years + 1))
        periods_per_year = compounding_map[viz_compounding]
        
        # Generate future values for each year
        values = []
        for year in years:
            periods = year * periods_per_year
            rate_per_period = viz_rate / (100 * periods_per_year)
            fv = viz_initial * ((1 + rate_per_period) ** periods)
            values.append(fv)
        
        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=f'{viz_rate}% Interest',
            line=dict(color='#1E88E5', width=3),
            marker=dict(size=8)
        ))
        
        # Add additional rates for comparison if selected
        if compare_rates:
            values2 = []
            values3 = []
            
            for year in years:
                periods = year * periods_per_year
                
                rate_per_period2 = viz_rate2 / (100 * periods_per_year)
                fv2 = viz_initial * ((1 + rate_per_period2) ** periods)
                values2.append(fv2)
                
                rate_per_period3 = viz_rate3 / (100 * periods_per_year)
                fv3 = viz_initial * ((1 + rate_per_period3) ** periods)
                values3.append(fv3)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=values2,
                mode='lines+markers',
                name=f'{viz_rate2}% Interest',
                line=dict(color='#43A047', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=years,
                y=values3,
                mode='lines+markers',
                name=f'{viz_rate3}% Interest',
                line=dict(color='#E53935', width=3),
                marker=dict(size=8)
            ))
        
        # Add a line for the initial value (no growth)
        fig.add_trace(go.Scatter(
            x=years,
            y=[viz_initial] * len(years),
            mode='lines',
            name='Initial Amount (No Growth)',
            line=dict(color='#9E9E9E', width=2, dash='dash')
        ))
        
        # Customize the plot
        fig.update_layout(
            title=f'Growth of ${viz_initial:,.2f} Over {viz_years} Years',
            xaxis_title='Years',
            yaxis_title='Value ($)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        # Format y-axis as currency
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        # Show the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Display some insights
        final_value = values[-1]
        interest_earned = final_value - viz_initial
        interest_percentage = (interest_earned / viz_initial) * 100
        
        st.markdown(f"""
        <div style='text-align: center;'>
            <p>After <b>{viz_years}</b> years at <b>{viz_rate}%</b> interest compounded <b>{viz_compounding.lower()}</b>:</p>
            <p><span class='metric-value'>${final_value:,.2f}</span> final amount</p>
            <p><span class='metric-value'>${interest_earned:,.2f}</span> total interest earned</p>
            <p><span class='metric-value'>{interest_percentage:.2f}%</span> total return</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Comparison Tool</h2>", unsafe_allow_html=True)
    st.markdown("<p>Compare different scenarios to make better financial decisions.</p>", unsafe_allow_html=True)
    
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        
        # Scenario setup
        st.markdown("### Scenario Setup")
        initial_amount = st.number_input("Initial Investment ($)", min_value=100.0, value=10000.0, step=100.0, key="comp_initial")
        time_horizon = st.slider("Investment Horizon (Years)", min_value=1, max_value=40, value=20, key="comp_years")
        
        # Investment A
        st.markdown("### Investment A")
        investment_a_name = st.text_input("Name", value="Conservative", key="name_a")
        investment_a_rate = st.number_input("Annual Return (%)", min_value=0.0, max_value=30.0, value=4.0, step=0.1, key="rate_a")
        investment_a_risk = st.selectbox("Risk Level", options=["Low", "Medium", "High"], index=0, key="risk_a")
        
        # Investment B
        st.markdown("### Investment B")
        investment_b_name = st.text_input("Name", value="Moderate", key="name_b")
        investment_b_rate = st.number_input("Annual Return (%)", min_value=0.0, max_value=30.0, value=8.0, step=0.1, key="rate_b")
        investment_b_risk = st.selectbox("Risk Level", options=["Low", "Medium", "High"], index=1, key="risk_b")
        
        # Investment C
        st.markdown("### Investment C")
        investment_c_name = st.text_input("Name", value="Aggressive", key="name_c")
        investment_c_rate = st.number_input("Annual Return (%)", min_value=0.0, max_value=30.0, value=12.0, step=0.1, key="rate_c")
        investment_c_risk = st.selectbox("Risk Level", options=["Low", "Medium", "High"], index=2, key="risk_c")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with comp_col2:
        st.markdown("<div class='calculator-card'>", unsafe_allow_html=True)
        
        # Prepare data for comparison
        years = list(range(time_horizon + 1))
        
        # Calculate values for each investment
        values_a = [initial_amount * ((1 + investment_a_rate/100) ** year) for year in years]
        values_b = [initial_amount * ((1 + investment_b_rate/100) ** year) for year in years]
        values_c = [initial_amount * ((1 + investment_c_rate/100) ** year) for year in years]
        
        # Create comparison chart
        fig = go.Figure()
        
        # Add traces for each investment
        fig.add_trace(go.Scatter(
            x=years,
            y=values_a,
            mode='lines',
            name=f'{investment_a_name} ({investment_a_rate}%)',
            line=dict(color='#2196F3', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values_b,
            mode='lines',
            name=f'{investment_b_name} ({investment_b_rate}%)',
            line=dict(color='#FF9800', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values_c,
            mode='lines',
            name=f'{investment_c_name} ({investment_c_rate}%)',
            line=dict(color='#F44336', width=3)
        ))
        
        # Customize the plot
        fig.update_layout(
            title=f'Comparison of ${initial_amount:,.2f} Invested Over {time_horizon} Years',
            xaxis_title='Years',
            yaxis_title='Value ($)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template='plotly_white',
            height=400
        )
        
        # Format y-axis as currency
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        # Show the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a summary table
        final_a = values_a[-1]
        final_b = values_b[-1]
        final_c = values_c[-1]
        
        growth_a = final_a - initial_amount
        growth_b = final_b - initial_amount
        growth_c = final_c - initial_amount
        
        percent_a = (growth_a / initial_amount) * 100
        percent_b = (growth_b / initial_amount) * 100
        percent_c = (growth_c / initial_amount) * 100
        
        comparison_data = {
            "Investment": [investment_a_name, investment_b_name, investment_c_name],
            "Annual Return": [f"{investment_a_rate}%", f"{investment_b_rate}%", f"{investment_c_rate}%"],
            "Risk Level": [investment_a_risk, investment_b_risk, investment_c_risk],
            "Final Value": [f"${final_a:,.2f}", f"${final_b:,.2f}", f"${final_c:,.2f}"],
            "Total Growth": [f"${growth_a:,.2f}", f"${growth_b:,.2f}", f"${growth_c:,.2f}"],
            "Growth %": [f"{percent_a:.2f}%", f"{percent_b:.2f}%", f"{percent_c:.2f}%"]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Display key insights
        st.markdown("### Key Insights")
        
        # Determine which investment has the highest return
        best_investment = comparison_data["Investment"][comparison_data["Final Value"].index(max(comparison_data["Final Value"]))]
        
        # Calculate difference between highest and lowest
        max_value = max(final_a, final_b, final_c)
        min_value = min(final_a, final_b, final_c)
        difference = max_value - min_value
        difference_percent = (difference / min_value) * 100
        
        st.markdown(f"""
        - The {best_investment} investment yields the highest final value after {time_horizon} years.
        - The difference between the highest and lowest performing investment is ${difference:,.2f} ({difference_percent:.2f}%).
        - Higher returns come with increased risk levels, which should be considered based on your risk tolerance.
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Learn About Time Value of Money</h2>", unsafe_allow_html=True)
    
    # Create expandable sections for educational content
    with st.expander("What is Present Value (PV)?", expanded=True):
        st.markdown("""
        **Present Value (PV)** is the current worth of a future sum of money or stream of cash flows given a specified rate of return.
        
        The present value equation is:
        
        $PV = \frac{FV}{(1 + r)^n}$
        
        Where:
        - PV = Present Value
        - FV = Future Value
        - r = Interest rate (as a decimal)
        - n = Number of periods
        
        **Example**: If you're offered $10,000 five years from now, and the interest rate is 5% per year, the present value would be:
        
        $PV = \frac{\$10,000}{(1 + 0.05)^5} = \$7,835.26$
        
        This means that $7,835.26 today is equivalent to $10,000 five years from now at a 5% interest rate.
        """)
    
    with st.expander("What is Future Value (FV)?"):
        st.markdown("""
        **Future Value (FV)** is the value of an asset or cash at a specified date in the future based on an assumed growth rate.
        
        The future value equation is:
        
        $FV = PV \times (1 + r)^n$
        
        Where:
        - FV = Future Value
        - PV = Present Value
        - r = Interest rate (as a decimal)
        - n = Number of periods
        
        **Example**: If you invest $5,000 today at an annual interest rate of 6% for 8 years, the future value would be:
        
        $FV = \$5,000 \times (1 + 0.06)^8 = \$7,971.56$
        
        This means your $5,000 investment would grow to $7,971.56 after 8 years at a 6% annual interest rate.
        """)
    
    with st.expander("The Rule of 72"):
        st.markdown("""
        **The Rule of 72** is a simplified way to estimate how long an investment will take to double at a fixed annual rate of return.
        
        $Years\; to\; Double = \frac{72}{Interest\; Rate (\%)}$
        
        **Example**: At an 8% annual interest rate, an investment will take approximately 72 ÷ 8 = 9 years to double.
        
        This rule gives a reasonable approximation for interest rates between 4% and 12% and is useful for quick mental calculations when making investment decisions.
        """)
    
    with st.expander("Compounding Frequency"):
        st.markdown("""
        **Compounding frequency** refers to how often interest is calculated and added to the principal amount. The more frequent the compounding, the greater the future value will be.
        
        Common compounding frequencies:
        - Annually (once per year)
        - Semi-annually (twice per year)
        - Quarterly (four times per year)
        - Monthly (12 times per year)
        - Daily (365 times per year)
        - Continuous (infinite times per year)
        
        The formula adjusts as follows:
        
        $FV = PV \times (1 + \frac{r}{m})^{m \times n}$
        
        Where:
        - m = Number of times compounding occurs per year
        - n = Number of years
        
        For continuous compounding:
        
        $FV = PV \times e^{r \times n}$
        
        Where:
        - e = Euler's number (approximately 2.71828)
        """)
    
    with st.expander("Time Value of Money in Financial Decision Making"):
        st.markdown("""
        The time value of money concept is fundamental to many financial decisions:
        
        1. **Investment Evaluation**: Calculating net present value (NPV) of future cash flows to determine if an investment is worthwhile.
        
        2. **Loan and Mortgage Decisions**: Understanding the true cost of borrowing and comparing different loan offers.
        
        3. **Retirement Planning**: Estimating how much to save now to achieve desired retirement income.
        
        4. **Business Valuation**: Determining the worth of a business based on its expected future cash flows.
        
        5. **Bond Pricing**: Calculating the present value of future interest payments and principal repayment.
        
        6. **Insurance and Annuity Planning**: Determining appropriate premiums or payouts based on future value calculations.
        
        Remember that money available today is worth more than the same amount in the future because of its potential earning capacity.
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Advanced Time Value of Money Calculator © 2025 | Created with Streamlit</div>", unsafe_allow_html=True)
