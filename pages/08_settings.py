import streamlit as st
from components.layout import page_header, section_header

page_header("System Settings", "Configure application preferences and telemetry feeds")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); padding: 24px; border-radius: 12px; margin-bottom: 2rem;">
            <h3 style="color: #E2E8F0; margin-top: 0;">Display Preferences</h3>
            <div style="margin-top: 16px;">
                <label style="color: #94A3B8; font-size: 0.9rem;">Theme Mode</label>
                <div style="color: #00E5FF; font-weight: bold; padding: 8px 0;">Deep Space (Forced)</div>
            </div>
            <div style="margin-top: 16px;">
                <label style="color: #94A3B8; font-size: 0.9rem;">Animation Quality</label>
                <select style="width: 100%; background: #0B0E14; color: white; border: 1px solid #334155; padding: 8px; border-radius: 4px; margin-top: 4px;">
                    <option>Cinematic (High)</option>
                    <option>Performance (Low)</option>
                </select>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); padding: 24px; border-radius: 12px; margin-bottom: 2rem;">
            <h3 style="color: #E2E8F0; margin-top: 0;">Data Connections</h3>
            <div style="margin-top: 16px;">
                <label style="color: #94A3B8; font-size: 0.9rem;">Telemetry Uplink</label>
                <div style="color: #00E5FF; padding: 8px 0; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 8px; height: 8px; background: #00E5FF; border-radius: 50%; box-shadow: 0 0 10px #00E5FF;"></div>
                    Connected (ISRO Deep Space Network)
                </div>
            </div>
            <div style="margin-top: 16px;">
                <label style="color: #94A3B8; font-size: 0.9rem;">Database Sync</label>
                 <div style="color: #00E5FF; padding: 8px 0; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 8px; height: 8px; background: #00E5FF; border-radius: 50%; box-shadow: 0 0 10px #00E5FF;"></div>
                    Synchronized
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

if st.button("Apply Configuration", type="primary"):
    st.success("Settings updated successfully.")
