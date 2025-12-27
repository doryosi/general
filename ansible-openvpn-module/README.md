# Ansible OpenVPN Module

A comprehensive Ansible module for installing and configuring OpenVPN on VPS instances.

## Features

- **Automatic PKI Generation**: Automatically generate certificates, keys, and DH parameters using Easy-RSA
- **Installation**: Automatically install OpenVPN and Easy-RSA
- **Server Configuration**: Generate server configuration files
- **Client Support**: Configure client connections
- **NAT Masquerading**: Automatic network address translation setup
- **Service Management**: Start, stop, restart, and check service status
- **Encryption**: Support for multiple cipher algorithms
- **Compression**: Optional LZ4 compression support
- **TLS Authentication**: Enhanced security with TLS authentication

## Requirements

- Ansible 2.9+
- Python 3.6+
- Linux system (Debian/Ubuntu or RHEL/CentOS)
- Root access on target systems

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ansible-openvpn-module.git
cd ansible-openvpn-module
```

2. Add to your Ansible configuration:
```ini
[defaults]
library = ./plugins/modules
roles_path = ./roles
```

## Quick Usage

A minimal example to run the module after cloning this repo and adding `plugins/modules` to your `ansible.cfg`:

```yaml
- hosts: vpn_servers
  become: yes
  tasks:
    - name: Configure OpenVPN server (minimal)
      openvpn_configure:
        mode: server
        action: configure
        config_file: /etc/openvpn/server.conf
        ca_cert: /etc/openvpn/ca.crt
        server_cert: /etc/openvpn/server.crt
        server_key: /etc/openvpn/server.key
        dh_pem: /etc/openvpn/dh.pem
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        enable_nat: true
        state: present
```

To run the provided integration-style playbook (example):

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/setup_openvpn_server.yml --ask-become-pass
```

Run the module's unit tests locally:

```bash
python3 tests/test_module.py
```

Notes:
- If you prefer not to modify `ansible.cfg`, copy `plugins/modules/openvpn_configure.py` into your project's `library/` directory.
- Some features (PKI generation) call system tools (`easyrsa`, `openvpn`) — ensure they are installed on target hosts or use `action: install`.

## Module Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | - | OpenVPN mode: `server` or `client` (required) |
| `action` | str | - | Action: `install`, `configure`, `start`, `stop`, `restart`, `status` (required) |
| `port` | int | 1194 | OpenVPN listening port |
| `protocol` | str | udp | Protocol: `udp` or `tcp` |
| `cipher` | str | AES-256-CBC | Encryption cipher |
| `vpn_network` | str | 10.8.0.0/24 | VPN network in CIDR notation |
| `vpn_netmask` | str | 255.255.255.0 | VPN network netmask |
| `enable_nat` | bool | true | Enable NAT masquerading |
| `enable_compress` | bool | true | Enable LZ4 compression |
| `ca_cert` | str | /etc/openvpn/ca.crt | Path to CA certificate |
| `server_cert` | str | /etc/openvpn/server.crt | Path to server certificate |
| `server_key` | str | /etc/openvpn/server.key | Path to server key |
| `dh_pem` | str | /etc/openvpn/dh.pem | Path to DH parameters |
| `tls_auth_key` | str | /etc/openvpn/ta.key | Path to TLS auth key |
| `config_file` | str | /etc/openvpn/server.conf | Path to config file |
| `state` | str | present | Desired state: `present`, `absent`, `started`, `stopped`, `restarted` |
| `generate_pki` | bool | false | Automatically generate PKI (certificates and keys) |
| `pki_dir` | str | /etc/openvpn/easy-rsa | Directory for Easy-RSA PKI |
| `key_size` | int | 2048 | Key size for PKI: 2048 or 4096 |
| `cert_days` | int | 3650 | Certificate validity in days |
| `client_to_client` | bool | false | Allow clients to communicate with each other |
| `topology` | str | subnet | Topology mode: `subnet`, `net30`, or `p2p` |
| `mssfix` | bool | true | Enable MSS fragment clamping |
| `fragment` | int | 0 | Fragment packet size (0 to disable) |
| `routes` | list | [] | Additional routes to push to clients |
| `redirect_gateway` | bool | true | Redirect all traffic through VPN |
| `dns_servers` | list | [8.8.8.8, 8.8.4.4] | DNS servers to push to clients |
| `ccd_dir` | str | /etc/openvpn/ccd | Directory for client-specific config files (CCD) |
| `ccd` | dict | {} | Mapping of client common names to `ifconfig-push` values |
| `duplicate_cn` | bool | false | Allow multiple clients with the same certificate CN (`duplicate-cn`) |
| `extra_server_options` | list | [] | Additional lines to append to the generated `server.conf` |

## Usage Examples

### Complete Server Setup (with automatic PKI generation)

```yaml
- name: Complete OpenVPN server setup
  hosts: vpn_servers
  become: yes
  tasks:
    - name: Install, generate PKI, and configure OpenVPN
      openvpn_configure:
        mode: server
        action: install
        generate_pki: true
        key_size: 2048
        cert_days: 3650
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        enable_nat: true
        state: present
```

### Basic Server Installation

