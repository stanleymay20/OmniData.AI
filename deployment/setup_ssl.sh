#!/bin/bash

# Exit on error
set -e

# Check if running in production
if [ "$ENVIRONMENT" != "production" ]; then
    echo "Not in production environment, skipping SSL setup"
    exit 0
fi

# Check for required environment variables
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Error: DOMAIN and EMAIL environment variables must be set"
    exit 1
fi

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
systemctl stop nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate for $DOMAIN..."
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN" \
    --preferred-challenges http

# Configure nginx with SSL
echo "Configuring nginx with SSL..."
cat > /etc/nginx/sites-available/default << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Start nginx
systemctl start nginx

# Set up automatic renewal
echo "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

echo "SSL setup completed successfully!" 