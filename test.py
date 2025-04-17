import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

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
    .results-box {
        padding: 1rem;
        background-color: #F0FDF4;
        border-radius: 5px;
        border-left: 4px solid #22C55E;
        margin-top: 1rem;
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
    .stock-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 1rem;
        background-color: #EFF6FF;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .stock-name {
        font-weight: 600;
        color: #1E40AF;
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
    
    # Add option to use stock names
    use_custom_names = st.checkbox("Use custom asset names", value=False)
    
    if use_custom_names:
        asset_a_name = st.text_input("Asset A Name", value="Technology ETF")
        asset_b_name = st.text_input("Asset B Name", value="Bond Fund")
    else:
        asset_a_name = "Asset A"
        asset_b_name = "Asset B"
    
    # Define sliders for inputs with better organization
    st.markdown("#### Expected Returns")
    mu_A = st.slider(f'Expected Return of {asset_a_name} (%)', 
                     min_value=0.0, max_value=50.0, value=8.9, step=0.1,
                     help="Annual expected return")
    mu_B = st.slider(f'Expected Return of {asset_b_name} (%)', 
                     min_value=0.0, max_value=50.0, value=9.2, step=0.1,
                     help="Annual expected return")
    
    st.markdown("#### Risk Parameters")
    sigma_A = st.slider(f'Standard Deviation of {asset_a_name} (%)', 
                        min_value=0.0, max_value=50.0, value=7.9, step=0.1,
                        help="Annual standard deviation (volatility)")
    sigma_B = st.slider(f'Standard Deviation of {asset_b_name} (%)', 
                        min_value=0.0, max_value=50.0, value=8.9, step=0.1,
                        help="Annual standard deviation (volatility)")
    
    rho = st.slider('Correlation Coefficient', 
                    min_value=-1.0, max_value=1.0, value=-0.5, step=0.01,
                    help="Correlation between the two assets (-1 to 1)")
    
    st.markdown('<div class="stock-display">', unsafe_allow_html=True)
    st.markdown(f'<span class="stock-name">{asset_a_name}</span> <span>Return: {mu_A}% | Risk: {sigma_A}%</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="stock-display">', unsafe_allow_html=True)
    st.markdown(f'<span class="stock-name">{asset_b_name}</span> <span>Return: {mu_B}% | Risk: {sigma_B}%</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Card for visualization controls
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Visualization Controls</div>', unsafe_allow_html=True)
    
    # Resolution slider
    resolution = st.select_slider(
        "Points on frontier:",
        options=["Low (50)", "Medium (100)", "High (200)", "Very High (500)"],
        value="High (200)",
        help="Higher resolution shows more data points on the frontier curve"
    )
    
    resolution_points = {
        "Low (50)": 50, 
        "Medium (100)": 100, 
        "High (200)": 200,
        "Very High (500)": 500
    }
    num_points = resolution_points[resolution]
    
    # Plotting options
    show_weights = st.checkbox("Show portfolio weights", value=True,
                              help="Display the weight of Asset A at different points on the frontier")
    show_cml = st.checkbox("Show Capital Market Line", value=False,
                          help="Display the Capital Market Line from risk-free rate to tangency portfolio")
    
    if show_cml:
        rf_rate = st.slider("Risk-free rate (%)", 
                           min_value=0.0, max_value=10.0, value=2.0, step=0.1,
                           help="Annual risk-free interest rate")
    else:
        rf_rate = 2.0  # Default value when not showing CML
    
    # Reference points
    show_reference_portfolios = st.checkbox("Show reference portfolios", value=True,
                                          help="Display markers for special portfolios like equal-weight")
    
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
rf_rate /= 100

# Generate parametric minimum-variance frontier
alphas = np.linspace(0, 1, num_points)
portfolio_returns = alphas * mu_A + (1 - alphas) * mu_B
portfolio_stds = np.sqrt(
    alphas**2 * sigma_A**2 +
    (1 - alphas)**2 * sigma_B**2 +
    2 * alphas * (1 - alphas) * rho * sigma_A * sigma_B
)

# For portfolio weights visualization
weights_A = alphas
weights_B = 1 - alphas

# Compute Minimum Variance Portfolio (MVP)
denominator = sigma_A**2 + sigma_B**2 - 2 * rho * sigma_A * sigma_B

# Handle division by zero
if abs(denominator) < 1e-10:  # Numerical stability check
    w_star = 0.5  # Use equal weighting for perfect correlation
else:
    w_star = (sigma_B**2 - rho * sigma_A * sigma_B) / denominator

w_star = max(0, min(w_star, 1))  # Ensure no short sales
w_star_B = 1 - w_star

mvp_return = w_star * mu_A + w_star_B * mu_B

# Correctly calculate MVP standard deviation
mvp_variance = (w_star**2 * sigma_A**2 + 
                w_star_B**2 * sigma_B**2 + 
                2 * w_star * w_star_B * rho * sigma_A * sigma_B)

# Check if variance is non-negative before calculating standard deviation
if mvp_variance >= 0:
    mvp_std = np.sqrt(mvp_variance)
else:
    mvp_std = 0  # Set to 0 if variance is negative (theoretical minimum)

# Calculate equal-weight portfolio (50/50)
eq_weight_return = 0.5 * mu_A + 0.5 * mu_B
eq_weight_variance = (0.5**2 * sigma_A**2 + 
                     0.5**2 * sigma_B**2 + 
                     2 * 0.5 * 0.5 * rho * sigma_A * sigma_B)
eq_weight_std = np.sqrt(eq_weight_variance)

# Calculate the tangency portfolio (if using risk-free rate)
if abs(mvp_std) > 1e-10:  # Avoid division by zero
    # Calculate Sharpe ratios for all portfolios on the frontier
    sharpe_ratios = (portfolio_returns - rf_rate) / portfolio_stds
    # Find the portfolio with maximum Sharpe ratio
    max_sharpe_idx = np.nanargmax(sharpe_ratios)
    tangency_return = portfolio_returns[max_sharpe_idx]
    tangency_std = portfolio_stds[max_sharpe_idx]
    tangency_weight_A = alphas[max_sharpe_idx]
    tangency_weight_B = 1 - tangency_weight_A
else:
    tangency_return = mvp_return
    tangency_std = mvp_std
    tangency_weight_A = w_star
    tangency_weight_B = w_star_B

# Split into efficient and inefficient frontiers
efficient_mask = portfolio_returns >= mvp_return  # Keep only points above or equal to MVP's return
efficient_returns = portfolio_returns[efficient_mask]
efficient_stds = portfolio_stds[efficient_mask]
efficient_weights_A = weights_A[efficient_mask]
efficient_weights_B = weights_B[efficient_mask]

inefficient_returns = portfolio_returns[~efficient_mask]
inefficient_stds = portfolio_stds[~efficient_mask]
inefficient_weights_A = weights_A[~efficient_mask]
inefficient_weights_B = weights_B[~efficient_mask]

with col2:
    # Card for the efficient frontier plot
    st.markdown('<div class="card plot-container">', unsafe_allow_html=True)
    
    # Create a plotly figure
    fig = go.Figure()
    
    # Add efficient frontier
    hovertemplate = f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>{asset_a_name}: %{{customdata[0]:.1f}}%<br>{asset_b_name}: %{{customdata[1]:.1f}}%<extra></extra>'
    
    # Add the efficient frontier
    fig.add_trace(go.Scatter(
        x=efficient_stds * 100,
        y=efficient_returns * 100,
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='#2563EB', width=3),
        customdata=np.vstack((efficient_weights_A * 100, efficient_weights_B * 100)).T,
        hovertemplate=hovertemplate
    ))
    
    # Add the inefficient frontier with dashed line
    fig.add_trace(go.Scatter(
        x=inefficient_stds * 100,
        y=inefficient_returns * 100,
        mode='lines',
        name='Inefficient Frontier',
        line=dict(color='#2563EB', width=3, dash='dash'),
        customdata=np.vstack((inefficient_weights_A * 100, inefficient_weights_B * 100)).T,
        hovertemplate=hovertemplate
    ))
    
    # Add individual assets
    fig.add_trace(go.Scatter(
        x=[sigma_A * 100],
        y=[mu_A * 100],
        mode='markers',
        marker=dict(size=12, color='#10B981', symbol='square'),
        name=asset_a_name,
        hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>Asset: {asset_a_name}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[sigma_B * 100],
        y=[mu_B * 100],
        mode='markers',
        marker=dict(size=12, color='#F97316', symbol='square'),
        name=asset_b_name,
        hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>Asset: {asset_b_name}<extra></extra>'
    ))
    
    # Add minimum variance portfolio point
    fig.add_trace(go.Scatter(
        x=[mvp_std * 100],
        y=[mvp_return * 100],
        mode='markers',
        marker=dict(size=14, color='#EF4444', symbol='star'),
        name='Minimum Variance Portfolio',
        hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>{asset_a_name}: {w_star*100:.1f}%<br>{asset_b_name}: {(1-w_star)*100:.1f}%<extra></extra>'
    ))
    
    # Add reference portfolios if requested
    if show_reference_portfolios:
        # Equal-weight portfolio
        fig.add_trace(go.Scatter(
            x=[eq_weight_std * 100],
            y=[eq_weight_return * 100],
            mode='markers',
            marker=dict(size=10, color='#A855F7', symbol='circle'),
            name='Equal-Weight Portfolio (50/50)',
            hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>{asset_a_name}: 50.0%<br>{asset_b_name}: 50.0%<extra></extra>'
        ))
    
    # Add CML if requested
    if show_cml:
        # Add risk-free point
        fig.add_trace(go.Scatter(
            x=[0],
            y=[rf_rate * 100],
            mode='markers',
            marker=dict(size=10, color='#0D9488', symbol='diamond'),
            name=f'Risk-Free Rate ({rf_rate*100:.1f}%)',
            hovertemplate='Risk: 0.00%<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        # Add tangency portfolio
        fig.add_trace(go.Scatter(
            x=[tangency_std * 100],
            y=[tangency_return * 100],
            mode='markers',
            marker=dict(size=12, color='#FB923C', symbol='diamond'),
            name='Tangency Portfolio',
            hovertemplate=f'Risk: %{{x:.2f}}%<br>Return: %{{y:.2f}}%<br>{asset_a_name}: {tangency_weight_A*100:.1f}%<br>{asset_b_name}: {tangency_weight_B*100:.1f}%<extra></extra>'
        ))
        
        # Add CML line
        # Extend the line beyond the tangency portfolio for visualization
        max_std = max(sigma_A, sigma_B) * 1.2
        cml_std = np.array([0, max_std])
        cml_return = rf_rate + (tangency_return - rf_rate) / tangency_std * cml_std
        
        fig.add_trace(go.Scatter(
            x=cml_std * 100,
            y=cml_return * 100,
            mode='lines',
            line=dict(color='#FB923C', width=2),
            name='Capital Market Line',
            hovertemplate='Risk: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        ))
    
    # Add colorful weights gradient if requested
    if show_weights:
        # Create a continuous color scale
        norm_weights = (alphas - min(alphas)) / (max(alphas) - min(alphas))
        colorscale = [[i, f'rgb({int(255*(1-w))}, {int(150*w+50)}, {int(255*w)})'
                      ] for i, w in zip(norm_weights, norm_weights)]
        
        fig.add_trace(go.Scatter(
            x=portfolio_stds * 100,
            y=portfolio_returns * 100,
            mode='markers',
            marker=dict(
                size=6,
                color=alphas,
                colorscale='Viridis',
                colorbar=dict(
                    title=f'{asset_a_name} Weight',
                    tickvals=[0, 0.25, 0.5, 0.75, 1],
                    ticktext=['0%', '25%', '50%', '75%', '100%']
                ),
                showscale=True
            ),
            name='Portfolio Weights',
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Customize the layout
    max_std = max(max(efficient_stds), max(inefficient_stds, default=0), sigma_A, sigma_B) * 100
    min_return = min(min(efficient_returns), min(inefficient_returns, default=mu_A), mu_A, mu_B) * 100
    max_return = max(max(efficient_returns), max(inefficient_returns, default=mu_B), mu_A, mu_B) * 100
    
    # Add padding to the axes
    x_padding = max_std * 0.1
    y_padding = (max_return - min_return) * 0.1
    
    fig.update_layout(
        title=dict(
            text="Two-Asset Efficient Frontier",
            font=dict(size=24, family="Arial, sans-serif", color="#1E3A8A"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Risk (Standard Deviation, %)",
            tickformat='.1f',
            gridcolor='rgba(230, 230, 230, 0.8)',
            range=[0, max_std + x_padding]
        ),
        yaxis=dict(
            title="Expected Return (%)",
            tickformat='.1f',
            gridcolor='rgba(230, 230, 230, 0.8)',
            range=[min_return - y_padding, max_return + y_padding]
        ),
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
        height=600,
        margin=dict(l=60, r=40, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results card
    st.markdown('<div class="results-box">', unsafe_allow_html=True)
    
    # Create a grid for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{mvp_std*100:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Minimum Risk (MVP)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{mvp_return*100:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">MVP Return</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{w_star*100:.1f}% / {(1-w_star)*100:.1f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">MVP Weights ({asset_a_name}/{asset_b_name})</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if show_cml:
        st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            sharpe = (tangency_return - rf_rate) / tangency_std if tangency_std > 0 else 0
            st.markdown(f'<div class="metric-value">{sharpe:.3f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Max Sharpe Ratio</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tangency_return*100:.2f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Tangency Return</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tangency_weight_A*100:.1f}% / {tangency_weight_B*100:.1f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-label">Tangency Weights ({asset_a_name}/{asset_b_name})</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Educational content
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
    
    if show_cml:
        with st.expander("📘 Understanding the Capital Market Line", expanded=False):
            st.markdown("""
            ### Capital Market Line (CML)
            
            The CML represents the set of efficient portfolios formed by combining the risk-free asset with the tangency portfolio.
            
            **Tangency Portfolio**: The portfolio on the efficient frontier that, when connected to the risk-free rate, creates the line with the steepest slope.
            
            **Sharpe Ratio**: Measures excess return per unit of risk.
            
            Sharpe Ratio = (R_p - R_f) / σ_p
            
            where:
            - R_p = Portfolio return
            - R_f = Risk-free rate
            - σ_p = Portfolio standard deviation
            
            The tangency portfolio has the highest Sharpe ratio among all portfolios on the efficient frontier.
            """)

# Footer
st.markdown('<div class="footer">Two-Asset Efficient Frontier Visualizer | For educational purposes</div>', unsafe_allow_html=True)
