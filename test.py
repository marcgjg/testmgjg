import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ────────── PAGE CONFIG ────────── #
st.set_page_config(page_title="Optimal Capital Structure",
                   page_icon="📐", layout="wide")
st.markdown('<h1 style="text-align:center; color:#1E3A8A;">📐 Optimal Capital Structure</h1>',
            unsafe_allow_html=True)

# ────────── SIDEBAR INPUTS ────────── #
sb = st.sidebar
sb.header("Core inputs")

V_U = sb.slider("Unlevered firm value  Vᵤ  (€ million)",
                50.0, 500.0, 200.0, 10.0,
                help="The value of the firm if it were financed entirely with equity (no debt).")
T_c = sb.slider("Corporate tax rate  T꜀  (%)",
                0.0, 50.0, 25.0, 0.5,
                help="The marginal corporate tax rate. Higher rates increase the tax shield benefit of debt.")

sb.markdown("---")
FD_total = sb.slider("PV of distress costs at 100 % debt  (€ million)",
                     0.0, 150.0, 40.0, 1.0,
                     help="The present value of financial distress costs (bankruptcy costs, lost customers, etc.) "
                          "if the firm were 100% debt-financed.")

# ────────── MODEL CONSTANTS ────────── #
BETA_DECAY  = 2.0   # red‑curve peak ≈ 50 % debt
FD_EXPONENT = 2.0
OFFSET      = 7     # spacing for arrows
DIST_GAP    = 3     # extra gap for PV(distress)
INDIGO      = "#6366F1"

# ────────── COMPUTE CURVES ────────── #
d_pct  = np.arange(0, 101)
d_frac = d_pct / 100

pv_tax = (T_c/100) * V_U * d_frac * np.exp(-BETA_DECAY * d_frac)
V_tax  = V_U + pv_tax

pv_fd  = FD_total * d_frac**FD_EXPONENT
V_L    = V_tax - pv_fd

opt_idx   = np.argmax(V_L)
opt_d_pct = int(d_pct[opt_idx])

x_left  = max(0,  opt_d_pct - OFFSET)
x_right = min(100, opt_d_pct + OFFSET)
x_dist  = min(100, x_right + DIST_GAP)

PVTS_top = V_tax[x_left]
VL_top   = V_L[x_right]
VDist_bot, VDist_top = V_L[x_dist], V_tax[x_dist]

# ────────── BUILD FIGURE ────────── #
fig = go.Figure()

fig.add_trace(go.Scatter(x=d_pct, y=V_L,
                         mode="lines", name="V<sub>L</sub> (levered)",
                         line=dict(color="black", width=3)))
fig.add_trace(go.Scatter(x=d_pct, y=V_tax,
                         mode="lines", name="V (tax shield only)",
                         line=dict(color="#d62728", width=2)))

fig.add_hline(y=V_U, line=dict(color=INDIGO, dash="dash"),
              annotation=dict(text="V<sub>U</sub> (unlevered)",
                              showarrow=False, yshift=-18,
                              font=dict(size=12, color=INDIGO)))

fig.add_shape(type="line", x0=opt_d_pct, x1=opt_d_pct,
              y0=0, y1=1, yref="paper",
              line=dict(color="grey", dash="dash"))
# Place "Optimal X% debt" label on the opposite side from "Value of levered firm"
_opt_xanchor = "right" if abs(opt_d_pct - x_right) < 15 else "left"
_opt_xshift  = -6 if _opt_xanchor == "right" else 6
fig.add_annotation(x=opt_d_pct, y=0.02, yref="paper",
                   text=f"Optimal {opt_d_pct}% debt",
                   textangle=-90, showarrow=False,
                   xanchor=_opt_xanchor, yanchor="bottom",
                   xshift=_opt_xshift,
                   font=dict(size=12, color="grey"))

# PV (tax shield) — double-headed arrow (two opposing arrows)
fig.add_annotation(x=x_left, y=PVTS_top,
                   ax=x_left, ay=V_U,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="#d62728")
fig.add_annotation(x=x_left, y=V_U,
                   ax=x_left, ay=PVTS_top,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="#d62728")
