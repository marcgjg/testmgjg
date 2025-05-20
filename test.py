import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ─────────────────  PAGE CONFIG  ───────────────── #
st.set_page_config(page_title="Capital Structure and WACC",
                   page_icon="📊", layout="wide")
st.markdown(
    '<h1 style="text-align:center; color:#1E3A8A;">📊 Capital Structure & WACC</h1>',
    unsafe_allow_html=True,
)

# ℹ️  ABOUT PANEL ---------------------------------- #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This interactive app lets you see how a firm’s **weighted average cost of capital (WACC)**
        changes as you vary its capital structure under **Modigliani–Miller with corporate taxes**
        (no financial-distress costs).

        *Key idea:* the tax deductibility of interest pushes WACC down as debt rises,  
        while the required return on equity rises because equity becomes riskier.
        """,
        unsafe_allow_html=True,
    )

    # show the MM equations with proper LaTeX
    st.latex(r"R_e = R_u + \bigl(R_u - R_d\bigr)\frac{D}{E}\,(1-T_c)")
    st.latex(r"\text{WACC} = R_u\;\bigl(1 - T_c \tfrac{D}{V}\bigr)")

    st.markdown(
        """
        Use the sliders in the sidebar to set the unlevered cost of equity, cost of debt,
        the tax rate, and your chosen debt ratio.  
        The plot highlights the debt level where WACC is at its minimum in this simplified setting.
        """,
        unsafe_allow_html=True,
    )

# ─────────── SIDEBAR INPUTS ─────────── #
sb = st.sidebar
sb.header("Core inputs")

r_u_percent = sb.slider("Unlevered cost of equity  rᵤ  (%)", 0.0, 20.0, 10.0, 0.1)
r_d_percent = sb.slider("Cost of debt  r_d  (%)",         0.0, 15.0,  5.0, 0.1)
T_c_percent = sb.slider("Corporate tax rate  T꜀  (%)",    0.0, 50.0, 25.0, 0.5)

sb.markdown("---")
selected_debt = sb.slider("Debt ratio (% of total capital)", 0, 100, 50, 1)

# ─────────── COMPUTATIONS ─────────── #
T       = T_c_percent / 100.0
d_pct   = np.arange(0, 101)        # 0 % … 100 %
d_frac  = d_pct / 100.0

# WACC (in %) under MM with taxes (no distress costs)
WACC_percent = r_u_percent * (1 - T * d_frac)

min_idx     = int(np.argmin(WACC_percent))
opt_d_pct   = int(d_pct[min_idx])
min_wacc    = WACC_percent[min_idx]

wacc_selected = r_u_percent * (1 - T * (selected_debt / 100.0))

# ─────────── PLOT ─────────── #
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=d_pct,
        y=WACC_percent,
        mode="lines",
        name="WACC",
        line=dict(color="black", width=3),
    )
)

fig.add_vline(
    x=opt_d_pct,
    line=dict(color="grey", dash="dash"),
    annotation=dict(text="Optimal debt", textangle=-90, showarrow=False, yshift=10),
)

fig.update_layout(
    xaxis_title="Debt ratio (%)",
    yaxis_title="WACC (%)",
    hovermode="x unified",
    font=dict(size=16),
    height=600,
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    margin=dict(l=80, r=80, t=30, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# ───────────  DOWNLOAD SVG BUTTON  ─────────── #
svg_bytes = fig.to_image(format="svg")      # requires plotly-kaleido
st.download_button("⬇️ Download SVG", svg_bytes,
                   file_name="wacc_plot.svg", mime="image/svg+xml")

# ─────────── SUMMARY ─────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct}% debt**, giving minimum **WACC = {min_wacc:.2f}%**"
)
st.write(f"At {selected_debt}% debt, WACC = **{wacc_selected:.2f}%**.")
