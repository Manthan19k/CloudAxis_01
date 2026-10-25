from __future__ import annotations

import asyncio
import random
from typing import List, Dict, Any

from app.models.server import PhysicalServer
from app.models.vm import VirtualMachine
from app.models.storage import Datastore
from app.models.network import NetworkDevice


class WindowsAdapter:
    """Mock Windows Server integration adapter"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connected = False
    
    async def connect(self) -> bool:
        """Simulate connection to Windows Server"""
        await asyncio.sleep(0.1)
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def get_servers(self) -> List[Dict[str, Any]]:
        """Get Windows servers"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "server_id": f"WIN-SRV-{i:04d}",
                "name": f"Windows Server {i}",
                "status": random.choice(["healthy", "warning", "critical"]),
                "ip_address": f"192.168.30.{10+i}",
                "datacenter": "DC-WINDOWS",
                "rack": f"Rack {(i % 3) + 1}",
                "model": "Windows Server 2022",
                "cpu_cores": random.choice([8, 12, 16, 24, 32]),
                "memory_gb": random.choice([32, 64, 128, 256]),
                "storage_tb": random.choice([1, 2, 4, 8])
            }
            for i in range(1, 11)
        ]
    
    async def get_virtual_machines(self) -> List[Dict[str, Any]]:
        """Get Hyper-V virtual machines"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "vm_id": f"WIN-VM-{i:04d}",
                "name": f"Hyper-V VM {i}",
                "status": random.choice(["healthy", "warning"]),
                "ip_address": f"10.20.{i//254}.{i%254}",
                "datacenter": "DC-WINDOWS",
                "cluster": f"Hyper-V-Cluster-{(i % 2) + 1}",
                "hypervisor": "Microsoft Hyper-V",
                "cpu_cores": random.choice([1, 2, 4, 8]),
                "memory_gb": random.choice([2, 4, 8, 16]),
                "storage_gb": random.choice([10, 20, 40, 60])
            }
            for i in range(1, 16)
        ]
    
    async def get_datastores(self) -> List[Dict[str, Any]]:
        """Get Windows storage (CSV, SMB shares)"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "ds_id": f"WIN-DS-{i:04d}",
                "name": f"Windows Storage {i}",
                "status": random.choice(["healthy", "warning"]),
                "capacity_gb": random.choice([200, 500, 1000, 2000]),
                "used_gb": random.randint(50, 1800),
                "type": random.choice(["CSV", "SMB", "NTFS"]),
                "location": f"DC-WINDOWS-Storage-{i}"
            }
            for i in range(1, 6)
        ]
    
    async def get_network_devices(self) -> List[Dict[str, Any]]:
        """Get Windows network adapters (limited)"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "dev_id": f"WIN-NET-{i:04d}",
                "name": f"Windows NIC {i}",
                "status": "healthy",
                "ip_address": f"192.168.40.{10+i}",
                "device_type": "network_adapter",
                "vendor": "Microsoft",
                "model": "Hyper-V Virtual Ethernet Adapter",
                "utilization_percent": random.uniform(5.0, 50.0),
                "location": f"DC-WINDOWS-Host-{i}"
            }
            for i in range(1, 6)
        ]
