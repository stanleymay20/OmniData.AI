#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Clone repository
git clone https://github.com/stanleymay20/OmniData.AI.git
cd OmniData.AI

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Get SSL certificate
sudo certbot --nginx -d scrollintel.yourdomain.com

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 6006/tcp
sudo ufw enable

# Set up automatic certificate renewal
echo "0 0 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab > /dev/null

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f 