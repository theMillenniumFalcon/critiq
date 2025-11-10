# Critiq

An advanced AI-powered code review system that provides comprehensive analysis of GitHub pull requests. The system leverages multiple specialized AI agents to analyze code style, detect bugs, identify security vulnerabilities, and assess performance implications.

## Features

- 🤖 Multiple AI Analysis Agents:
  - Style Analysis
  - Bug Detection
  - Security Analysis
  - Performance Analysis
- 🔄 Asynchronous Processing with Celery
- 📊 Real-time Progress Tracking
- 🔑 GitHub Integration
- 🎨 Modern, Responsive UI

## Architecture

### Frontend (Next.js)

The client application is built with:
- Next.js 16.0
- React 19.2
- TypeScript
- Tailwind CSS
- Shadcn/UI Components
- React Query for API state management
- Zod for form validation

### Backend (FastAPI)

The server is powered by:
- FastAPI
- Celery for async task processing
- SQLAlchemy for database operations
- LangChain for AI agent coordination
- Redis for caching and task queue
- Multiple AI models (Anthropic, OpenAI)

## Project Structure

```
├── client/                 # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # Utilities and API client
│   └── public/           # Static assets
│
└── server/                # FastAPI backend
    ├── app/              
    │   ├── agents/       # AI analysis agents
    │   ├── api/          # API endpoints
    │   ├── config/       # Configuration
    │   ├── db/           # Database models
    │   ├── services/     # Business logic
    │   └── utils/        # Helper utilities
    └── celery_app.py     # Celery configuration
```

## Getting Started

1. Clone the repository
2. Set up the frontend:
   ```bash
   cd client
   npm install
   npm run dev
   ```

3. Set up the backend:
   ```bash
   cd server
   pip install -e .
   uvicorn app.main:app --reload
   ```

4. Configure environment variables for:
   - GitHub API token
   - AI model API keys
   - Database credentials
   - Redis connection

## How it Works

1. Users submit GitHub pull requests for analysis through the web interface
2. The system coordinates multiple AI agents to analyze different aspects of the code
3. Each agent processes the code changes asynchronously
4. Real-time progress updates are provided to the user
5. Comprehensive analysis results are compiled and presented

## Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct.