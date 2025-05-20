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

# ℹ️  ABOUT PANEL ──────────────────────────────── #
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This app shows how a firm’s **weighted average cost of capital (WACC)** varies
        with leverage when you account for
        1. the tax benefit of debt (*Modigliani–Miller with taxes*), **and**
        2. the **expected costs of financial distress**, which push the cost of debt up
           as the debt ratio rises.

        **Assumptions**

        * Base (unlevered) cost of equity: \\(R_u\\)
        * Base cost of debt at very low leverage: \\(R_d\\)
        * Corporate tax rate: \\(T_c\\)
        * Extra yield spread that bondholders demand at 100 % debt: *Distress spread*
        * Spread grows with leverage as \\(\\text{spread} = \\text{Distress spread}\;(D/V)^n\\)

        The model therefore uses

        \\[
        \\begin{aligned}
        R_d(D) & = R_d + \\text{spread}(D)                       \\\\[3pt]
        R_e(D) & = R_u + \\bigl(R_u - R_d(D)\\bigr)\\frac{D}{E}(1-T_c) \\\\[3pt]
        \\text{WACC}(D) & = \\tfrac{E}{V} R_e(D) + \\tfrac{D}{V} R_d(D)(1-T_c)
        \\end{aligned}
        \\]

        where \\(D/V\\) is the chosen debt ratio and \\(E/V = 1-D/V\\).
        """,
        unsafe_allow_html=True,
    )

# ─────────── SIDEBAR INPUTS ───────────────────── #
sb = st.sidebar
sb.header("Core inputs")

r_u_percent = sb.slider("Unlevered cost of equity  rᵤ  (%)", 0.0, 20.0, 10.0, 0.1)
r_d_base    = sb.slider("Base cost of debt  r_d  (%)",        0.0, 15.0,  5.0, 0.1)
T_c_percent = sb.slider("Corporate tax rate  T꜀  (%)",        0.0, 50.0, 25.0, 0.5)

sb.markdown("### Financial-distress inputs")
fd_spread   = sb.slider("Extra debt spread at 100 % debt (%-points)",
                        0.0, 20.0, 6.0, 0.1)
fd_exp      = sb.slider("Convexity of spread  n  (1–3)",      1.0, 3.0, 2.0, 0.1)

sb.markdown("---")
selected_debt = sb.slider("Debt ratio (% of total capital)",
                          0, 100, 50, 1)

# ─────────── COMPUTATIONS ─────────────────────── #
T       = T_c_percent / 100.0
d_pct   = np.arange(0, 101)            # 0 … 100 %
d_frac  = d_pct / 100.0                # 0 … 1

# Cost of debt including distress spread
spread_percent = fd_spread * d_frac**fd_exp
R_d = r_d_base + spread_percent

# Avoid division-by-zero when D/V = 1
D_over_E = np.where(d_frac < 1, d_frac / (1 - d_frac + 1e-9), np.inf)

# Cost of equity under MM with the leverage-adjusted R_d
R_e = np.where(
    d_frac < 1,
    r_u_percent + (r_u_percent - R_d) * D_over_E * (1 - T),
    np.nan,                     # undefined at 100 % debt
)

# WACC for each leverage level
WACC_percent = np.where(
    d_frac < 1,
    (1 - d_frac) * R_e + d_frac * R_d * (1 - T),
    R_d * (1 - T),              # when equity → 0
)

# Optimal debt ratio (first global minimum)
min_idx     = int(np.nanargmin(WACC_percent))
opt_d_pct   = int(d_pct[min_idx])
min_wacc    = WACC_percent[min_idx]

# WACC at the debt ratio chosen on the slider
d_sel_frac  = selected_debt / 100.0
r_d_sel     = r_d_base + fd_spread * d_sel_frac**fd_exp
if selected_debt < 100:
    r_e_sel = r_u_percent + (r_u_percent - r_d_sel) * \
              d_sel_frac / (1 - d_sel_frac) * (1 - T)
    wacc_selected = (1 - d_sel_frac) * r_e_sel + d_sel_frac * r_d_sel * (1 - T)
else:                               # 100 % debt
    wacc_selected = r_d_sel * (1 - T)

# ─────────── PLOT ─────────────────────────────── #
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
    annotation=dict(text="Optimal debt", textangle=-90,
                    showarrow=False, yshift=10),
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

# ───────────  DOWNLOAD SVG BUTTON ─────────────── #
svg_bytes = fig.to_image(format="svg")        # needs plotly-kaleido
st.download_button("⬇️ Download SVG", svg_bytes,
                   file_name="wacc_plot.svg", mime="image/svg+xml")

# ─────────── SUMMARY ──────────────────────────── #
st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct}% debt**, "
    f"minimum **WACC = {min_wacc:.2f}%**"
)
st.write(f"At {selected_debt}% debt, WACC = **{wacc_selected:.2f}%**.")
