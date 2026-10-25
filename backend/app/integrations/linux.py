from __future__ import annotations

import asyncio
import random
from typing import List, Dict, Any

from app.models.server import PhysicalServer
from app.models.vm import VirtualMachine
from app.models.storage import Datastore
from app.models.network import NetworkDevice


class LinuxAdapter:
    """Mock Linux/KVM integration adapter"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connected = False
    
    async def connect(self) -> bool:
        """Simulate connection to Linux host"""
        await asyncio.sleep(0.1)
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    async def get_servers(self) -> List[Dict[str, Any]]:
        """Get Linux servers"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "server_id": f"LNX-SRV-{i:04d}",
                "name": f"Linux Server {i}",
                "status": random.choice(["healthy", "warning"]),
                "ip_address": f"192.168.50.{10+i}",
                "datacenter": "DC-LINUX",
                "rack": f"Rack {(i % 4) + 1}",
                "model": f"Linux Kernel {random.choice(['5.4', '5.10', '5.15', '6.2'])}",
                "cpu_cores": random.choice([4, 8, 12, 16, 24, 32]),
                "memory_gb": random.choice([16, 32, 64, 128, 256]),
                "storage_tb": random.choice([1, 2, 4, 8, 16])
            }
            for i in range(1, 16)
        ]
    
    async def get_virtual_machines(self) -> List[Dict[str, Any]]:
        """Get KVM/QEMU virtual machines"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "vm_id": f"LNX-VM-{i:04d}",
                "name": f"KVM VM {i}",
                "status": random.choice(["healthy", "warning"]),
                "ip_address": f"10.30.{i//254}.{i%254}",
                "datacenter": "DC-LINUX",
                "cluster": f"KVM-Cluster-{(i % 3) + 1}",
                "hypervisor": "KVM/QEMU",
                "cpu_cores": random.choice([1, 2, 4, 8]),
                "memory_gb": random.choice([1, 2, 4, 8, 16]),
                "storage_gb": random.choice([5, 10, 20, 40, 60])
            }
            for i in range(1, 21)
        ]
    
    async def get_datastores(self) -> List[Dict[str, Any]]:
        """Get Linux storage (LVM, ZFS, Ceph)"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "ds_id": f"LNX-DS-{i:04d}",
                "name": f"Linux Storage {i}",
                "status": random.choice(["healthy", "warning"]),
                "capacity_gb": random.choice([100, 500, 1000, 2000]),
                "used_gb": random.randint(20, 1800),
                "type": random.choice(["LVM", "ZFS", "Ceph", "ext4", "xfs"]),
                "location": f"DC-LINUX-Storage-{i}"
            }
            for i in range(1, 11)
        ]
    
    async def get_network_devices(self) -> List[Dict[str, Any]]:
        """Get Linux network devices"""
        if not self.connected:
            await self.connect()
        
        return [
            {
                "dev_id": f"LNX-NET-{i:04d}",
                "name": f"Linux NIC {i}",
                "status": random.choice(["healthy", "warning"]),
                "ip_address": f"192.168.60.{10+i}",
                "device_type": "network_interface",
                "vendor": random.choice(["Intel", "Realtek", "Mellanox"]),
                "model": random.choice(["I350", "82599", "ConnectX-4"]),
                "utilization_percent": random.uniform(10.0, 90.0),
                "location": f"DC-LINUX-Host-{i}"
            }
            for i in range(1, 11)
        ]
