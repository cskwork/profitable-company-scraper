# Profitable Company Scraper

A web application that helps users analyze company profitability and financial health using Yahoo Finance data. The application provides stock analysis, financial metrics, and translated summaries in multiple languages.

## Features

- Company search functionality
- Real-time stock data analysis
- Financial health assessment
- Multi-language support (English and Korean)
- Interactive stock price charts
- Key financial metrics display

## Project Structure

```
profitable-company-scraper/
├── api/                    # Main application backend
│   └── index.py           # Flask API endpoints and business logic
├── docs/                  # Frontend assets and documentation
│   └── js/               # JavaScript files for frontend
├── templates/            # HTML templates
│   └── index.html        # Main application page
├── data/                 # Data storage directory
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment configuration
└── vercel.json          # Vercel configuration (alternative deployment)
```

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, JavaScript
- APIs: Yahoo Finance (yfinance)
- Translation: Google Translate
- Deployment: Render

## Dependencies

```
flask==3.0.0
flask-cors==4.0.0
yfinance==0.2.31
googletrans==3.1.0a0
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cskwork/profitable-company-scraper.git
cd profitable-company-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python api/index.py
```

## Usage

1. Access the application through your web browser
2. Enter a company stock symbol or name in the search bar
3. View detailed financial analysis and metrics
4. Toggle between languages using the language selector

## Live Demo

The application is deployed and accessible at:
[Render Deployment](https://profitable-company-scraper.onrender.com)

## Development

The main application code is in `api/index.py`, which handles:
- Company search and data retrieval
- Financial analysis and calculations
- Multi-language support
- API endpoints for frontend interaction

## Archive

Previous versions and unused components are stored in the `archive/` directory for reference.

## License

MIT License
