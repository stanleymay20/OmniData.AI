# 🚀 ScrollIntel Deployment Guide

This guide provides detailed instructions for deploying ScrollIntel in various environments.

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

## 🔧 Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/stanleymay20/OmniData.AI.git
cd OmniData.AI
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🐳 Docker Deployment

### Local Development

1. Build and start services:
```bash
docker-compose up -d
```

2. Access services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:6006
- API Docs: http://localhost:6006/docs

### Production Deployment

1. Build production images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Start production services:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Cloud Deployment

### AWS EC2

1. Launch EC2 instance:
```bash
# Using AWS CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxx
```

2. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```

3. Deploy application:
```bash
git clone https://github.com/stanleymay20/OmniData.AI.git
cd OmniData.AI
docker-compose -f docker-compose.prod.yml up -d
```

### Google Cloud Run

1. Build container:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/scrollintel
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy scrollintel \
    --image gcr.io/YOUR_PROJECT_ID/scrollintel \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## 🔐 Security Considerations

1. Environment Variables:
   - Never commit `.env` files
   - Use secrets management in production
   - Rotate keys regularly

2. Network Security:
   - Use HTTPS in production
   - Configure CORS properly
   - Set up rate limiting

3. Database Security:
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

## 📊 Monitoring

1. Health Checks:
   - Backend: `GET /health`
   - Frontend: `GET /_stcore/health`

2. Logging:
   - Backend logs: `docker-compose logs -f backend`
   - Frontend logs: `docker-compose logs -f frontend`

3. Metrics:
   - Prometheus endpoint: `/metrics`
   - Grafana dashboard available

## 🔄 Scaling

1. Horizontal Scaling:
```bash
docker-compose up -d --scale backend=3
```

2. Load Balancing:
   - Use Nginx as reverse proxy
   - Configure sticky sessions

## 🛠️ Troubleshooting

1. Common Issues:
   - Database connection errors
   - Redis connection timeouts
   - Frontend build failures

2. Debug Commands:
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

## 📚 Additional Resources

- [API Documentation](http://localhost:6006/docs)
- [Frontend Guide](frontend/README.md)
- [Architecture Overview](ARCHITECTURE.md)

## 🤝 Support

For deployment support:
1. Check the documentation
2. Open an issue
3. Contact the maintainers

---

Made with 🔥 by ScrollIntel Team 