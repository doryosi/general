#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: openvpn_configure
short_description: Configure OpenVPN on a VPS
description:
  - Install and configure OpenVPN on a VPS
  - Generate server configuration
  - Manage certificates and keys
  - Control OpenVPN service
version_added: "1.0.0"
author: "Ansible OpenVPN Module"
options:
  mode:
    description:
      - OpenVPN operation mode (server or client)
    type: str
    choices: ['server', 'client']
    required: true
  action:
    description:
      - Action to perform (install, configure, start, stop, restart, status)
    type: str
    choices: ['install', 'configure', 'start', 'stop', 'restart', 'status']
    required: true
  config_file:
    description:
      - Path to OpenVPN configuration file
    type: str
    default: '/etc/openvpn/server.conf'
  ca_cert:
    description:
      - Path to CA certificate
    type: str
    default: '/etc/openvpn/ca.crt'
  server_cert:
    description:
      - Path to server certificate (for server mode)
    type: str
    default: '/etc/openvpn/server.crt'
  server_key:
    description:
      - Path to server key (for server mode)
    type: str
    default: '/etc/openvpn/server.key'
  dh_pem:
    description:
      - Path to Diffie-Hellman parameters
    type: str
    default: '/etc/openvpn/dh.pem'
  port:
    description:
      - OpenVPN listening port
    type: int
    default: 1194
  protocol:
    description:
      - Protocol to use (udp or tcp)
    type: str
    choices: ['udp', 'tcp']
    default: 'udp'
  cipher:
    description:
      - Encryption cipher
    type: str
    default: 'AES-256-CBC'
  vpn_network:
    description:
      - VPN network in CIDR notation (e.g., 10.8.0.0/24)
    type: str
    default: '10.8.0.0/24'
  vpn_netmask:
    description:
      - VPN network netmask
    type: str
    default: '255.255.255.0'
  enable_nat:
    description:
      - Enable NAT masquerading
    type: bool
    default: true
  enable_compress:
    description:
      - Enable compression
    type: bool
    default: true
  tls_auth_key:
    description:
      - Path to TLS auth key
    type: str
    default: '/etc/openvpn/ta.key'
  client_to_client:
    description:
      - Allow clients to communicate with each other
    type: bool
    default: false
  topology:
    description:
      - Topology mode for client subnets
    type: str
    choices: ['subnet', 'net30', 'p2p']
    default: 'subnet'
  mssfix:
    description:
      - Enable MSS fragment clamping
    type: bool
    default: true
  fragment:
    description:
      - Fragment packets with size (in bytes), 0 to disable
    type: int
    default: 0
  routes:
    description:
      - List of additional routes to push to clients
    type: list
    elements: str
    default: []
  redirect_gateway:
    description:
      - Redirect all traffic through VPN
    type: bool
    default: true
  dns_servers:
    description:
      - List of DNS servers to push to clients
    type: list
    elements: str
    default: ['8.8.8.8', '8.8.4.4']
  state:
    description:
      - Desired state of OpenVPN service
    type: str
    choices: ['present', 'absent', 'started', 'stopped', 'restarted']
    default: 'present'
  generate_pki:
    description:
      - Automatically generate PKI (certificates and keys)
    type: bool
    default: false
  pki_dir:
    description:
      - Directory for Easy-RSA PKI
    type: str
    default: '/etc/openvpn/easy-rsa'
  key_size:
    description:
      - Key size for PKI generation (2048 or 4096)
    type: int
    choices: [2048, 4096]
    default: 2048
  cert_days:
    description:
      - Certificate validity in days
    type: int
    default: 3650
requirements:
  - OpenVPN
  - Easy-RSA (for key generation)
extends_documentation_fragment:
  - action_common_attributes
attributes:
  check_mode:
    support: partial
  diff_mode:
    support: partial
  platform:
    platforms:
      - name: Linux
'''

EXAMPLES = r'''
# Complete OpenVPN server setup with PKI generation and advanced settings
- name: Complete OpenVPN server setup with client-to-client
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
    client_to_client: true
    topology: subnet
    mssfix: true
    redirect_gateway: true
    dns_servers:
      - 8.8.8.8
      - 8.8.4.4
    state: present

# Install and configure with custom routing and net30 topology
- name: Configure OpenVPN with custom routes
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

# Configure OpenVPN with custom cipher and advanced options
- name: Configure OpenVPN with advanced settings
  openvpn_configure:
    mode: server
    action: configure
    port: 443
    protocol: tcp
    cipher: 'AES-256-GCM'
    vpn_network: 10.9.0.0/24
    enable_compress: true
    client_to_client: true
    topology: subnet
    mssfix: true
    redirect_gateway: true
    state: present

