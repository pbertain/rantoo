#!/bin/bash

# Rantoo Management Script
# This script provides common management operations for the deployed application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ANSIBLE_DIR="ansible"
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Show usage information
show_usage() {
    echo "Rantoo Management Script"
    echo "========================"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  status     - Show application status"
    echo "  logs       - Show application logs"
    echo "  restart    - Restart the application"
    echo "  stop       - Stop the application"
    echo "  start      - Start the application"
    echo "  update     - Update application code"
    echo "  health     - Check application health"
    echo "  help       - Show this help message"
    echo ""
}

# Check application status
check_status() {
    print_header "Application Status"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m systemd -a "name=rantoo state=started"
}

# Show application logs
show_logs() {
    print_header "Application Logs (last 50 lines)"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m shell -a "journalctl -u rantoo -n 50 --no-pager"
}

# Restart application
restart_app() {
    print_header "Restarting Application"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m systemd -a "name=rantoo state=restarted" --become
    print_status "Application restarted"
}

# Stop application
stop_app() {
    print_header "Stopping Application"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m systemd -a "name=rantoo state=stopped" --become
    print_status "Application stopped"
}

# Start application
start_app() {
    print_header "Starting Application"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m systemd -a "name=rantoo state=started" --become
    print_status "Application started"
}

# Update application
update_app() {
    print_header "Updating Application"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m git -a "repo={{ ansible_play_dir }}/.. dest=/opt/rantoo/app version=main force=yes" --become
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m pip -a "requirements=/opt/rantoo/app/requirements.txt virtualenv=/opt/rantoo/venv" --become
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m systemd -a "name=rantoo state=restarted" --become
    print_status "Application updated and restarted"
}


# Check application health
check_health() {
    print_header "Application Health Check"
    cd "$ANSIBLE_DIR"
    ansible  --ask-vault-pass -i "../$INVENTORY" -u "$ANSIBLE_USER" --private-key "$PRIVATE_KEY" pb_home -m uri -a "url=http://localhost:33081/health return_content=yes"
}

# Main execution
main() {
    case "${1:-help}" in
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        restart)
            restart_app
            ;;
        stop)
            stop_app
            ;;
        start)
            start_app
            ;;
        update)
            update_app
            ;;
        health)
            check_health
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
