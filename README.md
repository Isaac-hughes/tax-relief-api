# UK Tax Relief API

A FastAPI-based REST API that provides personalised tax relief recommendations for UK professionals using zero-shot classification with the BART language model.

## Features

- Zero-shot classification for tax relief recommendations
- Profession-specific tax rules
- Request caching and rate limiting
- Response compression
- Performance monitoring
- CORS support for frontend integration

## Prerequisites

- Python 3.10+
- pip or pipenv

## Installation

1. Clone the repository:
   git clone <repository-url>
   cd tax-relief-api

2. Create and activate a virtual environment:
   python3.10 -m venv venv
   source venv/bin/activate # On Windows use: venv\Scripts\activate

3. Install dependencies:
   Install numpy first to avoid version conflicts
   pip install "numpy<2.0"
   Install other dependencies
   pip install fastapi uvicorn
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install transformers
   pip install pydantic

## Running the API

1. Start the server:
   uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`

2. View the API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/tax-relief

Generate tax relief recommendations based on profession and questions.

**Request Body:**

```json
{
  "profession": "Chef",
  "questions": "I clean my own uniform and buy kitchen knives for work"
}
```

**Response:**

```json
{
  "recommendations": [
    "Uniform cleaning allowance: Must purchase and clean uniform yourself",
    "Kitchen equipment allowance: Purchase of essential kitchen tools and equipment for work"
  ]
}
```
