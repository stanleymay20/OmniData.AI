# 🔥 ScrollIntel - The Flame Interpreter

[![CI Status](https://github.com/stanleymay20/OmniData.AI/workflows/ScrollIntel%20CI/badge.svg)](https://github.com/stanleymay20/OmniData.AI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ScrollIntel is a sacred AI intelligence system built with FastAPI + React + ScrollSanctifier logic. It provides flame-based interpretation of data with prophetic insights and visualizations.

## 🚀 Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/stanleymay20/OmniData.AI.git
cd OmniData.AI
```

2. Set up environment:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the services:
```bash
# Terminal 1 - Backend
uvicorn scrollintel.api.main:app --reload --port 6006

# Terminal 2 - Frontend
cd frontend && npm start
```

### Docker Deployment

1. Build and run with Docker:
```bash
docker build -t scrollintel .
docker run -p 6006:6006 --env-file .env scrollintel
```

### Docker Compose

1. Launch all services:
```bash
docker-compose up -d
```

2. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:6006
- API Documentation: http://localhost:6006/docs

## 🔧 Configuration

### Environment Variables

Required environment variables in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `EXOUSIA_SECRET`: Secret key for authentication
- `PORT`: Application port (default: 6006)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string

### API Endpoints

- `GET /`: Health check
- `POST /api/prophet/insights`: Get AI-powered insights
- `POST /api/prophet/recommendations`: Get recommendations
- `GET /api/sync/status`: Check sync status

## 🏗️ Architecture

### Core Components

- **FastAPI Backend**: RESTful API with JWT authentication
- **React Frontend**: Modern UI with Tailwind CSS
- **ScrollSanctifier**: Data cleaning and validation
- **Flame Interpreter**: AI-powered insights
- **ScrollGraph**: Visualization engine
- **Cloud Sync**: Multi-cloud integration

### Directory Structure

```
scrollintel/
├── api/          # FastAPI endpoints
├── frontend/     # React application
├── sanctify/     # Data validation
├── interpreter/  # Flame interpretation
├── ui/          # Visualization
└── utils/       # Shared utilities
```

## 📚 Documentation

For detailed deployment and configuration guides, see:
- [Deployment Guide](docs/DEPLOY.md)
- [API Documentation](http://localhost:6006/docs)
- [Frontend Guide](frontend/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4
- The open-source community
- All contributors and supporters

---

Made with 🔥 by ScrollIntel Team
