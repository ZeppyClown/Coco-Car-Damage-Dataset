# Automotive Assistant System Architecture

## System Overview

An AI-powered automotive knowledge assistant that combines traditional software engineering with ML for workshop and real-world automotive use. The system handles text and image queries for parts identification, vehicle valuation, paint codes, specifications, and diagnostics.

## Design Principles

1. **Deterministic First**: Use rule-based logic for critical operations (pricing, data retrieval, workflows)
2. **ML Where Needed**: Apply ML only for pattern recognition (intent detection, image analysis, fuzzy matching)
3. **Mechanic-Centric**: Responses optimized for workshop decision-making, not generic chatbot behavior
4. **Modular Architecture**: Independent modules with clear interfaces for maintainability
5. **Confidence-Aware**: Always return confidence scores and alternatives when uncertain

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                          │
│                   (FastAPI REST API)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                 Request Processor                           │
│  - Input validation & preprocessing                         │
│  - Multi-modal handling (text + images)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│              Intent Classification Engine                   │
│  - Query type detection (ML-based)                          │
│  - Entity extraction (make/model/year/VIN/codes)           │
│  - Confidence scoring                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Router  │
                    └────┬────┘
         ┌──────────┬────┼────┬──────────┬──────────┐
         │          │    │    │          │          │
    ┌────▼───┐ ┌───▼──┐ │ ┌──▼───┐ ┌────▼────┐ ┌──▼──────┐
    │ Parts  │ │Valua-│ │ │Paint │ │Specs    │ │Diagnos- │
    │ Lookup │ │tion  │ │ │Code  │ │Lookup   │ │tics     │
    │ Module │ │Engine│ │ │Lookup│ │Module   │ │Module   │
    └────┬───┘ └───┬──┘ │ └──┬───┘ └────┬────┘ └──┬──────┘
         │         │    │    │          │          │
         └─────────┴────┼────┴──────────┴──────────┘
                        │
                   ┌────▼────┐
                   │Response │
                   │Formatter│
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │  User   │
                   └─────────┘
