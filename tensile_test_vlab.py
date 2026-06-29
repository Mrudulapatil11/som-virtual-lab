"""
Virtual Lab: Tensile Test on Mild Steel Rod
Strength of Materials — Second Year Civil Engineering
Based on IS 432-1 (1982) and IS 1608-2005

Run with:  streamlit run tensile_test_vlab.py
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tensile Test — Mild Steel Rod | Virtual Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a3a6b 0%, #2563a8 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { font-size: 1.6rem; margin: 0; font-weight: 700; }
    .main-header p  { font-size: 0.9rem; margin: 0.3rem 0 0; opacity: 0.85; }

    .scene-header {
        background: #eef4fb;
        border-left: 5px solid #2563a8;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .scene-header h3 { color: #1a3a6b; margin: 0; font-size: 1.05rem; }
    .scene-header p  { color: #444; margin: 0.25rem 0 0; font-size: 0.85rem; }

    .lo-badge {
        display: inline-block;
        background: #dbeafe;
        color: #1e3a8a;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .result-ok  { color: #16a34a; font-weight: 700; }
    .result-fail{ color: #dc2626; font-weight: 700; }

    .formula-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-family: monospace;
        font-size: 0.92rem;
        margin-bottom: 0.5rem;
        color: #0c4a6e;
    }
    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .verdict-pass {
        background: #dcfce7;
        border: 1.5px solid #86efac;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #15803d;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .verdict-fail {
        background: #fee2e2;
        border: 1.5px solid #fca5a5;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #b91c1c;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXPERIMENTAL DATA (from IS / PPT)
# ─────────────────────────────────────────────
LOAD_DEFORM = [
    (0, 0.000), (4, 0.009), (8, 0.019), (12, 0.029),
    (16, 0.039), (20, 0.048), (24, 0.057), (28, 0.068),
    (32, 0.077), (36, 0.090), (42, 0.200), (44, 0.400),
    (41, 0.700), (41, 1.200), (41, 2.300), (45, 2.900),
    (48, 3.240), (50, 3.600), (52, 4.100), (54, 4.620),
    (56, 5.240), (58, 6.300), (59, 7.200), (58, 8.400),
    (55, 9.400), (47, 10.800),
]

IS_STANDARDS = {
    "Yield strength Re (N/mm²)":      250,
    "% Elongation A₃ (%)":            23,
    "Ultimate strength Rm (N/mm²)":   410,
}

SCENE_LABELS = [
    "1 · Concept",
    "2 · Measure Specimen",
    "3 · UTM Procedure",
    "4 · Apply Load",
    "5 · Post-Fracture",
    "6 · Calculations",
    "7 · Stress-Strain Graph",
    "8 · IS Code Comparison",
]

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = dict(
        scene=0,
        dx=12.4, dy=12.4, lc=70.0,
        du=8.0,  lu=71.8,
        force_ans=None,
        utm_checked=[False]*11,
        is_re=250.0, is_a3=23.0, is_rm=410.0,
        score=0,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# COMPUTED VALUES
# ─────────────────────────────────────────────
def compute():
    d1  = (st.session_state.dx + st.session_state.dy) / 2
    lo  = round(5 * d1, 2)
    du  = st.session_state.du
    lu  = st.session_state.lu
    Ai  = math.pi / 4 * d1**2
    Au  = math.pi / 4 * du**2
    yield_load = 41   # kN  (from experiment data)
    max_load   = 59   # kN
    Re  = yield_load * 1000 / Ai
    Rm  = max_load   * 1000 / Ai
    A3  = (lu - lo) / lo * 100
    Z   = (Ai - Au) / Ai * 100
    dL  = lu - lo
    # E from elastic slope: stress at 36 kN / strain at 0.09 mm
    strain_e = 0.090 / lo
    stress_e = 36 * 1000 / Ai
    E   = stress_e / strain_e
    return dict(d1=d1, lo=lo, du=du, lu=lu,
                Ai=Ai, Au=Au, Re=Re, Rm=Rm,
                A3=A3, Z=Z, dL=dL, E=E)

# ─────────────────────────────────────────────
# SIDEBAR — NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 Virtual Lab Navigator")
    st.markdown("**Tensile Test — Mild Steel**")
    st.divider()
    for i, label in enumerate(SCENE_LABELS):
        if st.button(label, key=f"nav_{i}",
                     use_container_width=True,
                     type="primary" if st.session_state.scene == i else "secondary"):
            st.session_state.scene = i
    st.divider()
    c = compute()
    st.markdown("**📋 Live readings**")
    st.metric("d₁ (avg diameter)", f"{c['d1']:.2f} mm")
    st.metric("L₀ (gauge length)",  f"{c['lo']:.2f} mm")
    st.metric("Re (yield str.)",    f"{c['Re']:.1f} N/mm²")
    st.metric("Rm (UTS)",           f"{c['Rm']:.1f} N/mm²")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🔬 Tensile Test on Mild Steel Rod — Virtual Lab</h1>
  <p>Strength of Materials &nbsp;|&nbsp; Second Year Civil Engineering &nbsp;|&nbsp; IS 432-1 (1982)</p>
</div>
""", unsafe_allow_html=True)

