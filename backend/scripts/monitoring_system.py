#!/usr/bin/env python3
"""
Comprehensive Monitoring System for Melbourne Celebrant Portal
Provides real-time monitoring, alerting, and maintenance automation.
"""

import sys
import os
import json
import asyncio
import time
import psutil
import requests
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import threading
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics data class."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    uptime: float
    active_connections: int
    response_time: float
    error_rate: float

@dataclass
class Alert:
    """Alert data class."""
    timestamp: datetime
    level: str  # 'info', 'warning', 'critical'
    category: str
    message: str
    details: Dict[str, Any]

class SystemMonitor:
    """Comprehensive system monitoring and alerting."""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config = self.load_config(config_path)
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.monitoring_interval = self.config.get("monitoring_interval", 60)  # seconds
        self.retention_days = self.config.get("retention_days", 30)
        
        # Initialize monitoring targets
        self.backend_url = self.config.get("backend_url", "http://localhost:8005")
        self.frontend_url = self.config.get("frontend_url", "http://localhost:3005")
        
        # Alert handlers
        self.alert_handlers = {
            "email": self.send_email_alert,
            "slack": self.send_slack_alert,
            "log": self.log_alert
        }
        
        logger.info("System monitor initialized")

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration."""
        default_config = {
            "alert_thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "response_time_ms": 2000.0,
                "error_rate_percent": 5.0
            },
            "monitoring_interval": 60,
            "retention_days": 30,
            "backend_url": "http://localhost:8005",
            "frontend_url": "http://localhost:3005",
            "email_config": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            "slack_config": {
                "enabled": False,
                "webhook_url": ""
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Create default config file
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics."""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            # Active connections
            active_connections = len(psutil.net_connections())
            
            # Response time and error rate
            response_time, error_rate = await self.measure_api_performance()
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_data,
                uptime=uptime,
                active_connections=active_connections,
                response_time=response_time,
                error_rate=error_rate
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={},
                uptime=0.0,
                active_connections=0,
                response_time=0.0,
                error_rate=100.0
            )

    async def measure_api_performance(self) -> tuple[float, float]:
        """Measure API response time and error rate."""
        response_times = []
        errors = 0
        total_requests = 0
        
        endpoints = ["/health", "/", "/docs"]
        
        for endpoint in endpoints:
            total_requests += 1
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                
                if response.status_code >= 400:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                logger.warning(f"API request failed for {endpoint}: {e}")
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        error_rate = (errors / total_requests) * 100 if total_requests > 0 else 100
        
        return avg_response_time, error_rate

    def check_thresholds(self, metrics: SystemMetrics) -> List[Alert]:
        """Check metrics against thresholds and generate alerts."""
        alerts = []
        
        # CPU threshold check
        if metrics.cpu_percent > self.alert_thresholds.get("cpu_percent", 80):
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning" if metrics.cpu_percent < 95 else "critical",
                category="performance",
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%",
                details={"cpu_percent": metrics.cpu_percent, "threshold": self.alert_thresholds.get("cpu_percent", 80)}
            ))
        
        # Memory threshold check
        if metrics.memory_percent > self.alert_thresholds.get("memory_percent", 85):
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning" if metrics.memory_percent < 95 else "critical",
                category="performance",
                message=f"High memory usage: {metrics.memory_percent:.1f}%",
                details={"memory_percent": metrics.memory_percent, "threshold": self.alert_thresholds.get("memory_percent", 85)}
            ))
        
        # Disk threshold check
        if metrics.disk_percent > self.alert_thresholds.get("disk_percent", 90):
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning" if metrics.disk_percent < 95 else "critical",
                category="storage",
                message=f"High disk usage: {metrics.disk_percent:.1f}%",
                details={"disk_percent": metrics.disk_percent, "threshold": self.alert_thresholds.get("disk_percent", 90)}
            ))
        
        # Response time threshold check
        if metrics.response_time > self.alert_thresholds.get("response_time_ms", 2000):
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning" if metrics.response_time < 5000 else "critical",
                category="performance",
                message=f"Slow response time: {metrics.response_time:.1f}ms",
                details={"response_time": metrics.response_time, "threshold": self.alert_thresholds.get("response_time_ms", 2000)}
            ))
        
        # Error rate threshold check
        if metrics.error_rate > self.alert_thresholds.get("error_rate_percent", 5):
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning" if metrics.error_rate < 20 else "critical",
                category="reliability",
                message=f"High error rate: {metrics.error_rate:.1f}%",
                details={"error_rate": metrics.error_rate, "threshold": self.alert_thresholds.get("error_rate_percent", 5)}
            ))
        
        return alerts

    async def check_service_health(self) -> List[Alert]:
        """Check health of all services."""
        alerts = []
        
        # Check backend health
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                alerts.append(Alert(
                    timestamp=datetime.now(),
                    level="critical",
                    category="service_health",
                    message=f"Backend health check failed: {response.status_code}",
                    details={"status_code": response.status_code, "response": response.text}
                ))
        except Exception as e:
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="critical",
                category="service_health",
                message="Backend service unreachable",
                details={"error": str(e)}
            ))
        
        # Check frontend health
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code != 200:
                alerts.append(Alert(
                    timestamp=datetime.now(),
                    level="warning",
                    category="service_health",
                    message=f"Frontend health check failed: {response.status_code}",
                    details={"status_code": response.status_code}
                ))
        except Exception as e:
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="warning",
                category="service_health",
                message="Frontend service unreachable",
                details={"error": str(e)}
            ))
        
        return alerts

    async def check_database_health(self) -> List[Alert]:
        """Check database health and performance."""
        alerts = []
        
        try:
            from app.core.database import engine, SessionLocal
            
            # Test database connection
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                if not result:
                    alerts.append(Alert(
                        timestamp=datetime.now(),
                        level="critical",
                        category="database",
                        message="Database connection test failed",
                        details={}
                    ))
            
            # Check database size and performance
            db = SessionLocal()
            try:
                # Check table sizes
                from app.models import User, Couple, Invoice
                
                user_count = db.query(User).count()
                couple_count = db.query(Couple).count()
                invoice_count = db.query(Invoice).count()
                
                # Alert if database is getting large
                total_records = user_count + couple_count + invoice_count
                if total_records > 10000:
                    alerts.append(Alert(
                        timestamp=datetime.now(),
                        level="info",
                        category="database",
                        message=f"Database growing: {total_records} records",
                        details={"user_count": user_count, "couple_count": couple_count, "invoice_count": invoice_count}
                    ))
                    
            finally:
                db.close()
                
        except Exception as e:
            alerts.append(Alert(
                timestamp=datetime.now(),
                level="critical",
                category="database",
                message="Database health check failed",
                details={"error": str(e)}
            ))
        
        return alerts

    def send_email_alert(self, alert: Alert):
        """Send email alert."""
        if not self.config.get("email_config", {}).get("enabled", False):
            return
        
        email_config = self.config["email_config"]
        
        try:
            msg = f"""
Alert: {alert.level.upper()} - {alert.category}
Time: {alert.timestamp}
Message: {alert.message}
Details: {json.dumps(alert.details, indent=2)}
            """
            
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                
                for recipient in email_config["recipients"]:
                    server.sendmail(
                        email_config["username"],
                        recipient,
                        f"Subject: System Alert - {alert.level.upper()}\n\n{msg}"
                    )
                    
            logger.info(f"Email alert sent to {len(email_config['recipients'])} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def send_slack_alert(self, alert: Alert):
        """Send Slack alert."""
        if not self.config.get("slack_config", {}).get("enabled", False):
            return
        
        webhook_url = self.config["slack_config"]["webhook_url"]
        
        try:
            payload = {
                "text": f"🚨 *{alert.level.upper()} Alert* - {alert.category}\n{alert.message}",
                "attachments": [{
                    "fields": [
                        {"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
                        {"title": "Category", "value": alert.category, "short": True},
                        {"title": "Details", "value": json.dumps(alert.details, indent=2), "short": False}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def log_alert(self, alert: Alert):
        """Log alert to file."""
        log_level = getattr(logging, alert.level.upper())
        logger.log(log_level, f"ALERT [{alert.category}]: {alert.message} - {alert.details}")

    def handle_alerts(self, alerts: List[Alert]):
        """Handle all alerts."""
        for alert in alerts:
            self.alerts.append(alert)
            
            # Send to all configured handlers
            for handler_name, handler_func in self.alert_handlers.items():
                try:
                    handler_func(alert)
                except Exception as e:
                    logger.error(f"Alert handler {handler_name} failed: {e}")

    def cleanup_old_data(self):
        """Clean up old metrics and alerts."""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        
        # Clean up old metrics
        self.metrics_history = [
            metric for metric in self.metrics_history 
            if metric.timestamp > cutoff_time
        ]
        
        # Clean up old alerts
        self.alerts = [
            alert for alert in self.alerts 
            if alert.timestamp > cutoff_time
        ]
        
        logger.info(f"Cleaned up data older than {self.retention_days} days")

    def save_metrics(self):
        """Save metrics to file."""
        try:
            metrics_data = [asdict(metric) for metric in self.metrics_history]
            alerts_data = [asdict(alert) for alert in self.alerts]
            
            data = {
                "metrics": metrics_data,
                "alerts": alerts_data,
                "last_updated": datetime.now().isoformat()
            }
            
            with open("monitoring_data.json", "w") as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    async def monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        try:
            # Collect metrics
            metrics = await self.collect_system_metrics()
            self.metrics_history.append(metrics)
            
            # Check thresholds
            threshold_alerts = self.check_thresholds(metrics)
            
            # Check service health
            health_alerts = await self.check_service_health()
            
            # Check database health
            db_alerts = await self.check_database_health()
            
            # Combine all alerts
            all_alerts = threshold_alerts + health_alerts + db_alerts
            
            # Handle alerts
            if all_alerts:
                self.handle_alerts(all_alerts)
            
            # Log current status
            logger.info(f"Monitoring cycle completed - CPU: {metrics.cpu_percent:.1f}%, "
                       f"Memory: {metrics.memory_percent:.1f}%, "
                       f"Response time: {metrics.response_time:.1f}ms, "
                       f"Alerts: {len(all_alerts)}")
            
            # Save data
            self.save_metrics()
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")

    async def start_monitoring(self):
        """Start continuous monitoring."""
        logger.info("Starting system monitoring...")
        
        while True:
            await self.monitoring_cycle()
            
            # Cleanup old data periodically
            if len(self.metrics_history) % 1440 == 0:  # Every 24 hours (assuming 1-minute intervals)
                self.cleanup_old_data()
            
            await asyncio.sleep(self.monitoring_interval)

    def generate_report(self) -> Dict[str, Any]:
        """Generate monitoring report."""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        # Calculate averages
        recent_metrics = self.metrics_history[-100:]  # Last 100 data points
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        
        # Count alerts by level
        alert_counts = {"info": 0, "warning": 0, "critical": 0}
        for alert in self.alerts:
            alert_counts[alert.level] += 1
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "monitoring_period": {
                "start": self.metrics_history[0].timestamp.isoformat(),
                "end": self.metrics_history[-1].timestamp.isoformat(),
                "total_metrics": len(self.metrics_history)
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "response_time_ms": avg_response_time,
                "error_rate_percent": avg_error_rate
            },
            "alerts": {
                "total": len(self.alerts),
                "by_level": alert_counts
            },
            "current_status": {
                "cpu_percent": self.metrics_history[-1].cpu_percent,
                "memory_percent": self.metrics_history[-1].memory_percent,
                "response_time_ms": self.metrics_history[-1].response_time,
                "error_rate_percent": self.metrics_history[-1].error_rate
            }
        }
        
        return report

def main():
    """Main function to run the monitoring system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Monitoring")
    parser.add_argument("--config", default="monitoring_config.json", help="Config file path")
    parser.add_argument("--report", action="store_true", help="Generate report and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(args.config)
    
    if args.report:
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
        return 0
    
    if args.daemon:
        # Run as daemon
        try:
            asyncio.run(monitor.start_monitoring())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            return 1
    else:
        # Run single cycle
        asyncio.run(monitor.monitoring_cycle())
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
