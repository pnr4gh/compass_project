#!/bin/bash

# Pull the latest code changes from the repository
echo "Pulling latest changes from Git..."
git pull || { echo "Git pull failed. Exiting."; exit 1; }

# Restart the compass service
echo "Restarting the compass service..."
sudo systemctl restart compass || { echo "Failed to restart compass. Exiting."; exit 1; }

# Restart the daemon service
echo "Restarting the daemon service..."
sudo systemctl daemon-reload || { echo "Failed to restart daemon. Exiting."; exit 1; }

# Restart the Nginx service
echo "Restarting Nginx..."
sudo systemctl restart nginx || { echo "Failed to restart Nginx. Exiting."; exit 1; }

echo "All services restarted successfully!"
