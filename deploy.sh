#!/bin/bash

# Rantoo Deployment Script
# This script deploys the Flask application using Ansible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ANSIBLE_DIR="ansible"
PLAYBOOK="playbooks/deploy.yml"
INVENTORY="hosts"
ANSIBLE_USER="ansible"
PRIVATE_KEY="~/.ssh/keys/nirdclub__id_ed25519"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if ansible is installed
check_ansible() {
    if ! command -v ansible-playbook &> /dev/null; then
        print_error "Ansible is not installed. Please install it first:"
        echo "  pip install ansible"
        echo "  or"
        echo "  brew install ansible  # on macOS"
        exit 1
    fi
}

# Check if inventory file exists
check_inventory() {
    if [ ! -f "$INVENTORY" ]; then
        print_error "Inventory file not found: $INVENTORY"
        print_error "Expected to find hosts file at: $INVENTORY"
        exit 1
    fi
    
    print_status "Using inventory file: $INVENTORY"
}

# Run ansible playbook
deploy() {
    print_status "Starting deployment..."
    
    cd "$ANSIBLE_DIR"
    
    # Test connection first
    print_status "Testing connection to hosts..."
    ansible --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m ping
    
    # Run the playbook
    print_status "Running deployment playbook..."
    ansible-playbook --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" "$PLAYBOOK"
    
    print_status "Deployment completed successfully!"
}

# Main execution
main() {
    print_status "Rantoo Deployment Script"
    echo "================================"
    
    check_ansible
    check_inventory
    deploy
}

# Run main function
main "$@"
