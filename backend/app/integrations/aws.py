from __future__ import annotations

import asyncio
import random
from typing import List, Dict, Any

from app.models.server import PhysicalServer
from app.models.vm import VirtualMachine
from app.models.storage import Datastore
from app.models.network import NetworkDevice


class AWSAdapter:
    """Mock AWS EC2 integration adapter"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "us-east-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.connected = False
    
    async def connect(self) -> bool:
        """Simulate connection to AWS"""
        await asyncio.sleep(0.1)
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def get_servers(self) -> List[Dict[str, Any]]:
        """Get EC2 instances (treated as servers)"""
        if not self.connected:
            await self.connect()
        
        instance_types = ["t3.micro", "t3.small", "t3.medium", "t3.large", "t3.xlarge", 
                         "m5.large", "m5.xlarge", "m5.2xlarge", "c5.large", "c5.xlarge"]
        
        return [
            {
                "server_id": f"AWS-EC2-{i:08d}",
                "name": f"EC2-Instance-{i}",
                "status": random.choice(["healthy", "warning"]),
                "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "datacenter": f"AWS-{self.region}",
                "rack": f"AZ-{chr(65 + (i % 3))}",  # Availability Zone
                "model": random.choice(instance_types),
                "cpu_cores": {"t3.micro": 2, "t3.small": 2, "t3.medium": 2, "t3.large": 2, 
                             "t3.xlarge": 4, "m5.large": 2, "m5.xlarge": 4, "m5.2xlarge": 8,
                             "c5.large": 2, "c5.xlarge": 4}.get(random.choice(instance_types), 2),
                "memory_gb": {"t3.micro": 1, "t3.small": 2, "t3.medium": 4, "t3.large": 8,
                             "t3.xlarge": 16, "m5.large": 8, "m5.xlarge": 16, "m5.2xlarge": 32,
                             "c5.large": 4, "c5.xlarge": 8}.get(random.choice(instance_types), 2),
                "storage_tb": random.choice([8, 16, 32, 64, 128])  # EBS storage
            }
            for i in range(1, 21)
        ]
    
    async def get_virtual_machines(self) -> List[Dict[str, Any]]:
        """AWS doesn't expose VMs at hypervisor level, return empty"""
        return []
    
    async def get_datastores(self) -> List[Dict[str, Any]]:
        """Get EBS volumes and S3 buckets (simplified)"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "ds_id": f"AWS-EBS-{i:08d}",
                "name": f"EBS Volume {i}",
                "status": "healthy",
                "capacity_gb": random.choice([10, 20, 50, 100, 200, 500]),
                "used_gb": random.randint(5, 450),
                "type": "EBS",
                "location": f"AWS-{self.region}-AZ-{chr(65 + (i % 3))}"
            }
            for i in range(1, 11)
        ] + [
            {
                "ds_id": f"AWS-S3-{i:04d}",
                "name": f"S3 Bucket {i}",
                "status": "healthy",
                "capacity_gb": 0,  # S3 is object storage, capacity varies
                "used_gb": random.randint(100, 5000),
                "type": "S3",
                "location": f"AWS-{self.region}-Global"
            }
            for i in range(1, 6)
        ]
    
    async def get_network_devices(self) -> List[Dict[str, Any]]:
        """Get AWS network components (VPC, ELB, etc.)"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "dev_id": f"AWS-VPC-{i:04d}",
                "name": f"VPC {i}",
                "status": "healthy",
                "ip_address": f"10.{i}.0.1",
                "device_type": "vpc",
                "vendor": "AWS",
                "model": "Amazon VPC",
                "utilization_percent": random.uniform(5.0, 60.0),
                "location": f"AWS-{self.region}"
            }
            for i in range(1, 4)
        ] + [
            {
                "dev_id": f"AWS-ELB-{i:04d}",
                "name": f"Elastic Load Balancer {i}",
                "status": "healthy",
                "ip_address": f"10.{i+10}.0.100",
                "device_type": "load_balancer",
                "vendor": "AWS",
                "model": "Application Load Balancer",
                "utilization_percent": random.uniform(10.0, 80.0),
                "location": f"AWS-{self.region}"
            }
            for i in range(1, 4)
        ]
