"""
OmniData.AI Streamlit Frontend
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List
import os

# Configure page
st.set_page_config(
    page_title="OmniData.AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

def init_session_state():
    """Initialize session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"

def make_api_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an API request to the backend."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{API_URL}{endpoint}", headers=headers, json=data)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
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
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)
        
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        if st.button("Process Data"):
            # TODO: Implement data processing logic
            st.success("Data processing started!")

def render_dashboard_builder():
    """Render the dashboard builder interface."""
    st.header("📊 Dashboard Builder")
    
    # Sample data source selection
    data_source = st.selectbox(
        "Select Data Source",
        ["Sales Data", "Customer Analytics", "Product Metrics"]
    )
    
    # Metric selection
    metrics = st.multiselect(
        "Select Metrics",
        ["Revenue", "Orders", "Customers", "Average Order Value"]
    )
    
    # Dimension selection
    dimensions = st.multiselect(
        "Select Dimensions",
        ["Date", "Product Category", "Region", "Customer Segment"]
    )
    
    if st.button("Generate Dashboard"):
        if metrics and dimensions:
            response = make_api_request(
                "/bi/dashboard",
                method="POST",
                data={
                    "data_source": data_source,
                    "metrics": metrics,
                    "dimensions": dimensions
                }
            )
            
            if "error" not in response:
                st.success("Dashboard generated successfully!")
                # TODO: Display dashboard components
        else:
            st.warning("Please select at least one metric and dimension.")

def render_ml_workspace():
    """Render the machine learning workspace."""
    st.header("🧠 Machine Learning Workspace")
    
    # Model configuration
    model_type = st.selectbox(
        "Select Model Type",
        ["Classification", "Regression", "Clustering"]
    )
    
    target_column = st.text_input("Target Column")
    
    # Advanced options
    with st.expander("Advanced Options"):
        hyperparameters = {
            "learning_rate": st.slider("Learning Rate", 0.001, 0.1, 0.01),
            "max_depth": st.slider("Max Depth", 3, 10, 5),
            "n_estimators": st.slider("Number of Estimators", 100, 1000, 200)
        }
    
    if st.button("Train Model"):
        if target_column:
            response = make_api_request(
                "/ml/train",
                method="POST",
                data={
                    "dataset_path": "current_dataset",  # TODO: Update with actual path
                    "target_column": target_column,
                    "model_type": model_type.lower(),
                    "hyperparameters": hyperparameters
                }
            )
            
            if "error" not in response:
                st.success("Model training started!")
        else:
            st.warning("Please specify a target column.")

def main():
    """Main application."""
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("OmniData.AI")
    st.sidebar.image("logo.png", width=100)  # TODO: Add logo
    
    view = st.sidebar.radio(
        "Navigation",
        ["Chat", "Data Upload", "Dashboard Builder", "ML Workspace"]
    )
    
    # Render selected view
    if view == "Chat":
        render_chat_interface()
    elif view == "Data Upload":
        render_data_upload()
    elif view == "Dashboard Builder":
        render_dashboard_builder()
    else:
        render_ml_workspace()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with ❤️ by OmniData.AI")

if __name__ == "__main__":
    main() 