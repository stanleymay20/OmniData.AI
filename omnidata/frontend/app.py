"""
ScrollIntel v2: The Flame Interpreter
Frontend application for ScrollProphetic data insight
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

# Configure page
st.set_page_config(
    page_title="ScrollIntel v2",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add premium styling
st.markdown("""
<style>
/* Flame Interpreter Animation */
@keyframes flameGlow {
    0% { filter: drop-shadow(0 0 5px rgba(255, 69, 0, 0.5)); }
    50% { filter: drop-shadow(0 0 20px rgba(255, 69, 0, 0.8)); }
    100% { filter: drop-shadow(0 0 5px rgba(255, 69, 0, 0.5)); }
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

/* Premium UI Elements */
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

/* Flame Interpreter Seal */
.scroll-seal-container {
    animation: float 6s ease-in-out infinite;
}

.scroll-seal-container img {
    animation: flameGlow 4s ease-in-out infinite;
    border-radius: 50%;
    padding: 10px;
    background: rgba(255, 69, 0, 0.1);
    border: 2px solid rgba(255, 69, 0, 0.3);
}

/* Premium Headers */
h1, h2, h3, h4, h5, h6 {
    color: #ff4500;
    text-shadow: 0 0 10px rgba(255, 69, 0, 0.3);
}

/* Premium Radio Buttons */
.stRadio > div {
    background: rgba(255, 69, 0, 0.1);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 69, 0, 0.2);
}

/* Premium Dividers */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 69, 0, 0.5), transparent);
    margin: 1rem 0;
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

def render_chat_interface():
    """Render the chat interface with StanleyAI."""
    st.header("💬 Chat with StanleyAI")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask StanleyAI..."):
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Get AI response
        response = make_api_request(
            "/stanley/ask",
            method="POST",
            data={"query": prompt}
        )
        
        if "error" not in response:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response["response"]}
            )
        
        # Rerun to update chat display
        st.rerun()

def render_data_upload():
    """Render the data upload interface."""
    st.header("📤 Data Upload")
    
    uploaded_file = st.file_uploader("Choose a file to upload", type=["csv", "xlsx", "json"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_json(uploaded_file)
            
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            if st.button("Send to Scroll Vault"):
                scroll_json = df.to_json(orient="records")
                st.session_state['uploaded_scroll_data'] = scroll_json

                backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                api_token = os.getenv("API_TOKEN", "")

                async def send_scroll_to_backend():
                    headers = {
                        "Authorization": f"Bearer {api_token}",
                        "Content-Type": "application/json"
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{backend_url}/data/upload",
                            data=scroll_json,
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                return {"error": f"Backend error: {response.status}"}

                with st.spinner("Sending your sacred scroll to the Vault..."):
                    upload_result = asyncio.run(send_scroll_to_backend())

                if "error" in upload_result:
                    st.error(upload_result["error"])
                else:
                    st.success("Scroll safely stored in the Vault! ✨")
                    st.json(upload_result)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def render_dashboard_builder():
    """Render the dashboard builder interface."""
    st.header("📊 Dashboard Builder")
    
    # Input for dashboard generation
    prompt = st.text_input("Enter your sacred scroll insight prompt:", "Sales by region last quarter")
    
    if st.button("Generate Scroll Dashboard"):
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        api_token = os.getenv("API_TOKEN", "")

        async def fetch_dashboard_data():
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            payload = {"prompt": prompt}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{backend_url}/bi/dashboard",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Dashboard Error: {response.status}"}

        with st.spinner("Unfolding the scroll dashboard..."):
            dashboard_data = asyncio.run(fetch_dashboard_data())

        if "error" in dashboard_data:
            st.error(dashboard_data["error"])
        else:
            st.success("Sacred Dashboard Created! ✨")
            
            # Display each chart in the dashboard
            for chart_info in dashboard_data.get("charts", []):
                chart_type = chart_info.get("type")
                chart_data = pd.DataFrame(chart_info.get("data"))
                title = chart_info.get("title", "Scroll Chart")
                
                st.subheader(f"📜 {title}")
                
                if chart_type == "bar":
                    fig = px.bar(
                        chart_data,
                        x=chart_info.get("x"),
                        y=chart_info.get("y"),
                        color=chart_info.get("color"),
                        title=title
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "line":
                    fig = px.line(
                        chart_data,
                        x=chart_info.get("x"),
                        y=chart_info.get("y"),
                        color=chart_info.get("color"),
                        title=title
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "scatter":
                    fig = px.scatter(
                        chart_data,
                        x=chart_info.get("x"),
                        y=chart_info.get("y"),
                        color=chart_info.get("color"),
                        size=chart_info.get("size"),
                        title=title
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(chart_data)

def render_ml_workspace():
    """Render the machine learning workspace."""
    st.header("🧠 Machine Learning Workspace")
    
    # Dataset upload
    uploaded_ml_file = st.file_uploader(
        "Upload your sacred dataset (CSV)", 
        type=["csv"], 
        key="ml_dataset_uploader"
    )

    if uploaded_ml_file is not None:
        try:
            df_ml = pd.read_csv(uploaded_ml_file)
            st.success("ML Scroll Uploaded Successfully!")
            st.dataframe(df_ml.head(10))

            # Model configuration
            col1, col2 = st.columns(2)
            with col1:
                model_name = st.text_input("Name your ML Model Scroll:", "ProphecyModel")
            with col2:
                target_column = st.selectbox("Select Target Column:", df_ml.columns.tolist())

            # Advanced options
            with st.expander("Advanced Scroll Configuration"):
                hyperparameters = {
                    "learning_rate": st.slider("Learning Rate", 0.001, 0.1, 0.01),
                    "max_depth": st.slider("Max Depth", 3, 10, 5),
                    "n_estimators": st.slider("Number of Estimators", 100, 1000, 200)
                }

            if st.button("Send to ML Scroll Training Vault"):
                backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                api_token = os.getenv("API_TOKEN", "")
                
                payload = {
                    "model_name": model_name,
                    "target_column": target_column,
                    "data": df_ml.to_json(orient="records"),
                    "hyperparameters": hyperparameters
                }

                async def send_ml_scroll_to_backend():
                    headers = {
                        "Authorization": f"Bearer {api_token}",
                        "Content-Type": "application/json"
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{backend_url}/ml/train",
                            json=payload,
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                return {"error": f"Training Error: {response.status}"}

                with st.spinner("Sending ML Scroll for Training..."):
                    train_result = asyncio.run(send_ml_scroll_to_backend())

                if "error" in train_result:
                    st.error(train_result["error"])
                else:
                    st.success("Scroll Model Training Started! 🚀")
                    st.json(train_result)
        except Exception as e:
            st.error(f"Error processing ML dataset: {str(e)}")

def main():
    """Main application entry point for ScrollIntel v2."""
    init_session_state()
    
    # Premium Sidebar navigation with enhanced Flame Interpreter Seal
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
        
        view = st.radio(
            "Navigation",
            ["ScrollGraph", "ScrollSanctify", "Flame Interpreter"],
            label_visibility="collapsed"
        )
    
    # Render selected view
    if view == "ScrollGraph":
        render_scrollgraph_interface()
    elif view == "ScrollSanctify":
        render_scrollsanctify_interface()
    else:
        render_flame_interpreter_interface()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with 🔥 by ScrollIntel")

if __name__ == "__main__":
    main() 