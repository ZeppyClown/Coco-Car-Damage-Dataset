# Automotive Assistant System

An AI-powered automotive knowledge and assistant system designed for workshop and real-world automotive use.

## Features

- **Intent Detection**: Automatically classifies user queries (parts, valuation, paint codes, specs, diagnostics)
- **Parts Identification**: Text and image-based parts lookup with compatibility checking
- **Vehicle Valuation**: Market-based pricing with comparable listings
- **Paint Code Lookup**: VIN-based and image-based paint color identification
- **Specifications**: Complete vehicle specs from VIN or make/model/year
- **Diagnostics**: Fault code lookup and troubleshooting assistance

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and module specifications.

## Implementation Plan

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the phased development roadmap.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- 8GB RAM minimum (16GB recommended)
- GPU recommended for ML training (optional for inference)

### Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd Coco\ Car\ Damage\ Dataset
```

2. Create a virtual environment:
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
cp .env.example .env
# Edit .env with your configuration
```

5. Start the services with Docker Compose:
```bash
docker-compose up -d
```

6. Run database migrations:
```bash
python scripts/init_db.py
```

7. Start the API server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. Access the API documentation:
```
http://localhost:8000/docs
```

## Development

### Project Structure

```
.
├── app/
│   ├── api/              # API endpoints
│   │   ├── v1/
│   │   │   ├── query.py
│   │   │   ├── parts.py
│   │   │   ├── valuation.py
│   │   │   ├── paint_code.py
│   │   │   ├── specifications.py
│   │   │   └── diagnostics.py
│   │   └── deps.py       # Dependencies
│   ├── core/             # Core functionality
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/           # ML models
│   │   ├── intent_classifier.py
│   │   ├── entity_extractor.py
│   │   ├── parts_classifier.py
│   │   └── paint_matcher.py
│   ├── services/         # Business logic
│   │   ├── intent_service.py
│   │   ├── parts_service.py
│   │   ├── valuation_service.py
│   │   ├── paint_service.py
│   │   ├── specs_service.py
│   │   └── diagnostics_service.py
│   ├── db/               # Database
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── session.py
│   │   └── migrations/
│   ├── schemas/          # Pydantic schemas
│   │   ├── query.py
│   │   ├── parts.py
│   │   ├── valuation.py
│   │   └── common.py
│   └── main.py           # FastAPI app
├── tests/
│   ├── unit/
│   └── integration/
├── data/
│   ├── raw/              # Raw datasets
│   ├── processed/        # Processed datasets
│   └── models/           # Trained models
├── scripts/
│   ├── init_db.py
│   ├── train_intent_classifier.py
│   ├── train_parts_classifier.py
│   └── seed_data.py
├── config/
│   └── logging.yaml
├── docs/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_intent_classifier.py
```

### Code Quality

```bash
# Format code
black app tests

# Lint
ruff check app tests

# Type checking
mypy app
```

## API Usage

### Query Endpoint (Main Entry Point)

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I need a brake pad for my 2015 Honda Civic",
    "context": {}
  }'
```

Response:
```json
{
  "success": true,
  "intent": "parts_identification",
  "confidence": 0.94,
  "entities": {
    "year": "2015",
    "make": "Honda",
    "model": "Civic",
    "part_name": "brake pad"
  },
  "result": {
    "matches": [
      {
        "part_number": "D1092",
        "name": "Front Brake Pad Set",
        "description": "Ceramic brake pads for 2015 Honda Civic",
        "compatibility": "Compatible with 2015 Honda Civic LX/EX/Touring",
        "price_range": {"min": 45.99, "max": 89.99},
        "confidence": 0.92
      }
    ]
  },
  "follow_up_questions": [
    "Do you need front or rear brake pads?"
  ],
  "next_steps": [
    "Verify your trim level for exact compatibility",
    "Check if rotors also need replacement"
  ]
}
```

### Parts Identification with Image

```bash
curl -X POST "http://localhost:8000/api/v1/parts/identify" \
  -F "image=@part_photo.jpg" \
  -F "description=brake part" \
  -F "vehicle={\"year\":\"2015\",\"make\":\"Honda\",\"model\":\"Civic\"}"
```

### Vehicle Valuation

```bash
curl -X POST "http://localhost:8000/api/v1/valuation/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "mileage": 75000,
    "condition": "Good",
    "location": "90210"
  }'
```

### Paint Code Lookup

```bash
curl -X GET "http://localhost:8000/api/v1/paint-code/lookup?vin=1HGBH41JXMN109186"
```

### Diagnostics

```bash
curl -X POST "http://localhost:8000/api/v1/diagnostics/troubleshoot" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": {"year": "2015", "make": "Honda", "model": "Civic"},
    "system": "engine",
    "fault_codes": ["P0171"],
    "symptoms": "rough idle, check engine light on"
  }'
```

## ML Model Training

### Intent Classifier

```bash
python scripts/train_intent_classifier.py \
  --data data/raw/intent_training_data.json \
  --model distilbert-base-uncased \
  --epochs 10 \
  --output data/models/intent_classifier_v1
```

### Parts Image Classifier

```bash
python scripts/train_parts_classifier.py \
  --data data/raw/parts_images/ \
  --model resnet50 \
  --epochs 20 \
  --output data/models/parts_classifier_v1
```

## Configuration

Key environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `NEO4J_URI`: Neo4j connection string
- `API_KEY`: API key for authentication
- `VIN_DECODER_API_KEY`: VIN decoder service API key
- `MARKET_DATA_API_KEY`: Market data API key (KBB, Edmunds)

## Deployment

### Docker

```bash
docker build -t automotive-assistant .
docker run -p 8000:8000 automotive-assistant
```

### Docker Compose

```bash
docker-compose up -d
```

### Production

See [docs/deployment.md](docs/deployment.md) for production deployment guide.

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run code quality checks
4. Submit pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions, please open a GitHub issue.
