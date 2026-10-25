from __future__ import annotations

import asyncio
import random
from typing import List, Dict, Any, Optional

from app.models.monitoring import MetricSample


class PrometheusAdapter:
    """Mock Prometheus integration adapter"""
    
    def __init__(self, host: str, port: int = 9090):
        self.host = host
        self.port = port
        self.connected = False
    
    async def connect(self) -> bool:
        """Simulate connection to Prometheus"""
        await asyncio.sleep(0.1)
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def query_metrics(self, query: str, start: Optional[float] = None, 
                           end: Optional[float] = None, step: str = "1m") -> List[Dict[str, Any]]:
        """Query Prometheus for metrics"""
        if not self.connected:
            await self.connect()
        
        # Simulate query delay
        await asyncio.sleep(0.2)
        
        # Return mock data based on query type
        if "cpu_utilization" in query:
            return self._generate_cpu_metrics(start, end, step)
        elif "memory_utilization" in query:
            return self._generate_memory_metrics(start, end, step)
        elif "disk_utilization" in query:
            return self._generate_disk_metrics(start, end, step)
        elif "network_utilization" in query:
            return self._generate_network_metrics(start, end, step)
        else:
            return []
    
    def _generate_cpu_metrics(self, start, end, step) -> List[Dict[str, Any]]:
        """Generate mock CPU utilization metrics"""
        results = []
        devices = [f"server-{i}" for i in range(1, 6)] + [f"vm-{i}" for i in range(1, 11)]
        
        for device in devices:
            values = []
            timestamp = start or 0
            end_time = end or 9999999999
            
            while timestamp < end_time:
                value = random.uniform(10.0, 95.0)
                values.append([str(timestamp), str(value)])
                timestamp += 60  # 1 minute step
            
            results.append({
                "metric": {
                    "__name__": "cpu_utilization",
                    "device": device,
                    "instance": f"{self.host}:{self.port}"
                },
                "values": values
            })
        
        return results
    
    def _generate_memory_metrics(self, start, end, step) -> List[Dict[str, Any]]:
        """Generate mock memory utilization metrics"""
        results = []
        devices = [f"server-{i}" for i in range(1, 6)] + [f"vm-{i}" for i in range(1, 11)]
        
        for device in devices:
            values = []
            timestamp = start or 0
            end_time = end or 9999999999
            
            while timestamp < end_time:
                value = random.uniform(20.0, 90.0)
                values.append([str(timestamp), str(value)])
                timestamp += 60
            
            results.append({
                "metric": {
                    "__name__": "memory_utilization",
                    "device": device,
                    "instance": f"{self.host}:{self.port}"
                },
                "values": values
            })
        
        return results
    
    def _generate_disk_metrics(self, start, end, step) -> List[Dict[str, Any]]:
        """Generate mock disk utilization metrics"""
        results = []
        devices = [f"datastore-{i}" for i in range(1, 6)]
        
        for device in devices:
            values = []
            timestamp = start or 0
            end_time = end or 9999999999
            
            while timestamp < end_time:
                value = random.uniform(10.0, 95.0)
                values.append([str(timestamp), str(value)])
                timestamp += 60
            
            results.append({
                "metric": {
                    "__name__": "disk_utilization",
                    "device": device,
                    "instance": f"{self.host}:{self.port}"
                },
                "values": values
            })
        
        return results
    
    def _generate_network_metrics(self, start, end, step) -> List[Dict[str, Any]]:
        """Generate mock network utilization metrics"""
        results = []
        devices = [f"switch-{i}" for i in range(1, 4)] + [f"router-{i}" for i in range(1, 3)]
        
        for device in devices:
            values = []
            timestamp = start or 0
            end_time = end or 9999999999
            
            while timestamp < end_time:
                value = random.uniform(5.0, 80.0)
                values.append([str(timestamp), str(value)])
                timestamp += 60
            
            results.append({
                "metric": {
                    "__name__": "network_utilization",
                    "device": device,
                    "instance": f"{self.host}:{self.port}"
                },
                "values": values
            })
        
        return results
    
    async def get_latest_metrics(self) -> List[MetricSample]:
        """Get latest metrics from Prometheus"""
        if not self.connected:
            await self.connect()
        
        # Get current time
        import time
        end_time = time.time()
        start_time = end_time - 300  # Last 5 minutes
        
        # Query various metrics
        cpu_results = await self.query_metrics(
            'cpu_utilization', 
            start=start_time, 
            end=end_time, 
            step="1m"
        )
        
        memory_results = await self.query_metrics(
            'memory_utilization',
            start=start_time,
            end=end_time,
            step="1m"
        )
        
        metrics = []
        
        # Process CPU results
        for result in cpu_results:
            device = result["metric"]["device"]
            if result["values"]:
                latest_value = float(result["values"][-1][1])
                metrics.append(MetricSample(
                    device_id=device,
                    device_name=device.replace("-", " ").title(),
                    metric_type="cpu_utilization",
                    metric_value=latest_value,
                    unit="percent"
                ))
        
        # Process Memory results
        for result in memory_results:
            device = result["metric"]["device"]
            if result["values"]:
                latest_value = float(result["values"][-1][1])
                metrics.append(MetricSample(
                    device_id=device,
                    device_name=device.replace("-", " ").title(),
                    metric_type="memory_utilization",
                    metric_value=latest_value,
                    unit="percent"
                ))
        
        return metrics
