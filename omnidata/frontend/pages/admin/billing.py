"""
Admin billing dashboard for OmniData.AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, Any

def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"

def get_revenue_metrics(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get revenue metrics from API."""
    response = requests.get(
        f"{st.session_state.api_url}/admin/billing/metrics",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        headers={"Authorization": f"Bearer {st.session_state.api_token}"}
    )
    return response.json()

def render_revenue_metrics():
    """Render revenue metrics section."""
    st.subheader("📈 Revenue Metrics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
    
    # Get metrics
    metrics = get_revenue_metrics(start_date, end_date)
    
    # Display KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric(
            "MRR",
            format_currency(metrics["mrr"]),
            f"{metrics['mrr_growth']}%"
        )
    
    with kpi2:
        st.metric(
            "Total Revenue",
            format_currency(metrics["total_revenue"]),
            f"{metrics['revenue_growth']}%"
        )
    
    with kpi3:
        st.metric(
            "Active Subscriptions",
            metrics["active_subscriptions"],
            f"{metrics['subscription_growth']}%"
        )
    
    with kpi4:
        st.metric(
            "Avg. Revenue/User",
            format_currency(metrics["arpu"]),
            f"{metrics['arpu_growth']}%"
        )
    
    # Revenue chart
    st.plotly_chart(
        px.line(
            metrics["revenue_data"],
            x="date",
            y="revenue",
            title="Daily Revenue"
        ),
        use_container_width=True
    )
    
    # Plan distribution
    st.plotly_chart(
        px.pie(
            metrics["plan_distribution"],
            values="count",
            names="plan",
            title="Subscription Plan Distribution"
        ),
        use_container_width=True
    )

def render_customer_table():
    """Render customer subscriptions table."""
    st.subheader("👥 Customer Subscriptions")
    
    # Get customer data
    response = requests.get(
        f"{st.session_state.api_url}/admin/billing/customers",
        headers={"Authorization": f"Bearer {st.session_state.api_token}"}
    )
    customers = response.json()["customers"]
    
    # Convert to DataFrame
    df = pd.DataFrame(customers)
    
    # Add action buttons
    def on_manage_click(customer_id: int):
        st.session_state.selected_customer = customer_id
    
    for idx, row in df.iterrows():
        df.loc[idx, "Actions"] = st.button(
            "Manage",
            key=f"manage_{row['id']}",
            on_click=on_manage_click,
            args=(row["id"],)
        )
    
    # Display table
    st.dataframe(
        df[["id", "email", "plan", "status", "mrr", "joined_date", "Actions"]],
        use_container_width=True
    )

def render_customer_details():
    """Render selected customer details."""
    if "selected_customer" not in st.session_state:
        return
    
    st.subheader("Customer Details")
    
    # Get customer details
    response = requests.get(
        f"{st.session_state.api_url}/admin/billing/customers/{st.session_state.selected_customer}",
        headers={"Authorization": f"Bearer {st.session_state.api_token}"}
    )
    customer = response.json()["customer"]
    
    # Display customer info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Customer Information**")
        st.write(f"Email: {customer['email']}")
        st.write(f"Plan: {customer['plan']}")
        st.write(f"Status: {customer['status']}")
        st.write(f"MRR: {format_currency(customer['mrr'])}")
    
    with col2:
        st.write("**Usage Statistics**")
        st.write(f"AI Requests: {customer['usage']['ai_requests']}")
        st.write(f"Storage Used: {customer['usage']['storage_gb']} GB")
        st.write(f"Models Deployed: {customer['usage']['model_deployments']}")
    
    # Usage chart
    st.plotly_chart(
        px.line(
            customer["usage_history"],
            x="date",
            y=["ai_requests", "storage_gb", "model_deployments"],
            title="Resource Usage History"
        ),
        use_container_width=True
    )
    
    # Invoice history
    st.write("**Invoice History**")
    st.dataframe(
        pd.DataFrame(customer["invoices"]),
        use_container_width=True
    )

def render_marketplace_metrics():
    """Render marketplace metrics."""
    st.subheader("🛍️ Marketplace Metrics")
    
    # Get marketplace data
    response = requests.get(
        f"{st.session_state.api_url}/admin/billing/marketplace",
        headers={"Authorization": f"Bearer {st.session_state.api_token}"}
    )
    marketplace = response.json()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Items",
            marketplace["total_items"],
            f"{marketplace['items_growth']}%"
        )
    
    with col2:
        st.metric(
            "Total Sales",
            format_currency(marketplace["total_sales"]),
            f"{marketplace['sales_growth']}%"
        )
    
    with col3:
        st.metric(
            "Active Sellers",
            marketplace["active_sellers"],
            f"{marketplace['sellers_growth']}%"
        )
    
    # Sales by category
    st.plotly_chart(
        px.bar(
            marketplace["sales_by_category"],
            x="category",
            y="sales",
            title="Sales by Category"
        ),
        use_container_width=True
    )

def main():
    """Main function for billing dashboard."""
    st.title("💰 Billing & Revenue Dashboard")
    
    # Navigation
    tab1, tab2, tab3 = st.tabs([
        "Revenue Metrics",
        "Customer Management",
        "Marketplace"
    ])
    
    with tab1:
        render_revenue_metrics()
    
    with tab2:
        render_customer_table()
        render_customer_details()
    
    with tab3:
        render_marketplace_metrics()

if __name__ == "__main__":
    main() 