scene = st.session_state.scene

# ═══════════════════════════════════════════════════════
# SCENE 0 — CONCEPT
# ═══════════════════════════════════════════════════════
if scene == 0:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 1 — What is Tensile Force?</h3>
      <p>Learning Objective: Recall the concept of tension force and experiment setup. (Bloom's Level 1 — Remember)</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""<div class="lo-badge">LO 1 · Remember</div>""", unsafe_allow_html=True)
        st.markdown("#### About this experiment")
        st.markdown("""
        When a **tensile force** acts along the **longitudinal axis** of a member, it causes
        **elongation**. The tensile stress per unit cross-sectional area is the **tensile strength**.

        This experiment finds:
        - **E** — Modulus of Elasticity (N/mm²)
        - **Re** — Yield Strength (N/mm²)
        - **Rm** — Ultimate Tensile Strength (N/mm²)
        - **A₃** — Percentage Elongation after fracture (%)

        Results are verified against **IS 432-1 (1982)** requirements.
        """)

    with col2:
        st.markdown("#### ✅ Task — Identify the tensile force diagram")
        st.markdown("Which of the following shows **tensile force** acting on a rod?")
        ans = st.radio(
            "Select the correct diagram:",
            options=["← Compression →  (forces push inward)",
                     "→ Tension ←  (forces pull outward)",
                     "↑↓ Shear  (forces act transversely)"],
            index=None,
            key="force_q"
        )
        if ans:
            if "Tension" in ans:
                st.success("✅ Correct! Tensile force acts **outward** along the longitudinal axis, causing the rod to elongate.")
                st.session_state.score = max(st.session_state.score, 3)
            else:
                st.error("❌ Not quite. Tensile force pulls the rod **outward** from both ends.")

        fig = go.Figure()
        # Rod
        fig.add_shape(type="rect", x0=1, x1=7, y0=0.4, y1=0.6,
                      fillcolor="#888", line_color="#555")
        # Arrows outward
        fig.add_annotation(x=1, y=0.5, ax=0.2, ay=0, xref="x", yref="y",
                           axref="x", ayref="y",
                           arrowhead=2, arrowsize=1.5, arrowcolor="#2563a8", arrowwidth=2.5)
        fig.add_annotation(x=7, y=0.5, ax=7.8, ay=0, xref="x", yref="y",
                           axref="x", ayref="y",
                           arrowhead=2, arrowsize=1.5, arrowcolor="#2563a8", arrowwidth=2.5)
        fig.add_annotation(x=0.5, y=0.5, text="F", showarrow=False,
                           font=dict(size=16, color="#2563a8"))
        fig.add_annotation(x=7.5, y=0.5, text="F", showarrow=False,
                           font=dict(size=16, color="#2563a8"))
        fig.update_layout(height=160, margin=dict(l=10,r=10,t=10,b=10),
                          xaxis=dict(visible=False, range=[0,8]),
                          yaxis=dict(visible=False, range=[0,1]),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    st.button("Next: Measure Specimen →", on_click=lambda: st.session_state.update(scene=1),
              type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 1 — MEASURE SPECIMEN
# ═══════════════════════════════════════════════════════
elif scene == 1:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 2 — Measure the Mild Steel Specimen</h3>
      <p>Learning Objective: Use Vernier caliper and scale to measure specimen dimensions. (Bloom's Level 3 — Apply)</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""<div class="lo-badge">LO 2 · Apply — Vernier Caliper</div>""", unsafe_allow_html=True)
        st.markdown("#### Initial Diameter of MS Rod")
        st.markdown("Move the sliders to simulate closing the Vernier caliper jaws on the rod.")

        dx = st.slider("Diameter in X-direction (mm)", 10.0, 15.0, 12.4, 0.2, key="dx_slide")
        st.session_state.dx = dx

        st.markdown("*Rotate caliper 90° and measure in Y-direction:*")
        dy = st.slider("Diameter in Y-direction (mm)", 10.0, 15.0, 12.4, 0.2, key="dy_slide")
        st.session_state.dy = dy

        d1 = (dx + dy) / 2
        st.session_state.d1_computed = d1

        st.markdown(f"""
        <div class="info-card">
          <b>Observation Table — Initial Diameter</b><br>
          dx (X direction) = <b>{dx:.1f} mm</b><br>
          dy (Y direction) = <b>{dy:.1f} mm</b><br>
          Average d₁ = (dx + dy) / 2 = <b>{d1:.2f} mm</b>
        </div>""", unsafe_allow_html=True)

    with col2:
        # Draw cross-section
        theta = np.linspace(0, 2*np.pi, 100)
        r = d1 / 2
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r*np.cos(theta), y=r*np.sin(theta),
                                 fill='toself', fillcolor='#9ca3af',
                                 line=dict(color='#374151', width=2),
                                 name="Cross-section"))
        fig.add_shape(type="line", x0=-r, x1=r, y0=0, y1=0,
                      line=dict(color="#2563a8", width=1.5, dash="dash"))
        fig.add_shape(type="line", x0=0, x1=0, y0=-r, y1=r,
                      line=dict(color="#dc2626", width=1.5, dash="dash"))
        fig.add_annotation(x=r+0.3, y=0, text=f"dx={dx:.1f}", showarrow=False,
                           font=dict(size=11, color="#2563a8"))
        fig.add_annotation(x=0, y=r+0.3, text=f"dy={dy:.1f}", showarrow=False,
                           font=dict(size=11, color="#dc2626"))
        fig.add_annotation(x=0, y=-r-0.6, text=f"d₁ = {d1:.2f} mm", showarrow=False,
                           font=dict(size=13, color="#111"))
        fig.update_layout(height=240, margin=dict(l=20,r=20,t=20,b=20),
                          xaxis=dict(visible=False, scaleanchor="y"),
                          yaxis=dict(visible=False),
                          showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                          title=dict(text="Rod cross-section view", font=dict(size=13)))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown("#### Parallel Length (Lc)")
        lc = st.slider("Parallel length Lc (mm)", 50.0, 90.0, 70.0, 1.0)
        st.session_state.lc = lc
        st.markdown(f"Lc = **{lc:.0f} mm**")

    with col4:
        st.markdown("#### Gauge Length (L₀)")
        lo = 5 * d1
        st.markdown(f"""
        <div class="formula-box">L₀ = 5 × d₁ = 5 × {d1:.2f} = <b>{lo:.2f} mm</b></div>
        """, unsafe_allow_html=True)
        st.info(f"✅ Gauge length L₀ = **{lo:.2f} mm**\n\nMark this length on the rod before fixing in UTM.")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=0))
    with col_nav2:
        st.button("Next: UTM Procedure →", on_click=lambda: st.session_state.update(scene=2),
                  type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 2 — UTM PROCEDURE
# ═══════════════════════════════════════════════════════
elif scene == 2:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 3 — Fix Specimen in Universal Testing Machine</h3>
      <p>Learning Objective: Follow correct UTM setup procedure. (Bloom's Level 3 — Apply)</p>
    </div>""", unsafe_allow_html=True)

    utm_steps = [
        ("Fix specimen in middle beam jaw (lower grip)", "Drag and place the MS rod into the middle beam jaw."),
        ("Tighten 4X handle clockwise", "Rotate the 4X handle clockwise to grip the specimen in the lower jaw."),
        ("Press UP button (▲) on control panel", "Move the middle beam upward so the rod enters the upper (2X) jaw."),
        ("Tighten 2X handle clockwise", "Lock the upper jaw by tightening the 2X handle."),
        ("Open Pressure Valve P (rotate → red)", "Turn pressure valve P to open position (indicator goes red)."),
        ("Open Load Valve L (rotate → red)", "Turn load valve L to open position (indicator goes red)."),
        ("Press START button S", "Start the hydraulic pump — load panel shows F:0, CHT:0."),
        ("Gradually open Load Valve to apply load", "Increase load slowly — observe F (kN) and CHT (mm) rising on the panel."),
        ("Monitor F and CHT readings continuously", "Record readings at each increment for the observation table."),
        ("Press CLOSE valve when fracture occurs", "After fracture, close the valve immediately to stop loading."),
        ("Rotate Pressure Valve P back to green (safe)", "Release pressure safely before removing the broken specimen."),
    ]

    st.markdown("#### ✅ Procedure Checklist — tick each step as you complete it")
    checked = st.session_state.utm_checked
    all_done = True
    for i, (step, detail) in enumerate(utm_steps):
        col_chk, col_txt = st.columns([0.06, 0.94])
        with col_chk:
            checked[i] = st.checkbox("", value=checked[i], key=f"utm_chk_{i}")
        with col_txt:
            color = "#16a34a" if checked[i] else "#374151"
            weight = "600" if checked[i] else "400"
            st.markdown(f"<span style='color:{color};font-weight:{weight};'>"
                        f"Step {i+1}: {step}</span><br>"
                        f"<span style='color:#6b7280;font-size:0.82rem;'>{detail}</span>",
                        unsafe_allow_html=True)
        if not checked[i]:
            all_done = False
    st.session_state.utm_checked = checked

    done_count = sum(checked)
    st.progress(done_count / len(utm_steps))
    st.caption(f"{done_count}/{len(utm_steps)} steps completed")

    if all_done:
        st.success("🎉 All steps completed! You are ready to apply load.")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=1))
    with col_nav2:
        if done_count >= 6:
            st.button("Next: Apply Load →", on_click=lambda: st.session_state.update(scene=3),
                      type="primary")
        else:
            st.warning("Complete at least 6 steps to proceed.")

# ═══════════════════════════════════════════════════════
# SCENE 3 — LOAD vs DEFORMATION
# ═══════════════════════════════════════════════════════
elif scene == 3:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 4 — Apply Load and Record Observations</h3>
      <p>Learning Objective: Read load (F) and deformation (CHT) from UTM panel. (Bloom's Level 3 — Apply)</p>
    </div>""", unsafe_allow_html=True)

    loads  = [p[0] for p in LOAD_DEFORM]
    defms  = [p[1] for p in LOAD_DEFORM]

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        # Color zones
        colors = []
        for f, c in LOAD_DEFORM:
            if c <= 0.09:
                colors.append("#2563a8")   # elastic
            elif f <= 44 and c <= 0.4:
                colors.append("#f59e0b")   # yield
            elif f >= 44:
                colors.append("#16a34a")   # strain hardening
            else:
                colors.append("#dc2626")   # necking

        fig = go.Figure()
        # Elastic zone
        el_f = [p[0] for p in LOAD_DEFORM if p[1] <= 0.09]
        el_d = [p[1] for p in LOAD_DEFORM if p[1] <= 0.09]
        fig.add_trace(go.Scatter(x=el_d, y=el_f, mode='lines+markers',
                                 name='Elastic zone', line=dict(color='#2563a8', width=3),
                                 marker=dict(size=5)))
        # Yield
        y_idx = [(f,d) for f,d in LOAD_DEFORM if d >= 0.09 and d <= 0.4]
        fig.add_trace(go.Scatter(x=[p[1] for p in y_idx], y=[p[0] for p in y_idx],
                                 mode='lines+markers', name='Yield zone',
                                 line=dict(color='#f59e0b', width=3), marker=dict(size=5)))
        # Strain hardening
        sh_idx = [(f,d) for f,d in LOAD_DEFORM if d >= 0.4 and f >= 41]
        fig.add_trace(go.Scatter(x=[p[1] for p in sh_idx], y=[p[0] for p in sh_idx],
                                 mode='lines+markers', name='Strain hardening',
                                 line=dict(color='#16a34a', width=3), marker=dict(size=5)))
        # Necking
        nk_idx = [(f,d) for f,d in LOAD_DEFORM if d >= 7.2]
        fig.add_trace(go.Scatter(x=[p[1] for p in nk_idx], y=[p[0] for p in nk_idx],
                                 mode='lines+markers', name='Necking / fracture',
                                 line=dict(color='#dc2626', width=3), marker=dict(size=5)))

        # Key point annotations
        annotations = [
            dict(x=0, y=0, text="O", showarrow=True, ax=15, ay=-20,
                 font=dict(size=12, color="#111")),
            dict(x=0.09, y=36, text="A (yield pt)", showarrow=True, ax=30, ay=-20,
                 font=dict(size=11, color="#f59e0b")),
            dict(x=0.4, y=44, text="B (upper yield)", showarrow=True, ax=40, ay=-15,
                 font=dict(size=11, color="#f59e0b")),
            dict(x=7.2, y=59, text="C (UTS)", showarrow=True, ax=20, ay=-20,
                 font=dict(size=11, color="#16a34a")),
            dict(x=10.8, y=47, text="D (fracture)", showarrow=True, ax=-30, ay=20,
                 font=dict(size=11, color="#dc2626")),
        ]
        fig.update_layout(
            height=380,
            title=dict(text="Load (kN) vs Deformation CHT (mm)", font=dict(size=14)),
            xaxis=dict(title="Deformation CHT (mm)", gridcolor="#e5e7eb"),
            yaxis=dict(title="Load F (kN)", gridcolor="#e5e7eb"),
            annotations=annotations,
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=60, r=20, t=60, b=50)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📋 Observation Table")
        st.markdown("Load F (kN) vs Deformation CHT (mm)")
        import pandas as pd
        df = pd.DataFrame(LOAD_DEFORM, columns=["Load F (kN)", "CHT (mm)"])
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True, height=380)

    st.markdown("#### 🔑 Key observations from the graph")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Max load (UTS)", "59 kN", "Point C")
    col_b.metric("Yield load", "41 kN", "Point A")
    col_c.metric("Fracture load", "47 kN", "Point D")
    col_d.metric("Max deformation", "10.8 mm", "At fracture")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=2))
    with col_nav2:
        st.button("Next: Post-Fracture →", on_click=lambda: st.session_state.update(scene=4),
                  type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 4 — POST-FRACTURE
# ═══════════════════════════════════════════════════════
elif scene == 4:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 5 — Post-Fracture Measurements</h3>
      <p>Join the broken pieces and measure final diameter (du) and final gauge length (Lu).</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""<div class="lo-badge">LO 2 · Apply — Post fracture Vernier caliper</div>""",
                    unsafe_allow_html=True)
        st.markdown("#### Final diameter (du)")
        st.markdown("Measure the neck (narrowest) portion of the broken specimen.")
        du = st.slider("Final diameter du (mm)", 5.0, 12.0, 8.0, 0.2)
        st.session_state.du = du
        st.markdown(f"du = **{du:.1f} mm**")

        st.markdown("#### Final gauge length (Lu)")
        st.markdown("Join the two broken pieces end-to-end and measure between gauge marks.")
        lu = st.slider("Final gauge length Lu (mm)", 60.0, 90.0, 71.8, 0.2)
        st.session_state.lu = lu
        st.markdown(f"Lu = **{lu:.1f} mm**")

    with col2:
        d1 = (st.session_state.dx + st.session_state.dy) / 2
        lo = 5 * d1

        fig = go.Figure()
        # Original rod outline
        fig.add_shape(type="rect", x0=0, x1=10, y0=-d1/2, y1=d1/2,
                      fillcolor="#9ca3af", opacity=0.3,
                      line=dict(color="#9ca3af", dash="dot"))
        # Broken left piece
        fig.add_shape(type="rect", x0=0, x1=4.2, y0=-d1/2, y1=d1/2,
                      fillcolor="#6b7280", line=dict(color="#374151", width=1.5))
        # Necked region
        fig.add_shape(type="rect", x0=4.2, x1=5.8, y0=-du/2, y1=du/2,
                      fillcolor="#ef4444", line=dict(color="#b91c1c", width=1.5))
        # Broken right piece
        fig.add_shape(type="rect", x0=5.8, x1=10, y0=-d1/2, y1=d1/2,
                      fillcolor="#6b7280", line=dict(color="#374151", width=1.5))
        # Gauge length annotation
        fig.add_annotation(x=5, y=-d1/2-1, text=f"Lu = {lu:.1f} mm",
                           showarrow=False, font=dict(size=11, color="#2563a8"))
        fig.add_annotation(x=5, y=d1/2+0.8, text=f"du = {du:.1f} mm (necked)",
                           showarrow=False, font=dict(size=11, color="#dc2626"))
        fig.update_layout(height=220, margin=dict(l=10,r=10,t=30,b=40),
                          xaxis=dict(visible=False, range=[-0.5,10.5]),
                          yaxis=dict(visible=False, range=[-d1/2-2, d1/2+2]),
                          plot_bgcolor="white", paper_bgcolor="white",
                          title=dict(text="Fractured specimen — side view", font=dict(size=13)))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="info-card">
          <b>Summary</b><br>
          Initial d₁ = {d1:.2f} mm &nbsp;→&nbsp; Final du = {du:.1f} mm<br>
          Initial L₀ = {lo:.2f} mm &nbsp;→&nbsp; Final Lu = {lu:.1f} mm<br>
          Elongation = <b>{lu-lo:.2f} mm</b>
        </div>""", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=3))
    with col_nav2:
        st.button("Next: Calculations →", on_click=lambda: st.session_state.update(scene=5),
                  type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 5 — CALCULATIONS
# ═══════════════════════════════════════════════════════
elif scene == 5:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 6 — Calculations</h3>
      <p>Learning Objective: Calculate all material properties from observations. (Bloom's Level 4 — Analyze)</p>
    </div>""", unsafe_allow_html=True)

    c = compute()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""<div class="lo-badge">LO 3 · Analyze — Calculate properties</div>""",
                    unsafe_allow_html=True)
        st.markdown("#### Formulae")
        formulas = [
            ("Initial area",          "Ai = π/4 × d₁²",                       f"= {c['Ai']:.2f} mm²"),
            ("Final area",            "Au = π/4 × du²",                        f"= {c['Au']:.2f} mm²"),
            ("Elongation",            "ΔL = Lu − L₀",                          f"= {c['dL']:.2f} mm"),
            ("% Elongation A₃",       "A₃ = (Lu − L₀) / L₀ × 100",            f"= {c['A3']:.2f} %"),
            ("% Reduction Z",         "Z = (Ai − Au) / Ai × 100",              f"= {c['Z']:.2f} %"),
            ("Yield strength Re",     "Re = Yield load × 1000 / Ai",           f"= {c['Re']:.2f} N/mm²"),
            ("Ultimate strength Rm",  "Rm = Max load × 1000 / Ai",             f"= {c['Rm']:.2f} N/mm²"),
            ("Modulus of elasticity", "E = Stress / Strain (elastic zone)",     f"= {c['E']:.0f} N/mm²"),
        ]
        for name, formula, result in formulas:
            st.markdown(f"""
            <div class="formula-box">
              <b>{name}</b><br>
              {formula} &nbsp;<span style='color:#0369a1;'><b>{result}</b></span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Calculation table")
        import pandas as pd
        rows = {
            "Parameter": [
                "Initial diameter d₁ (mm)",
                "Initial gauge length L₀ (mm)",
                "Final diameter du (mm)",
                "Final gauge length Lu (mm)",
                "Initial area Ai (mm²)",
                "Final area Au (mm²)",
                "Elongation ΔL (mm)",
                "% Elongation A₃ (%)",
                "% Reduction of area Z (%)",
                "Yield strength Re (N/mm²)",
                "Ultimate strength Rm (N/mm²)",
                "Modulus of Elasticity E (N/mm²)",
            ],
            "Value": [
                f"{c['d1']:.2f}", f"{c['lo']:.2f}",
                f"{c['du']:.2f}", f"{c['lu']:.2f}",
                f"{c['Ai']:.2f}", f"{c['Au']:.2f}",
                f"{c['dL']:.2f}", f"{c['A3']:.2f}",
                f"{c['Z']:.2f}",  f"{c['Re']:.2f}",
                f"{c['Rm']:.2f}", f"{c['E']:.0f}",
            ]
        }
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("#### Key metrics")
        m1, m2 = st.columns(2)
        m1.metric("Yield strength Re", f"{c['Re']:.1f} N/mm²")
        m2.metric("Ultimate strength Rm", f"{c['Rm']:.1f} N/mm²")
        m3, m4 = st.columns(2)
        m3.metric("% Elongation A₃", f"{c['A3']:.1f} %")
        m4.metric("Modulus E", f"{c['E']:.0f} N/mm²")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=4))
    with col_nav2:
        st.button("Next: Stress-Strain Graph →", on_click=lambda: st.session_state.update(scene=6),
                  type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 6 — STRESS-STRAIN CURVE
# ═══════════════════════════════════════════════════════
elif scene == 6:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 7 — Stress-Strain Curve</h3>
      <p>Interactive graph showing all zones of the mild steel stress-strain response.</p>
    </div>""", unsafe_allow_html=True)

    c = compute()
    Ai = c["Ai"]
    lo = c["lo"]

    stresses = [f * 1000 / float(Ai) for f, _ in LOAD_DEFORM]
    strains  = [d / lo for _, d in LOAD_DEFORM]

    fig = go.Figure()

    zones = [
        ("Elastic zone",       slice(0, 10),  "#2563a8"),
        ("Yield zone",         slice(9, 13),  "#f59e0b"),
        ("Strain hardening",   slice(12, 23), "#16a34a"),
        ("Necking / fracture", slice(22, 26), "#dc2626"),
    ]
    for name, sl, color in zones:
        fig.add_trace(go.Scatter(
            x=strains[sl], y=stresses[sl],
            mode='lines+markers', name=name,
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color),
            hovertemplate="Strain: %{x:.4f}<br>Stress: %{y:.1f} N/mm²<extra>"+name+"</extra>"
        ))

    key_pts = [
        (0, 0, "O (origin)"),
        (strains[9],  stresses[9],  "A (yield point)"),
        (strains[11], stresses[11], "B (upper yield)"),
        (strains[22], stresses[22], "C (UTS)"),
        (strains[25], stresses[25], "D (fracture)"),
    ]
    for x, y, label in key_pts:
        fig.add_annotation(x=x, y=y, text=label,
                           showarrow=True, ax=25, ay=-25,
                           font=dict(size=11, color="#111"),
                           bgcolor="white", bordercolor="#ccc", borderwidth=1)

    fig.update_layout(
        height=420,
        title=dict(text="Stress (N/mm²) vs Strain — Mild Steel", font=dict(size=15)),
        xaxis=dict(title="Strain (ΔL/L₀)", gridcolor="#e5e7eb", zeroline=True),
        yaxis=dict(title="Stress (N/mm²)", gridcolor="#e5e7eb", zeroline=True),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=60, r=20, t=70, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Zone explanation")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.markdown("🔵 **Elastic zone**\nStress ∝ Strain (Hooke's law). Rod returns to original shape on unloading.")
    col_b.markdown("🟡 **Yield zone**\nLoad drops slightly — plastic deformation begins. Upper and lower yield points.")
    col_c.markdown("🟢 **Strain hardening**\nMaterial strengthens as dislocations accumulate. Load rises to UTS.")
    col_d.markdown("🔴 **Necking / fracture**\nLocal thinning (necking) at weakest point → fracture. Load drops rapidly.")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=5))
    with col_nav2:
        st.button("Next: IS Code Comparison →", on_click=lambda: st.session_state.update(scene=7),
                  type="primary")

