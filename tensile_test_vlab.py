"""
Virtual Lab: Tensile Test on Mild Steel Rod
Strength of Materials — Second Year Civil Engineering
IS 432-1 (1982)
Run: streamlit run tensile_test_vlab.py
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Tensile Test Virtual Lab", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.main-header{background:linear-gradient(90deg,#1a3a6b,#2563a8);color:#fff;padding:1rem 1.5rem;border-radius:10px;margin-bottom:1rem;}
.main-header h1{font-size:1.4rem;margin:0;font-weight:700;}
.main-header p{font-size:0.85rem;margin:0.2rem 0 0;opacity:0.85;}
.lo-badge{display:inline-block;background:#dbeafe;color:#1e3a8a;padding:3px 12px;border-radius:20px;font-size:0.78rem;font-weight:600;margin-bottom:0.5rem;}
.instr{background:#f0f9ff;border-left:4px solid #2563a8;padding:0.6rem 1rem;border-radius:0 8px 8px 0;font-size:13px;color:#0c4a6e;margin-bottom:0.75rem;}
.correct{background:#dcfce7;border:1.5px solid #86efac;border-radius:8px;padding:0.6rem 1rem;color:#15803d;font-weight:600;font-size:13px;margin-top:0.5rem;}
.wrong{background:#fee2e2;border:1.5px solid #fca5a5;border-radius:8px;padding:0.6rem 1rem;color:#b91c1c;font-weight:600;font-size:13px;margin-top:0.5rem;}
.obs-box{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:0.75rem 1rem;font-size:13px;margin-top:0.5rem;}
.formula{background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;padding:0.5rem 0.8rem;font-family:monospace;font-size:12px;color:#0c4a6e;margin:4px 0;}
.verdict-pass{background:#dcfce7;border:1.5px solid #86efac;border-radius:8px;padding:0.8rem 1rem;color:#15803d;font-weight:600;margin-top:0.5rem;}
.verdict-fail{background:#fee2e2;border:1.5px solid #fca5a5;border-radius:8px;padding:0.8rem 1rem;color:#b91c1c;font-weight:600;margin-top:0.5rem;}
div[data-testid="stMetricValue"]{font-size:1.4rem!important;}
</style>
""", unsafe_allow_html=True)

