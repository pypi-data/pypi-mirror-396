# 🧠 Iotamine Python SDK

**Iotamine** is a powerful and easy-to-use cloud platform designed for developers and startups. This Python SDK allows you to interact with the Iotamine Cloud API to programmatically deploy, manage, and monitor Virtual Private Servers (VPS) and core resources.

---

## 🚀 Features

- Create and manage VPS instances
- Start, stop, restart, power off VMs
- Add or remove disks and IPs
- Set reverse DNS
- Take and restore from snapshots
- Configure firewall rules
- List OS templates and Points of Presence (PoPs)

---

## 📦 Installation

```bash
pip install iotamine
````

---

## 🔑 Authentication

All requests require an API key. You can obtain this from your [Iotamine dashboard](https://iotamine.com/control).

---

## 🛠️ Usage Example

```python
from iotamine import Iotamine

# Initialize client
client = Iotamine("your-api-key")

# List available OS and POPs
os_list = client.core.list_os()
pop_list = client.core.list_pop()

# Create a new VM
vm = client.vm.create(
    hostname="test-server",
    password="strongpassword123",
    operating_system=os_list[0]['id'],
    pop=pop_list[0]['id'],
    cores=2,
    ram=4096,
    disk=80
)

print("VM Created:", vm)

# List all VMs
print(client.vm.list())
```

---

## 🧰 API Reference

### `Iotamine(api_key)`

Main entrypoint to interact with Iotamine API.

### VM Methods

| Method                             | Description                  |
| ---------------------------------- | ---------------------------- |
| `create(...)`                      | Create a new VM              |
| `list()`                           | List all VMs                 |
| `details(vps_id)`                  | Get details of a specific VM |
| `start(vps_id)`                    | Start the VM                 |
| `stop(vps_id)`                     | Stop the VM                  |
| `restart(vps_id)`                  | Restart the VM               |
| `poweroff(vps_id)`                 | Force shutdown the VM        |
| `rebuild(vps_id, os_id, password)` | Reinstall VM                 |
| `destroy(vps_id)`                  | Destroy the VM               |
| `stats(vps_id)`                    | Get usage stats              |
| `vnc(vps_id)`                      | Get VNC connection details   |

### Disk Management

| Method                           | Description            |
| -------------------------------- | ---------------------- |
| `list_disk(vps_id)`              | List attached disks    |
| `add_disk(vps_id, size)`         | Add a new disk         |
| `delete_disk(vps_id, disk_uuid)` | Delete a specific disk |

### IP Management

| Method                            | Description          |
| --------------------------------- | -------------------- |
| `add_ip(vps_id)`                  | Add an additional IP |
| `delete_ip(vps_id, ip_addr)`      | Remove an IP address |
| `add_rdns(vps_id, ip_addr, rdns)` | Set reverse DNS      |

### Snapshots

| Method                                  | Description           |
| --------------------------------------- | --------------------- |
| `list_snapshots(vps_id)`                | List snapshots        |
| `create_snapshot(vps_id)`               | Take snapshot         |
| `restore_snapshot(vps_id, snapshot_id)` | Restore from snapshot |
| `delete_snapshot(vps_id, snapshot_id)`  | Delete snapshot       |

### Firewall

| Method                                 | Description  |
| -------------------------------------- | ------------ |
| `list_firewall_rules(vps_id)`          | View rules   |
| `update_firewall_rules(vps_id, rules)` | Modify rules |

---

### Core Methods

| Method       | Description                                 |
| ------------ | ------------------------------------------- |
| `list_os()`  | List available operating systems            |
| `list_pop()` | List available Points of Presence (regions) |

---

## 🧪 Development

Clone this repository:

```bash
git clone https://github.com/piyushladhar/iotamine.git
cd iotamine
pip install -e .
```

---

## 📄 License

This SDK is open-sourced under the [MIT License](LICENSE).

---

## 🌐 Links

* [🌍 Iotamine Website](https://iotamine.com)
* [🎮 Control Panel](https://iotamine.com/control)

