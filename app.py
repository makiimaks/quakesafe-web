import streamlit as st
from roboflow import Roboflow

# Setup
rf = Roboflow(api_key="Rj2YqGsFTUbqH8zvjt89") 
project = rf.project("quakesafe-fddoq")
model = project.version(5).model 

st.title("🛡️ QuakeSafe: Earthquake Hazard Detector")

uploaded_file = st.file_uploader("Upload a room photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    results = model.predict("temp.jpg", confidence=25).json()
    st.image("temp.jpg", use_container_width=True)

    # 1. DEFINE POINT VALUES (From Table 1)
    hazard_values = {
        "Blocked exits or pathways": 5,
        "Exposed electrical wires": 5,
        "Heavy objects in elevated or overhead areas": 4,
        "Dangerous chemicals that may spill": 3,
        "Structural defects": 3,
        "Glass or ceramics that may fall or shatter": 2,
        "Sharp edges from furniture": 2
    }

    # 2. CALCULATE MAX POTENTIAL SCORE
    # This is the sum of all possible hazards (Total = 24)
    max_possible_score = sum(hazard_values.values()) 

    # 3. CALCULATE ACTUAL SCORE
    actual_score = 0
    detected_classes = set() # To avoid double-counting the same type of hazard

    for p in results['predictions']:
        hazard_name = p['class']
        if hazard_name in hazard_values:
            # We add the score only once per category for the percentage
            if hazard_name not in detected_classes:
                actual_score += hazard_values[hazard_name]
                detected_classes.add(hazard_name)

    # 4. CALCULATE RISK PERCENTAGE
    risk_percentage = (actual_score / max_possible_score) * 100

# 5. DETAILED HAZARD LIST
    st.markdown("---")
    st.subheader("📝 Detected Hazard Details")
    
    if detected_classes:
        # We create a nice list showing exactly what the AI found
        for hazard in detected_classes:
            points = hazard_values[hazard]
            
            # Using different icons to make it look professional
            if points == 5:
                st.error(f"⚠️ **{hazard}** (High Severity: +5 pts)")
            elif points == 4:
                st.warning(f"📦 **{hazard}** (Medium Severity: +4 pts)")
            else:
                st.info(f"🔍 **{hazard}** (Low Severity: +{points} pts)")
                
        st.caption(f"Detected {len(detected_classes)} out of 7 possible hazard categories.")
    else:
        st.success("✅ No specific hazards identified from the 7 monitored categories.")

    # 6. DISPLAY RESULTS
    st.subheader(f"Risk Analysis: {risk_percentage:.1f}%")
    st.progress(risk_percentage / 100) # Visual loading bar

    if risk_percentage >= 60:
        st.error(f"🔴 HIGH RISK ({risk_percentage:.1f}%). Multiple severe hazards detected.")
    elif 30 <= risk_percentage < 60:
        st.warning(f"🟡 MODERATE RISK ({risk_percentage:.1f}%). Room needs safety adjustments.")
    else:
        st.success(f"🟢 LOW RISK ({risk_percentage:.1f}%). Room is relatively safe.")
    
    st.write(f"Detected {len(detected_classes)} out of 7 hazard categories.")