# ═══════════════════════════════════════════════════════
# SCENE 7 — IS CODE COMPARISON
# ═══════════════════════════════════════════════════════
elif scene == 7:
    st.markdown("""
    <div class="scene-header">
      <h3>Scene 8 — IS Code Comparison</h3>
      <p>Learning Objective: Compare experimental results with IS 432-1 (1982) and give verdict. (Bloom's Level 4 — Evaluate)</p>
    </div>""", unsafe_allow_html=True)

    c = compute()

    col1, col2 = st.columns([1.1, 0.9])
    with col1:
        st.markdown("""<div class="lo-badge">LO 4 · Evaluate — IS 432-1 (1982)</div>""",
                    unsafe_allow_html=True)
        st.markdown("#### Enter IS specified minimum values")
        st.markdown("Refer IS 432-1 (1982) for mild steel Grade I requirements:")

        is_re = st.number_input("IS min. Yield strength Re (N/mm²)", value=250.0, step=10.0)
        is_a3 = st.number_input("IS min. % Elongation A₃ (%)",       value=23.0,  step=1.0)
        is_rm = st.number_input("IS min. Ultimate strength Rm (N/mm²)", value=410.0, step=10.0)

        st.markdown("#### Comparison table")
        params = [
            ("Yield strength Re (N/mm²)",    float(c["Re"]), is_re),
            ("% Elongation A₃ (%)",          float(c["A3"]), is_a3),
            ("Ultimate strength Rm (N/mm²)", float(c["Rm"]), is_rm),
        ]

        import pandas as pd
        results = []
        all_pass = True
        for name, exp, is_val in params:
            passed = exp >= is_val
            if not passed:
                all_pass = False
            results.append({
                "Parameter":          name,
                "Experimental value": f"{exp:.2f}",
                "IS minimum":         f"{is_val:.1f}",
                "Result":             "✅ Satisfactory" if passed else "❌ Not satisfactory",
            })
        df_res = pd.DataFrame(results)
        st.dataframe(df_res, use_container_width=True, hide_index=True)

        if all_pass:
            st.markdown("""<div class="verdict-pass">
              ✅ Sample ACCEPTED — All parameters satisfy IS 432-1 (1982) requirements.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="verdict-fail">
              ❌ Sample REJECTED — One or more parameters do not meet IS 432-1 (1982) minimum requirements.
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Final observation summary")
        st.markdown(f"""
        | Measurement | Initial | Final |
        |---|---|---|
        | Diameter (mm) | {c['d1']:.2f} | {c['du']:.2f} |
        | Gauge length (mm) | {c['lo']:.2f} | {c['lu']:.2f} |
        | Area (mm²) | {c['Ai']:.2f} | {c['Au']:.2f} |
        """)

        st.markdown("#### All calculated results")
        st.markdown(f"""
        | Property | Value |
        |---|---|
        | Yield strength Re | **{c['Re']:.2f} N/mm²** |
        | Ultimate strength Rm | **{c['Rm']:.2f} N/mm²** |
        | % Elongation A₃ | **{c['A3']:.2f} %** |
        | % Reduction Z | **{c['Z']:.2f} %** |
        | Elongation ΔL | **{c['dL']:.2f} mm** |
        | Modulus of Elasticity E | **{c['E']:.0f} N/mm²** |
        """)

        st.markdown("#### IS 432-1 Grade I — Reference")
        st.info("""
        **IS 432-1 (1982) — Mild Steel Grade I:**
        - Yield strength Re ≥ **250 N/mm²**
        - % Elongation A₃ ≥ **23 %**
        - Ultimate strength Rm ≥ **410 N/mm²**
        """)

    st.divider()
    st.markdown("#### 🎉 Experiment complete!")
    st.success(f"You have successfully completed the Tensile Test on Mild Steel Rod virtual lab. "
               f"Score: **{st.session_state.score + 10} / 31 points** (based on tasks completed).")

    col_nav1, _ = st.columns(2)
    with col_nav1:
        st.button("← Back", on_click=lambda: st.session_state.update(scene=6))

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#9ca3af;font-size:0.8rem;'>"
    "Virtual Lab · Tensile Test on Mild Steel Rod · IS 432-1 (1982) · "
    "Strength of Materials · Civil Engineering"
    "</p>",
    unsafe_allow_html=True
)
