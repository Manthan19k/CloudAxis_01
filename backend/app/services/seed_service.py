from __future__ import annotations

import datetime as dt
import random
from typing import List

from app.core.security import hash_password
from app.models.user import Role, User
from app.models.server import PhysicalServer
from app.models.vm import VirtualMachine
from app.models.storage import Datastore
from app.models.network import NetworkDevice
from app.models.alert import Alert
from app.models.monitoring import MetricSample
from app.models.inventory import InventoryItem
from app.repositories.user import UserRepository
from app.repositories.server import ServerRepository
from app.repositories.vm import VMRepository
from app.repositories.storage import StorageRepository
from app.repositories.network import NetworkRepository
from app.repositories.alert import AlertRepository
from app.repositories.monitoring import MonitoringRepository
from app.repositories.inventory import InventoryRepository


class SeedService:
    def __init__(
        self,
        user_repo: UserRepository,
        server_repo: ServerRepository,
        vm_repo: VMRepository,
        storage_repo: StorageRepository,
        network_repo: NetworkRepository,
        alert_repo: AlertRepository,
        monitoring_repo: MonitoringRepository,
        inventory_repo: InventoryRepository,
    ):
        self.user_repo = user_repo
        self.server_repo = server_repo
        self.vm_repo = vm_repo
        self.storage_repo = storage_repo
        self.network_repo = network_repo
        self.alert_repo = alert_repo
        self.monitoring_repo = monitoring_repo
        self.inventory_repo = inventory_repo

    async def seed_all(self):
        """Seed the database with realistic demo data"""
        await self.seed_roles()
        await self.seed_users()
        await self.seed_servers()
        await self.seed_vms()
        await self.seed_storage()
        await self.seed_network()
        await self.seed_inventory()
        await self.seed_alerts()
        await self.seed_monitoring()
        print("Database seeding completed!")

    async def seed_roles(self):
        """Seed basic roles if they don't exist"""
        roles = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "engineer", "description": "Engineer with read/write access"},
            {"name": "manager", "description": "Manager with read-only access"},
            {"name": "viewer", "description": "Viewer with limited read access"},
        ]
        
        for role_data in roles:
            # Simple approach: just create and let DB handle constraints
            role = Role(**role_data)
            self.user_repo.session.add(role)
        
        try:
            await self.user_repo.session.flush()
        except Exception:
            # Roles might already exist, rollback and continue
            await self.user_repo.session.rollback()

    async def seed_users(self):
        """Seed demo users"""
        users_data = [
            {
                "name": "John Administrator",
                "email": "admin@cloudaxis.com",
                "password": "AdminPass123!",
                "role_name": "admin",
                "department": "IT"
            },
            {
                "name": "Jane Engineer",
                "email": "engineer@cloudaxis.com",
                "password": "EngPass123!",
                "role_name": "engineer",
                "department": "Engineering"
            },
            {
                "name": "Bob Manager",
                "email": "manager@cloudaxis.com",
                "password": "MgrPass123!",
                "role_name": "manager",
                "department": "Operations"
            },
            {
                "name": "Alice Viewer",
                "email": "viewer@cloudaxis.com",
                "password": "ViewPass123!",
                "role_name": "viewer",
                "department": "Finance"
            }
        ]
        
        for user_data in users_data:
            # Check if user already exists
            existing = await self.user_repo.get_by_email(user_data["email"])
            if not existing:
                await self.user_repo.create_user(
                    name=user_data["name"],
                    email=user_data["email"],
                    password=user_data["password"],
                    role_name=user_data["role_name"],
                    department=user_data["department"]
                )

    async def seed_servers(self):
        """Seed physical servers"""
        servers_data = [
            {
                "server_id": "SRV-1000",
                "name": "Web Server 01",
                "status": "healthy",
                    "ip": "192.168.1.10",
                    "location": "DC-01",
                "rack": "Rack A",
                    "os": "Ubuntu 22.04",
                    "cpu": 32.0,
                    "memory": 128.0,
                    "storage": 4.0,
                    "temperature": 42.0,
                    "owner": "IT",
                    "department": "Engineering",
                    "vm_count": 4,
                    "uptime_days": 120
                },
                {
                    "server_id": "SRV-1001",
                    "name": "Database Server 01",
                    "status": "healthy",
                    "ip": "192.168.1.11",
                    "location": "DC-01",
                    "rack": "Rack A",
                    "os": "RHEL 9",
                    "cpu": 48.0,
                    "memory": 256.0,
                    "storage": 8.0,
                    "temperature": 45.0,
                    "owner": "IT",
                    "department": "Engineering",
                    "vm_count": 2,
                    "uptime_days": 200
                },
                {
                    "server_id": "SRV-1002",
                    "name": "Application Server 01",
                    "status": "warning",
                    "ip": "192.168.1.12",
                    "location": "DC-01",
                    "rack": "Rack B",
                    "os": "Ubuntu 22.04",
                    "cpu": 24.0,
                    "memory": 64.0,
                    "storage": 2.0,
                    "temperature": 68.0,
                    "owner": "IT",
                    "department": "Operations",
                    "vm_count": 3,
                    "uptime_days": 90
                },
                {
                    "server_id": "SRV-1003",
                    "name": "Load Balancer 01",
                    "status": "healthy",
                    "ip": "192.168.1.20",
                    "location": "DC-01",
                    "rack": "Rack C",
                    "os": "F5 TMOS",
                    "cpu": 8.0,
                    "memory": 32.0,
                    "storage": 1.0,
                    "temperature": 38.0,
                    "owner": "IT",
                    "department": "Networking",
                    "vm_count": 0,
                    "uptime_days": 365
                }
            ]

        for server_data in servers_data:
            existing = await self.server_repo.get_by_server_id(server_data["server_id"])
            if not existing:
                server = PhysicalServer(**server_data)
                await self.server_repo.create(server)

    async def seed_vms(self):
        """Seed virtual machines"""
        # First get the servers to associate VMs with them
        servers = await self.server_repo.list_servers()
        server_map = {s.server_id: s.id for s in servers}
        
        vms_data = [
            {
                "vm_id": "VM-2000",
                "name": "Web VM 01",
                "status": "healthy",
                    "ip": "10.0.1.10",
                    "host_id": server_map.get("SRV-1000", 1),
                    "host_name": "Web Server 01",
                    "os": "Ubuntu 22.04",
                    "v_cpu": 4,
                "memory_gb": 8,
                    "disk_gb": 50,
                    "cpu": 4.0,
                    "memory": 8.0,
                    "owner": "Engineering",
                    "department": "Engineering",
                    "snapshots": 3
                },
                {
                    "vm_id": "VM-2001",
                    "name": "Web VM 02",
                    "status": "healthy",
                    "ip": "10.0.1.11",
                    "host_id": server_map.get("SRV-1000", 1),
                    "host_name": "Web Server 01",
                    "os": "Ubuntu 22.04",
                    "v_cpu": 4,
                    "memory_gb": 8,
                    "disk_gb": 50,
                    "cpu": 4.0,
                    "memory": 8.0,
                    "owner": "Engineering",
                    "department": "Engineering",
                    "snapshots": 2
                },
                {
                    "vm_id": "VM-2002",
                    "name": "Database VM 01",
                    "status": "healthy",
                    "ip": "10.0.1.20",
                    "host_id": server_map.get("SRV-1001", 2),
                    "host_name": "Database Server 01",
                    "os": "RHEL 9",
                    "v_cpu": 8,
                    "memory_gb": 32,
                    "disk_gb": 100,
                    "cpu": 8.0,
                    "memory": 32.0,
                    "owner": "IT",
                    "department": "Engineering",
                    "snapshots": 5
                },
                {
                    "vm_id": "VM-2003",
                    "name": "App VM 01",
                    "status": "warning",
                    "ip": "10.0.1.30",
                    "host_id": server_map.get("SRV-1002", 3),
                    "host_name": "Application Server 01",
                    "os": "Ubuntu 22.04",
                    "v_cpu": 2,
                    "memory_gb": 4,
                    "disk_gb": 20,
                    "cpu": 2.0,
                    "memory": 4.0,
                    "owner": "Operations",
                    "department": "Operations",
                    "snapshots": 1
                }
            ]

        for vm_data in vms_data:
            existing = await self.vm_repo.get_by_vm_id(vm_data["vm_id"])
            if not existing:
                vm = VirtualMachine(**vm_data)
                await self.vm_repo.create(vm)

    async def seed_storage(self):
        """Seed datastores"""
        storages_data = [
            {
                "ds_id": "DS-3000",
                "name": "NFS Datastore 01",
                "status": "healthy",
                    "capacity_tb": 2.0,
                    "used_tb": 0.85,
                "type": "NFS",
                "location": "DC-01-NAS-01"
            },
            {
                "ds_id": "DS-3001",
                "name": "Fibre Channel Datastore 01",
                "status": "healthy",
                    "capacity_tb": 4.0,
                    "used_tb": 1.2,
                "type": "FC",
                "location": "DC-01-SAN-01"
            },
            {
                "ds_id": "DS-3002",
                "name": "SSD Datastore 01",
                "status": "warning",
                    "capacity_tb": 1.0,
                    "used_tb": 0.95,
                "type": "SSD",
                "location": "DC-01-SSD-01"
            }
        ]
        
        for storage_data in storages_data:
            existing = await self.storage_repo.get_by_ds_id(storage_data["ds_id"])
            if not existing:
                datastore = Datastore(**storage_data)
                await self.storage_repo.create(datastore)

    async def seed_network(self):
        """Seed network devices"""
        network_data = [
            {
                "dev_id": "NET-4000",
                "name": "Core Switch 01",
                "status": "healthy",
                    "ip": "192.168.0.1",
                    "type": "switch",
                "vendor": "Cisco",
                    "throughput_gbps": 45.2,
                    "latency_ms": 1.2,
                    "packet_loss": 0.01
            },
            {
                "dev_id": "NET-4001",
                "name": "Firewall 01",
                "status": "healthy",
                    "ip": "192.168.0.254",
                    "type": "firewall",
                "vendor": "Palo Alto",
                    "throughput_gbps": 23.8,
                    "latency_ms": 0.8,
                    "packet_loss": 0.0
            },
            {
                "dev_id": "NET-4002",
                "name": "Router 01",
                "status": "warning",
                    "ip": "192.168.0.250",
                    "type": "router",
                "vendor": "Juniper",
                    "throughput_gbps": 78.9,
                    "latency_ms": 5.4,
                    "packet_loss": 0.3
            }
        ]
        
        for device_data in network_data:
            existing = await self.network_repo.get_by_dev_id(device_data["dev_id"])
            if not existing:
                device = NetworkDevice(**device_data)
                await self.network_repo.create(device)

    async def seed_inventory(self):
        """Seed inventory items"""
        inventory_data = [
            {
                "inv_id": "INV-5000",
                "name": "Intel Xeon Gold 6338",
                "category": "CPU",
                "status": "Active",
                "vendor": "Intel",
                "serial": "SN-CPU-001",
                "purchased_at": dt.datetime(2024, 1, 15),
                "warranty_until": dt.datetime(2027, 1, 15)
            },
            {
                "inv_id": "INV-5001",
                "name": "Samsung 32GB DDR4 RAM",
                "category": "Memory",
                "status": "Active",
                "vendor": "Samsung",
                "serial": "SN-RAM-001",
                "purchased_at": dt.datetime(2024, 3, 10),
                "warranty_until": dt.datetime(2027, 3, 10)
            },
            {
                "inv_id": "INV-5002",
                "name": "Seagate 4TB Enterprise HDD",
                "category": "Storage",
                "status": "Active",
                "vendor": "Seagate",
                "serial": "SN-HDD-001",
                "purchased_at": dt.datetime(2024, 6, 5),
                "warranty_until": dt.datetime(2027, 6, 5)
            },
            {
                "inv_id": "INV-5003",
                "name": "Cisco SFP+ 10G Transceiver",
                "category": "Networking",
                "status": "Retired",
                "vendor": "Cisco",
                "serial": "SN-NET-001",
                "purchased_at": dt.datetime(2024, 2, 20),
                "warranty_until": dt.datetime(2027, 2, 20)
            }
            ]

        for item_data in inventory_data:
            existing = await self.inventory_repo.get_by_inv_id(item_data["inv_id"])
            if not existing:
                item = InventoryItem(**item_data)
                await self.inventory_repo.create(item)

    async def seed_alerts(self):
        """Seed alerts"""
        alerts_data = [
            {
                "alert_id": "ALT-6000",
                "severity": "critical",
                    "title": "Database Server High CPU Usage",
                    "source": "SRV-1001",
                    "triggered_at": dt.datetime.utcnow() - dt.timedelta(minutes=10),
                    "acknowledged": False,
                    "resolved": False,
                    "assignee": "Jane Engineer"
                },
                {
                    "alert_id": "ALT-6001",
                    "severity": "warning",
                "title": "Storage Utilization Warning",
                    "source": "DS-3002",
                    "triggered_at": dt.datetime.utcnow() - dt.timedelta(hours=2),
                    "acknowledged": True,
                    "resolved": False,
                    "assignee": "Bob Manager"
                },
                {
                    "alert_id": "ALT-6002",
                    "severity": "info",
                    "title": "Network Link Flapping",
                "source": "NET-4002",
                    "triggered_at": dt.datetime.utcnow() - dt.timedelta(days=1),
                    "acknowledged": True,
                    "resolved": True,
                    "assignee": "Jane Engineer"
                }
            ]

        for alert_data in alerts_data:
            existing = await self.alert_repo.get_by_alert_id(alert_data["alert_id"])
            if not existing:
                alert = Alert(**alert_data)
                await self.alert_repo.create(alert)

    async def seed_monitoring(self):
        """Seed monitoring samples"""
        # Get some devices to associate metrics with
        servers = await self.server_repo.list_servers()
        vms = await self.vm_repo.list_vms()
        network_devices = await self.network_repo.list_devices()

        all_devices = []
        all_devices.extend([s.server_id for s in servers])
        all_devices.extend([v.vm_id for v in vms])
        all_devices.extend([d.dev_id for d in network_devices])

        # Generate metrics for the last 24 hours
        now = dt.datetime.utcnow()
        metrics_to_create = []

        for device_id in all_devices[:10]:  # Limit to first 10 devices
            for i in range(0, 24, 2):  # Every 2 hours
                timestamp = now - dt.timedelta(hours=i)

                # CPU usage metric
                metrics_to_create.append(MetricSample(
                    source=device_id,
                    metric="cpu_utilization",
                    value=random.uniform(10.0, 95.0),
                    unit="percent",
                    recorded_at=timestamp
                ))

                # Memory usage metric
                metrics_to_create.append(MetricSample(
                    source=device_id,
                    metric="memory_utilization",
                    value=random.uniform(20.0, 90.0),
                    unit="percent",
                    recorded_at=timestamp
                ))

        # Add all metrics in batches
        for i in range(0, len(metrics_to_create), 100):
            batch = metrics_to_create[i:i+100]
            self.monitoring_repo.session.add_all(batch)

        try:
            await self.monitoring_repo.session.flush()
        except Exception:
            await self.monitoring_repo.session.rollback()
