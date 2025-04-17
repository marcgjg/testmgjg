import streamlit as st
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set the page layout to wide and add a custom title/icon
st.set_page_config(
    page_title="NPV/IRR Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (matching the PV/FV app)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    .card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
        font-size: 0.8rem;
        color: #64748B;
    }
    .stSlider label {
        font-weight: 500;
        color: #334155;
    }
    .plot-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background-color: #F0F9FF;
        border-left: 4px solid #0284C7;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0px 5px 5px 0px;
    }
    .cf-table {
        margin-top: 1rem;
    }
    .cf-table th {
        text-align: center;
        background-color: #EFF6FF;
    }
    .results-box {
        padding: 1rem;
        background-color: #F0FDF4;
        border-radius: 5px;
        border-left: 4px solid #22C55E;
        margin-top: 1rem;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FEF2F2;
        border-radius: 5px;
        border-left: 4px solid #EF4444;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Custom header with logo/title
st.markdown('<h1 class="main-header">📊 NPV and IRR Visualizer</h1>', unsafe_allow_html=True)

# Add a description
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown("""
    This tool helps you visualize the **Net Present Value (NPV)** and **Internal Rate of Return (IRR)** for a series of cash flows.
    
    - **NPV (Net Present Value)**: Calculates the present value of future cash flows minus the initial investment
    - **IRR (Internal Rate of Return)**: The discount rate at which the NPV equals zero
    
    Enter your cash flows as comma-separated values, with the initial investment as a negative number.
    """)

# Create two columns: left for controls; right for diagram
col_left, col_right = st.columns([1, 2])

with col_left:
    # Card for input controls
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Cash Flow Inputs</div>', unsafe_allow_html=True)
    
    # Let students enter cash flows as comma-separated values
    cash_flow_input = st.text_area(
        "Enter cash flows for each period (comma separated):",
        "-1000, 300, 400, 500, 600",
        help="Enter the initial investment as a negative number, followed by the cash inflows"
    )
    
    # Convert the cash flow input into a list of floats
    try:
        cash_flows = [float(x.strip()) for x in cash_flow_input.split(",")]
        valid_input = True
    except Exception:
        st.markdown('<div class="warning-box">Invalid input. Please enter valid numbers separated by commas.</div>', unsafe_allow_html=True)
        valid_input = False
    
    # Option to add a template
    if st.button("📋 Use Example Template"):
        cash_flow_input = "-1000, 300, 400, 500, 600"
        st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if valid_input:
        # Card for displaying cash flow table
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Cash Flow Summary</div>', unsafe_allow_html=True)
        
        # Create a table showing periods and cash flows
        periods = list(range(len(cash_flows)))
        cf_data = {"Period": periods, "Cash Flow": cash_flows}
        
        # Display cash flow table with custom styling
        st.markdown('<div class="cf-table">', unsafe_allow_html=True)
        cf_table = "<table width='100%'><thead><tr><th>Period</th><th>Cash Flow</th></tr></thead><tbody>"
        
        for i, cf in zip(periods, cash_flows):
            # Highlight negative values in red, positive in green
            color = "#DC2626" if cf < 0 else "#16A34A" if cf > 0 else "#000000"
            cf_table += f"<tr><td style='text-align: center;'>{i}</td><td style='text-align: right; color: {color};'>€{cf:,.2f}</td></tr>"
        
        cf_table += "</tbody></table>"
        st.markdown(cf_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Calculate and display initial investment and total cash inflows
        init_investment = cash_flows[0] if cash_flows[0] < 0 else 0
        total_inflows = sum(cf for cf in cash_flows if cf > 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Initial Investment", f"€{init_investment:,.2f}")
        with col2:
            st.metric("Total Cash Inflows", f"€{total_inflows:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Card for discount rate controls
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Discount Rate Settings</div>', unsafe_allow_html=True)
    
    # Slider to select a discount rate range (in percentages)
    discount_rate_range = st.slider(
        "Discount Rate Range (%):",
        min_value=0,
        max_value=50,
        value=(5, 30),
        help="Select the range of discount rates to analyze"
    )
    min_rate, max_rate = discount_rate_range
    min_rate_dec = min_rate / 100.0
    max_rate_dec = max_rate / 100.0
    
    # Add resolution control
    resolution = st.select_slider(
        "Chart Resolution:",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="Higher resolution shows more data points but may be slower"
    )
    
    resolution_points = {"Low": 50, "Medium": 100, "High": 200}
    num_points = resolution_points[resolution]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Information box
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    The NPV is calculated as:
    
    NPV = CF₀ + CF₁/(1+r)¹ + CF₂/(1+r)² + ... + CFₙ/(1+r)ⁿ
    
    Where:
    - CF = Cash flow in period t
    - r = Discount rate
    - n = Number of periods
    
    The IRR is the discount rate where NPV = 0
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Define a function to compute NPV
def compute_npv(cash_flows, r):
    return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))

if valid_input:
    # Generate a set of discount rates to evaluate
    rates = np.linspace(min_rate_dec, max_rate_dec, num_points)
    npv_values = [compute_npv(cash_flows, r) for r in rates]
    
    # Calculate the IRR using numpy_financial
    try:
        irr = npf.irr(cash_flows)
        irr_percent = irr * 100
        irr_valid = True
    except Exception:
        irr = None
        irr_valid = False
    
    with col_right:
        # Card for NPV visualization
        st.markdown('<div class="card plot-container">', unsafe_allow_html=True)
        
        # Create the plotly figure
        fig = go.Figure()
        
        # Add the NPV curve
        fig.add_trace(go.Scatter(
            x=rates * 100,
            y=npv_values,
            mode='lines',
            name='NPV Curve',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='Rate: %{x:.2f}%<br>NPV: €%{y:.2f}<extra></extra>'
        ))
        
        # Add zero line
        fig.add_shape(
            type="line",
            x0=min_rate,
            y0=0,
            x1=max_rate,
            y1=0,
            line=dict(
                color="black",
                width=1,
                dash="dash",
            )
        )
        
        # If IRR is computed and lies within the selected discount rate range, mark it
        if irr_valid and (min_rate <= (irr * 100) <= max_rate):
            npv_at_irr = compute_npv(cash_flows, irr)
            
            # Add IRR point
            fig.add_trace(go.Scatter(
                x=[irr * 100],
                y=[npv_at_irr],
                mode='markers',
                marker=dict(size=12, color='red', symbol='circle'),
                name=f'IRR = {irr_percent:.2f}%',
                hovertemplate='IRR: %{x:.2f}%<br>NPV: €%{y:.2f}<extra></extra>'
            ))
            
            # Add IRR vertical line
            fig.add_shape(
                type="line",
                x0=irr * 100,
                y0=min(npv_values) if min(npv_values) < 0 else 0,
                x1=irr * 100,
                y1=0,
                line=dict(
                    color="red",
                    width=1,
                    dash="dash",
                )
            )
            
            # Add IRR annotation
            fig.add_annotation(
                x=irr * 100,
                y=0,
                text=f"IRR: {irr_percent:.2f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="red",
                ax=0,
                ay=-40,
                bordercolor="red",
                borderwidth=2,
                borderpad=4,
                bgcolor="white",
                opacity=0.8,
                font=dict(color="red")
            )
        
        # Customize the layout
        fig.update_layout(
            title=dict(
                text="NPV vs. Discount Rate",
                font=dict(size=24, family="Arial, sans-serif", color="#1E3A8A"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Discount Rate (%)",
                tickformat='.1f',
                gridcolor='rgba(230, 230, 230, 0.8)'
            ),
            yaxis=dict(
                title="Net Present Value (€)",
                tickformat=',.2f',
                gridcolor='rgba(230, 230, 230, 0.8)',
                zeroline=True,
                zerolinecolor='rgba(0, 0, 0, 0.2)',
                zerolinewidth=1
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='closest',
            height=600,
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Results section
        if irr_valid:
            st.markdown('<div class="results-box">', unsafe_allow_html=True)
            
            # Create columns for results
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.markdown(f"**Internal Rate of Return (IRR):** {irr_percent:.2f}%")
                st.markdown("*The discount rate at which NPV equals zero*")
            
            with res_col2:
                # Calculate NPV at a common discount rate (10%)
                standard_rate = 0.10  # 10%
                npv_at_standard = compute_npv(cash_flows, standard_rate)
                st.markdown(f"**NPV at 10% discount rate:** €{npv_at_standard:,.2f}")
                
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("**No valid IRR found within the given range.**")
            st.markdown("This usually happens when the cash flows don't change sign (from negative to positive or vice versa).")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add additional information about the results
        with st.expander("📈 NPV Interpretation", expanded=False):
            st.markdown("""
            ### Interpreting NPV Results
            
            - **Positive NPV**: The investment adds value, and should be accepted
            - **Negative NPV**: The investment subtracts value, and should be rejected
            - **Zero NPV**: The investment breaks even
            
            ### Decision Rule
            
            Accept investment opportunities with positive NPVs at your required rate of return.
            When comparing mutually exclusive projects, choose the one with the highest NPV.
            """)
        
        with st.expander("💰 IRR Interpretation", expanded=False):
            st.markdown("""
            ### Interpreting IRR Results
            
            The IRR is the discount rate that makes the NPV equal to zero. It represents the annualized effective return rate:
            
            - If IRR > Required Rate of Return: Accept the project
            - If IRR < Required Rate of Return: Reject the project
            
            ### Limitations
            
            - Multiple IRRs can exist if cash flows change sign more than once
            - IRR assumes reinvestment at the IRR rate itself, which may be unrealistic
            - IRR may give misleading results when comparing mutually exclusive projects
            """)

# Footer
st.markdown('<div class="footer">NPV and IRR Visualizer | For educational purposes</div>', unsafe_allow_html=True)
