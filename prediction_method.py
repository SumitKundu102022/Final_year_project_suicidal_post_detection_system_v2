import streamlit as st
import plotly.express as px
import pandas as pd

def display_prediction(prediction, bdi_score, severity):
    """Function to display prediction results in UI."""
    if prediction > 0.5:
        st.warning("⚠ This post has been identified as a *Potential Suicide Post*")
    else:
        st.success("✅ This post has been identified as a *Non-Suicide Post*")
    
    st.info(f"The model predicts with a *{prediction * 100:.2f}%* probability that this post is a "
            f"{'*Potential Suicide Post' if prediction > 0.5 else 'Non-Suicide Post*'}.")
    
    # Display BDI-II Score and Severity
    st.info(f"*BDI-II Score:* {bdi_score}  \n*Severity Level:* {severity}")
    
    # Doctor consultancy suggestion based on severity (specific to India - West Bengal)
    if severity == "Minimal Depression":
        st.success("🧘 You appear to have minimal depressive symptoms. Maintain healthy routines and self-care practices.")
    elif severity == "Mild Depression":
        st.warning("💬 You may benefit from speaking to a counselor. Early support is helpful.")
        st.markdown("""
        📞 *Talk to a trained counselor:*  
        - *KIRAN Helpline (India, 24x7):* 14416  
        - *Institute of Psychiatry, Kolkata:* 033 2225 0779
        """)
    elif severity == "Moderate Depression":
        st.error("🧑‍⚕ You should consult a mental health professional in West Bengal soon.")
        st.markdown("""
        📞 *Mental Health Helplines:*  
        - *KIRAN National Helpline:* 14416  
        - *Kolkata Mental Health Clinic:* 033 2461 9000  
        - *Institute of Psychiatry, Kolkata:* 033 2225 0779
        """)
    elif severity == "Severe Depression":
        st.error("🚨 Immediate help is recommended. Reach out to a psychiatrist or emergency mental health service.")
        st.markdown("""
        📞 *Emergency Support (West Bengal):*  
        - *KIRAN Helpline (24x7): 14416*  
        - *Institute of Psychiatry (IOP), Kolkata:* 033 2225 0779  
        - *Mental Health Foundation, Kolkata:* 98300 65774  
        - Or visit the nearest government hospital or psychiatric unit.
        """)
    
    # Data for probability chart
    class_label = ["Potential Suicide Post", "Non-Suicide Post"]
    prob_list = [prediction * 100, 100 - prediction * 100]
    df_prob = pd.DataFrame({"Post Classification": class_label, "Probability (%)": prob_list})
    
    # Plotly bar chart for probability comparison
    fig = px.bar(df_prob, x='Post Classification', y='Probability (%)', color='Post Classification',
                 title="Prediction Probability Comparison", text_auto=True)
    fig.update_layout(xaxis_title="Post Classification", yaxis_title="Probability (%)")
    
    st.plotly_chart(fig, use_container_width=True)