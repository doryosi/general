# Ansible OpenVPN Module - Contributing Guide

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ansible-openvpn-module.git
cd ansible-openvpn-module
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install ansible pytest mock
```

## Testing

### Unit Tests
```bash
python3 -m pytest tests/test_module.py -v
```

### Module Validation
```bash
ansible-doc -M plugins/modules openvpn_configure
```

### Playbook Syntax Check
```bash
ansible-playbook --syntax-check playbooks/setup_openvpn_server.yml
```

### Dry Run
```bash
ansible-playbook -i inventory/hosts.ini playbooks/setup_openvpn_server.yml --check
```

## Code Style

- Follow Python PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

## Contribution Process

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Add feature description"
```

3. Push to your fork:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request with:
   - Clear description of changes
   - Test results
   - Any breaking changes noted

## Module Enhancement Ideas

- [ ] Support for client certificate generation
- [ ] Log rotation configuration
- [ ] Performance tuning options
- [ ] Multi-protocol support
- [ ] IPv6 support
- [ ] Integration with Let's Encrypt
- [ ] Monitoring and alerting setup

## Bug Reports

Include:
- Ansible version
- Python version
- OS/Distribution
- Error messages and logs
- Steps to reproduce

## Contact

For questions, create an issue or reach out to the maintainers.
