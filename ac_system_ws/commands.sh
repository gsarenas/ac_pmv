# Enable auto load on boot
sudo systemctl enable mosquitto

# Disable auto load on boot
sudo systemctl disable mosquitto

# Start mosquitto
sudo systemctl start mosquitto

# Stop mosquitto
sudo systemctl stop mosquitto

# Restart mosquitto
sudo systemctl restart mosquitto

# Check mosquitto status
sudo systemctl status mosquitto

# Edit mosquitto config
sudo nano /etc/mosquitto/mosquitto.conf

# Start node-red
node-red

# Restart node-red
node-red-restart

# Edit node-red config
nano ~/.node-red/settings.js

# Reset node-red
sudo rm -r ~/.node-red/flows.json