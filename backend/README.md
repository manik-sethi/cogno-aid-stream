# BCI Confusion Monitor Backend

A Python backend service for monitoring student confusion levels using Brain-Computer Interface (BCI) data from EMOTIV devices.

## Features

- **Real-time BCI Data Processing**: Connect to EMOTIV devices and process EEG signals
- **Confusion Detection**: ML-based analysis of brain activity to detect confusion levels
- **Smart Screenshot Analysis**: Automatic screen capture and AI analysis when confusion threshold is exceeded
- **Contextual Help Generation**: LLM-powered help suggestions based on screen content
- **WebSocket Communication**: Real-time data streaming to frontend
- **Learning Analytics**: Track learning progress and generate insights
- **Mock Mode**: Development mode with simulated data when hardware isn't available

## Architecture

```
backend/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration and settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Multi-service deployment
├── bci/                        # BCI device integration
│   ├── emotiv_connector.py     # EMOTIV SDK integration
│   ├── confusion_detector.py   # ML confusion detection
│   └── data_processor.py       # EEG signal processing
├── ai/                         # AI/ML components
│   ├── screenshot_analyzer.py  # Screen capture and analysis
│   ├── help_generator.py       # Contextual help generation
│   └── llm_client.py          # LLM API integration
├── websocket/                  # Real-time communication
│   └── connection_manager.py   # WebSocket connection management
└── database/                   # Data persistence
    ├── models.py              # SQLAlchemy models
    └── database.py            # Database operations
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./bci_monitor.db

# OpenAI API (optional, uses mock mode if not provided)
OPENAI_API_KEY=your-openai-api-key

# EMOTIV API (optional, uses mock mode if not provided)
EMOTIV_CLIENT_ID=your-emotiv-client-id
EMOTIV_CLIENT_SECRET=your-emotiv-client-secret

# Development settings
DEBUG=true
LOG_LEVEL=INFO
MOCK_BCI_MODE=true
MOCK_LLM_MODE=true

# CORS for frontend
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

### 3. Run the Server

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or just the backend
docker build -t bci-backend .
docker run -p 8000:8000 bci-backend
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### WebSocket
- `WS /ws` - Real-time data streaming

### Configuration  
- `POST /threshold` - Update confusion threshold

## Real-time Data Flow

1. **BCI Data Collection**: EMOTIV device streams EEG data
2. **Signal Processing**: Raw signals are filtered and cleaned
3. **Confusion Analysis**: ML model analyzes brain activity patterns
4. **Threshold Monitoring**: System monitors for confusion spikes
5. **Screenshot Trigger**: Automatic screen capture when threshold exceeded
6. **AI Analysis**: LLM analyzes screenshot content for context
7. **Help Generation**: Contextual learning suggestions generated
8. **Frontend Updates**: Real-time updates sent via WebSocket

## Configuration Options

### BCI Settings
```python
CONFUSION_THRESHOLD=0.7         # Confusion level trigger (0.0-1.0)
SAMPLING_RATE=128              # EEG sampling rate (Hz)
CONFUSION_WINDOW_SIZE=50       # Analysis window size
```

### Signal Processing
```python
SIGNAL_HIGHPASS_FREQ=1.0       # High-pass filter (Hz)
SIGNAL_LOWPASS_FREQ=50.0       # Low-pass filter (Hz)
SIGNAL_NOTCH_FREQ=60.0         # Notch filter for power line noise
ARTIFACT_THRESHOLD=200.0       # Artifact detection threshold (μV)
```

### AI Integration
```python
OPENAI_MODEL=gpt-4-vision-preview  # Model for image analysis
OPENAI_TEXT_MODEL=gpt-4            # Model for text analysis
OPENAI_MAX_TOKENS=500              # Max response tokens
OPENAI_TEMPERATURE=0.7             # Response creativity
```

## Development Features

### Mock Mode
When hardware isn't available, the system runs in mock mode:
- Simulated EEG data generation
- Realistic confusion level variations
- Mock LLM responses for development

### Database Models
- **BCISession**: Monitoring session tracking
- **ConfusionData**: Real-time confusion measurements  
- **ScreenshotAnalysis**: Screen capture analysis results
- **HelpSuggestion**: Generated learning suggestions
- **LearningAnalytics**: Session insights and metrics

### WebSocket Events
```javascript
// Confusion level updates
{
  "type": "confusion_update",
  "data": {
    "level": 0.65,
    "timestamp": 1640995200,
    "threshold_exceeded": false
  }
}

// Help suggestions
{
  "type": "help_suggestion", 
  "data": {
    "suggestions": ["Break the problem into steps", "Review the concept"],
    "confusion_level": 0.75,
    "context": {...}
  }
}

// BCI device status
{
  "type": "bci_status",
  "data": {
    "connected": true,
    "device_info": {"type": "EMOTIV EPOC+", "channels": 14}
  }
}
```

## Production Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:5432/bci_monitor
OPENAI_API_KEY=sk-your-production-key
EMOTIV_CLIENT_ID=your-production-client-id
EMOTIV_CLIENT_SECRET=your-production-secret
DEBUG=false
MOCK_BCI_MODE=false
MOCK_LLM_MODE=false
SECRET_KEY=your-secure-secret-key
```

### Docker Deployment
```bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Monitoring
- Health check endpoint: `/health`  
- Metrics endpoint: `/metrics` (if enabled)
- Log files: `./logs/bci_monitor.log`

## Troubleshooting

### Common Issues

1. **EMOTIV Connection Failed**
   - Ensure EMOTIV device is paired and connected
   - Check client ID and secret in environment variables
   - Verify EMOTIV SDK installation

2. **High CPU Usage**
   - Reduce sampling rate or window size
   - Enable signal processing optimizations
   - Check for memory leaks in long-running sessions

3. **WebSocket Disconnections**
   - Check network stability
   - Verify CORS settings
   - Monitor connection timeouts

### Logs and Debugging
```bash
# View real-time logs
tail -f logs/bci_monitor.log

# Enable SQL query logging
DATABASE_ECHO=true

# Enable debug mode
DEBUG=true
LOG_LEVEL=DEBUG
```

## Contributing

1. Follow Python PEP 8 style guidelines
2. Add type hints for all function parameters and returns
3. Write unit tests for new features
4. Update documentation for API changes
5. Test with both mock and real hardware when possible

## License

This project is part of the BCI Confusion Monitor system for educational research.