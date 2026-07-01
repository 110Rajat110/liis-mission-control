import streamlit as st
from components.layout import page_header

page_header("About LIIS", "Lunar Ice Intelligence System")

st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); padding: 32px; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h1 style="font-size: 4rem; margin-bottom: 0; color: #00E5FF; font-family: 'JetBrains Mono', monospace; letter-spacing: -2px;">LIIS</h1>
        <p style="color: #94A3B8; font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase;">v1.0 Prototype</p>
        
        <div style="margin-top: 32px; color: #E2E8F0; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.6;">
            Built for the <strong>Bharatiya Antariksh Hackathon</strong>, this application demonstrates a next-generation 
            Mission Control Operating System tailored for the detection, analysis, and utilization of lunar water-ice.
        </div>
        
        <div style="margin-top: 48px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px;">
            <p style="color: #94A3B8; font-size: 0.9rem;">
                Powered by Python, Streamlit, Plotly, and PyDeck.<br>
                UI inspired by SpaceX, NASA, and modern spatial computing systems.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