fig.add_annotation(x=x_left, y=V_U,
                   text="PV (tax shield)",
                   showarrow=False, font=dict(size=12, color="#d62728"),
                   xanchor="center", yanchor="top", yshift=-6)

# V_L — double-headed arrow (two opposing arrows)
fig.add_annotation(x=x_right, y=VL_top,
                   ax=x_right, ay=V_U,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="black")
fig.add_annotation(x=x_right, y=V_U,
                   ax=x_right, ay=VL_top,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="black")
fig.add_annotation(x=x_right, y=V_U,
                   text="Net gain from debt",
                   showarrow=False, font=dict(size=12, color="black"),
                   xanchor="center", yanchor="top", yshift=-6)

# PV(distress costs) — double-headed arrow (two opposing arrows)
fig.add_annotation(x=x_dist, y=VDist_top,
                   ax=x_dist, ay=VDist_bot,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="grey")
fig.add_annotation(x=x_dist, y=VDist_bot,
                   ax=x_dist, ay=VDist_top,
                   xref="x", yref="y", axref="x", ayref="y",
                   text="", showarrow=True,
                   arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                   arrowcolor="grey")
fig.add_annotation(x=x_dist + 1.5, y=(VDist_bot + VDist_top)/2,
                   text="PV(distress costs)",
                   showarrow=False, font=dict(size=12, color="grey"),
                   xanchor="left", align="left")

fig.update_layout(xaxis_title="Debt as % of Assets",
                  yaxis_title="Firm value (€ million)",
                  hovermode="x unified",
                  font=dict(size=16),
                  height=620,
                  legend=dict(orientation="h", y=-0.25, x=0.5,
                              xanchor="center"),
                  margin=dict(l=80, r=80, t=30, b=40))

# 🚀  Show chart with SVG download built‑in (camera icon)
config = {"toImageButtonOptions": {"format": "svg"}}
st.plotly_chart(fig, use_container_width=True, config=config)

st.markdown(
    f"**Optimal capital structure:** **{opt_d_pct}% debt**, "
    f"levered firm value **€{VL_top:,.1f} million**"
)

with st.expander("Data table"):
    df = pd.DataFrame({
        "Debt %": d_pct,
        "PV Tax Shield": pv_tax,
        "PV Distress Cost": pv_fd,
        "V (Tax only)": V_tax,
        "V Levered": V_L,
    })
    st.dataframe(df.style.format("{:.2f}"),
                 use_container_width=True, height=280)

with st.expander("📐 The trade-off theory — key formulas"):
    st.markdown(r"""
**Static trade-off theory** balances the tax benefit of debt against the costs of financial distress:

$$
V_L = V_U + PV(\text{tax shield}) - PV(\text{distress costs})
$$

| Symbol | Meaning |
|--------|---------|
| $V_L$ | Value of the levered firm |
| $V_U$ | Value of the unlevered firm (all-equity) |
| $PV(\text{tax shield})$ | Present value of interest tax savings |
| $PV(\text{distress costs})$ | Present value of expected bankruptcy / distress costs |

In this app the **tax shield** is modelled with an exponential decay to capture the idea
that the marginal benefit of debt diminishes at high leverage:

$$
PV(\text{tax shield}) = T_c \cdot V_U \cdot \frac{D}{V} \cdot e^{-\beta \, D/V}
$$

and **distress costs** are convex in leverage:

$$
PV(\text{distress costs}) = \overline{FD} \cdot \left(\frac{D}{V}\right)^{\gamma}
$$

where $\overline{FD}$ is the distress cost at 100% debt, $\beta$ controls how fast the tax shield decays, and $\gamma$ controls the convexity of distress costs.

The **optimal capital structure** is the debt ratio $D^*/V$ that maximises $V_L$.
""")

st.markdown(
    '<div style="text-align:center; padding-top:1rem; color:#6B7280;">'
    'Optimal Capital Structure Visualiser | Developed by Prof. Marc Goergen with the help of ChatGPT'
    '</div>',
    unsafe_allow_html=True,
)