```yaml
- name: Install and configure OpenVPN server with PKI
  hosts: vpn_servers
  become: yes
  tasks:
    - name: Install OpenVPN
      openvpn_configure:
        mode: server
        action: install
        generate_pki: true
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        enable_nat: true
        state: present

    - name: Configure OpenVPN
      openvpn_configure:
        mode: server
        action: configure
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        enable_nat: true

    - name: Start OpenVPN
      openvpn_configure:
        mode: server
        action: start
        state: started
```

### Advanced Configuration with Custom Routing

```yaml
- name: Configure OpenVPN with custom routes and net30 topology
  hosts: vpn_servers
  become: yes
  tasks:
    - name: Configure OpenVPN with routing
      openvpn_configure:
        mode: server
        action: configure
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        client_to_client: true
        topology: net30
        mssfix: true
        fragment: 1500
        routes:
          - "192.168.1.0 255.255.255.0"
          - "192.168.2.0 255.255.255.0"
        redirect_gateway: true
        dns_servers:
          - 1.1.1.1
          - 1.0.0.1
        state: present

    - name: Start OpenVPN
      openvpn_configure:
        mode: server
        action: start
        state: started
```

### Server Configuration with Client-to-Client Communication

```yaml
- name: Configure OpenVPN with client-to-client
  hosts: vpn_servers
  become: yes
  tasks:
    - name: Install and configure OpenVPN
      openvpn_configure:
        mode: server
        action: install
        generate_pki: true
        port: 1194
        protocol: udp
        vpn_network: 10.8.0.0/24
        client_to_client: true
        topology: subnet
        mssfix: true
        redirect_gateway: true
        dns_servers:
          - 8.8.8.8
          - 8.8.4.4
        enable_nat: true
        state: present

    - name: Start OpenVPN
      openvpn_configure:
        mode: server
        action: start
        state: started

### Client-Config-Dir (CCD) Example

```yaml
- name: Configure CCD for specific clients
  openvpn_configure:
    mode: server
    action: configure
    ccd_dir: /etc/openvpn/ccd
    ccd:
      client1: ["10.8.0.2", "255.255.255.0"]
      client2: "10.8.0.3 255.255.255.0"
    state: present
```
```

### Advanced Network Configuration

```yaml
- name: Configure with custom routing and topology
  openvpn_configure:
    mode: server
    action: configure
    port: 443
    protocol: tcp
    cipher: 'AES-256-GCM'
    vpn_network: 10.9.0.0/24
    topology: subnet
    enable_compress: true
    client_to_client: true
    mssfix: true
    fragment: 1500
    routes:
      - "10.0.0.0 255.255.0.0"
      - "192.168.0.0 255.255.0.0"
    redirect_gateway: true
    dns_servers:
      - 1.1.1.1
      - 8.8.8.8
    state: present
```

### Advanced Configuration

```yaml
- name: Configure OpenVPN with custom settings
  openvpn_configure:
    mode: server
    action: configure
    port: 443
    protocol: tcp
    cipher: 'AES-256-GCM'
    vpn_network: '192.168.100.0/24'
    enable_nat: true
    enable_compress: true
    state: present
```

### Service Management

```yaml
- name: Restart OpenVPN service
  openvpn_configure:
    mode: server
    action: restart

- name: Check OpenVPN status
  openvpn_configure:
    mode: server
    action: status
  register: openvpn_status

- name: Display status
  debug:
    msg: "{{ openvpn_status.status }}"
```

## Directory Structure

```
ansible-openvpn-module/
├── plugins/
│   └── modules/
│       └── openvpn_configure.py      # Main module
├── roles/
│   └── openvpn/
│       ├── tasks/
│       │   └── main.yml              # Role tasks
│       ├── templates/
│       │   └── server.conf.j2        # Config template
│       └── handlers/
│           └── main.yml              # Handlers
├── playbooks/
│   ├── setup_openvpn_server.yml
│   └── setup_openvpn_client.yml
├── tests/
│   └── test_module.py
└── README.md
```

## Configuration Files

### Server Configuration
The module generates `/etc/openvpn/server.conf` with the following settings:
- Configurable port (default: 1194)
- Protocol selection (UDP or TCP)
- VPN network and netmask
- Encryption cipher and compression
- DNS and routing configuration
- TLS authentication

### Generated Files
- `/etc/openvpn/server.conf` - Main server configuration
- `/etc/openvpn/openvpn-status.log` - Status log file

## Prerequisites

Before running the module, you have two options:

### Option 1: Automatic PKI Generation (Recommended)

Simply enable PKI generation in the module:
```yaml
openvpn_configure:
  mode: server
  action: install
  generate_pki: true
  key_size: 2048
  cert_days: 3650
```

The module will automatically:
- Initialize PKI
- Generate CA certificate
- Generate server certificate and key
- Generate Diffie-Hellman parameters
- Generate TLS authentication key

### Option 2: Pre-Generated Certificates

If you prefer to generate certificates separately, you can use the provided script:

```bash
sudo bash scripts/generate_certs.sh
```

Then set `generate_pki: false` when running the module.

## Supported Systems

- Ubuntu 18.04+
- Debian 9+
- CentOS 7+
- RHEL 7+

## Troubleshooting

### Module not found
Ensure the `library` path is set correctly in your Ansible configuration.

### Permission denied
Make sure you're running with `become: yes` for tasks requiring root access.

### Service won't start
Check certificates exist at the paths specified and have correct permissions.

## License

MIT

## Contributing

Contributions are welcome! Please submit pull requests or issues.

## Author

Created for managing OpenVPN configurations across VPS infrastructure.
