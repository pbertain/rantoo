#!/bin/bash

# Rantoo Deployment Script
# This script deploys the Rantoo Flask application using Ansible

set -e

# Configuration
ANSIBLE_DIR="ansible"
PLAYBOOK="playbooks/deploy.yml"
INVENTORY="hosts"
ANSIBLE_USER="ansible"
PRIVATE_KEY="~/.ssh/keys/nirdclub__id_ed25519"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if inventory file exists
check_inventory() {
    if [ ! -f "$INVENTORY" ]; then
        print_error "Inventory file '$INVENTORY' not found!"
        exit 1
    fi
    print_status "Using inventory file: $INVENTORY"
}

# Deploy function
deploy() {
    print_status "Starting deployment..."
    
    cd "$ANSIBLE_DIR"
    
    # Test connection first
    print_status "Testing connection to hosts..."
    ansible -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m ping
    
    # Run the playbook
    print_status "Running deployment playbook..."
    ansible-playbook --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" "$PLAYBOOK"
    
    print_status "Deployment completed successfully!"
}

# Main execution
main() {
    echo -e "${BLUE}[INFO]${NC} Rantoo Deployment Script"
    echo "================================"
    
    check_inventory
    deploy
    
    print_success "All done!"
}

# Run main function
main "$@"
