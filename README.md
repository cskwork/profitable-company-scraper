# Profitable Company Analyzer

A web application that helps analyze publicly traded companies using real-time financial data and multi-language support.

## Features

- Real-time company search and financial data analysis
- Interactive stock price charts
- Multi-language support (English, Korean, Japanese, Chinese, Spanish, French, German)
- Comprehensive financial metrics and analysis
- Mobile-responsive design

## Deployment

The application is split into two parts:

1. Frontend (GitHub Pages)
   - Static website hosted on GitHub Pages
   - Located in the `/docs` directory

2. Backend (Vercel)
   - Flask API hosted on Vercel
   - Located in the `/api` directory

### Setup Instructions

1. Deploy the Backend (Vercel):
   ```bash
   npm install -g vercel
   vercel login
   vercel
   ```

2. Update Frontend Configuration:
   - Get your Vercel deployment URL
   - Update `docs/js/config.js` with your Vercel URL

3. Deploy Frontend (GitHub Pages):
   - Push your changes to GitHub
   - Go to repository Settings > Pages
   - Set source branch to `main` and folder to `/docs`

## Development

### Prerequisites
- Python 3.10+
- Node.js and npm (for Vercel CLI)

### Local Development
1. Install backend dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. Run the Flask development server:
   ```bash
   python index.py
   ```

3. Open `docs/index.html` in your browser

## Technologies Used

- Frontend:
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - Plotly.js
  - jQuery

- Backend:
  - Python Flask
  - yfinance
  - googletrans
  - pandas

## License

MIT License
