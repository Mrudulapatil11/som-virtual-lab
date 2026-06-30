"""
Virtual Lab: Tensile Test on Mild Steel Rod
Strength of Materials -- Second Year Civil Engineering
IS 432-1 (1982)
Uses original images from instructor's PPT (assets/ folder)
Run: streamlit run tensile_test_vlab.py
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import base64
import os

st.set_page_config(page_title="Tensile Test Virtual Lab", page_icon="\U0001F52C", layout="wide")

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

def img_b64(name):
    path = os.path.join(ASSET_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

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
.utm-stage{position:relative;width:100%;max-width:520px;margin:0 auto;}
.utm-stage img{width:100%;display:block;}
.utm-overlay-panel{position:absolute;top:34%;left:54%;width:30%;background:#0f172a;color:#22c55e;
  font-family:'Courier New',monospace;font-size:13px;padding:6px 10px;border-radius:4px;text-align:left;line-height:1.5;}
.utm-overlay-phase{position:absolute;bottom:2%;left:5%;font-weight:800;font-size:13px;padding:4px 10px;border-radius:6px;background:white;border:2px solid;}
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
    st.markdown("### \U0001F52C Experiment Scenes")
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
<h1>\U0001F52C Tensile Test on Mild Steel Rod -- Virtual Lab</h1>
<p>Strength of Materials | Second Year Civil Engineering | IS 432-1 (1982)</p>
</div>""", unsafe_allow_html=True)

sc = st.session_state.scene

# ============================================================
# SCENE 0 -- CONCEPT (using actual PPT stick-figure images)
# ============================================================
if sc == 0:
    st.markdown('<div class="lo-badge">Scene 1 - LO1 - Remember: Tensile Force Concept</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Look at the force diagrams below (from your course material). Click the one that shows TENSILE force acting on a rod.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    tens_b64 = img_b64("tensile_force_concept.png")
    shear_b64 = img_b64("shear_force_concept.png")

    with col1:
        st.markdown("**Diagram A**")
        if tens_b64:
            st.markdown(f'<img src="data:image/png;base64,{tens_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;padding:8px;background:white;">', unsafe_allow_html=True)
        if st.button("Select Diagram A", use_container_width=True, key="sel_a"):
            st.session_state.force_ans = "tension"
    with col2:
        st.markdown("**Diagram B**")
        if shear_b64:
            st.markdown(f'<img src="data:image/png;base64,{shear_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;padding:8px;background:white;">', unsafe_allow_html=True)
        if st.button("Select Diagram B", use_container_width=True, key="sel_b"):
            st.session_state.force_ans = "shear"

    if st.session_state.force_ans == "tension":
        st.markdown('<div class="correct">Correct! Diagram A shows tensile force -- both people pull OUTWARD on the bar, causing elongation along the longitudinal axis.</div>', unsafe_allow_html=True)
        st.button("Next: Learn UTM Parts", on_click=lambda: st.session_state.update(scene=1), type="primary")
    elif st.session_state.force_ans == "shear":
        st.markdown('<div class="wrong">Not quite -- Diagram B shows a balanced/transverse load (like sitting on a beam), not tensile pulling. Try Diagram A.</div>', unsafe_allow_html=True)

    st.markdown("#### About this experiment")
    st.markdown("""When force is applied on a member of an elastic material, the member elongates.
    If elongation occurs as a change in length, that external force is called tensile force.
    Tensile force acts along the longitudinal axis. This experiment finds the Modulus of Elasticity,
    Yield strength, Ultimate strength, and Percentage elongation after fracture -- verified against
    **IS 432-1 (1982)** requirements.""")

# ============================================================
# SCENE 1 -- UTM PARTS (using actual PPT UTM image with clickable hotspots)
# ============================================================
elif sc == 1:
    st.markdown('<div class="lo-badge">Scene 2 - LO1 - Remember: Identify UTM Parts</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">This is your actual Universal Testing Machine (UTM) diagram. Click a part name below to learn what it does.</div>', unsafe_allow_html=True)

    utm_b64 = img_b64("utm_machine.png")
    col_img, col_info = st.columns([1.3, 0.7])
    with col_img:
        if utm_b64:
            st.markdown(f'<img src="data:image/png;base64,{utm_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:6px;">', unsafe_allow_html=True)

    with col_info:
        st.markdown("#### Click a part:")
        parts = {
            "Upper Beam": "Fixed top beam -- holds the UPPER jaw that grips the TOP of the MS rod.",
            "Middle Beam": "Movable beam -- moves UP using hydraulic pressure, pulling the rod until fracture.",
            "Lower Beam": "Fixed base beam -- holds the LOWER jaw gripping the BOTTOM of the rod.",
            "4X Handle": "Tighten clockwise to lock the MS rod into the LOWER (middle beam) jaw first.",
            "2X Handle": "Tighten clockwise to lock the MS rod into the UPPER beam jaw after pressing UP.",
            "P Valve (red)": "Pressure Valve -- open it to allow hydraulic fluid to build pressure.",
            "L Valve (green)": "Load Valve -- open it to apply tensile load gradually on the rod.",
            "S / O / Up / Down buttons": "S=Start pump, O=Off/Stop, Up/Down arrows move the middle beam.",
            "F : / CHT : Display": "Live readout panel -- F shows Load in kN, CHT shows deformation in mm.",
        }
        for name, desc in parts.items():
            if st.button(name, use_container_width=True, key=f"part_{name}"):
                st.session_state['utm_part_sel'] = name
        if 'utm_part_sel' in st.session_state and st.session_state.utm_part_sel in parts:
            nm = st.session_state.utm_part_sel
            st.markdown(f'<div class="correct">{nm}: {parts[nm]}</div>', unsafe_allow_html=True)

    st.button("Next: Measure Specimen", on_click=lambda: st.session_state.update(scene=2), type="primary")

# ============================================================
# SCENE 2 -- MEASURE (using actual PPT Vernier caliper images)
# ============================================================
elif sc == 2:
    st.markdown('<div class="lo-badge">Scene 3 - LO2 - Apply: Measure Diameter with Vernier Caliper</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">This is your actual Vernier caliper diagram. Move the slider to record the reading in X direction, then rotate 90 degrees for Y direction.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8])
    cal_h_b64 = img_b64("vernier_caliper_horizontal.png")
    cal_v_b64 = img_b64("vernier_caliper_vertical.png")

    with col1:
        st.markdown("**Step 1 -- Measurement in X-direction**")
        if cal_h_b64:
            st.markdown(f'<img src="data:image/png;base64,{cal_h_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:8px;">', unsafe_allow_html=True)
        dx = st.slider("Reading on main + vernier scale -- X direction (mm)", 10.0, 15.0, st.session_state.dx, 0.2, key="dx_sl")
        st.session_state.dx = dx

        st.markdown("**Step 2 -- Rotate caliper 90 degrees -- Y-direction**")
        if cal_v_b64:
            st.markdown(f'<img src="data:image/png;base64,{cal_v_b64}" style="width:55%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:8px;display:block;margin:0 auto;">', unsafe_allow_html=True)
        dy = st.slider("Reading on main + vernier scale -- Y direction (mm)", 10.0, 15.0, st.session_state.dy, 0.2, key="dy_sl")
        st.session_state.dy = dy

    with col2:
        d1 = (dx + dy) / 2
        lo = round(5 * d1, 2)
        st.markdown("**Observation Table -- Initial Diameter**")
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

# ============================================================
# SCENE 3 -- FIX ROD IN UTM (using actual UTM image with overlay panel)
# ============================================================
elif sc == 3:
    st.markdown('<div class="lo-badge">Scene 4 - LO2 - Apply: Fix MS Rod in UTM Step by Step</div>', unsafe_allow_html=True)

    stage = st.session_state.utm_stage
    utm_rod_b64 = img_b64("utm_rod_inserted.png")
    utm_b64 = img_b64("utm_machine.png")

    steps_info = [
        ("Step 1", "Place MS rod into the middle beam lower jaw", "Click: Insert rod into jaw"),
        ("Step 2", "Tighten 4X handle clockwise to grip rod firmly", "Click: Tighten 4X handle"),
        ("Step 3", "Press UP button -- middle beam rises, rod enters upper jaw", "Click: Press UP button"),
        ("Step 4", "Tighten 2X handle to lock upper jaw", "Click: Tighten 2X handle"),
        ("Step 5", "Open Pressure Valve P and Load Valve L", "Click: Open valves -- ready!"),
    ]

    col_img, col_ctrl = st.columns([1.2, 0.8])
    with col_img:
        if stage == 0:
            img_show = utm_b64
            caption = "Empty UTM -- no specimen loaded yet"
        else:
            img_show = utm_rod_b64
            caption = "MS rod fixed in jaws" if stage < 5 else "Rod fixed, valves open -- ready to test!"
        if img_show:
            st.markdown(f'<img src="data:image/png;base64,{img_show}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:6px;">', unsafe_allow_html=True)
        st.caption(caption)
        if stage >= 5:
            st.success("F: 0   CHT: 0  --  Machine ready to start test")

    with col_ctrl:
        st.markdown("#### Procedure -- click each step in order")
        for i, (snum, sdesc, sinstr) in enumerate(steps_info):
            done = i < stage
            active = i == stage
            bg = "#dcfce7" if done else ("#dbeafe" if active else "#f8fafc")
            border = "#86efac" if done else ("#93c5fd" if active else "#e2e8f0")
            icon = "[done]" if done else ("[now]" if active else "[ ]")
            st.markdown(f"""<div style="background:{bg};border:1.5px solid {border};border-radius:8px;
                        padding:8px 12px;margin-bottom:6px;font-size:12px;">
                        <b>{icon} {snum}:</b> {sdesc}</div>""", unsafe_allow_html=True)

        if stage < len(steps_info):
            if st.button(steps_info[stage][2], type="primary", use_container_width=True, key="utm_btn"):
                st.session_state.utm_stage += 1
                st.rerun()
        else:
            st.markdown('<div class="correct">Rod is fixed in UTM! Ready to apply load.</div>', unsafe_allow_html=True)
            st.button("Next: Apply Load", on_click=lambda: st.session_state.update(scene=4), type="primary")

# ============================================================
# SCENE 4 -- APPLY LOAD (UTM image + live overlay readout + graph)
# ============================================================
elif sc == 4:
    st.markdown('<div class="lo-badge">Scene 5 - LO2 - Apply: Run Tensile Test -- Watch Load and Deformation</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Press NEXT LOAD STEP to increase load. Watch the F and CHT readout change on the UTM panel and the graph build live, exactly as in the real lab.</div>', unsafe_allow_html=True)

    step = st.session_state.load_step
    total = len(LOAD_DEFORM)
    F = LOAD_DEFORM[step][0]
    CHT = LOAD_DEFORM[step][1]

    col_anim, col_graph = st.columns([0.85, 1.15])

    with col_anim:
        utm_rod_b64 = img_b64("utm_rod_inserted.png")
        if CHT <= 0.09:
            phase, pc = "ELASTIC ZONE", "#2563a8"
        elif F <= 44 and CHT <= 0.4:
            phase, pc = "YIELDING ZONE", "#f59e0b"
        elif step < 22:
            phase, pc = "STRAIN HARDENING", "#16a34a"
        else:
            phase, pc = "NECKING / FRACTURE", "#dc2626"

        if utm_rod_b64:
            st.markdown(f"""
            <div class="utm-stage">
              <img src="data:image/png;base64,{utm_rod_b64}">
              <div class="utm-overlay-panel">F: {F} kN<br>CHT: {CHT:.3f} mm</div>
              <div class="utm-overlay-phase" style="color:{pc};border-color:{pc};">{phase}</div>
            </div>
            """, unsafe_allow_html=True)
        if step == total - 1:
            st.error("ROD HAS FRACTURED at the necked section")

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
        fig2.update_layout(height=300,
                           title=dict(text="Load F (kN) vs Deformation CHT (mm)", font=dict(size=12)),
                           xaxis=dict(title="CHT (mm)", range=[-0.2, 12], gridcolor="#f1f5f9"),
                           yaxis=dict(title="F (kN)", range=[-2, 65], gridcolor="#f1f5f9"),
                           plot_bgcolor="white", paper_bgcolor="white",
                           showlegend=True, legend=dict(orientation="h", y=1.1),
                           margin=dict(l=50, r=10, t=50, b=50))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Reference graph (from your course material)**")
        ref_b64 = img_b64("load_deform_reference.png")
        if ref_b64:
            st.markdown(f'<img src="data:image/png;base64,{ref_b64}" style="width:80%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:6px;display:block;margin:0 auto;">', unsafe_allow_html=True)

        import pandas as pd
        df_all = pd.DataFrame(LOAD_DEFORM[:step + 1], columns=["Load F (kN)", "CHT (mm)"])
        df_all.index = df_all.index + 1
        st.dataframe(df_all, use_container_width=True, height=160)

    if step == total - 1:
        st.success("Test complete -- rod has fractured! Proceed to post-fracture measurements.")
        st.button("Next: Post-Fracture Measurements", on_click=lambda: st.session_state.update(scene=5), type="primary")

# ============================================================
# SCENE 5 -- POST FRACTURE
# ============================================================
elif sc == 5:
    st.markdown('<div class="lo-badge">Scene 6 - LO2 - Apply: Post-Fracture Measurements</div>', unsafe_allow_html=True)
    st.markdown('<div class="instr">Join the two broken pieces end-to-end. Measure final diameter (du) at the neck and final gauge length (Lu) between the gauge marks, using the same Vernier caliper.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        cal_h_b64 = img_b64("vernier_caliper_horizontal.png")
        if cal_h_b64:
            st.markdown(f'<img src="data:image/png;base64,{cal_h_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:8px;">', unsafe_allow_html=True)
        du = st.slider("Final diameter du at neck (mm)", 4.0, 12.0, st.session_state.du, 0.2)
        st.session_state.du = du
        lu = st.slider("Final gauge length Lu (mm)", 60.0, 90.0, st.session_state.lu, 0.2)
        st.session_state.lu = lu

    with col2:
        d1 = (st.session_state.dx + st.session_state.dy) / 2
        lo = round(5 * d1, 2)
        st.markdown("**Post-Fracture Observation Table**")
        st.markdown(f"""<div class="obs-box">
        <table style="width:100%;font-size:13px;border-collapse:collapse;">
        <tr style="background:#dbeafe;"><td style="padding:5px;"><b>Parameter</b></td><td><b>Initial</b></td><td><b>Final</b></td></tr>
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">Diameter (mm)</td><td>{d1:.2f}</td><td><b style="color:#dc2626;">{du:.1f}</b></td></tr>
        <tr style="border-bottom:1px solid #e2e8f0;"><td style="padding:5px;">Gauge length (mm)</td><td>{lo:.2f}</td><td><b style="color:#2563a8;">{lu:.1f}</b></td></tr>
        <tr><td style="padding:5px;">Area (mm2)</td><td>{math.pi/4*d1**2:.2f}</td><td><b>{math.pi/4*du**2:.2f}</b></td></tr>
        </table></div>""", unsafe_allow_html=True)
        st.info(f"Elongation = Lu - L0 = {lu:.1f} - {lo:.2f} = **{lu - lo:.2f} mm**")

    st.button("Next: Calculations", on_click=lambda: st.session_state.update(scene=6), type="primary")

# ============================================================
# SCENE 6 -- CALCULATIONS
# ============================================================
elif sc == 6:
    st.markdown('<div class="lo-badge">Scene 7 - LO3 - Analyze: Calculate Material Properties</div>', unsafe_allow_html=True)

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

# ============================================================
# SCENE 7 -- IS CODE (using actual IS table image)
# ============================================================
elif sc == 7:
    st.markdown('<div class="lo-badge">Scene 8 - LO4 - Evaluate: Compare with IS 432-1 (1982)</div>', unsafe_allow_html=True)

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
        st.markdown("#### IS 432-1 (1982) -- official table (from your course material)")
        is_b64 = img_b64("is_code_table.png")
        if is_b64:
            st.markdown(f'<img src="data:image/png;base64,{is_b64}" style="width:100%;border:1px solid #e2e8f0;border-radius:8px;background:white;padding:8px;">', unsafe_allow_html=True)

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
            st.markdown('<div class="verdict-pass">SAMPLE ACCEPTED -- All parameters satisfy IS 432-1 (1982).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="verdict-fail">SAMPLE REJECTED -- One or more parameters do not meet IS 432-1 (1982).</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Your results")
        st.markdown(f"""<div class="obs-box">
        Re = <b>{Re:.2f} N/mm2</b><br>
        Rm = <b>{Rm:.2f} N/mm2</b><br>
        A3 = <b>{A3:.2f} %</b>
        </div>""", unsafe_allow_html=True)
        st.success("Experiment Complete!")

st.divider()
st.markdown("<p style='text-align:center;color:#9ca3af;font-size:0.8rem;'>Virtual Lab - Tensile Test on Mild Steel - IS 432-1 (1982) - Civil Engineering</p>", unsafe_allow_html=True)
