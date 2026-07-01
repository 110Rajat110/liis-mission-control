import streamlit as st
import plotly.graph_objects as go
from components.layout import page_header, section_header
from components.cards import metric_card, status_badge

page_header("Mission Summary", "Comprehensive overview of analysis results and actionable intelligence")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); padding: 24px; border-radius: 12px; margin-bottom: 2rem;">
            <h3 style="color: #00E5FF; margin-top: 0; margin-bottom: 16px;">Executive Intelligence Report</h3>
            <p style="color: #E2E8F0; font-size: 1.05rem; line-height: 1.6;">
                Analysis of <strong>Sector 7G (Lunar South Pole)</strong> is complete. The fused sensor data strongly indicates the presence of 
                near-surface volatiles. The primary target zone at <strong>Charlie Crater (-88.9°, -30.0°)</strong> exhibits a Peak Confidence of 94.2%.
            </p>
            <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6;">
                The proposed traverse route from Alpha Base circumvents major topographic hazards, ensuring a 92% Safety Score for the rover deployment.
                Volumetric estimates place the accessible ice mass at approximately 1.24 million kilograms.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3D Summary Chart
    categories = ['Ice Confidence', 'Terrain Safety', 'Illumination', 'Accessibility', 'Resource Value']
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[94.2, 85.0, 42.0, 78.5, 99.0],
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 229, 255, 0.2)',
        line=dict(color='#00E5FF', width=2),
        name='Charlie Crater'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[64.0, 92.0, 88.0, 95.0, 50.0],
        theta=categories,
        fill='toself',
        fillcolor='rgba(41, 121, 255, 0.2)',
        line=dict(color='#2979FF', width=2),
        name='Alpha Base'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(color="#E2E8F0", gridcolor="rgba(255,255,255,0.1)")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(color="#E2E8F0")),
        height=400,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header("Final Metrics")
    metric_card("Mission Readiness", "GO", "", True)
    st.markdown("<br>", unsafe_allow_html=True)
    metric_card("Data Integrity", "99.9%", "Verified", True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: rgba(41, 121, 255, 0.1); border: 1px solid rgba(41, 121, 255, 0.3); padding: 16px; border-radius: 8px;">
            <h4 style="color: #2979FF; margin-top: 0; margin-bottom: 12px; font-weight: 600;">System Actions</h4>
            <button style="width: 100%; background: #2979FF; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-bottom: 8px; font-family: 'Outfit', sans-serif;">GENERATE PDF REPORT</button>
            <button style="width: 100%; background: transparent; border: 1px solid #2979FF; color: #2979FF; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-family: 'Outfit', sans-serif;">TRANSMIT TO EARTH</button>
        </div>
    """, unsafe_allow_html=True)
