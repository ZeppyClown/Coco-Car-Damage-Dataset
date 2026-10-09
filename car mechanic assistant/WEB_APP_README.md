> Historical prototype snapshot. The October 2026 rebuild changes behaviour and commands; see [BUILD_STATUS.md](BUILD_STATUS.md) and [QUICKSTART.md](QUICKSTART.md) for the current verified state.

# Car Mechanic Assistant - Web Application

A simple web interface for the AI-powered car mechanic assistant.

## Quick Start

### 1. Make sure the vector database is built

```bash
python src/vector_store.py
```

### 2. Start the web server

```bash
python web_app.py
```

### 3. Open your browser

Navigate to: **http://localhost:8080**

## Features

- 🔧 **Ask diagnostic questions** - Get AI-powered answers about car issues
- 📚 **Source tracking** - See which knowledge base documents were used
- 💡 **Example queries** - Quick-start buttons for common questions
- 📱 **Responsive design** - Works on desktop and mobile

## Example Queries

- "P0300 code on Honda Accord, what does it mean?"
- "2008 BMW 335i hard to start when hot, loses power under boost"
- "Engine shakes at idle, what to check?"
- "What oil should I use in a turbocharged engine?"
- "BMW paint code 300, what color is this?"

## Troubleshooting

### Port already in use
If port 5000 is already in use, you can change it:

```bash
export PORT=8080
python web_app.py
```

### API Key not found
Make sure your `.env` file contains:

```
GOOGLE_API_KEY=your_api_key_here
```

### Empty database
If you get no results, rebuild the database:

```bash
python src/vector_store.py --reset
```

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Google Gemini (via RAG system)
- **Database**: ChromaDB (vector embeddings)

## File Structure

```
web_app.py              # Flask application
templates/
  └── index.html        # Web interface
static/
  └── style.css         # Styling
src/
  ├── rag_system.py     # RAG logic
  ├── vector_store.py   # Vector database
  └── ...
```

## API Endpoints

- `GET /` - Main web interface
- `POST /query` - Submit queries (JSON)
- `GET /health` - Health check

## Development

To run in debug mode (auto-reload on file changes):

```bash
python web_app.py
```

Debug mode is enabled by default in `web_app.py`.
