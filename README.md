# OmniData.AI - The All-in-One AI Data Platform

OmniData.AI is an enterprise-grade, cross-domain AI data platform that combines the capabilities of data engineering, analysis, business intelligence, and machine learning into a single, unified solution. At its core is StanleyAI, an intelligent agent that coordinates all platform operations and assists users through natural language interaction.

## 🌟 Features

### Data Engineering
- ETL pipeline creation and management
- Data ingestion from multiple sources
- API connectors for various data services
- Automated data quality checks

### Data Analysis
- SQL query interface
- Interactive exploratory data analysis (EDA)
- KPI visualization and tracking
- Custom analysis workflows

### Business Intelligence
- Dynamic dashboard creation
- Executive reporting
- Real-time metrics monitoring
- Custom visualization builder

### Machine Learning
- AutoML capabilities
- Model training and deployment
- Performance evaluation
- Model monitoring and maintenance

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- OpenAI API key (for GPT-4)
- Google API key (for Gemini, optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/omnidata-ai.git
cd omnidata-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your API keys and configuration
```

5. Start the platform using Docker Compose:
```bash
docker-compose up -d
```

### Running the Platform

1. Start the FastAPI backend:
```bash
uvicorn omnidata.api.main:app --reload
```

2. Launch the Streamlit frontend:
```bash
streamlit run omnidata/frontend/app.py
```

3. Access the platform:
- Web UI: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## 🔧 Architecture

### Core Components

1. **StanleyAI Agent**
   - Natural language understanding
   - Task coordination
   - Intelligent decision making
   - Memory and context management

2. **FastAPI Backend**
   - RESTful API endpoints
   - JWT authentication
   - Async request handling
   - Service orchestration

3. **Streamlit Frontend**
   - Interactive chat interface
   - Data visualization
   - Dashboard builder
   - ML workspace

4. **Data Processing Engine**
   - ETL pipeline execution
   - Data transformation
   - Quality validation
   - Storage management

### Integration Points

- **VSCode Extension**: Direct IDE integration
- **Chrome Extension**: Web-based interaction
- **Mobile App**: React Native companion
- **Slack/Telegram**: Chat platform integration

## 🛠️ Development

### Project Structure
```
omnidata/
├── api/                 # FastAPI backend
├── frontend/           # Streamlit frontend
├── stanleyai/         # AI agent core
├── data_engineer/     # ETL and pipeline modules
├── analyst/           # Analysis tools
├── bi/                # BI and reporting
├── scientist/         # ML and AutoML
└── utils/            # Shared utilities
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support, please:
1. Check the [documentation](docs/)
2. Open an issue
3. Contact the maintainers

## 🙏 Acknowledgments

- OpenAI for GPT-4
- Google for Gemini
- The open-source community

---
Made with ❤️ by OmniData.AI Team # OmniData.AI
