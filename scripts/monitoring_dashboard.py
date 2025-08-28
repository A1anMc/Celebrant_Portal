#!/usr/bin/env python3
"""
Real-time monitoring dashboard for Melbourne Celebrant Portal.
Provides live system monitoring and alerting capabilities.
"""

import asyncio
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psutil
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

from backend.app.core.monitoring.health_checks import health_checker
from backend.app.core.monitoring import metrics

console = Console()

class MonitoringDashboard:
    """Real-time monitoring dashboard."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.health_history = []
        self.alert_history = []
        self.start_time = datetime.now()
    
    async def run_dashboard(self):
        """Run the monitoring dashboard."""
        console.print("[bold blue]Melbourne Celebrant Portal - Monitoring Dashboard[/bold blue]")
        console.print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print("Press Ctrl+C to exit\n")
        
        with Live(self.generate_dashboard(), refresh_per_second=1) as live:
            while True:
                try:
                    # Update dashboard
                    live.update(self.generate_dashboard())
                    
                    # Run health check every 30 seconds
                    if len(self.health_history) == 0 or \
                       (datetime.now() - self.health_history[-1]["timestamp"]).seconds > 30:
                        await self.run_health_check()
                    
                    await asyncio.sleep(1)
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Monitoring stopped[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    await asyncio.sleep(5)
    
    async def run_health_check(self):
        """Run a health check and store results."""
        try:
            health_results = await health_checker.run_full_health_check()
            health_results["timestamp"] = datetime.now()
            self.health_history.append(health_results)
            
            # Keep only last 100 health checks
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            # Check for alerts
            if health_checker.should_alert(health_results):
                self.alert_history.append({
                    "timestamp": datetime.now(),
                    "message": f"System health degraded: {health_results.get('overall_status')}",
                    "details": health_results
                })
                
                # Keep only last 50 alerts
                if len(self.alert_history) > 50:
                    self.alert_history = self.alert_history[-50:]
                
                console.print(f"[red]ALERT: {self.alert_history[-1]['message']}[/red]")
                
        except Exception as e:
            console.print(f"[red]Health check failed: {e}[/red]")
    
    def generate_dashboard(self) -> Layout:
        """Generate the dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split_column(
            Layout(name="health"),
            Layout(name="performance")
        )
        
        layout["right"].split_column(
            Layout(name="alerts"),
            Layout(name="metrics")
        )
        
        # Header
        layout["header"].update(Panel(
            f"[bold blue]Melbourne Celebrant Portal - System Monitor[/bold blue]\n"
            f"Uptime: {self.get_uptime()} | "
            f"Last Health Check: {self.get_last_health_check()}",
            style="blue"
        ))
        
        # Health Status
        layout["health"].update(self.generate_health_table())
        
        # Performance Metrics
        layout["performance"].update(self.generate_performance_table())
        
        # Alerts
        layout["alerts"].update(self.generate_alerts_panel())
        
        # System Metrics
        layout["metrics"].update(self.generate_metrics_panel())
        
        # Footer
        layout["footer"].update(Panel(
            f"[dim]Monitoring Dashboard | "
            f"Health Checks: {len(self.health_history)} | "
            f"Alerts: {len(self.alert_history)} | "
            f"API: {self.api_url}[/dim]",
            style="dim"
        ))
        
        return layout
    
    def generate_health_table(self) -> Panel:
        """Generate health status table."""
        if not self.health_history:
            return Panel("No health data available", title="System Health")
        
        latest_health = self.health_history[-1]
        checks = latest_health.get("checks", {})
        
        table = Table(title="System Health Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="green")
        table.add_column("Last Check", style="dim")
        
        for component_name, component_data in checks.items():
            status = component_data.get("status", "unknown")
            status_style = {
                "healthy": "green",
                "warning": "yellow",
                "unhealthy": "red"
            }.get(status, "white")
            
            details = self.get_component_details(component_data)
            last_check = component_data.get("last_check", "unknown")
            
            table.add_row(
                component_name.title(),
                f"[{status_style}]{status}[/{status_style}]",
                details,
                last_check
            )
        
        return Panel(table, title="System Health")
    
    def generate_performance_table(self) -> Panel:
        """Generate performance metrics table."""
        if not self.health_history:
            return Panel("No performance data available", title="Performance")
        
        latest_health = self.health_history[-1]
        performance = latest_health.get("performance", {})
        
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # System metrics
        system_checks = latest_health.get("checks", {}).get("system", {})
        if system_checks:
            table.add_row("CPU Usage", f"{system_checks.get('cpu_usage', 0)}%")
            table.add_row("Memory Usage", f"{system_checks.get('memory_usage', 0)}%")
            table.add_row("Disk Usage", f"{system_checks.get('disk_usage', 0)}%")
        
        # Application metrics
        app_checks = latest_health.get("checks", {}).get("application", {})
        if app_checks:
            table.add_row("Error Rate", f"{app_checks.get('error_rate', 0)}%")
            table.add_row("Avg Response Time", f"{app_checks.get('avg_response_time', 0)}ms")
            table.add_row("Total Requests", str(app_checks.get("total_requests", 0)))
        
        # Database metrics
        db_checks = latest_health.get("checks", {}).get("database", {})
        if db_checks:
            table.add_row("DB Query Time", f"{db_checks.get('query_time', 0)}ms")
            table.add_row("DB Size", db_checks.get("database_size", "unknown"))
        
        return Panel(table, title="Performance Metrics")
    
    def generate_alerts_panel(self) -> Panel:
        """Generate alerts panel."""
        if not self.alert_history:
            return Panel("No alerts", title="Recent Alerts", style="green")
        
        # Show last 5 alerts
        recent_alerts = self.alert_history[-5:]
        
        alert_text = ""
        for alert in recent_alerts:
            timestamp = alert["timestamp"].strftime("%H:%M:%S")
            message = alert["message"]
            alert_text += f"[red]{timestamp}[/red]: {message}\n"
        
        return Panel(alert_text, title="Recent Alerts", style="red")
    
    def generate_metrics_panel(self) -> Panel:
        """Generate system metrics panel."""
        try:
            # Get current metrics
            current_metrics = metrics.get_metrics()
            
            table = Table(title="Live Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Request Count", str(current_metrics.get("request_count", 0)))
            table.add_row("Error Count", str(current_metrics.get("error_count", 0)))
            table.add_row("Avg Response Time", f"{current_metrics.get('avg_response_time', 0):.2f}ms")
            table.add_row("Database Queries", str(current_metrics.get("database_queries", 0)))
            table.add_row("Auth Failures", str(current_metrics.get("auth_failures", 0)))
            
            return Panel(table, title="Live Metrics")
            
        except Exception as e:
            return Panel(f"Error loading metrics: {e}", title="Live Metrics", style="red")
    
    def get_component_details(self, component_data: Dict[str, Any]) -> str:
        """Get formatted details for a component."""
        if component_data.get("status") == "unhealthy":
            return f"Error: {component_data.get('error', 'Unknown error')}"
        
        details = []
        
        if "connection" in component_data:
            details.append(f"Connection: {component_data['connection']}")
        
        if "query_time" in component_data:
            details.append(f"Query: {component_data['query_time']}ms")
        
        if "ping_time" in component_data:
            details.append(f"Ping: {component_data['ping_time']}ms")
        
        if "user_count" in component_data:
            details.append(f"Users: {component_data['user_count']}")
        
        return " | ".join(details) if details else "OK"
    
    def get_uptime(self) -> str:
        """Get system uptime."""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{uptime.days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_last_health_check(self) -> str:
        """Get last health check time."""
        if not self.health_history:
            return "Never"
        
        last_check = self.health_history[-1]["timestamp"]
        time_diff = datetime.now() - last_check
        return f"{time_diff.seconds}s ago"

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Melbourne Celebrant Portal Monitoring Dashboard")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="API URL (default: http://localhost:8000)")
    parser.add_argument("--interval", type=int, default=30,
                       help="Health check interval in seconds (default: 30)")
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard(args.api_url)
    
    try:
        await dashboard.run_dashboard()
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Dashboard error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
