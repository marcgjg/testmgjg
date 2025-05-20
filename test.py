import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ─────────────────  PAGE CONFIG  ───────────────── #
st.set_page_config(page_title="Capital Structure and WACC",
                   page_icon="📊", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">📊 Capital Structure & WACC</h1>',
            unsafe_allow_html=True)

# ℹ️  ABOUT PANEL ---------------------------------- #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This interactive app allows you to explore how the **weighted average cost of capital (WACC)** changes with a firm's capital structure under the assumptions of **Modigliani–Miller with corporate taxes** (no financial distress costs).
        
        As leverage increases, the required return on equity rises (due to higher risk) according to **R<sub>e</sub> = R<sub>u</sub> + (R<sub>u</sub> – R<sub>d</sub>) (D/E) (1 – T<sub>c</sub>)**:contentReference[oaicite:0]{index=0}. Meanwhile, the tax deductibility of interest causes the **WACC** to decline as the debt ratio increases:contentReference[oaicite:1]{index=1}. In this simplified scenario (ignoring distress costs), the WACC is minimized at 100% debt financing, reflecting the tax benefit of debt.
        
        *Use the sliders in the sidebar to adjust the unlevered cost of equity, cost of debt, tax rate, and the debt ratio. The plot will update to show the WACC curve, with a dashed line indicating the debt percentage that yields the minimum WACC.*
        """,
        unsafe_allow_html=True
    )

# ─────────── SIDEBAR INPUTS ─────────── #
sb = st.sidebar
sb.header("Core inputs")

# Slider inputs for model parameters
r_u_percent = sb.slider("Unlevered cost of equity  rᵤ  (%)", 0.0, 20.0, 10.0, 0.1)
r_d_percent = sb.slider("Cost of debt  r_d  (%)", 0.0, 15.0, 5.0, 0.1)
T_c_percent = sb.slider("Corporate tax rate  T꜀  (%)", 0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
selected_debt = sb.slider("Debt ratio (% of total capital)", 0, 100, 50, 1)

# ─────────── COMPUTATIONS ─────────── #
# Convert percentages to fractions for calculations
T = T_c_percent / 100.0
d_pct = np.arange(0, 101)               # debt percentage from 0% to 100%
d_frac = d_pct / 100.0                  # fraction of debt in total capital

# Compute WACC for each debt percentage (Modigliani–Miller with taxes formula)
# WACC (in percent) = r_u_percent * (1 – T * debt_fraction)
WACC_percent = r_u_percent * (1 - T * d_frac)

# Identify the minimum WACC and its debt percentage
min_idx = int(np.argmin(WACC_percent))
opt_d_pct = int(d_pct[min_idx])
min_wacc = WACC_percent[min_idx]

# WACC for the selected debt ratio slider
wacc_selected = r_u_percent * (1 - T * (selected_debt / 100.0))

# ─────────── PLOT ─────────── #
fig = go.Figure()
fig.add_trace(go.Scatter(x=d_pct, y=WACC_percent,
                         mode="lines", name="WACC",
                         line=dict(color="black", width=3)))

# Add a vertical dashed line at the optimal debt ratio
fig.add_vline(x=opt_d_pct, line=dict(color="grey", dash="dash"),
              annotation=dict(text="Optimal debt",
                              textangle=-90, showarrow=False, yshift=10))

# Configure plot axes and layout
fig.update_layout(xaxis_title="Debt ratio (%)",
                  yaxis_title="WACC (%)",
                  hovermode="x unified",
                  font=dict(size=16),
                  height=600,
                  legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
                  margin=dict(l=80, r=80, t=30, b=40))

st.plotly_chart(fig, use_container_width=True)

# ───────────  DOWNLOAD SVG BUTTON  ─────────── #
svg_bytes = fig.to_image(format="svg")    # requires plotly kaleido for static image export
st.download_button("⬇️ Download SVG", svg_bytes,
                   file_name="wacc_plot.svg", mime="image/svg+xml")

# ─────────── SUMMARY ─────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct}% debt**, resulting in minimum **WACC = {min_wacc:.2f}%**"
)
# Display current selected debt WACC as additional info
st.write(f"At {selected_debt}% debt, WACC = **{wacc_selected:.2f}%**.")
