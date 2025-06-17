from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time
from googletrans import Translator

app = Flask(__name__, template_folder='../templates', static_folder='../static')
translator = Translator()

def search_companies(query):
    """Search for companies using Yahoo Finance API."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if 'quotes' in data:
        return [{
            'symbol': quote.get('symbol'),
            'name': quote.get('shortname'),
            'exchange': quote.get('exchange'),
            'type': quote.get('quoteType')
        } for quote in data['quotes'] if quote.get('quoteType') == 'EQUITY']
    return []

def get_company_data(symbol):
    """Get comprehensive company data using yfinance."""
    try:
        print(f"Fetching data for symbol: {symbol}")
        stock = yf.Ticker(symbol)
        
        # Force info download with a small delay to avoid rate limits
        time.sleep(1)
        info = stock.info
        
        print(f"Raw info keys: {info.keys() if info else 'No info available'}")
        
        if not info or len(info) == 0:
            print(f"No data found for symbol: {symbol}")
            return None
            
        # Basic company info - required fields
        company_info = {
            'symbol': symbol,
            'name': info.get('shortName', info.get('longName', 'N/A')),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'currency': info.get('currency', 'USD')
        }
        
        # Format market cap
        market_cap = info.get('marketCap', 0)
        if market_cap:
            if market_cap > 1e12:
                market_cap_str = f"{market_cap/1e12:.2f}T"
            elif market_cap > 1e9:
                market_cap_str = f"{market_cap/1e9:.2f}B"
            elif market_cap > 1e6:
                market_cap_str = f"{market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"{market_cap:.2f}"
        else:
            market_cap_str = "N/A"

        # Get trailing PE or forward PE if trailing is not available
        trailing_pe = info.get('trailingPE', info.get('forwardPE', 0))
        
        # Calculate revenue growth, default to 0 if not available
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth is None:
            revenue_growth = 0

        # Safely get profit margins
        profit_margins = info.get('profitMargins', 0)
        if profit_margins is None:
            profit_margins = 0

        # Combine all data
        company_info.update({
            'Market Cap': market_cap_str,
            'Enterprise Value': info.get('enterpriseValue', 'N/A'),
            'Trailing P/E': trailing_pe,
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'PEG Ratio (5yr expected)': info.get('pegRatio', 'N/A'),
            'Price/Sales': info.get('priceToSalesTrailing12Months', 'N/A'),
            'Price/Book': info.get('priceToBook', 'N/A'),
            'Enterprise Value/Revenue': info.get('enterpriseToRevenue', 'N/A'),
            'Enterprise Value/EBITDA': info.get('enterpriseToEbitda', 'N/A'),
            'Profit Margin': f"{profit_margins * 100:.2f}%" if profit_margins is not None else 'N/A',
            'Operating Margin  (ttm)': f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') is not None else 'N/A',
            'Return on Assets  (ttm)': f"{info.get('returnOnAssets', 0) * 100:.2f}%" if info.get('returnOnAssets') is not None else 'N/A',
            'Return on Equity  (ttm)': f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') is not None else 'N/A',
            'Revenue  (ttm)': info.get('totalRevenue', 'N/A'),
            'Revenue Per Share  (ttm)': info.get('revenuePerShare', 'N/A'),
            'Quarterly Revenue Growth  (yoy)': f"{revenue_growth * 100:.2f}%" if revenue_growth is not None else 'N/A',
            'Gross Profit  (ttm)': info.get('grossProfits', 'N/A'),
            'EBITDA': info.get('ebitda', 'N/A'),
            'Net Income': info.get('netIncomeToCommon', 'N/A'),
            'EPS (ttm)': info.get('trailingEps', 'N/A'),
            'EPS Growth (yoy)': f"{info.get('earningsGrowth', 0) * 100:.2f}%" if info.get('earningsGrowth') is not None else 'N/A',
            'Free Cash Flow': info.get('freeCashflow', 'N/A'),
            'Operating Cash Flow': info.get('operatingCashflow', 'N/A'),
            'Beta (5Y Monthly)': info.get('beta', 'N/A'),
            'Shares Outstanding': info.get('sharesOutstanding', 'N/A'),
            'Forward Annual Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') is not None else 'N/A',
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Company Description': info.get('longBusinessSummary', 'No description available.')
        })
        
        print(f"Successfully processed data for {symbol}")
        return company_info
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_stock_data(symbol, period='1y'):
    """Get historical stock data."""
    try:
        print(f"Fetching historical data for {symbol}")
        stock = yf.Ticker(symbol)
        
        # Try to download with a small delay
        time.sleep(1)
        hist = stock.history(period=period, interval='1d')
        
        if hist.empty:
            print(f"No historical data found for symbol: {symbol}")
            return None
            
        # Convert index to string dates
        hist.index = hist.index.strftime('%Y-%m-%d')
        
        # Round values to 2 decimal places
        for col in hist.columns:
            if hist[col].dtype in ['float64', 'float32']:
                hist[col] = hist[col].round(2)
                
        return hist
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {str(e)}")
        return None

def generate_company_summary(company_data, stock_history):
    """Generate a brief summary of company's financial health and performance."""
    try:
        # Extract key metrics
        profit_margin = float(company_data['Profit Margin'].strip('%'))
        pe_ratio = float(company_data['Trailing P/E']) if company_data['Trailing P/E'] != 0 else 0
        revenue_growth = float(company_data['Quarterly Revenue Growth  (yoy)'].strip('%'))
        operating_margin = float(company_data['Operating Margin  (ttm)'].strip('%'))
        roe = float(company_data['Return on Equity  (ttm)'].strip('%'))
        
        # Calculate stock performance
        if not stock_history.empty:
            start_price = stock_history['Close'].iloc[0]
            end_price = stock_history['Close'].iloc[-1]
            price_change_pct = ((end_price - start_price) / start_price) * 100
        else:
            price_change_pct = 0
        
        # Generate summary insights
        insights = []
        
        # Add company sector and industry
        if company_data['Sector'] != 'N/A':
            insights.append(f"Operating in {company_data['Sector']} sector, {company_data['Industry']} industry")
        
        # Profitability assessment
        if profit_margin > 20:
            insights.append("Highly profitable with strong profit margins")
        elif profit_margin > 10:
            insights.append("Good profitability")
        else:
            insights.append("Lower profit margins compared to industry standards")
        
        # Growth assessment
        if revenue_growth > 20:
            insights.append("Exceptional revenue growth")
        elif revenue_growth > 10:
            insights.append("Solid revenue growth")
        elif revenue_growth > 0:
            insights.append("Moderate revenue growth")
        else:
            insights.append("Declining revenue")
        
        # Efficiency assessment
        if operating_margin > 25:
            insights.append("Excellent operational efficiency")
        elif operating_margin > 15:
            insights.append("Good operational efficiency")
        else:
            insights.append("Room for operational improvement")
        
        # ROE assessment
        if roe > 20:
            insights.append("Strong return on equity")
        elif roe > 10:
            insights.append("Decent return on equity")
        else:
            insights.append("Below average return on equity")
        
        # Stock performance
        if price_change_pct > 20:
            insights.append(f"Strong stock performance (+{price_change_pct:.1f}% past year)")
        elif price_change_pct > 0:
            insights.append(f"Positive stock performance (+{price_change_pct:.1f}% past year)")
        else:
            insights.append(f"Declining stock value ({price_change_pct:.1f}% past year)")
        
        # Dividend information
        dividend_yield = float(company_data['Forward Annual Dividend Yield'].strip('%'))
        if dividend_yield > 0:
            insights.append(f"Pays dividend with {dividend_yield:.2f}% yield")
        
        # Overall assessment
        overall_score = 0
        if profit_margin > 15: overall_score += 1
        if revenue_growth > 10: overall_score += 1
        if operating_margin > 20: overall_score += 1
        if roe > 15: overall_score += 1
        if price_change_pct > 10: overall_score += 1
        
        if overall_score >= 4:
            overall = "Strong performer with excellent fundamentals"
        elif overall_score >= 2:
            overall = "Solid company with good potential"
        else:
            overall = "Shows some challenges, careful analysis recommended"
        
        return {
            'insights': insights,
            'overall': overall,
            'metrics_summary': {
                'profit_margin': profit_margin,
                'revenue_growth': revenue_growth,
                'operating_margin': operating_margin,
                'roe': roe,
                'price_change_pct': price_change_pct,
                'dividend_yield': dividend_yield
            }
        }
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return {
            'insights': ["Insufficient data to generate complete analysis"],
            'overall': "Limited data available",
            'metrics_summary': {
                'profit_margin': 0,
                'revenue_growth': 0,
                'operating_margin': 0,
                'roe': 0,
                'price_change_pct': 0,
                'dividend_yield': 0
            }
        }

