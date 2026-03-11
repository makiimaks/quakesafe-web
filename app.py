import streamlit as st
from roboflow import Roboflow

# --- CONFIGURATION ---
st.set_page_config(page_title="QuakeSafe AI", page_icon="🚨")

# Setup Roboflow
rf = Roboflow(api_key="Rj2YqGsFTUbqH8zvjt89") 
project = rf.project("quakesafe-fddoq")
model = project.version(7).model 

st.title("🚨 QuakeSafe: Earthquake Hazard Detector")

uploaded_file = st.file_uploader("Upload a room photo for safety analysis", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    results = model.predict("temp.jpg", confidence=15).json()
    st.image("temp.jpg", use_container_width=True)

    # 1. POINT VALUES
    hazard_values = {
        "Blocked exits or pathways": 5,
        "Exposed electrical wires": 5,
        "Heavy objects in elevated or overhead areas": 4,
        "Dangerous chemicals that may spill": 3,
        "Structural defects": 3,
        "Glass or ceramics that may fall or shatter": 2,
        "Sharp edges from furniture": 2
    }

    # 2. SCORING LOGIC
    actual_score = 0
    detected_classes = set()

    for p in results['predictions']:
        hazard_name = p['class']
        if hazard_name in hazard_values:
            if hazard_name not in detected_classes:
                actual_score += hazard_values[hazard_name]
                detected_classes.add(hazard_name)

    # 3. MATH: NORMALIZED CATEGORY RISK (NCR)
    if detected_classes:
        dynamic_max_potential = len(detected_classes) * 5 
        risk_percentage = (actual_score / dynamic_max_potential) * 100
    else:
        risk_percentage = 0.0
        dynamic_max_potential = 0

    # 4. LAYOUT PART A: DETECTED HAZARD DETAILS (Shows first)
    st.markdown("---")
    st.subheader("📝 Detected Hazard Details")
    
    if detected_classes:
        for hazard in detected_classes:
            points = hazard_values[hazard]
            if points == 5:
                st.error(f"⚠️ **{hazard}** (High Severity: +{points} pts)")
            elif points == 4:
                st.warning(f"📦 **{hazard}** (Medium Severity: +{points} pts)")
            else:
                st.info(f"🔍 **{hazard}** (Low Severity: +{points} pts)")
        
        st.caption(f"Detected {len(detected_classes)} out of 7 possible hazard categories.")
    else:
        st.success("✅ No hazards identified in the uploaded image.")

    # 5. LAYOUT PART B: RISK ANALYSIS & PROGRESS BAR (Shows second)
    st.subheader(f"Risk Analysis: {risk_percentage:.1f}%")
    st.progress(risk_percentage / 100) 

    # 6. LAYOUT PART C: FINAL STATUS ALERT
    if risk_percentage >= 60:
        st.error(f"🔴 HIGH RISK ({risk_percentage:.1f}%). Multiple severe hazards detected.")
    elif 30 <= risk_percentage < 60:
        st.warning(f"🟡 MODERATE RISK ({risk_percentage:.1f}%). Room needs safety adjustments.")
    else:
        st.success(f"🟢 LOW RISK ({risk_percentage:.1f}%). Room is relatively safe.")
    
    st.write(f"Detected {len(detected_classes)} out of 7 hazard categories.")




