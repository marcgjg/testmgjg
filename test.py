import streamlit as st
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go

# -----------------------
# Page Set‑up (matches the Industry Game)
# -----------------------
st.set_page_config(
    page_title="NPV & IRR Visualizer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------
# 🔧 Shared Visual Style (adapted from game.py)
# -----------------------
#  Only the CSS / visual layer has been touched – no functional code below this
#  point has been modified.
#
#  • Colour palette & typography now match the matching‑game app
#  • Gradient headline, soft cards, and info / warning boxes share the same
#    look‑and‑feel
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* headline – gradient identical to game.py banner */
        .gradient-header {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg,#667eea 0%,#764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1.2rem;
        }

        /* generic card container, echoing the game.py panels */
        .card {
            background-color: #F8FAFC;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.06);
            margin-bottom: 1.25rem;
        }

        /* section subtitles */
        .subheader {
            font-size: 1.35rem;
            font-weight: 600;
            color: #4F46E5;  /* indigo‑500 */
            margin-bottom: .75rem;
        }

        /* info / warning style blocks – colours mirror game.py */
        .info-box {
            background-color: #E0F2FE;   /* sky‑100 */
            border-left: 4px solid #0EA5E9; /* sky‑500 */
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin-bottom: 1rem;
        }
        .results-box {
            background-color: #DCFCE7;   /* green‑100 */
            border-left: 4px solid #22C55E; /* green‑500 */
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin-top: 1rem;
        }
        .warning-box {
            background-color: #FEF2F2;  /* red‑50 */
            border-left: 4px solid #EF4444; /* red‑500 */
            padding: 1rem;
            border-radius: 0 6px 6px 0;
            margin-top: 1rem;
        }
        /* simple table styling */
        .cf-table th {
            background-color: #EEF2FF; /* indigo‑50 */
            text-align: center;
            padding: .35rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Banner (mirrors progress‑banner in game.py)
st.markdown(
    '<h1 class="gradient-header">📊 NPV and IRR Visualizer</h1>',
    unsafe_allow_html=True,
)

# -------------  
#  TOOL INFO
# -------------
with st.expander("ℹ️ About this tool", expanded=False):
    st.markdown(
        """
        This tool helps you **visualise** the Net Present Value (NPV) and Internal Rate of Return (IRR)
        for any cash‑flow series you provide – now with the same look‑and‑feel as the *Industry Matching Game*.
        """
    )

# Keep session‑state template button untouched
if "use_template" not in st.session_state:
    st.session_state.use_template = False

def set_template():
    st.session_state.use_template = True

# -------------  
#  LAYOUT – same left / right split as before (unchanged logic)
# -------------
col_left, col_right = st.columns([1, 2])

# ---------------------------------------------------------------------------
# LEFT PANEL :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ---------------------------------------------------------------------------
with col_left:
    # ––– Cash‑flow input –––––––––––––––––––––––––––––––––––––––––––––––
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Cash‑Flow Inputs</div>', unsafe_allow_html=True)

    default_cash_flows = "-1000, 300, 400, 500, 600" if st.session_state.use_template else ""
    cash_flow_input = st.text_area(
        "Enter cash flows (comma‑separated):",
        default_cash_flows,
        help="Start with the negative initial outlay, then the inflows",
    )
    if st.session_state.use_template:
        st.session_state.use_template = False

    # validation ‑ unchanged
    try:
        cash_flows = [float(x.strip()) for x in cash_flow_input.split(",")]
        valid_input = True
    except Exception:
        st.markdown(
            '<div class="warning-box">Invalid input. Please enter valid numbers separated by commas.</div>',
            unsafe_allow_html=True,
        )
        valid_input = False

    if st.button("📋 Use Example Template", on_click=set_template):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

    # ––– Cash‑flow table & metrics ––––––––––––––––––––––––––––––––––––
    if valid_input:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Cash‑Flow Summary</div>', unsafe_allow_html=True)

        periods = list(range(len(cash_flows)))
        cf_table = "<table width='100%'><thead><tr><th>Period</th><th>Cash Flow</th></tr></thead><tbody>"
        for i, cf in zip(periods, cash_flows):
            color = "#DC2626" if cf < 0 else "#16A34A" if cf > 0 else "#000000"
            cf_table += f"<tr><td style='text-align:center;'>{i}</td><td style='text-align:right;color:{color};'>€{cf:,.2f}</td></tr>"
        cf_table += "</tbody></table>"
        st.markdown(cf_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        init_investment = cash_flows[0] if cash_flows[0] < 0 else 0
        total_inflows  = sum(cf for cf in cash_flows if cf > 0)
        col1, col2 = st.columns(2)
        col1.metric("Initial Investment", f"€{init_investment:,.2f}")
        col2.metric("Total Inflows", f"€{total_inflows:,.2f}")

    # ––– Discount‑rate settings ––––––––––––––––––––––––––––––––––––––––
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Discount‑Rate Settings</div>', unsafe_allow_html=True)

    discount_rate_range = st.slider(
        "Discount Rate (%) range:", 0, 50, (5, 30)
    )
    min_rate, max_rate = discount_rate_range
    min_rate_dec, max_rate_dec = min_rate / 100, max_rate / 100

    resolution = st.radio(
        "Chart detail:", ["Standard", "High"], index=1, horizontal=True
    )
    num_points = 500 if resolution == "High" else 100
    st.markdown('</div>', unsafe_allow_html=True)

    # ––– Info box ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(
        "NPV = ∑ CFₜ / (1+r)ᵗ  — IRR = r where NPV = 0",
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
#   FUNCTIONS (unchanged) :::::::::::::::::::::::::::::::::::::::::::::::::::
# ---------------------------------------------------------------------------

def compute_npv(cash_flows, r):
    return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))

def find_multiple_irrs(cash_flows, rate_min=1e-4, rate_max=0.9999, precision=1e-4):
    dense_rates = np.linspace(rate_min, rate_max, 10_000)
    dense_npvs  = [compute_npv(cash_flows, r) for r in dense_rates]

    zeroes = []
    for i in range(1, len(dense_npvs)):
        if dense_npvs[i-1] * dense_npvs[i] <= 0:
            lo, hi = dense_rates[i-1], dense_rates[i]
            while hi - lo > precision:
                mid = (lo + hi)/2
                if compute_npv(cash_flows, mid) * compute_npv(cash_flows, lo) <= 0:
                    hi = mid
                else:
                    lo = mid
            zeroes.append((lo+hi)/2)

    sign_changes = sum(
        1 for j in range(1, len(cash_flows)) if cash_flows[j-1]*cash_flows[j] < 0
    )
    if len(zeroes) > 1:
        filtered = [zeroes[0]]
        for irr in zeroes[1:]:
            if min(abs(irr - z) for z in filtered) > 0.01:
                filtered.append(irr)
        zeroes = filtered

    return zeroes, sign_changes

# ---------------------------------------------------------------------------
# RIGHT PANEL :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ---------------------------------------------------------------------------
if valid_input:
    rates = np.linspace(min_rate_dec, max_rate_dec, num_points)
    npv_values = [compute_npv(cash_flows, r) for r in rates]

    irrs, sign_changes = find_multiple_irrs(cash_flows)
    try:
        npf_irr = npf.irr(cash_flows)
        if all(abs(npf_irr - irr) > 0.01 for irr in irrs):
            irrs.append(npf_irr)
    except Exception:
        pass
    irrs.sort()
    irrs_pct = [irr*100 for irr in irrs]

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=rates*100,
                y=npv_values,
                mode="lines",
                line=dict(color="#667eea", width=3),
                name="NPV curve",
                hovertemplate="Rate: %{x:.2f}%<br>NPV: €%{y:.2f}<extra></extra>",
            )
        )
        fig.add_shape(type="line", x0=min_rate, x1=max_rate, y0=0, y1=0,
                      line=dict(color="#666", dash="dash"))

        irr_colors = ["#EF4444", "#8B5CF6", "#F97316", "#10B981"]
        for idx, (irr, irr_pct) in enumerate(zip(irrs, irrs_pct)):
            if min_rate <= irr_pct <= max_rate:
                col = irr_colors[idx % len(irr_colors)]
                fig.add_trace(
                    go.Scatter(x=[irr_pct], y=[0], mode="markers",
                               marker=dict(size=12, color=col),
                               name=f"IRR {idx+1}: {irr_pct:.2f}%"))
                fig.add_shape(type="line", x0=irr_pct, x1=irr_pct,
                              y0=min(npv_values), y1=0,
                              line=dict(color=col, dash="dash"))
                fig.add_annotation(x=irr_pct, y=0, text=f"IRR {idx+1}: {irr_pct:.2f}%",
                                    showarrow=True, arrowhead=2, arrowcolor=col,
                                    ax=0, ay=-40-idx*30, bgcolor="white")

        fig.update_layout(
            title="NPV vs. Discount Rate",
            xaxis_title="Discount Rate (%)",
            yaxis_title="Net Present Value (€)",
            height=600,
            margin=dict(l=60, r=60, t=60, b=100),
            legend=dict(orientation="h", y=-.25, x=.5)
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "toImageButtonOptions": {
                    "format": "svg",
                    "filename": "npv_irr_chart",
                    "width": 1000,
                    "height": 600,
                    "scale": 2,
                }
            },
        )

        # ––– Results ––––––––––––––––––––––––––––––––––––––––––––––––
        if irrs:
            st.markdown('<div class="results-box">', unsafe_allow_html=True)
            if len(irrs) > 1:
                irr_list = ", ".join(f"{p:.2f}%" for p in irrs_pct)
                st.markdown(f"**Multiple IRRs**: {irr_list}")
            else:
                st.markdown(f"**IRR**: {irrs_pct[0]:.2f}%")
            std_rate = .10
            st.markdown(
                f"**NPV @ 10%**: €{compute_npv(cash_flows, std_rate):,.2f}")
            if sign_changes > 1:
                st.markdown(f"Cash‑flow sign‑changes: {sign_changes}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("**No valid IRR found in the selected range.**")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# FOOTER – uniform style like game.py
# ---------------------------------------------------------------------------
st.markdown(
    "<div style='text-align:center;color:#6B7280;font-size:13px;padding:20px;'>"
    "NPV & IRR Visualizer | Developed by Prof. Marc Goergen with ChatGPT, Perplexity, Claude"
    "</div>",
    unsafe_allow_html=True,
)