```

## Core Modules

### 1. Intent Classification Engine

**Purpose**: Determine user intent and extract entities

**Inputs**:
- Text query (natural language)
- Images (optional)
- Context (conversation history, optional)

**Outputs**:
- Intent label: `parts_identification`, `vehicle_valuation`, `paint_code`, `specifications`, `diagnostics`
- Extracted entities: `{make, model, year, vin, system, fault_codes, keywords, ...}`
- Confidence score: 0.0-1.0

**Implementation**:
- Fine-tuned transformer model (BERT/DistilBERT) for intent classification
- Named Entity Recognition (NER) for extracting vehicle details
- Rule-based extraction for VINs, fault codes (regex patterns)
- Multi-modal fusion if image provided

**Training Data Needed**:
- 5K-10K labeled automotive queries across all intent categories
- Entity annotations for vehicle makes/models/years

### 2. Parts Lookup Module

**Purpose**: Identify parts from descriptions or images and provide compatibility info

**Inputs**:
- Part description (text)
- Part image (optional)
- Vehicle context (make/model/year/VIN)

**Outputs**:
- Part matches: `[{part_number, name, description, compatibility, price_range, suppliers}]`
- Confidence scores per match
- Compatibility warnings
- Alternate/OEM equivalents

**Sub-components**:
- **Image Recognition**: CNN-based part classifier (trained on automotive parts dataset)
- **Text Matching**: TF-IDF + semantic search over parts database
- **Compatibility Engine**: Rule-based lookup using vehicle specs + part fitment data
- **Parts Database**: SQLite/PostgreSQL with indexed part catalog

**Data Sources**:
- Aftermarket parts catalogs (APIs: RockAuto, AutoZone, NAPA)
- OEM parts databases
- Custom image dataset for visual part recognition

### 3. Vehicle Valuation Engine

**Purpose**: Estimate market value based on vehicle details and condition

**Inputs**:
- Vehicle identification (VIN or make/model/year)
- Mileage
- Condition (text description + optional images)
- Location (zip code)

**Outputs**:
- Estimated value: `{low, average, high}`
- Comparable listings: `[{source, price, mileage, location, listing_url}]`
- Value factors: breakdown of adjustments (condition, mileage, location)

**Implementation**:
- **Deterministic Pricing**: Aggregate comparable listings from multiple sources
- **Condition Assessment**: ML model to score condition from text/images (optional enhancement)
- **Market Data APIs**: Kelley Blue Book, Edmunds, Cars.com, Autotrader scrapers
- **Regression Model**: Trained on historical sales data for price prediction when APIs unavailable

### 4. Paint Code Lookup Module

**Purpose**: Identify paint color codes from VIN or image

**Inputs**:
- VIN (primary method)
- Color image of vehicle (fallback)
- Vehicle make/model/year

**Outputs**:
- Paint code: manufacturer-specific code
- Color name: commercial name
- Paint formula: mixing ratios (if available)
- Match confidence (if image-based)

**Implementation**:
- **VIN Decode**: Deterministic lookup using VIN databases
- **Image-based**: CNN trained on vehicle colors → closest paint code match
- **Database**: Manufacturer paint code databases (year/make/model indexed)

### 5. Vehicle Specifications Module

**Purpose**: Retrieve detailed technical specifications

**Inputs**:
- VIN (preferred)
- Make/model/year/trim

**Outputs**:
- Complete vehicle specs: engine, transmission, dimensions, capacities, features
- Service intervals and fluid specs
- Recall information

**Implementation**:
- VIN decoder (NHTSA API, commercial VIN databases)
- Specifications database (SQLite/PostgreSQL)
- Static data with periodic updates

### 6. Diagnostics & Troubleshooting Module

**Purpose**: Assist with fault diagnosis and repair procedures

**Inputs**:
- Vehicle identification
- System (engine, transmission, brakes, etc.)
- Fault codes (DTCs)
- Symptom description

**Outputs**:
- Likely causes: ranked list with probabilities
- Diagnostic steps: troubleshooting flowchart
- Repair procedures: step-by-step instructions
- Parts needed: linked to parts module
- Software/coding requirements (for modern vehicles)

**Implementation**:
- **Fault Code Database**: DTC definitions with common causes
- **Diagnostic Knowledge Base**: Graph database (Neo4j) of symptoms → causes → repairs
- **Retrieval System**: Semantic search over repair manuals and technical bulletins
- **Reasoning Engine**: Rule-based + ML ranking of likely causes

## Data Layer

### Databases

1. **Parts Database** (PostgreSQL)
   - Tables: parts, compatibility, manufacturers, suppliers
   - Indexes: part_number, vehicle_compatibility, category

2. **Vehicle Specifications** (PostgreSQL)
   - Tables: vehicles, specs, paint_codes, recalls
   - Indexes: vin, make_model_year

3. **Diagnostics Knowledge Base** (Neo4j Graph DB)
   - Nodes: symptoms, causes, repairs, parts
   - Relationships: leads_to, requires, compatible_with

4. **Market Data Cache** (Redis)
   - TTL-based cache for valuation API responses
   - Recent comparable listings

### External APIs

- VIN Decoding: NHTSA, Carfax, AutoCheck
- Parts Data: RockAuto, AutoZone, NAPA, FCP Euro APIs
- Market Data: KBB, Edmunds, Autotrader
- Paint Codes: Manufacturer databases

## ML Components

### Models Required

1. **Intent Classifier**
   - Architecture: DistilBERT or BERT-base
   - Training: Multi-class classification (5-6 intent classes)
   - Dataset: 5K-10K labeled queries
   - Metrics: Accuracy, F1-score per class

2. **Entity Extractor (NER)**
   - Architecture: BERT-based NER or spaCy custom NER
   - Entities: MAKE, MODEL, YEAR, VIN, SYSTEM, FAULT_CODE, PART_NAME
   - Training: 3K-5K annotated queries

3. **Parts Image Classifier**
   - Architecture: ResNet50 or EfficientNet
   - Classes: 50-100 common automotive parts
   - Dataset: 10K+ labeled images (augmented)
   - Metrics: Top-1 and Top-5 accuracy

4. **Paint Color Matcher**
   - Architecture: CNN feature extractor + similarity search
   - Training: Color images mapped to manufacturer paint codes
   - Dataset: 2K+ paint code samples with images

5. **Condition Assessment (Optional)**
   - Architecture: Multi-modal model (CLIP-based or custom)
   - Input: Images + text description
   - Output: Condition score (1-10)

### Training Infrastructure

- Dataset storage: S3 or local storage
- Training: PyTorch on GPU (local or cloud)
- Model versioning: MLflow or Weights & Biases
- Model serving: TorchServe or FastAPI endpoints

## API Design

### REST API Endpoints

```
POST /api/v1/query
  - Main entry point for all queries
  - Request: {text, images[], context{}}
  - Response: {intent, entities, result{}, confidence}

