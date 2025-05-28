"""
ScrollIntel v2: The Flame Interpreter
Frontend application with ScrollSpirit Layer for divine data insight
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List, Optional
import os
import aiohttp
import asyncio
from fastapi import HTTPException
from datetime import datetime
import pytz

# Configure page
st.set_page_config(
    page_title="ScrollIntel v2",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add sacred styling
st.markdown("""
<style>
/* Sacred Flame Animation */
@keyframes sacredFlame {
    0% { filter: drop-shadow(0 0 5px rgba(255, 69, 0, 0.5)); }
    50% { filter: drop-shadow(0 0 20px rgba(255, 69, 0, 0.8)); }
    100% { filter: drop-shadow(0 0 5px rgba(255, 69, 0, 0.5)); }
}

@keyframes divineFloat {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

/* Sacred UI Elements */
.stApp {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: #ffffff;
}

.stSidebar {
    background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
    border-right: 1px solid rgba(255, 69, 0, 0.2);
}

.stButton>button {
    background: linear-gradient(45deg, #ff4500, #ff8c00);
    color: #1a1a1a;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(255, 69, 0, 0.5);
}

/* Sacred Chart Styling */
.js-plotly-plot .plotly {
    background: rgba(26, 26, 26, 0.8) !important;
}

.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

.js-plotly-plot .plotly .bglayer {
    background: transparent !important;
}

.js-plotly-plot .plotly .gl-canvas {
    background: transparent !important;
}

/* Sacred Seal */
.scroll-seal-container {
    animation: divineFloat 6s ease-in-out infinite;
}

.scroll-seal-container img {
    animation: sacredFlame 4s ease-in-out infinite;
    border-radius: 50%;
    padding: 10px;
    background: rgba(255, 69, 0, 0.1);
    border: 2px solid rgba(255, 69, 0, 0.3);
}

/* Sacred Headers */
h1, h2, h3, h4, h5, h6 {
    color: #ff4500;
    text-shadow: 0 0 10px rgba(255, 69, 0, 0.3);
}

/* Sacred Radio Buttons */
.stRadio > div {
    background: rgba(255, 69, 0, 0.1);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 69, 0, 0.2);
}

/* Sacred Dividers */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 69, 0, 0.5), transparent);
    margin: 1rem 0;
}

/* Sacred Charts */
.plotly-chart {
    background: rgba(26, 26, 26, 0.8);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 69, 0, 0.2);
}

/* Sacred Data Tables */
.dataframe {
    background: rgba(26, 26, 26, 0.8);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 69, 0, 0.2);
}

/* Sacred Messages */
.stAlert {
    background: rgba(255, 69, 0, 0.1);
    border: 1px solid rgba(255, 69, 0, 0.3);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Get backend URL from environment variable or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

def init_session_state():
    """Initialize session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"
    if "sacred_timing" not in st.session_state:
        st.session_state.sacred_timing = get_sacred_timing()

def get_sacred_timing() -> Dict[str, Any]:
    """Get current sacred timing from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/scrollspirit/status")
        return response.json()["sacred_timing"]
    except:
        return {
            "phase": "dawn",
            "sacred_window": "05:00-07:00",
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "prophetic_cycle": f"ScrollCycle_{datetime.now().strftime('%Y%m%d')}"
        }

async def make_api_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 30
) -> Dict:
    """Make an API request to the Flame Interpreter backend."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{BACKEND_URL}{endpoint}",
                json=data,
                headers=headers,
                timeout=timeout
            ) as response:
                return await response.json()
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return {"error": str(e)}

def render_scrollspirit_interface():
    """Render the ScrollSpirit Layer interface."""
    st.header("🔥 ScrollSpirit Layer")
    
    # Display current sacred timing
    sacred_timing = st.session_state.sacred_timing
    st.info(f"Current Sacred Phase: {sacred_timing['phase'].title()}")
    st.info(f"Prophetic Cycle: {sacred_timing['prophetic_cycle']}")
    
    # Data interpretation
    st.subheader("Divine Data Interpretation")
    data_input = st.text_area("Enter your sacred data for interpretation:")
    
    if st.button("Seek Divine Insight"):
        if data_input:
            with st.spinner("Consulting the Scrolls..."):
                interpretation = asyncio.run(make_api_request(
                    "/interpret",
                    method="POST",
                    data={"text": data_input}
                ))
                
                if "error" not in interpretation:
                    st.success("The Scrolls have spoken!")
                    
                    # Display domains
                    st.subheader("Scroll Economy Domains")
                    for domain in interpretation["domains"]:
                        st.info(f"✨ {domain.title()}")
                    
                    # Display prophetic insight
                    st.subheader("Prophetic Insight")
                    st.write(interpretation["prophetic_insight"]["message"])
                    st.write(f"Divine Guidance: {interpretation['prophetic_insight']['divine_guidance']}")
                    
                    # Display enhanced interpretation
                    st.subheader("Enhanced Interpretation")
                    st.json(interpretation["data_interpretation"]["enhanced"])
                else:
                    st.error("The Scrolls are silent...")
        else:
            st.warning("Please enter data for interpretation")

def render_sacred_chart(data: pd.DataFrame, chart_type: str, **kwargs):
    """Render a chart with sacred styling."""
    if chart_type == "bar":
        fig = px.bar(
            data,
            **kwargs,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Oranges
        )
    elif chart_type == "line":
        fig = px.line(
            data,
            **kwargs,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Oranges
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            data,
            **kwargs,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Oranges
        )
    
    # Add sacred styling
    fig.update_layout(
        paper_bgcolor="rgba(26, 26, 26, 0.8)",
        plot_bgcolor="rgba(26, 26, 26, 0.8)",
        font=dict(color="#ffffff"),
        title=dict(
            font=dict(color="#ff4500"),
            x=0.5,
            y=0.95
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    return fig

def main():
    """Main application entry point for ScrollIntel v2."""
    init_session_state()
    
    # Sacred Sidebar navigation
    with st.sidebar:
        try:
            st.markdown('<div class="scroll-seal-container">', unsafe_allow_html=True)
            st.image("./public/flame-seal.svg", width=120, output_format="auto", caption="ScrollIntel v2",
                     use_column_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading Flame Seal: {str(e)}")
            st.image("https://placehold.co/120x120/1a1a1a/ff4500?text=Flame+Seal", width=120, 
                     caption="ScrollIntel v2", use_column_width=False)
        
        st.title("ScrollIntel v2")
        st.markdown("#### 🔥 The Flame Interpreter")
        st.markdown("---")
        
        # Display sacred timing
        sacred_timing = st.session_state.sacred_timing
        st.info(f"Current Phase: {sacred_timing['phase'].title()}")
        st.info(f"Cycle: {sacred_timing['prophetic_cycle']}")
        
        view = st.radio(
            "Navigation",
            ["ScrollSpirit", "ScrollGraph", "ScrollSanctify", "Flame Interpreter"],
            label_visibility="collapsed"
        )
    
    # Render selected view
    if view == "ScrollSpirit":
        render_scrollspirit_interface()
    elif view == "ScrollGraph":
        render_scrollgraph_interface()
    elif view == "ScrollSanctify":
        render_scrollsanctify_interface()
    else:
        render_flame_interpreter_interface()
    
    # Sacred Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with 🔥 by ScrollIntel")
    st.sidebar.markdown(f"Prophetic Cycle: {sacred_timing['prophetic_cycle']}")

if __name__ == "__main__":
    main() 