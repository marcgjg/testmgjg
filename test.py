import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Set the page layout to wide and add a custom title/icon
st.set_page_config(
    page_title="Two-Asset Frontier",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (matching the previous apps)
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
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        padding: 1rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
    }
    .metric-label {
        color: #64748B;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Custom header with logo/title
st.markdown('<h1 class="main-header">📈 Two-Asset Efficient Frontier</h1>', unsafe_allow_html=True)

# Add a description
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown("""
    This tool visualizes the **Efficient Frontier** for a portfolio of two assets.
    
    - The **Efficient Frontier** shows all optimal portfolios that offer the highest expected return for a defined level of risk
    - The **Minimum Variance Portfolio (MVP)** is the portfolio with the lowest possible risk
    
    Adjust the sliders to see how changes in returns, standard deviations, and correlation affect the frontier.
    """)

# Create columns for inputs and plot
col1, col2 = st.columns([1, 2])

with col1:
    # Card for asset inputs
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Asset Parameters</div>', unsafe_allow_html=True)
    
    # Define sliders for inputs with better organization
    st.markdown("#### Expected Returns")
    mu_A = st.slider('Expected Return of Stock A (%)', 
                     min_value=0.0, max_value=50.0, value=8.9, step=0.1,
                     help="Annual expected return")
    mu_B = st.slider('Expected Return of Stock B (%)', 
                     min_value=0.0, max_value=50.0, value=9.2, step=0.1,
                     help="Annual expected return")
    
    st.markdown("#### Risk Parameters")
    sigma_A = st.slider('Standard Deviation of Stock A (%)', 
                        min_value=0.0, max_value=50.0, value=7.9, step=0.1,
                        help="Annual standard deviation (volatility)")
    sigma_B = st.slider('Standard Deviation of Stock B (%)', 
                        min_value=0.0, max_value=50.0, value=8.9, step=0.1,
                        help="Annual standard deviation (volatility)")
    
    rho = st.slider('Correlation Coefficient', 
                    min_value=-1.0, max_value=1.0, value=-0.5, step=0.01,
                    help="Correlation between the two assets (-1 to 1)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Information box for correlation
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"""
    **Current Correlation: {rho:.2f}**
    
    - Perfect negative correlation: -1.0
    - No correlation: 0.0
    - Perfect positive correlation: 1.0
    
    Diversification benefits are strongest when correlation is negative or low.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Convert sliders back to decimal form for calculations
mu_A /= 100
mu_B /= 100
sigma_A /= 100
sigma_B /= 100

# Generate parametric minimum-variance frontier
alphas = np.linspace(0, 1, 100)
portfolio_returns = alphas * mu_A + (1 - alphas) * mu_B
portfolio_stds = np.sqrt(
    alphas**2 * sigma_A**2 +
    (1 - alphas)**2 * sigma_B**2 +
    2 * alphas * (1 - alphas) * rho * sigma_A * sigma_B
)

# Compute Minimum Variance Portfolio (MVP)
denominator = sigma_A**2 + sigma_B**2 - 2 * rho * sigma_A * sigma_B

# Handle division by zero
if denominator == 0:
    w_star = sigma_B / (sigma_A + sigma_B)  # Special handling for rho = -1
else:
    w_star = (sigma_B**2 - rho * sigma_A * sigma_B) / denominator

w_star = max(0, min(w_star, 1))  # Ensure no short sales

mvp_return = w_star * mu_A + (1 - w_star) * mu_B

# Correctly calculate MVP standard deviation
mvp_variance = w_star**2 * sigma_A**2 + (1 - w_star)**2 * sigma_B**2 + 2 * w_star * (1 - w_star) * rho * sigma_A * sigma_B

# Check if variance is non-negative before calculating standard deviation
if mvp_variance >= 0:
    mvp_std = np.sqrt(mvp_variance)
else:
    mvp_std = 0  # Set to 0 if variance is negative (theoretical minimum variance portfolio)

# Special case handling: If returns are equal, MVP is the only efficient portfolio
if mu_A == mu_B:
    # Create the plotly figure for equal returns case
    with col2:
        st.markdown('<div class="card plot-container">', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        # Add Stock A and B points
        fig.add_trace(go.Scatter(
            x=[sigma_A * 100],
            y=[mu_A * 100],
            mode='markers',
            marker=dict(size=12, color='#10B981', symbol='square'),
            name='Stock A',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<br>Asset: Stock A<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[sigma_B * 100],
            y=[mu_B * 100],
            mode='markers',
            marker=dict(size=12, color='#F97316', symbol='square'),
            name='Stock B',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<br>Asset: Stock B<extra></extra>'
        ))
        
        # Add MVP point
        fig.add_trace(go.Scatter(
            x=[mvp_std * 100],
            y=[mvp_return * 100],
            mode='markers',
            marker=dict(size=14, color='#EF4444', symbol='star'),
            name='Minimum Variance Portfolio',
            hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>Stock A: {w_star*100:.1f}%<br>Stock B: {(1-w_star)*100:.1f}%<extra></extra>'
        ))
        
        # Customize the layout
        max_std = max(sigma_A, sigma_B) * 100 + 1
        min_return = min(mu_A, mu_B) * 100 - 1
        max_return = max(mu_A, mu_B) * 100 + 1
        
        fig.update_layout(
            title=dict(
                text="Minimum Variance Portfolio",
                font=dict(size=24, family="Arial, sans-serif", color="#1E3A8A"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Standard Deviation (%)",
                tickformat='.1f',
                gridcolor='rgba(230, 230, 230, 0.8)',
                range=[0, max_std]
            ),
            yaxis=dict(
                title="Expected Return (%)",
                tickformat='.1f',
                gridcolor='rgba(230, 230, 230, 0.8)',
                range=[min_return, max_return]
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='closest',
            height=600,
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Results box
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Portfolio Results</div>', unsafe_allow_html=True)
        
        # Create a grid for metrics
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mvp_std*100:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Minimum Standard Deviation</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mvp_return*100:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">MVP Return</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_c:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{w_star*100:.1f}% / {(1-w_star)*100:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">MVP Weights (Stock A/B)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Split into efficient and inefficient frontiers
    efficient_mask = portfolio_returns >= mvp_return  # Keep only points above or equal to MVP's return
    efficient_returns = portfolio_returns[efficient_mask]
    efficient_stds = portfolio_stds[efficient_mask]
    inefficient_returns = portfolio_returns[~efficient_mask]
    inefficient_stds = portfolio_stds[~efficient_mask]
    
    # Create the plotly figure for normal case
    with col2:
        st.markdown('<div class="card plot-container">', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        # Add efficient frontier
        fig.add_trace(go.Scatter(
            x=efficient_stds * 100,
            y=efficient_returns * 100,
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='#2563EB', width=3),
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        # Add inefficient frontier
        fig.add_trace(go.Scatter(
            x=inefficient_stds * 100,
            y=inefficient_returns * 100,
            mode='lines',
            name='Inefficient Frontier',
            line=dict(color='#2563EB', width=3, dash='dash'),
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        # Add Stock A and B points
        fig.add_trace(go.Scatter(
            x=[sigma_A * 100],
            y=[mu_A * 100],
            mode='markers',
            marker=dict(size=12, color='#10B981', symbol='square'),
            name='Stock A',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<br>Asset: Stock A<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[sigma_B * 100],
            y=[mu_B * 100],
            mode='markers',
            marker=dict(size=12, color='#F97316', symbol='square'),
            name='Stock B',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<br>Asset: Stock B<extra></extra>'
        ))
        
        # Add MVP point
        fig.add_trace(go.Scatter(
            x=[mvp_std * 100],
            y=[mvp_return * 100],
            mode='markers',
            marker=dict(size=14, color='#EF4444', symbol='star'),
            name='Minimum Variance Portfolio',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<br>Stock A: {:.1f}%<br>Stock B: {:.1f}%<extra></extra>'.format(
                w_star*100, (1-w_star)*100)
        ))
        
        # Set x-axis limits with default value for empty lists
        max_efficient_std = max(efficient_stds, default=0)
        max_inefficient_std = max(inefficient_stds, default=0)
        
        # Customize the layout
        fig.update_layout(
            title=dict(
                text="Efficient Frontier with Minimum-Variance Portfolio (MVP)",
                font=dict(size=24, family="Arial, sans-serif", color="#1E3A8A"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Standard Deviation (%)",
                tickformat='.1f',
                gridcolor='rgba(230, 230, 230, 0.8)',
                range=[0, max(max_efficient_std, max_inefficient_std) * 100 + 1]
            ),
            yaxis=dict(
                title="Expected Return (%)",
                tickformat='.1f',
                gridcolor='rgba(230, 230, 230, 0.8)',
                range=[min(min(efficient_returns), min(inefficient_returns, default=mu_A)) * 100 - 1, 
                      max(max(efficient_returns), max(inefficient_returns, default=mu_B)) * 100 + 1]
            ),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='closest',
            height=600,
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Results box
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Portfolio Results</div>', unsafe_allow_html=True)
        
        # Create a grid for metrics
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mvp_std*100:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Minimum Standard Deviation</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mvp_return*100:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">MVP Return</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_c:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{w_star*100:.1f}% / {(1-w_star)*100:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">MVP Weights (Stock A/B)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add educational content
with st.expander("📘 Understanding the Efficient Frontier", expanded=False):
    st.markdown("""
    ### Key Concepts
    
    **Efficient Frontier**: The set of optimal portfolios that offer the highest expected return for a defined level of risk.
    
    **Minimum Variance Portfolio (MVP)**: The portfolio with the lowest possible risk, regardless of return.
    
    **Correlation Effects**:
    - Negative correlation (-1 to 0): Strong diversification benefits
    - Zero correlation (0): Good diversification 
    - Positive correlation (0 to +1): Limited diversification benefits
    
    ### Portfolio Optimization
    
    The weight of asset A in the minimum variance portfolio is given by:
    
    w_A = (σ²_B - ρ·σ_A·σ_B) / (σ²_A + σ²_B - 2·ρ·σ_A·σ_B)
    
    where:
    - σ²_A, σ²_B = variances of assets A and B
    - ρ = correlation coefficient
    - σ_A, σ_B = standard deviations of assets A and B
    """)

# Footer
st.markdown('<div class="footer">Two-Asset Efficient Frontier Visualizer | For educational purposes</div>', unsafe_allow_html=True)