# Start OpenVPN service
- name: Start OpenVPN
  openvpn_configure:
    mode: server
    action: start
    state: started

# Check OpenVPN status
- name: Check OpenVPN status
  openvpn_configure:
    mode: server
    action: status
  register: openvpn_status

- name: Display OpenVPN status
  debug:
    msg: "{{ openvpn_status.status }}"
'''

RETURN = r'''
changed:
  description: Whether changes were made
  type: bool
  returned: always
message:
  description: Human-readable description of changes
  type: str
  returned: always
status:
  description: Status of OpenVPN service
  type: str
  returned: when action is 'status'
config_path:
  description: Path to configuration file
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess
import sys


def run_command(command, check=False):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def check_openvpn_installed():
    """Check if OpenVPN is installed."""
    returncode, _, _ = run_command('which openvpn')
    return returncode == 0


def install_openvpn(module):
    """Install OpenVPN."""
    # Detect package manager
    if os.path.exists('/etc/debian_version'):
        cmd = 'apt-get update && apt-get install -y openvpn easy-rsa'
    elif os.path.exists('/etc/redhat-release'):
        cmd = 'yum install -y openvpn easy-rsa'
    else:
        module.fail_json(msg='Unsupported operating system')

    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        module.fail_json(msg=f'Failed to install OpenVPN: {stderr}')
    
    return True


