import streamlit as st
from config.theme import Colors

def metric_card(title: str, value: str, delta: str = None, is_positive: bool = True):
    """Renders a glassmorphism metric card using HTML/CSS inside Streamlit."""
    delta_color = Colors.PRIMARY if is_positive else Colors.ACCENT
    delta_html = f'<span style="color: {delta_color}; font-size: 0.9rem; font-weight: 600; margin-left: 8px;">{delta}</span>' if delta else ''
    
    st.markdown(f"""
        <div style="
            background: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, border-color 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.borderColor='{Colors.PRIMARY}'" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='{Colors.BORDER}'">
            <div style="color: {Colors.TEXT_SECONDARY}; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 8px;">
                {title}
            </div>
            <div style="display: flex; align-items: baseline;">
                <div style="color: {Colors.TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                    {value}
                </div>
                {delta_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def status_badge(status: str, variant: str = "success"):
    """Renders a glowing status badge."""
    colors = {
        "success": ("#00E5FF", "rgba(0, 229, 255, 0.1)"),
        "warning": ("#FFAB00", "rgba(255, 171, 0, 0.1)"),
        "danger": ("#F43F5E", "rgba(244, 63, 94, 0.1)"),
        "info": ("#2979FF", "rgba(41, 121, 255, 0.1)")
    }
    
    text_color, bg_color = colors.get(variant, colors["info"])
    
    return f'<span style="background: {bg_color}; color: {text_color}; border: 1px solid {text_color}; padding: 4px 12px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 0 10px {bg_color};">{status}</span>'
