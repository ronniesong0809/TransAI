# Translation API

A robust translation API service with quality assessment, feedback system, and analytics.

## Features

- Text translation with quality assessment
- Translation memory for similar text matching
- Batch translation support
- Human review and modification system
- User feedback collection
- Comprehensive analytics
- Translation caching

## Tech Stack

- FastAPI
- SQLAlchemy
- OpenAI API
- Pydantic for data validation

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/translation-api.git
cd translation-api
```

2. Create and activate virtual environment:
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

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

After starting the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

#### Translation
- `POST /api/v1/translations/` - Translate single text
- `POST /api/v1/translations/batch` - Batch translate multiple texts
- `POST /api/v1/translations/{translation_id}/review` - Review translation

#### Feedback
- `POST /api/v1/feedback/{translation_id}` - Submit feedback
- `GET /api/v1/feedback/{translation_id}` - Get feedback for a translation
- `GET /api/v1/feedback/stats/overall` - Get overall feedback statistics

#### Analytics
- `GET /api/v1/analytics/overview` - Get translation analytics overview
- `GET /api/v1/analytics/language-pairs` - Get language pair statistics

## Project Structure

```
apis/
│   └── endpoints/
│       ├── translation.py
│       ├── feedback.py
│       └── analytics.py
core/
│   ├── config.py
│   ├── database.py
│   ├── openai_client.py
│   └── translation_memory.py
models/
│   ├── translation.py
│   └── feedback.py
schemas/
│   ├── translation.py
│   ├── feedback.py
│   └── analytics.py
services/
│   ├── translation_service.py
│   ├── feedback_service.py
│   └── review_service.py
└── main.py
```

## Configuration

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_openai_base_url
DATABASE_URL=sqlite:///./translations.db
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the translation backend
- FastAPI team for the excellent web framework
- SQLAlchemy team for the ORM 