#!/bin/bash
# OpenVPN Certificate Generation Script
# Run this before deploying OpenVPN

set -e

# Configuration
OPENVPN_DIR="/etc/openvpn"
EASYRSA_DIR="/etc/openvpn/easy-rsa"
KEY_SIZE=2048
CERT_DAYS=3650  # 10 years

echo "=========================================="
echo "OpenVPN Certificate Generation Script"
echo "=========================================="

# Check if Easy-RSA is installed
if ! command -v easyrsa &> /dev/null; then
    echo "Installing Easy-RSA..."
    apt-get update
    apt-get install -y easy-rsa
fi

# Create Easy-RSA directory
if [ ! -d "$EASYRSA_DIR" ]; then
    echo "Creating Easy-RSA directory..."
    mkdir -p "$EASYRSA_DIR"
    cp -r /usr/share/easy-rsa/* "$EASYRSA_DIR/"
fi

cd "$EASYRSA_DIR"

# Initialize PKI
echo "Initializing PKI..."
./easyrsa init-pki || true

# Build CA
echo "Building CA certificate..."
./easyrsa build-ca nopass

# Generate server key and certificate
echo "Generating server certificate..."
./easyrsa gen-req server nopass
./easyrsa sign-req server server

# Generate Diffie-Hellman parameters
echo "Generating Diffie-Hellman parameters (this may take a while)..."
./easyrsa gen-dh

# Generate TLS authentication key
echo "Generating TLS authentication key..."
cd "$OPENVPN_DIR"
openvpn --genkey --secret ta.key || echo "TLS auth key might already exist"

# Copy certificates to OpenVPN directory
echo "Copying certificates..."
cp "$EASYRSA_DIR/pki/ca.crt" "$OPENVPN_DIR/"
cp "$EASYRSA_DIR/pki/issued/server.crt" "$OPENVPN_DIR/"
cp "$EASYRSA_DIR/pki/private/server.key" "$OPENVPN_DIR/"
cp "$EASYRSA_DIR/pki/dh.pem" "$OPENVPN_DIR/"

# Set proper permissions
echo "Setting permissions..."
chmod 600 "$OPENVPN_DIR"/server.key
chmod 644 "$OPENVPN_DIR"/server.crt
chmod 644 "$OPENVPN_DIR"/ca.crt
chmod 644 "$OPENVPN_DIR"/dh.pem
chmod 600 "$OPENVPN_DIR"/ta.key

echo "=========================================="
echo "Certificate generation completed!"
echo "Certificates saved to: $OPENVPN_DIR"
echo "=========================================="
echo ""
echo "Files created:"
ls -la "$OPENVPN_DIR"/*.{crt,key,pem} 2>/dev/null || true