def si(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

si('scene', 0); si('dx', 12.4); si('dy', 12.4); si('lc', 70.0)
si('du', 8.0); si('lu', 71.8); si('force_ans', None)
si('utm_stage', 0); si('load_step', 0)

LOAD_DEFORM = [
    (0,0.000),(4,0.009),(8,0.019),(12,0.029),(16,0.039),(20,0.048),
    (24,0.057),(28,0.068),(32,0.077),(36,0.090),(42,0.200),(44,0.400),
    (41,0.700),(41,1.200),(41,2.300),(45,2.900),(48,3.240),(50,3.600),
    (52,4.100),(54,4.620),(56,5.240),(58,6.300),(59,7.200),(58,8.400),
    (55,9.400),(47,10.800)
]

SCENES = ['1.Concept','2.UTM Parts','3.Measure','4.Fix in UTM','5.Apply Load','6.Post-Fracture','7.Calculations','8.IS Code']

with st.sidebar:
    st.markdown("### 🔬 Experiment Scenes")
    for i, s in enumerate(SCENES):
        t = "primary" if st.session_state.scene == i else "secondary"
        if st.button(s, key=f"nav{i}", use_container_width=True, type=t):
            st.session_state.scene = i
    st.divider()
    d1 = (st.session_state.dx + st.session_state.dy) / 2
    lo = round(5 * d1, 2)
    st.metric("d1 avg", f"{d1:.2f} mm")
    st.metric("L0", f"{lo:.2f} mm")

st.markdown("""<div class="main-header">
<h1>🔬 Tensile Test on Mild Steel Rod — Virtual Lab</h1>
<p>Strength of Materials | Second Year Civil Engineering | IS 432-1 (1982)</p>
</div>""", unsafe_allow_html=True)

sc = st.session_state.scene

# SCENE 0 — CONCEPT
if sc == 0:
    st.markdown('<div class="lo-badge">Scene 1 · LO1 · Remember — Tensile Force Concept</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Look at the three force diagrams below. Click the one that shows TENSILE force acting on a rod.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    def force_fig(title, arrow_left_out, arrow_right_out, color):
        fig = go.Figure()
        fig.add_shape(type="rect", x0=1.5, x1=6.5, y0=0.35, y1=0.65, fillcolor="#6b7280", line_color="#374151")
        ax1 = 0.3 if arrow_left_out else 2.5
        ax2 = 7.7 if arrow_right_out else 5.5
        fig.add_annotation(x=1.5, y=0.5, ax=ax1, ay=0, xref="x", yref="y", axref="x", ayref="y",
                           arrowhead=2, arrowsize=2, arrowcolor=color, arrowwidth=3)
        fig.add_annotation(x=6.5, y=0.5, ax=ax2, ay=0, xref="x", yref="y", axref="x", ayref="y",
                           arrowhead=2, arrowsize=2, arrowcolor=color, arrowwidth=3)
        fig.add_annotation(x=0.5, y=0.5, text="F", showarrow=False, font=dict(size=16, color=color))
        fig.add_annotation(x=7.5, y=0.5, text="F", showarrow=False, font=dict(size=16, color=color))
        fig.update_layout(height=130, margin=dict(l=5, r=5, t=30, b=5),
                          title=dict(text=title, font=dict(size=13, color="#1f2328"), x=0.5),
                          xaxis=dict(visible=False, range=[0, 8]),
                          yaxis=dict(visible=False, range=[0, 1]),
                          plot_bgcolor="white", paper_bgcolor="white")
        return fig

    with col1:
        st.plotly_chart(force_fig("Compression (inward)", False, False, "#dc2626"), use_container_width=True)
        if st.button("Select Compression", use_container_width=True, key="sel_comp"):
            st.session_state.force_ans = "compression"
    with col2:
        st.plotly_chart(force_fig("Tension / Tensile (outward)", True, True, "#2563a8"), use_container_width=True)
        if st.button("Select Tension", use_container_width=True, key="sel_tens"):
            st.session_state.force_ans = "tension"
    with col3:
        fig3 = go.Figure()
        fig3.add_shape(type="rect", x0=1.5, x1=6.5, y0=0.35, y1=0.65, fillcolor="#6b7280", line_color="#374151")
        fig3.add_annotation(x=4, y=0.65, ax=4, ay=0.95, xref="x", yref="y", axref="x", ayref="y",
                            arrowhead=2, arrowsize=2, arrowcolor="#f59e0b", arrowwidth=3)
        fig3.add_annotation(x=4, y=0.35, ax=4, ay=0.05, xref="x", yref="y", axref="x", ayref="y",
                            arrowhead=2, arrowsize=2, arrowcolor="#f59e0b", arrowwidth=3)
        fig3.update_layout(height=130, margin=dict(l=5, r=5, t=30, b=5),
                           title=dict(text="Shear (transverse)", font=dict(size=13), x=0.5),
                           xaxis=dict(visible=False, range=[0, 8]),
                           yaxis=dict(visible=False, range=[0, 1]),
                           plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)
        if st.button("Select Shear", use_container_width=True, key="sel_shear"):
            st.session_state.force_ans = "shear"

    if st.session_state.force_ans == "tension":
        st.markdown('<div class="correct">Correct! Tensile force pulls the rod OUTWARD from both ends causing elongation along the longitudinal axis.</div>', unsafe_allow_html=True)
        st.button("Next: Learn UTM Parts", on_click=lambda: st.session_state.update(scene=1), type="primary")
    elif st.session_state.force_ans in ["compression", "shear"]:
        st.markdown('<div class="wrong">Wrong! Tensile force acts OUTWARD (pulling). Select the Tension diagram.</div>', unsafe_allow_html=True)

# SCENE 1 — UTM PARTS
elif sc == 1:
    st.markdown('<div class="lo-badge">Scene 2 · LO1 · Remember — Identify UTM Parts</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">The Universal Testing Machine (UTM) is shown below. Click each part button to learn what it does in the experiment.</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_shape(type="rect", x0=0.5, x1=9.5, y0=0, y1=0.7, fillcolor="#94a3b8", line_color="#475569", line_width=2)
    fig.add_annotation(x=5, y=0.35, text="LOWER BEAM", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=0.5, x1=9.5, y0=9.3, y1=10, fillcolor="#94a3b8", line_color="#475569", line_width=2)
    fig.add_annotation(x=5, y=9.65, text="UPPER BEAM", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=0.5, x1=1.5, y0=0.7, y1=9.3, fillcolor="#cbd5e1", line_color="#94a3b8")
    fig.add_shape(type="rect", x0=8.5, x1=9.5, y0=0.7, y1=9.3, fillcolor="#cbd5e1", line_color="#94a3b8")
    fig.add_shape(type="rect", x0=1.5, x1=8.5, y0=4.5, y1=5.2, fillcolor="#64748b", line_color="#334155", line_width=2)
    fig.add_annotation(x=5, y=4.85, text="MIDDLE BEAM (moves up/down)", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=4.6, x1=5.4, y0=0.7, y1=9.3, fillcolor="#f59e0b", line_color="#b45309", line_width=2)
    fig.add_annotation(x=6.5, y=5.0, text="MS Rod (Specimen)", showarrow=True, ax=-0.8, ay=0,
                       font=dict(size=9, color="#b45309"), arrowcolor="#b45309", arrowwidth=1.5)
    fig.add_shape(type="rect", x0=0, x1=1.5, y0=4.6, y1=5.1, fillcolor="#6366f1", line_color="#4338ca", line_width=2)
    fig.add_annotation(x=0.75, y=4.85, text="4X", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=8.5, x1=10, y0=8.7, y1=9.2, fillcolor="#8b5cf6", line_color="#6d28d9", line_width=2)
    fig.add_annotation(x=9.25, y=8.95, text="2X", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=6, x1=8.5, y0=1.0, y1=3.8, fillcolor="#1e293b", line_color="#0f172a", line_width=2)
    fig.add_annotation(x=7.25, y=3.5, text="CONTROL PANEL", showarrow=False, font=dict(size=8, color="#94a3b8"))
    fig.add_shape(type="circle", x0=6.3, x1=6.9, y0=2.7, y1=3.3, fillcolor="#22c55e", line_color="#15803d")
    fig.add_annotation(x=6.6, y=3.0, text="S", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
    fig.add_shape(type="circle", x0=7.2, x1=7.8, y0=2.7, y1=3.3, fillcolor="#3b82f6", line_color="#1d4ed8")
    fig.add_annotation(x=7.5, y=3.0, text="UP", showarrow=False, font=dict(size=8, color="#fff", family="Arial Black"))
    fig.add_shape(type="circle", x0=6.3, x1=6.9, y0=1.8, y1=2.4, fillcolor="#dc2626", line_color="#991b1b")
    fig.add_annotation(x=6.6, y=2.1, text="P", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
    fig.add_shape(type="circle", x0=7.2, x1=7.8, y0=1.8, y1=2.4, fillcolor="#2563a8", line_color="#1e3a8a")
    fig.add_annotation(x=7.5, y=2.1, text="L", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
    fig.add_shape(type="rect", x0=6.2, x1=8.3, y0=1.05, y1=1.7, fillcolor="#0f172a", line_color="#1e293b")
    fig.add_annotation(x=7.25, y=1.38, text="F: 0   CHT: 0", showarrow=False, font=dict(size=9, color="#22c55e", family="Courier New"))
    fig.update_layout(height=420, margin=dict(l=20, r=80, t=10, b=10),
                      xaxis=dict(visible=False, range=[-0.5, 11]),
                      yaxis=dict(visible=False, range=[-0.5, 10.5]),
                      plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Click a part to learn what it does:")
    parts = {
        "Upper Beam": "Fixed top beam — holds the UPPER jaw (2X handle) that grips the TOP of the MS rod.",
        "Middle Beam": "Movable beam — moves UP using hydraulic pressure, pulling the rod until fracture.",
        "Lower Beam": "Fixed base beam — holds the LOWER jaw (4X handle) gripping the BOTTOM of the rod.",
        "4X Handle": "Tighten clockwise to lock MS rod into the LOWER (middle beam) jaw first.",
        "2X Handle": "Tighten clockwise to lock MS rod into the UPPER beam jaw after pressing UP button.",
        "P Valve (red)": "Pressure Valve — open it (turn red) to allow hydraulic fluid to build pressure.",
        "L Valve (blue)": "Load Valve — open it to apply tensile load on the rod. Rotate to start loading.",
        "S Button (green)": "START button — press to start the hydraulic pump before opening load valve.",
    }
    cols = st.columns(4)
    for i, (name, _) in enumerate(parts.items()):
        with cols[i % 4]:
            if st.button(name, use_container_width=True, key=f"part{i}"):
                st.session_state['utm_part_sel'] = name
    if 'utm_part_sel' in st.session_state and st.session_state.utm_part_sel in parts:
        nm = st.session_state.utm_part_sel
        st.markdown(f'<div class="correct">🔩 <b>{nm}</b> — {parts[nm]}</div>', unsafe_allow_html=True)

    st.button("Next: Measure Specimen", on_click=lambda: st.session_state.update(scene=2), type="primary")

# SCENE 2 — MEASURE
elif sc == 2:
    st.markdown('<div class="lo-badge">Scene 3 · LO2 · Apply — Measure Diameter with Vernier Caliper</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Move the slider to close the Vernier caliper jaws on the MS rod. Measure in X direction, then rotate 90 degrees and measure in Y direction.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("**Step 1 — Measurement in X-direction**")
        dx = st.slider("Close caliper jaws on rod (X direction) mm", 10.0, 15.0, st.session_state.dx, 0.2, key="dx_sl")
        st.session_state.dx = dx

        fig = go.Figure()
        rod_r = dx / 2
        theta = np.linspace(0, 2 * np.pi, 80)
        fig.add_trace(go.Scatter(x=rod_r * np.cos(theta), y=rod_r * np.sin(theta),
                                 fill='toself', fillcolor='#f59e0b',
                                 line=dict(color='#b45309', width=2), showlegend=False))
        fig.add_shape(type="rect", x0=-rod_r - 2.5, x1=-rod_r, y0=-0.5, y1=0.5, fillcolor="#3b82f6", line_color="#1d4ed8", line_width=2)
        fig.add_shape(type="rect", x0=rod_r, x1=rod_r + 2.5, y0=-0.5, y1=0.5, fillcolor="#3b82f6", line_color="#1d4ed8", line_width=2)
        fig.add_shape(type="rect", x0=-rod_r - 2.5, x1=-rod_r - 0.3, y0=-1.5, y1=1.5, fillcolor="#93c5fd", line_color="#3b82f6")
        fig.add_shape(type="rect", x0=rod_r + 0.3, x1=rod_r + 2.5, y0=-1.5, y1=1.5, fillcolor="#93c5fd", line_color="#3b82f6")
        fig.add_annotation(x=-rod_r, y=-2.0, ax=rod_r, ay=-2.0, xref="x", yref="y", axref="x", ayref="y",
                           arrowhead=2, arrowcolor="#dc2626", arrowwidth=2)
        fig.add_annotation(x=rod_r, y=-2.0, ax=-rod_r, ay=-2.0, xref="x", yref="y", axref="x", ayref="y",
                           arrowhead=2, arrowcolor="#dc2626", arrowwidth=2)
        fig.add_annotation(x=0, y=-2.6, text=f"dx = {dx:.1f} mm", showarrow=False, font=dict(size=13, color="#dc2626"))
        fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis=dict(visible=False, range=[-10, 10], scaleanchor="y"),
                          yaxis=dict(visible=False, range=[-3.5, 3.5]),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Step 2 — Rotate caliper 90 degrees — Y-direction**")
        dy = st.slider("Close caliper jaws on rod (Y direction) mm", 10.0, 15.0, st.session_state.dy, 0.2, key="dy_sl")
        st.session_state.dy = dy

    with col2:
        d1 = (dx + dy) / 2
        lo = round(5 * d1, 2)
        st.markdown("**Observation Table — Initial Diameter**")
        st.markdown(f"""<div class="obs-box">
        <table style="width:100%;font-size:13px;border-collapse:collapse;">
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">dx (X direction)</td><td><b>{dx:.1f} mm</b></td></tr>
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">dy (Y direction)</td><td><b>{dy:.1f} mm</b></td></tr>
        <tr style="background:#dbeafe;"><td style="padding:5px;"><b>d1 = (dx+dy)/2</b></td><td><b>{d1:.2f} mm</b></td></tr>
        </table></div>""", unsafe_allow_html=True)

        st.markdown("**Gauge Length**")
        st.markdown(f'<div class="formula">L0 = 5 x d1 = 5 x {d1:.2f} = <b>{lo:.2f} mm</b></div>', unsafe_allow_html=True)
        st.info(f"Mark gauge length {lo:.2f} mm on the rod using the marking pin before fixing in UTM.")

        st.markdown("**Parallel Length (Lc)**")
        lc = st.slider("Measure Lc with scale (mm)", 50.0, 90.0, st.session_state.lc, 1.0)
        st.session_state.lc = lc
        st.markdown(f"Lc = **{lc:.0f} mm**")

    st.button("Next: Fix Rod in UTM", on_click=lambda: st.session_state.update(scene=3), type="primary")

# SCENE 3 — FIX ROD IN UTM (animated steps)
elif sc == 3:
    st.markdown('<div class="lo-badge">Scene 4 · LO2 · Apply — Fix MS Rod in UTM Step by Step</div>', unsafe_allow_html=True)

    stage = st.session_state.utm_stage

    def draw_utm(stage):
        fig = go.Figure()
        # Lower beam
        fig.add_shape(type="rect", x0=0.5, x1=9.5, y0=0, y1=0.7, fillcolor="#94a3b8", line_color="#475569", line_width=2)
        fig.add_annotation(x=5, y=0.35, text="LOWER BEAM", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
        # Upper beam
        fig.add_shape(type="rect", x0=0.5, x1=9.5, y0=9.3, y1=10, fillcolor="#94a3b8", line_color="#475569", line_width=2)
        fig.add_annotation(x=5, y=9.65, text="UPPER BEAM", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
        # Columns
        fig.add_shape(type="rect", x0=0.5, x1=1.5, y0=0.7, y1=9.3, fillcolor="#cbd5e1", line_color="#94a3b8")
        fig.add_shape(type="rect", x0=8.5, x1=9.5, y0=0.7, y1=9.3, fillcolor="#cbd5e1", line_color="#94a3b8")
        # Middle beam
        mid_y = 4.8 if stage >= 2 else 3.0
        fig.add_shape(type="rect", x0=1.5, x1=8.5, y0=mid_y, y1=mid_y + 0.7, fillcolor="#64748b", line_color="#334155", line_width=2)
        fig.add_annotation(x=5, y=mid_y + 0.35, text="MIDDLE BEAM", showarrow=False, font=dict(size=8, color="#fff", family="Arial Black"))
        # 4X handle
        h4c = "#22c55e" if stage >= 1 else "#6366f1"
        fig.add_shape(type="rect", x0=0, x1=1.5, y0=mid_y + 0.1, y1=mid_y + 0.6, fillcolor=h4c, line_color="#4338ca", line_width=2)
        fig.add_annotation(x=0.75, y=mid_y + 0.35, text="4X", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
        # 2X handle
        h2c = "#22c55e" if stage >= 3 else "#8b5cf6"
        fig.add_shape(type="rect", x0=8.5, x1=10, y0=8.7, y1=9.2, fillcolor=h2c, line_color="#6d28d9", line_width=2)
        fig.add_annotation(x=9.25, y=8.95, text="2X", showarrow=False, font=dict(size=9, color="#fff", family="Arial Black"))
        # MS Rod
        if stage == 0:
            # Rod outside — to the right
            fig.add_shape(type="rect", x0=11, x1=11.8, y0=2, y1=5, fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            fig.add_annotation(x=11.4, y=5.4, text="MS Rod", showarrow=False, font=dict(size=9, color="#b45309"))
            fig.add_annotation(x=9.5, y=3.5, text="Drag rod\ninto jaw", showarrow=True, ax=1.3, ay=0,
                               font=dict(size=9, color="#dc2626"), arrowcolor="#dc2626", arrowwidth=1.5)
        elif stage == 1:
            # Rod in lower jaw, not upper
            fig.add_shape(type="rect", x0=4.6, x1=5.4, y0=0.7, y1=mid_y, fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            fig.add_shape(type="rect", x0=4.3, x1=4.6, y0=mid_y - 0.4, y1=mid_y, fillcolor="#475569", line_color="#1e293b")
            fig.add_shape(type="rect", x0=5.4, x1=5.7, y0=mid_y - 0.4, y1=mid_y, fillcolor="#475569", line_color="#1e293b")
            fig.add_annotation(x=7, y=mid_y + 1.5, text="4X tightened!\nPress UP button", showarrow=False, font=dict(size=9, color="#16a34a", family="Arial Black"))
        elif stage == 2:
            # Middle beam raised, rod spans to upper beam
            fig.add_shape(type="rect", x0=4.6, x1=5.4, y0=0.7, y1=9.3, fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            for y0, y1 in [(mid_y - 0.4, mid_y), (8.8, 9.3)]:
                fig.add_shape(type="rect", x0=4.3, x1=4.6, y0=y0, y1=y1, fillcolor="#475569", line_color="#1e293b")
                fig.add_shape(type="rect", x0=5.4, x1=5.7, y0=y0, y1=y1, fillcolor="#475569", line_color="#1e293b")
            fig.add_annotation(x=7, y=7, text="Rod in upper jaw!\nNow tighten 2X", showarrow=False, font=dict(size=9, color="#2563a8", family="Arial Black"))
        elif stage >= 3:
            # Fully fixed
            fig.add_shape(type="rect", x0=4.6, x1=5.4, y0=0.7, y1=9.3, fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            for y0, y1 in [(mid_y - 0.4, mid_y), (8.8, 9.3)]:
                fig.add_shape(type="rect", x0=4.3, x1=4.6, y0=y0, y1=y1, fillcolor="#475569", line_color="#1e293b")
                fig.add_shape(type="rect", x0=5.4, x1=5.7, y0=y0, y1=y1, fillcolor="#475569", line_color="#1e293b")
            # Control panel
            fig.add_shape(type="rect", x0=6, x1=8.5, y0=1.0, y1=3.8, fillcolor="#1e293b", line_color="#0f172a", line_width=2)
            pc = "#ef4444" if stage >= 4 else "#6b7280"
            lc = "#3b82f6" if stage >= 4 else "#6b7280"
            fig.add_shape(type="circle", x0=6.3, x1=6.9, y0=1.2, y1=1.8, fillcolor=pc, line_color="#111", line_width=1.5)
            fig.add_annotation(x=6.6, y=1.5, text="P", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
            fig.add_shape(type="circle", x0=7.3, x1=7.9, y0=1.2, y1=1.8, fillcolor=lc, line_color="#111", line_width=1.5)
            fig.add_annotation(x=7.6, y=1.5, text="L", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
            fig.add_shape(type="circle", x0=6.3, x1=6.9, y0=2.1, y1=2.7, fillcolor="#22c55e", line_color="#111", line_width=1.5)
            fig.add_annotation(x=6.6, y=2.4, text="S", showarrow=False, font=dict(size=10, color="#fff", family="Arial Black"))
            fig.add_shape(type="rect", x0=6.1, x1=8.4, y0=2.85, y1=3.7, fillcolor="#0f172a", line_color="#1e293b")
            fig.add_annotation(x=7.25, y=3.28, text="F: 0   CHT: 0", showarrow=False, font=dict(size=9, color="#22c55e", family="Courier New"))
            if stage >= 4:
                fig.add_annotation(x=3.5, y=5.5, text="READY TO TEST!", showarrow=False, font=dict(size=12, color="#16a34a", family="Arial Black"))

        fig.update_layout(height=400, margin=dict(l=20, r=20, t=10, b=10),
                          xaxis=dict(visible=False, range=[-0.5, 12.5]),
                          yaxis=dict(visible=False, range=[-0.5, 10.5]),
                          plot_bgcolor="white", paper_bgcolor="white")
        return fig

    steps_info = [
        ("Step 1", "Place MS rod into the middle beam lower jaw", "Click to insert rod into jaw"),
        ("Step 2", "Tighten 4X handle clockwise to grip rod firmly", "Click to tighten 4X handle"),
        ("Step 3", "Press UP button — middle beam rises, rod enters upper jaw", "Click to press UP button"),
        ("Step 4", "Tighten 2X handle to lock upper jaw", "Click to tighten 2X handle"),
        ("Step 5", "Open Pressure Valve P and Load Valve L (both turn active colour)", "Click to open valves"),
    ]

    col_utm, col_ctrl = st.columns([1.2, 0.8])
    with col_utm:
        st.plotly_chart(draw_utm(stage), use_container_width=True)

    with col_ctrl:
        st.markdown("#### Procedure — click each step in order")
        for i, (snum, sdesc, sinstr) in enumerate(steps_info):
            done = i < stage
            active = i == stage
            bg = "#dcfce7" if done else ("#dbeafe" if active else "#f8fafc")
            border = "#86efac" if done else ("#93c5fd" if active else "#e2e8f0")
            icon = "✅" if done else ("▶️" if active else "⭕")
            st.markdown(f"""<div style="background:{bg};border:1.5px solid {border};border-radius:8px;
                        padding:8px 12px;margin-bottom:6px;font-size:12px;">
                        {icon} <b>{snum}:</b> {sdesc}</div>""", unsafe_allow_html=True)

        if stage < len(steps_info):
            if st.button(steps_info[stage][2], type="primary", use_container_width=True, key="utm_btn"):
                st.session_state.utm_stage += 1
                st.rerun()
        else:
            st.markdown('<div class="correct">Rod is fixed in UTM! Ready to apply load.</div>', unsafe_allow_html=True)
            st.button("Next: Apply Load", on_click=lambda: st.session_state.update(scene=4), type="primary")

# SCENE 4 — APPLY LOAD (animated rod elongation + live graph)
elif sc == 4:
    st.markdown('<div class="lo-badge">Scene 5 · LO2 · Apply — Run Tensile Test — Watch Rod Elongate and Fracture</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Press NEXT LOAD STEP to increase load one step at a time. Watch the rod stretch, then neck and fracture. The graph builds live.</div>', unsafe_allow_html=True)

    step = st.session_state.load_step
    total = len(LOAD_DEFORM)
    F = LOAD_DEFORM[step][0]
    CHT = LOAD_DEFORM[step][1]

    col_anim, col_graph = st.columns([0.85, 1.15])

    with col_anim:
        fig = go.Figure()
        # Beams
        fig.add_shape(type="rect", x0=0, x1=8, y0=0, y1=0.6, fillcolor="#94a3b8", line_color="#475569", line_width=2)
        fig.add_shape(type="rect", x0=0, x1=8, y0=9.4, y1=10, fillcolor="#94a3b8", line_color="#475569", line_width=2)
        # Columns
        fig.add_shape(type="rect", x0=0, x1=0.8, y0=0.6, y1=9.4, fillcolor="#cbd5e1", line_color="#94a3b8")
        fig.add_shape(type="rect", x0=7.2, x1=8, y0=0.6, y1=9.4, fillcolor="#cbd5e1", line_color="#94a3b8")
        # Middle beam moves DOWN as deformation increases
        beam_y = max(3.5, 4.8 - CHT * 0.3)
        fig.add_shape(type="rect", x0=0.8, x1=7.2, y0=beam_y, y1=beam_y + 0.6, fillcolor="#64748b", line_color="#334155", line_width=2)
        fig.add_annotation(x=4, y=beam_y + 0.3, text="MIDDLE BEAM", showarrow=False, font=dict(size=8, color="#fff"))
        # Rod shape changes with loading
        rod_top = 9.4
        rod_bot = beam_y + 0.6
        neck = 1.0
        if step >= 22:
            neck = 0.45
        elif step >= 14:
            neck = 0.75
        elif step >= 10:
            neck = 0.9
        rw = 0.4  # full rod width
        nw = rw * neck  # necked width
        if step < 22:
            # Normal or slightly thinner rod
            fig.add_shape(type="rect", x0=4 - nw, x1=4 + nw, y0=rod_bot, y1=rod_top,
                          fillcolor="#f59e0b", line_color="#b45309", line_width=2)
        else:
            # Show necking in middle
            mid = (rod_bot + rod_top) / 2
            fig.add_shape(type="rect", x0=4 - rw, x1=4 + rw, y0=mid + 0.6, y1=rod_top,
                          fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            fig.add_shape(type="rect", x0=4 - rw, x1=4 + rw, y0=rod_bot, y1=mid - 0.6,
                          fillcolor="#f59e0b", line_color="#b45309", line_width=2)
            fig.add_shape(type="rect", x0=4 - nw, x1=4 + nw, y0=mid - 0.6, y1=mid + 0.6,
                          fillcolor="#ef4444", line_color="#b91c1c", line_width=2)
            if step == total - 1:
                fig.add_annotation(x=5.5, y=mid, text="FRACTURE!", showarrow=False,
                                   font=dict(size=11, color="#dc2626", family="Arial Black"))
        # Force arrows
        if F > 0:
            fig.add_annotation(x=4, y=rod_bot, ax=4, ay=rod_bot - 1.5, xref="x", yref="y", axref="x", ayref="y",
                               arrowhead=2, arrowcolor="#dc2626", arrowwidth=3, arrowsize=1.2)
            fig.add_annotation(x=4, y=rod_top, ax=4, ay=rod_top + 1.5, xref="x", yref="y", axref="x", ayref="y",
                               arrowhead=2, arrowcolor="#dc2626", arrowwidth=3, arrowsize=1.2)
        # Control panel display
        fig.add_shape(type="rect", x0=0.9, x1=3.8, y0=0.8, y1=2.5, fillcolor="#1e293b", line_color="#0f172a", line_width=2)
        fig.add_annotation(x=2.35, y=2.1, text="F (kN)", showarrow=False, font=dict(size=8, color="#94a3b8"))
        fig.add_annotation(x=2.35, y=1.65, text=str(F), showarrow=False, font=dict(size=18, color="#22c55e", family="Courier New"))
        fig.add_annotation(x=2.35, y=1.1, text=f"CHT: {CHT:.3f} mm", showarrow=False, font=dict(size=9, color="#60a5fa", family="Courier New"))
        # Phase
        if CHT <= 0.09:
            phase, pc = "Elastic zone", "#2563a8"
        elif F <= 44 and CHT <= 0.4:
            phase, pc = "Yield zone", "#f59e0b"
        elif step < 22:
            phase, pc = "Strain hardening", "#16a34a"
        else:
            phase, pc = "NECKING / FRACTURE", "#dc2626"
        fig.add_annotation(x=4, y=0.3, text=phase, showarrow=False, font=dict(size=10, color=pc, family="Arial Black"))

        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis=dict(visible=False, range=[-0.5, 9]),
                          yaxis=dict(visible=False, range=[-0.5, 12]),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("NEXT LOAD STEP", type="primary", use_container_width=True):
                if step < total - 1:
                    st.session_state.load_step += 1
                    st.rerun()
        with c2:
            if st.button("JUMP +3 STEPS", use_container_width=True):
                st.session_state.load_step = min(step + 3, total - 1)
                st.rerun()
        with c3:
            if st.button("RESET", use_container_width=True):
                st.session_state.load_step = 0
                st.rerun()
        st.caption(f"Step {step + 1} of {total}  |  F = {F} kN  |  CHT = {CHT:.3f} mm")

    with col_graph:
        loads = [p[0] for p in LOAD_DEFORM[:step + 1]]
        defms = [p[1] for p in LOAD_DEFORM[:step + 1]]
        colors = []
        for p in LOAD_DEFORM[:step + 1]:
            if p[1] <= 0.09:
                colors.append("#2563a8")
            elif p[0] <= 44 and p[1] <= 0.4:
                colors.append("#f59e0b")
            elif p[1] <= 7.2:
                colors.append("#16a34a")
            else:
                colors.append("#dc2626")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=defms, y=loads, mode='lines+markers',
                                  line=dict(color='#2563a8', width=2.5),
                                  marker=dict(size=7, color=colors),
                                  name="F vs CHT"))
        if step > 0:
            fig2.add_trace(go.Scatter(x=[CHT], y=[F], mode='markers',
                                      marker=dict(size=14, color='#dc2626', symbol='star'),
                                      name="Current"))
        for kx, ky, kl in [(0.09, 36, "Yield"), (0.4, 44, "Upper yield"), (7.2, 59, "UTS"), (10.8, 47, "Fracture")]:
            if CHT >= kx * 0.8:
                fig2.add_annotation(x=kx, y=ky, text=kl, showarrow=True, ax=25, ay=-22,
                                    font=dict(size=10, color="#374151"),
                                    bgcolor="white", bordercolor="#d1d5db", borderwidth=1)
        fig2.update_layout(height=280,
                           title=dict(text="Load F (kN) vs Deformation CHT (mm)", font=dict(size=12)),
                           xaxis=dict(title="CHT (mm)", range=[-0.2, 12], gridcolor="#f1f5f9"),
                           yaxis=dict(title="F (kN)", range=[-2, 65], gridcolor="#f1f5f9"),
                           plot_bgcolor="white", paper_bgcolor="white",
                           showlegend=True, legend=dict(orientation="h", y=1.1),
                           margin=dict(l=50, r=10, t=50, b=50))
        st.plotly_chart(fig2, use_container_width=True)

        import pandas as pd
        df_all = pd.DataFrame(LOAD_DEFORM[:step + 1], columns=["Load F (kN)", "CHT (mm)"])
        df_all.index = df_all.index + 1
        st.dataframe(df_all, use_container_width=True, height=180)

    if step == total - 1:
        st.success("Test complete — rod has fractured! Proceed to post-fracture measurements.")
        st.button("Next: Post-Fracture Measurements", on_click=lambda: st.session_state.update(scene=5), type="primary")

# SCENE 5 — POST FRACTURE
elif sc == 5:
    st.markdown('<div class="lo-badge">Scene 6 · LO2 · Apply — Post-Fracture Measurements</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Join the two broken pieces end-to-end. Measure final diameter (du) at the neck and final gauge length (Lu) between the gauge marks.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        du = st.slider("Final diameter du at neck (mm)", 4.0, 12.0, st.session_state.du, 0.2)
        st.session_state.du = du
        lu = st.slider("Final gauge length Lu (mm)", 60.0, 90.0, st.session_state.lu, 0.2)
        st.session_state.lu = lu

        d1 = (st.session_state.dx + st.session_state.dy) / 2
        lo = round(5 * d1, 2)

        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, x1=4, y0=-d1 / 2, y1=d1 / 2, fillcolor="#9ca3af", line_color="#374151", line_width=2)
        fig.add_shape(type="rect", x0=6, x1=10, y0=-d1 / 2, y1=d1 / 2, fillcolor="#9ca3af", line_color="#374151", line_width=2)
        fig.add_shape(type="rect", x0=3.5, x1=4, y0=-du / 2, y1=du / 2, fillcolor="#ef4444", line_color="#b91c1c", line_width=2)
        fig.add_shape(type="rect", x0=6, x1=6.5, y0=-du / 2, y1=du / 2, fillcolor="#ef4444", line_color="#b91c1c", line_width=2)
        fig.add_annotation(x=5, y=0, text="FRACTURE", showarrow=False, font=dict(size=10, color="#dc2626", family="Arial Black"))
        for gx in [0.5, 9.5]:
            fig.add_shape(type="line", x0=gx, x1=gx, y0=-d1 / 2 - 0.5, y1=d1 / 2 + 0.5,
                          line=dict(color="#dc2626", width=2, dash="dash"))
        fig.add_annotation(x=5, y=-d1 / 2 - 1.2, text=f"Lu = {lu:.1f} mm (joined end-to-end)",
                           showarrow=False, font=dict(size=11, color="#2563a8"))
        fig.add_annotation(x=5, y=du / 2 + 0.8, text=f"du = {du:.1f} mm (neck)",
                           showarrow=False, font=dict(size=10, color="#dc2626"))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=40),
                          xaxis=dict(visible=False, range=[-0.5, 10.5]),
                          yaxis=dict(visible=False, range=[-d1 / 2 - 2, d1 / 2 + 2]),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Post-Fracture Observation Table**")
        st.markdown(f"""<div class="obs-box">
        <table style="width:100%;font-size:13px;border-collapse:collapse;">
        <tr style="background:#dbeafe;"><td style="padding:5px;"><b>Parameter</b></td><td><b>Initial</b></td><td><b>Final</b></td></tr>
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">Diameter (mm)</td><td>{d1:.2f}</td><td><b style="color:#dc2626;">{du:.1f}</b></td></tr>
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">Gauge length (mm)</td><td>{lo:.2f}</td><td><b style="color:#2563a8;">{lu:.1f}</b></td></tr>
        <tr><td style="padding:5px;">Area (mm²)</td><td>{math.pi/4*d1**2:.2f}</td><td><b>{math.pi/4*du**2:.2f}</b></td></tr>
        </table></div>""", unsafe_allow_html=True)
        st.info(f"Elongation = Lu - L0 = {lu:.1f} - {lo:.2f} = **{lu - lo:.2f} mm**")

    st.button("Next: Calculations", on_click=lambda: st.session_state.update(scene=6), type="primary")

# SCENE 6 — CALCULATIONS
elif sc == 6:
    st.markdown('<div class="lo-badge">Scene 7 · LO3 · Analyze — Calculate Material Properties</div>', unsafe_allow_html=True)

    d1 = (st.session_state.dx + st.session_state.dy) / 2
    lo = round(5 * d1, 2)
    du = st.session_state.du
    lu = st.session_state.lu
    Ai = math.pi / 4 * d1 ** 2
    Au = math.pi / 4 * du ** 2
    Re = 41 * 1000 / Ai
    Rm = 59 * 1000 / Ai
    A3 = (lu - lo) / lo * 100
    Z = (Ai - Au) / Ai * 100
    dL = lu - lo
    E = (36 * 1000 / Ai) / (0.090 / lo)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Formulae used")
        for name, formula, val in [
            ("Ai", "pi/4 x d1^2", f"{Ai:.2f} mm2"),
            ("Au", "pi/4 x du^2", f"{Au:.2f} mm2"),
            ("Elongation dL", "Lu - L0", f"{dL:.2f} mm"),
            ("% Elongation A3", "(Lu-L0)/L0 x 100", f"{A3:.2f} %"),
            ("% Reduction Z", "(Ai-Au)/Ai x 100", f"{Z:.2f} %"),
            ("Yield strength Re", "Yield load x 1000 / Ai", f"{Re:.2f} N/mm2"),
            ("Ultimate strength Rm", "Max load x 1000 / Ai", f"{Rm:.2f} N/mm2"),
            ("Modulus E", "Stress/Strain (elastic zone)", f"{E:.0f} N/mm2"),
        ]:
            st.markdown(f'<div class="formula"><b>{name}</b> = {formula} = <span style="color:#0369a1;font-weight:700;">{val}</span></div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Result summary")
        m1, m2 = st.columns(2)
        m1.metric("Re (yield)", f"{Re:.1f}", "N/mm2")
        m2.metric("Rm (UTS)", f"{Rm:.1f}", "N/mm2")
        m3, m4 = st.columns(2)
        m3.metric("A3 (elong.)", f"{A3:.1f}", "%")
        m4.metric("Z (reduction)", f"{Z:.1f}", "%")
        st.metric("E (modulus)", f"{E:.0f}", "N/mm2")

        import pandas as pd
        df = pd.DataFrame({
            "Parameter": ["d1 (mm)", "L0 (mm)", "du (mm)", "Lu (mm)", "Ai (mm2)", "Au (mm2)",
                          "dL (mm)", "A3 (%)", "Z (%)", "Re (N/mm2)", "Rm (N/mm2)", "E (N/mm2)"],
            "Value": [f"{d1:.2f}", f"{lo:.2f}", f"{du:.2f}", f"{lu:.2f}",
                      f"{Ai:.2f}", f"{Au:.2f}", f"{dL:.2f}", f"{A3:.2f}",
                      f"{Z:.2f}", f"{Re:.2f}", f"{Rm:.2f}", f"{E:.0f}"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Stress-Strain Curve")
    stresses = [f * 1000 / Ai for f, _ in LOAD_DEFORM]
    strains = [d / lo for _, d in LOAD_DEFORM]
    fig = go.Figure()
    for sl, col, nm in [(slice(0, 10), "#2563a8", "Elastic"), (slice(9, 13), "#f59e0b", "Yield"),
                        (slice(12, 23), "#16a34a", "Strain hardening"), (slice(22, 26), "#dc2626", "Necking")]:
        fig.add_trace(go.Scatter(x=strains[sl], y=stresses[sl], mode='lines+markers', name=nm,
                                 line=dict(color=col, width=3), marker=dict(size=6, color=col)))
    for x, y, l in [(0, 0, "O"), (strains[9], stresses[9], "A-yield"),
                    (strains[11], stresses[11], "B-upper yield"), (strains[22], stresses[22], "C-UTS"),
                    (strains[25], stresses[25], "D-fracture")]:
        fig.add_annotation(x=x, y=y, text=l, showarrow=True, ax=25, ay=-25,
                           font=dict(size=10, color="#111"), bgcolor="white", bordercolor="#d1d5db", borderwidth=1)
    fig.update_layout(height=320,
                      xaxis=dict(title="Strain (dL/L0)", gridcolor="#f1f5f9"),
                      yaxis=dict(title="Stress (N/mm2)", gridcolor="#f1f5f9"),
                      plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", y=1.1), margin=dict(l=60, r=20, t=30, b=50))
    st.plotly_chart(fig, use_container_width=True)
    st.button("Next: IS Code Comparison", on_click=lambda: st.session_state.update(scene=7), type="primary")

# SCENE 7 — IS CODE
elif sc == 7:
    st.markdown('<div class="lo-badge">Scene 8 · LO4 · Evaluate — Compare with IS 432-1 (1982)</div>', unsafe_allow_html=True)

    d1 = (st.session_state.dx + st.session_state.dy) / 2
    lo = round(5 * d1, 2)
    du = st.session_state.du
    lu = st.session_state.lu
    Ai = math.pi / 4 * d1 ** 2
    Re = 41 * 1000 / Ai
    Rm = 59 * 1000 / Ai
    A3 = (lu - lo) / lo * 100

    col1, col2 = st.columns([1.1, 0.9])
    with col1:
        st.markdown("#### Enter IS 432-1 minimum values")
        is_re = st.number_input("IS min. Yield strength Re (N/mm2)", value=250.0, step=10.0)
        is_a3 = st.number_input("IS min. % Elongation A3 (%)", value=23.0, step=1.0)
        is_rm = st.number_input("IS min. Ultimate strength Rm (N/mm2)", value=410.0, step=10.0)

        import pandas as pd
        rows = []
        all_pass = True
        for nm, exp, isv in [("Yield strength Re (N/mm2)", Re, is_re),
                              ("% Elongation A3 (%)", A3, is_a3),
                              ("Ultimate strength Rm (N/mm2)", Rm, is_rm)]:
            passed = exp >= isv
            if not passed:
                all_pass = False
            rows.append({"Parameter": nm, "Experimental": f"{exp:.2f}",
                         "IS Minimum": f"{isv:.1f}",
                         "Result": "Satisfactory" if passed else "Not satisfactory"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if all_pass:
            st.markdown('<div class="verdict-pass">SAMPLE ACCEPTED — All parameters satisfy IS 432-1 (1982).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="verdict-fail">SAMPLE REJECTED — One or more parameters do not meet IS 432-1 (1982).</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### IS 432-1 Grade I Reference")
        st.info("IS 432-1 (1982) Mild Steel Grade I:\n- Re >= 250 N/mm2\n- A3 >= 23 %\n- Rm >= 410 N/mm2")
        st.markdown("#### Your results")
        st.markdown(f"""<div class="obs-box">
        Re = <b>{Re:.2f} N/mm2</b><br>
        Rm = <b>{Rm:.2f} N/mm2</b><br>
        A3 = <b>{A3:.2f} %</b>
        </div>""", unsafe_allow_html=True)
        st.success("Experiment Complete!")

st.divider()
st.markdown("<p style='text-align:center;color:#9ca3af;font-size:0.8rem;'>Virtual Lab - Tensile Test on Mild Steel - IS 432-1 (1982) - Civil Engineering</p>", unsafe_allow_html=True)
