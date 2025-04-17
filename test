import streamlit as st
import numpy as np
import pandas as pd
import uuid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from PIL import Image
import io

# Set the page layout to wide and add a custom title/icon
st.set_page_config(
    page_title="PV/FV Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
</style>
""", unsafe_allow_html=True)

def get_colors():
    """Return a list of aesthetically pleasing colors for the chart."""
    return [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Yellow-green
        '#17becf',  # Teal
    ]

def format_currency(value):
    """Format a value as currency."""
    return f"€{value:,.2f}"

def main():
    # Custom header with logo/title
    st.markdown('<h1 class="main-header">💰 Future Value / Present Value Visualizer</h1>', unsafe_allow_html=True)
    
    # Add a description
    with st.expander("ℹ️ About this tool", expanded=False):
        st.markdown("""
        This tool helps you visualize the concepts of **Present Value (PV)** and **Future Value (FV)** 
        for different interest rates and time periods.
        
        - **Future Value (FV)**: Shows how €100 invested today grows over time
        - **Present Value (PV)**: Shows what amount today is equivalent to €100 in the future
        
        Add multiple curves to compare different scenarios.
        """)

    # Initialize session state to store curves and previous parameters
    if "curves" not in st.session_state:
        st.session_state["curves"] = {}  # To store curves (key: unique, value: (label, series))
    if "prev_years" not in st.session_state:
        st.session_state["prev_years"] = None
    if "prev_calc_type" not in st.session_state:
        st.session_state["prev_calc_type"] = None
    if "curve_colors" not in st.session_state:
        st.session_state["curve_colors"] = {}

    # Use two columns with a better proportion
    col1, col2 = st.columns([1, 2])

    with col1:
        # Card-like container for calculation options
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Calculation Settings</div>', unsafe_allow_html=True)
        
        calculation_type = st.radio(
            "Select Calculation Type:",
            ("Future Value", "Present Value"),
            horizontal=True
        )

        principal = st.number_input(
            "Initial Amount (€):", 
            min_value=1, 
            max_value=10000, 
            value=100,
            step=10,
            help="The starting amount for FV or final amount for PV calculations"
        )

        years = st.slider(
            "Number of years:", 
            min_value=1, 
            max_value=50, 
            value=10,
            help="Time horizon for the calculation"
        )
        
        interest_rate_percent = st.slider(
            "Interest/Discount rate (%):", 
            min_value=0.0, 
            max_value=20.0, 
            value=5.0,
            step=0.1,
            help="Annual interest rate for FV or discount rate for PV"
        )
        interest_rate = interest_rate_percent / 100.0
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart controls
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Chart Controls</div>', unsafe_allow_html=True)
        
        col_add, col_reset = st.columns(2)
        with col_add:
            add_curve = st.button("➕ Add to Chart", use_container_width=True)
        with col_reset:
            reset_button = st.button("🔄 Reset Chart", use_container_width=True)
        
        # Reset curves on button click
        if reset_button:
            st.session_state["curves"] = {}
            st.session_state["curve_colors"] = {}

        # Clear curves automatically when switching FV/PV
        if st.session_state["prev_calc_type"] is not None and calculation_type != st.session_state["prev_calc_type"]:
            st.session_state["curves"] = {}
            st.session_state["curve_colors"] = {}

        # Update the stored previous parameters
        st.session_state["prev_years"] = years
        st.session_state["prev_calc_type"] = calculation_type
        st.markdown('</div>', unsafe_allow_html=True)

        # Calculate the current curve
        year_range = np.arange(0, years + 1)
        if calculation_type == "Future Value":
            # FV = principal * (1 + r)^n
            values = principal * (1 + interest_rate)**year_range
            calc_label = "Future Value"
        else:
            # PV = principal / (1 + r)^n
            values = principal / ((1 + interest_rate)**year_range)
            calc_label = "Present Value"

        # Create a Pandas Series for easy plotting
        curve_series = pd.Series(data=values.round(2), index=year_range)
        
        # Add curve to chart when button is clicked
        if add_curve:
            curve_label = f"{calc_label} @ {interest_rate_percent}%"
            curve_key = f"{uuid.uuid4().hex[:5]}"
            st.session_state["curves"][curve_key] = (curve_label, curve_series)
            
            # Assign a color from our palette
            colors = get_colors()
            color_idx = len(st.session_state["curve_colors"]) % len(colors)
            st.session_state["curve_colors"][curve_key] = colors[color_idx]
            
            # Show success message
            st.success(f"Added curve: {curve_label}")

        # Display the current calculation table
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="subheader">Current {calc_label}</div>', unsafe_allow_html=True)
        
        # Create a more visually appealing table
        df_current = pd.DataFrame({"Year": year_range, "Value (€)": curve_series.values})
        
        # Add visual indicator of growth/decay
        if len(df_current) > 1:
            max_val = df_current["Value (€)"].max()
            min_val = df_current["Value (€)"].min()
            range_val = max_val - min_val
            
            def color_scale(val):
                if calculation_type == "Future Value":
                    # Blue gradient for FV (darker = higher value)
                    normalized = (val - min_val) / range_val if range_val > 0 else 0
                    return f'background-color: rgba(25, 118, 210, {normalized * 0.4})'
                else:
                    # Green gradient for PV (darker = higher value)
                    normalized = (val - min_val) / range_val if range_val > 0 else 0
                    return f'background-color: rgba(46, 125, 50, {normalized * 0.4})'
            
            styled_df = df_current.style.format({
                "Value (€)": format_currency
            }).applymap(color_scale, subset=["Value (€)"])
            
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(df_current.style.format({"Value (€)": format_currency}), use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Card-like container for the chart
        st.markdown('<div class="card plot-container">', unsafe_allow_html=True)
        
        # Create a plotly figure for better interactivity
        if st.session_state["curves"]:
            # Combine all stored curves into a single DataFrame
            df_plot = pd.DataFrame()
            for curve_key, (label, series) in st.session_state["curves"].items():
                df_plot[label] = series
            
            # Create an interactive Plotly figure
            fig = go.Figure()
            
            for curve_key, (label, _) in st.session_state["curves"].items():
                color = st.session_state["curve_colors"].get(curve_key, "#1f77b4")
                fig.add_trace(go.Scatter(
                    x=df_plot.index,
                    y=df_plot[label],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color, width=3),
                    marker=dict(size=8, color=color),
                    hovertemplate='Year: %{x}<br>Value: €%{y:.2f}<extra></extra>'
                ))
            
            # Customize the layout
            title = f"{'Future Value' if calculation_type == 'Future Value' else 'Present Value'} Comparison"
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=24, family="Arial, sans-serif", color="#1E3A8A"),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title="Year",
                    tickmode='linear',
                    tick0=0,
                    dtick=5 if years > 20 else 1,
                    gridcolor='rgba(230, 230, 230, 0.8)'
                ),
                yaxis=dict(
                    title="Value (€)",
                    gridcolor='rgba(230, 230, 230, 0.8)',
                    tickformat=',.2f'
                ),
                plot_bgcolor='rgba(248, 250, 252, 0.5)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='closest',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                height=600,
                margin=dict(l=60, r=40, t=80, b=80)
            )
            
            # Add a horizontal line at the initial value
            fig.add_shape(
                type="line",
                x0=0,
                y0=principal,
                x1=years,
                y1=principal,
                line=dict(
                    color="rgba(128, 128, 128, 0.5)",
                    width=2,
                    dash="dash",
                ),
                name="Initial Value"
            )
            
            # Add annotations
            fig.add_annotation(
                x=0,
                y=principal,
                text=f"Initial: €{principal}",
                showarrow=False,
                yshift=10,
                font=dict(color="rgba(128, 128, 128, 1)")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Show a message when no curves are added
            st.info("Use the '➕ Add to Chart' button to add curves for comparison.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer with information
    st.markdown('<div class="footer">Explore how money grows or discounts over time with different interest rates.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