def generate_pki(module, params):
    """Generate PKI using Easy-RSA."""
    pki_dir = params['pki_dir']
    openvpn_dir = os.path.dirname(params['ca_cert'])
    key_size = params['key_size']
    cert_days = params['cert_days']
    
    message = []
    
    # Create PKI directory
    os.makedirs(pki_dir, exist_ok=True)
    
    # Check if Easy-RSA is available
    returncode, _, _ = run_command('which easyrsa')
    if returncode != 0:
        module.fail_json(msg='Easy-RSA not found. Please install it first.')
    
    # Initialize PKI if not already done
    if not os.path.exists(f'{pki_dir}/pki'):
        cmd = f'cd {pki_dir} && easyrsa init-pki'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to initialize PKI: {stderr}')
        message.append('PKI initialized')
    
    # Generate CA certificate
    if not os.path.exists(f'{pki_dir}/pki/ca.crt'):
        cmd = f'cd {pki_dir} && easyrsa build-ca nopass'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to generate CA: {stderr}')
        message.append('CA certificate generated')
    
    # Generate server certificate and key
    if not os.path.exists(f'{pki_dir}/pki/issued/server.crt'):
        cmd = f'cd {pki_dir} && easyrsa gen-req server nopass'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to generate server request: {stderr}')
        
        cmd = f'cd {pki_dir} && easyrsa sign-req server server nopass'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to sign server certificate: {stderr}')
        message.append('Server certificate generated')
    
    # Generate Diffie-Hellman parameters
    if not os.path.exists(f'{pki_dir}/pki/dh.pem'):
        cmd = f'cd {pki_dir} && easyrsa gen-dh'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to generate DH parameters: {stderr}')
        message.append('Diffie-Hellman parameters generated')
    
    # Generate TLS authentication key
    if not os.path.exists(params['tls_auth_key']):
        cmd = f'openvpn --genkey --secret {params["tls_auth_key"]}'
        returncode, _, stderr = run_command(cmd)
        if returncode != 0:
            module.fail_json(msg=f'Failed to generate TLS auth key: {stderr}')
        message.append('TLS authentication key generated')
    
    # Copy certificates to OpenVPN directory
    os.makedirs(openvpn_dir, exist_ok=True)
    
    files_to_copy = [
        (f'{pki_dir}/pki/ca.crt', params['ca_cert']),
        (f'{pki_dir}/pki/issued/server.crt', params['server_cert']),
        (f'{pki_dir}/pki/private/server.key', params['server_key']),
        (f'{pki_dir}/pki/dh.pem', params['dh_pem']),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                with open(src, 'r') as f_in:
                    content = f_in.read()
                with open(dst, 'w') as f_out:
                    f_out.write(content)
                os.chmod(dst, 0o600)
            except Exception as e:
                module.fail_json(msg=f'Failed to copy {src} to {dst}: {str(e)}')
    
    # Set proper permissions
    try:
        os.chmod(params['server_key'], 0o600)
        os.chmod(params['ca_cert'], 0o644)
        os.chmod(params['server_cert'], 0o644)
        os.chmod(params['dh_pem'], 0o644)
        os.chmod(params['tls_auth_key'], 0o600)
    except Exception as e:
        module.fail_json(msg=f'Failed to set permissions: {str(e)}')
    
    return True, ' | '.join(message) if message else 'PKI already exists'


def write_ccd_files(module, params):
    """Write client-specific configuration (CCD) files with ifconfig-push."""
    ccd = params.get('ccd') or {}
    ccd_dir = params.get('ccd_dir') or '/etc/openvpn/ccd'

    if not ccd:
        return False, 'No CCD entries'

    try:
        os.makedirs(ccd_dir, exist_ok=True)
    except Exception as e:
        module.fail_json(msg=f'Failed to create ccd directory {ccd_dir}: {str(e)}')

    changed = False
    messages = []
    for client, value in ccd.items():
        # Accept string or list for the ifconfig-push value
        if isinstance(value, (list, tuple)):
            ifconfig_value = ' '.join(str(v) for v in value)
        else:
            ifconfig_value = str(value)

        filename = os.path.join(ccd_dir, client)
        content = f"ifconfig-push {ifconfig_value}\n"

        # Write if different
        try:
            if not os.path.exists(filename) or open(filename).read() != content:
                with open(filename, 'w') as f:
                    f.write(content)
                os.chmod(filename, 0o600)
                changed = True
                messages.append(f'Wrote CCD for {client}')
        except Exception as e:
            module.fail_json(msg=f'Failed to write CCD file {filename}: {str(e)}')

    return changed, ' | '.join(messages)



def generate_server_config(module, params):
    """Generate OpenVPN server configuration."""
    config_content = f"""
# OpenVPN Server Configuration
port {params['port']}
proto {params['protocol']}
dev tun

ca {params['ca_cert']}
cert {params['server_cert']}
key {params['server_key']}
dh {params['dh_pem']}

tls-auth {params['tls_auth_key']} 0

cipher {params['cipher']}

server {params['vpn_network']} {params['vpn_netmask']}

"""

    # Add topology setting if not p2p
    if params.get('topology', 'subnet') != 'p2p':
      config_content += f"topology {params.get('topology', 'subnet')}\n"

    # Add client-to-client if enabled
    if params.get('client_to_client'):
      config_content += "client-to-client\n"

    # Allow duplicate CNs if requested
    if params.get('duplicate_cn'):
      config_content += "duplicate-cn\n"

    # Add redirect-gateway if enabled
    if params.get('redirect_gateway'):
      config_content += 'push "redirect-gateway def1 bypass-dhcp"\n'

    # Add DNS servers
    for dns in params.get('dns_servers', []):
      config_content += f'push "dhcp-option DNS {dns}"\n'

    # Add custom routes
    for route in params.get('routes', []):
      config_content += f'push "route {route}"\n'

    # Add MSS fix if enabled
    if params.get('mssfix'):
      config_content += "mssfix\n"

    # Add fragment if specified
    if params.get('fragment', 0) > 0:
      config_content += f"fragment {params.get('fragment', 0)}\n"

    # Common default server settings
    default_server_settings = [
      "persist-key",
      "persist-tun",
      "user nobody",
      "group nogroup",
      "status openvpn-status.log",
      "verb 3",
      "mute 20",
      "keepalive 10 120",
    ]

    for line in default_server_settings:
      config_content += f"{line}\n"

    # Append any extra server options provided by the user
    for opt in params.get('extra_server_options', []) or []:
      config_content += f"{opt}\n"

    if params.get('enable_compress'):
      config_content += "compress lz4\n"
    
    config_content += """
user nobody
group nogroup

persist-key
persist-tun

status openvpn-status.log
verb 3
"""

    config_path = params['config_file']
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    config_changed = False
    if not os.path.exists(config_path):
        config_changed = True
    else:
        with open(config_path, 'r') as f:
            if f.read() != config_content:
                config_changed = True
    
    if config_changed or module.params.get('state') == 'present':
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    return config_changed, config_path


def configure_nat(module, params):
    """Configure NAT masquerading for VPN traffic."""
    if not params['enable_nat']:
        return False
    
    # Enable IP forwarding
    run_command('sysctl -w net.ipv4.ip_forward=1')
    
    # Add iptables rules
    cmd = f"iptables -t nat -A POSTROUTING -s {params['vpn_network']} -o eth0 -j MASQUERADE"
    returncode, stdout, stderr = run_command(cmd)
    
    # Save iptables rules
    run_command('iptables-save > /etc/iptables/rules.v4')
    
    return returncode == 0


def manage_service(module, action):
    """Manage OpenVPN service."""
    service_name = 'openvpn@server'
    
    if action == 'start':
        cmd = f'systemctl start {service_name}'
    elif action == 'stop':
        cmd = f'systemctl stop {service_name}'
    elif action == 'restart':
        cmd = f'systemctl restart {service_name}'
    elif action == 'status':
        cmd = f'systemctl status {service_name}'
    else:
        return False, 'Unknown action'
    
    returncode, stdout, stderr = run_command(cmd)
    
    if action == 'status':
        return True, stdout
    
    return returncode == 0, stdout + stderr


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mode=dict(type='str', choices=['server', 'client'], required=True),
            action=dict(type='str', choices=['install', 'configure', 'start', 'stop', 'restart', 'status'], required=True),
            config_file=dict(type='str', default='/etc/openvpn/server.conf'),
            ca_cert=dict(type='str', default='/etc/openvpn/ca.crt'),
            server_cert=dict(type='str', default='/etc/openvpn/server.crt'),
            server_key=dict(type='str', default='/etc/openvpn/server.key'),
            dh_pem=dict(type='str', default='/etc/openvpn/dh.pem'),
            port=dict(type='int', default=1194),
            protocol=dict(type='str', choices=['udp', 'tcp'], default='udp'),
            cipher=dict(type='str', default='AES-256-CBC'),
            vpn_network=dict(type='str', default='10.8.0.0/24'),
            vpn_netmask=dict(type='str', default='255.255.255.0'),
            enable_nat=dict(type='bool', default=True),
            enable_compress=dict(type='bool', default=True),
            tls_auth_key=dict(type='str', default='/etc/openvpn/ta.key'),
            client_to_client=dict(type='bool', default=False),
            topology=dict(type='str', choices=['subnet', 'net30', 'p2p'], default='subnet'),
            mssfix=dict(type='bool', default=True),
            fragment=dict(type='int', default=0),
            routes=dict(type='list', elements='str', default=[]),
            redirect_gateway=dict(type='bool', default=True),
            dns_servers=dict(type='list', elements='str', default=['8.8.8.8', '8.8.4.4']),
            duplicate_cn=dict(type='bool', default=False),
            ccd_dir=dict(type='str', default='/etc/openvpn/ccd'),
            ccd=dict(type='dict', default={}),
            extra_server_options=dict(type='list', elements='str', default=[]),
            state=dict(type='str', choices=['present', 'absent', 'started', 'stopped', 'restarted'], default='present'),
            generate_pki=dict(type='bool', default=False),
            pki_dir=dict(type='str', default='/etc/openvpn/easy-rsa'),
            key_size=dict(type='int', choices=[2048, 4096], default=2048),
            cert_days=dict(type='int', default=3650),
        ),
        supports_check_mode=True,
        required_together=[['mode', 'action']],
    )

    params = module.params
    changed = False
    message = []
    status = None

    try:
        # Check if OpenVPN is installed
        if not check_openvpn_installed() and params['action'] == 'install':
            if not module.check_mode:
                install_openvpn(module)
            changed = True
            message.append('OpenVPN installed')

        # Generate PKI if requested
        if params['generate_pki'] and params['action'] == 'install':
            if not module.check_mode:
                pki_success, pki_message = generate_pki(module, params)
                if pki_success:
                    changed = True
                    message.append(pki_message)
            else:
                message.append('Would generate PKI')

        # Configure OpenVPN
        if params['action'] == 'configure':
            if not module.check_mode:
                config_changed, config_path = generate_server_config(module, params)
                if config_changed:
                    changed = True
                    message.append(f'Configuration written to {config_path}')
                
                if params['enable_nat']:
                    nat_configured = configure_nat(module, params)
                    if nat_configured:
                        changed = True
                        message.append('NAT masquerading configured')
                # Write client-config-dir files if specified
                if params.get('ccd'):
                  ccd_changed, ccd_msg = write_ccd_files(module, params)
                  if ccd_changed:
                    changed = True
                    message.append(ccd_msg)
            else:
                message.append('Would generate configuration')

        # Manage service
        if params['action'] in ['start', 'stop', 'restart', 'status']:
            if not module.check_mode:
                success, output = manage_service(module, params['action'])
                if params['action'] == 'status':
                    status = output
                elif success:
                    changed = True
                    message.append(f"Service {params['action']} successful")
            else:
                message.append(f'Would {params["action"]} service')

        module.exit_json(
            changed=changed,
            message=' | '.join(message) if message else 'No changes',
            status=status,
            config_path=params['config_file']
        )

    except Exception as e:
        module.fail_json(msg=f'Error: {str(e)}')


if __name__ == '__main__':
    main()