def translate_text(text, target_lang='ko'):
    """Translate text to target language."""
    if not text or not isinstance(text, str):
        return text
    try:
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def translate_company_data(data, target_lang):
    """Translate company data to target language."""
    if not data:
        return data
        
    translated_data = data.copy()
    
    # Translate text fields
    text_fields = ['name', 'Company Description', 'Sector', 'Industry']
    for field in text_fields:
        if field in translated_data:
            translated_data[field] = translate_text(translated_data[field], target_lang)
            
    return translated_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    results = search_companies(query)
    return jsonify(results)

@app.route('/api/analyze/<symbol>')
def analyze_company(symbol):
    try:
        # Get target language from query parameter, default to English
        target_lang = request.args.get('lang', 'en')
        
        # Validate symbol
        if not symbol or not isinstance(symbol, str):
            error_msg = 'Invalid symbol'
            if target_lang != 'en':
                error_msg = translate_text(error_msg, target_lang)
            return jsonify({'error': error_msg}), 400

        # Clean the symbol
        symbol = symbol.strip().upper()
        
        # Get company data first
        company_data = get_company_data(symbol)
        if not company_data:
            error_msg = f'Unable to fetch data for {symbol}. Please verify the company symbol.'
            if target_lang != 'en':
                error_msg = translate_text(error_msg, target_lang)
            return jsonify({'error': error_msg}), 404
        
        # Store company name for error messages
        company_name = company_data.get('name', symbol)
        
        # Get historical data with retry
        max_retries = 3
        hist = None
        
        for attempt in range(max_retries):
            hist = get_stock_data(symbol)
            if hist is not None:
                break
            print(f"Retry {attempt + 1} for historical data")
            time.sleep(2)  # Wait before retry
            
        if hist is None:
            error_msg = f'Unable to fetch historical data for {company_name}'
            if target_lang != 'en':
                error_msg = translate_text(error_msg, target_lang)
            return jsonify({'error': error_msg}), 404
            
        # Convert historical data to list of records
        hist_data = []
        try:
            for date, row in hist.iterrows():
                hist_data.append({
                    'Date': date,
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Volume': int(row['Volume'])
                })
        except Exception as e:
            print(f"Error converting historical data: {str(e)}")
            error_msg = f'Error processing historical data for {company_name}'
            if target_lang != 'en':
                error_msg = translate_text(error_msg, target_lang)
            return jsonify({'error': error_msg}), 500
        
        # Generate summary
        try:
            summary = generate_company_summary(company_data, hist)
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            error_msg = f'Error generating analysis for {company_name}'
            if target_lang != 'en':
                error_msg = translate_text(error_msg, target_lang)
            return jsonify({'error': error_msg}), 500
        
        # Translate data if needed
        if target_lang != 'en':
            try:
                company_data = translate_company_data(company_data, target_lang)
                summary = translate_text(summary, target_lang)
            except Exception as e:
                print(f"Translation error: {str(e)}")
                # Continue with untranslated data if translation fails
        
        analysis = {
            'company_data': company_data,
            'stock_history': hist_data,
            'key_metrics': {
                'profitability': float(company_data['Profit Margin'].strip('%')) if isinstance(company_data['Profit Margin'], str) else 0,
                'pe_ratio': float(company_data['Trailing P/E']) if company_data['Trailing P/E'] != 'N/A' else 0,
                'market_cap': company_data['Market Cap'],
                'revenue_growth': float(company_data['Quarterly Revenue Growth  (yoy)'].strip('%')) if isinstance(company_data['Quarterly Revenue Growth  (yoy)'], str) else 0
            },
            'summary': summary
        }
        
        return jsonify(analysis)
    except Exception as e:
        print(f"Error in analyze_company: {str(e)}")
        error_msg = f'An error occurred while analyzing {symbol}: {str(e)}'
        if target_lang != 'en':
            error_msg = translate_text(error_msg, target_lang)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)
