"""
Preview script for OmniData.AI key management system.
"""

import os
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from omnidata.security.key_manager import KeyManager
from redis import Redis
from faker import Faker

console = Console()
fake = Faker()

def simulate_redis():
    """Create a simulated Redis instance for preview."""
    try:
        return Redis(host='localhost', port=6379, db=0)
    except:
        console.print("[yellow]Warning: Redis not available, using mock data[/yellow]")
        return None

def create_key_status_table() -> Table:
    """Create a table showing API key statuses."""
    table = Table(title="🔑 API Key Status")
    
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Usage Today", style="yellow")
    table.add_column("Last Rotation", style="magenta")
    
    services = {
        "OPENAI": os.getenv('OPENAI_API_KEY'),
        "HUGGINGFACE": os.getenv('HUGGINGFACE_API_KEY'),
        "GEMINI": os.getenv('GEMINI_KEY'),
        "ELEVENLABS": os.getenv('ELEVENLABS_API_KEY'),
        "STRIPE": os.getenv('STRIPE_SECRET_KEY'),
        "PAYPAL": os.getenv('PAYPAL_CLIENT_ID')
    }
    
    for service, key in services.items():
        status = "🟢 Active" if key else "🔴 Missing"
        usage = fake.random_int(min=0, max=1000)
        threshold = int(os.getenv('SECURITY_ALERT_THRESHOLD', 100))
        usage_str = f"{usage}/{threshold}"
        rotation = fake.date_time_this_month().strftime("%Y-%m-%d %H:%M")
        
        table.add_row(
            service,
            status,
            usage_str,
            rotation
        )
    
    return table

def create_security_panel() -> Panel:
    """Create a panel showing security settings."""
    settings = [
        f"🔄 Key Rotation: {os.getenv('KEY_ROTATION_INTERVAL_DAYS', 30)} days",
        f"🔒 SSL: {os.getenv('SSL_ENABLED', 'true')}",
        f"🌍 Geo-Restriction: {os.getenv('GEO_RESTRICTION_ENABLED', 'true')}",
        f"🚫 Rate Limit: {os.getenv('IP_RATE_LIMIT_REQUESTS', 100)}/{os.getenv('IP_RATE_LIMIT_WINDOW_MINUTES', 15)}min",
        f"🔐 PCI Compliance: {os.getenv('PCI_COMPLIANCE_MODE', 'true')}",
        f"🛡️ CSP Enabled: {os.getenv('CSP_ENABLED', 'true')}"
    ]
    
    return Panel(
        "\n".join(settings),
        title="🔒 Security Settings",
        border_style="blue"
    )

def create_monitoring_panel() -> Panel:
    """Create a panel showing monitoring status."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    alerts = [
        f"[green]{current_time} - System operational[/green]",
        f"[yellow]{fake.date_time_this_hour().strftime('%H:%M:%S')} - High API usage detected (OpenAI)[/yellow]",
        f"[blue]{fake.date_time_this_hour().strftime('%H:%M:%S')} - Key rotation scheduled for Stripe[/blue]",
        f"[yellow]{fake.date_time_this_hour().strftime('%H:%M:%S')} - Rate limit warning for IP {fake.ipv4()}[/yellow]",
        f"[red]{fake.date_time_this_hour().strftime('%H:%M:%S')} - Failed auth attempt from {fake.country()}[/red]"
    ]
    
    return Panel(
        "\n".join(alerts),
        title="🚨 Security Alerts",
        border_style="red"
    )

def create_stats_panel() -> Panel:
    """Create a panel showing usage statistics."""
    stats = [
        f"📊 Total API Calls Today: {fake.random_int(min=1000, max=10000)}",
        f"🌐 Active Services: {fake.random_int(min=4, max=6)}/6",
        f"🔑 Keys Rotated This Month: {fake.random_int(min=1, max=5)}",
        f"⚠️ Security Incidents: {fake.random_int(min=0, max=3)}",
        f"🚫 Blocked IPs: {fake.random_int(min=0, max=50)}"
    ]
    
    return Panel(
        "\n".join(stats),
        title="📈 Statistics",
        border_style="green"
    )

def preview_key_management():
    """Run an interactive preview of the key management system."""
    console.clear()
    console.print("[bold blue]OmniData.AI Key Management Preview[/bold blue]")
    
    try:
        layout = Layout()
        layout.split_column(
            Layout(name="upper", ratio=3),
            Layout(name="lower", ratio=2)
        )
        layout["upper"].split_row(
            Layout(name="keys", ratio=2),
            Layout(name="security")
        )
        layout["lower"].split_row(
            Layout(name="monitoring"),
            Layout(name="stats")
        )
        
        with Live(layout, refresh_per_second=1) as live:
            while True:
                # Update displays
                layout["keys"].update(create_key_status_table())
                layout["security"].update(create_security_panel())
                layout["monitoring"].update(create_monitoring_panel())
                layout["stats"].update(create_stats_panel())
                
                time.sleep(2)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Preview stopped by user (Ctrl+C)[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
    finally:
        console.print("\n[green]Preview completed[/green]")

if __name__ == "__main__":
    preview_key_management() 