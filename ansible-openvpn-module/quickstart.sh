#!/bin/bash
# Quick start script for OpenVPN Ansible Module

set -e

echo "=========================================="
echo "OpenVPN Ansible Module - Quick Start"
echo "=========================================="
echo ""

# Check for required tools
echo "[1] Checking prerequisites..."
for cmd in ansible ansible-playbook python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is not installed"
        exit 1
    fi
done
echo "✓ All prerequisites installed"
echo ""

# Display structure
echo "[2] Module Structure:"
echo "├── plugins/modules/openvpn_configure.py - Main module"
echo "├── roles/openvpn/ - OpenVPN role"
echo "├── playbooks/"
echo "│   ├── setup_openvpn_server.yml"
echo "│   └── setup_openvpn_client.yml"
echo "├── inventory/hosts.ini - Host inventory"
echo "└── scripts/generate_certs.sh - Certificate generation"
echo ""

# Instructions
echo "[3] Getting Started:"
echo ""
echo "Step 1: Generate OpenVPN certificates (on server)"
echo "  sudo bash scripts/generate_certs.sh"
echo ""
echo "Step 2: Update inventory file"
echo "  Edit inventory/hosts.ini with your server/client IPs"
echo ""
echo "Step 3: Run the playbook"
echo "  ansible-playbook playbooks/setup_openvpn_server.yml"
echo ""
echo "Step 4: Check OpenVPN status"
echo "  ssh user@vpn-server 'sudo systemctl status openvpn@server'"
echo ""
echo "=========================================="
echo ""
echo "For more information, see README.md"
echo ""
