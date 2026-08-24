# Add this to install.sh after the agent service installation:
if [[ "$DASHBOARD_OPTION" == "1" ]]; then
    print_info "Installing dashboard service..."
    sudo cp deploy/containerguard-dashboard.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable containerguard-dashboard
    sudo systemctl start containerguard-dashboard
    print_success "Dashboard service started"
fi
