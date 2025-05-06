# Convo AI

A locally-hosted AI assistant that combines lightweight language models with text-to-speech capabilities.

## Prerequisites

- Python 3.8+
- Docker
- Ollama (for LLM)
- OpenWebUI (for interface)

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama:
```bash
brew install ollama  # macOS
# or
curl https://ollama.ai/install.sh | sh  # Linux
```

3. Pull the LLM model:
```bash
ollama pull phi3:4b-q4_0
```

4. Start the services:
```bash
# Terminal 1 - LLM
ollama serve

# Terminal 2 - Sesame TTS
docker run -p 5000:5000 phildougherty/sesame_csm_openai

# Terminal 3 - API Server
python src/main.py

# Terminal 4 - OpenWebUI
git clone https://github.com/OpenWebUI/OpenWebUI
cd OpenWebUI && docker compose up
```

5. Access the interface at http://localhost:3000

## Configuration

Create a `.env` file in the root directory with your configuration:

```env
OPENAI_API_KEY=your_key_here  # For moderation
```

## Features

- Lightweight LLM (Phi-3-mini or Gemma-2B)
- Sesame CSM-1B text-to-speech
- Content moderation
- Web interface with voice capabilities

## Development

The project uses FastAPI for the backend API. The main components are:

- `src/main.py`: FastAPI application and routes
- `requirements.txt`: Python dependencies

## License

MIT 