POST /api/v1/parts/identify
  - Specific parts lookup
  - Request: {description, image, vehicle{}}
  - Response: {matches[], confidence}

POST /api/v1/valuation/estimate
  - Vehicle valuation
  - Request: {vin/vehicle{}, mileage, condition{}, location}
  - Response: {estimate{}, comparables[], factors{}}

POST /api/v1/paint-code/lookup
  - Paint code identification
  - Request: {vin, image, vehicle{}}
  - Response: {code, name, formula, confidence}

GET /api/v1/specifications/{vin}
  - Vehicle specifications by VIN
  - Response: {specs{}, recalls[]}

POST /api/v1/diagnostics/troubleshoot
  - Diagnostic assistance
  - Request: {vehicle{}, system, codes[], symptoms}
  - Response: {causes[], diagnostic_steps[], repairs[]}
```

### Response Format

All responses follow this structure:

```json
{
  "success": true,
  "intent": "parts_identification",
  "confidence": 0.92,
  "result": {
    // Module-specific results
  },
  "metadata": {
    "processing_time_ms": 234,
    "models_used": ["intent_classifier_v2", "parts_cnn_v1"],
    "sources": ["rockauto_api", "parts_db"]
  },
  "follow_up_questions": [
    "Do you need the OEM part or are aftermarket alternatives acceptable?"
  ],
  "next_steps": [
    "Check compatibility with your specific trim level",
    "Compare prices from multiple suppliers"
  ]
}
```

## Technology Stack

### Backend
- **Framework**: FastAPI (async, high performance, automatic API docs)
- **Language**: Python 3.10+
- **Databases**: PostgreSQL (relational), Neo4j (graph), Redis (cache)
- **ORM**: SQLAlchemy
- **API Client**: httpx (async HTTP)

### ML/AI
- **Framework**: PyTorch
- **NLP**: Transformers (Hugging Face), spaCy
- **Computer Vision**: torchvision, timm
- **Model Serving**: TorchServe or embedded in FastAPI

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **API Gateway**: FastAPI built-in (or Nginx for production)
- **Task Queue**: Celery + Redis (for async processing)
- **Monitoring**: Prometheus + Grafana
- **Logging**: structlog + ELK stack (optional)

### Development
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, ruff, mypy
- **Documentation**: mkdocs
- **Version Control**: Git + GitHub

## Deployment Architecture

### Development Setup
```
docker-compose.yml:
  - fastapi-app (port 8000)
  - postgresql (port 5432)
  - neo4j (port 7474, 7687)
  - redis (port 6379)
```

### Production Considerations
- Kubernetes for orchestration
- Separate ML model serving endpoints
- CDN for static assets (images)
- Rate limiting and authentication
- Database replication
- Multi-region deployment (optional)

## Security & Performance

### Security
- API key authentication for external access
- Rate limiting per user/IP
- Input validation and sanitization
- VIN/PII data handling compliance
- HTTPS only in production

### Performance
- Response caching (Redis)
- Database query optimization (indexes, connection pooling)
- Model inference optimization (ONNX, TorchScript)
- Async I/O for API calls
- Image preprocessing pipeline
- Target: < 500ms for text queries, < 2s for image queries

## Monitoring & Observability

- Request logging with structured logs
- Model performance metrics (accuracy, latency)
- API endpoint metrics (requests/sec, error rates)
- Database performance monitoring
- Alert on model degradation or API failures
- User feedback collection for continuous improvement

## Next Steps

See `IMPLEMENTATION_PLAN.md` for phased development roadmap.
