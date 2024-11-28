from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from googletrans import Translator
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
translator = Translator()

def translate_text(text, dest_lang='en'):
    if not text or dest_lang == 'en':
        return text
    try:
        return translator.translate(text, dest=dest_lang).text
    except:
        return text

@app.route('/api/search')
def search_company():
    query = request.args.get('query', '')
    lang = request.args.get('lang', 'en')
    
    if not query:
        return jsonify([])
    
    try:
        # Use yfinance to search for companies
        companies = yf.Tickers(query).tickers
        results = []
        
        for symbol, company in companies.items():
            info = company.info
            if info:
                name = info.get('longName', '') or info.get('shortName', '')
                if lang != 'en':
                    name = translate_text(name, lang)
                results.append({
                    'symbol': symbol,
                    'name': name
                })
        
        return jsonify(results[:5])  # Limit to top 5 results
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<symbol>')
def analyze_company(symbol):
    lang = request.args.get('lang', 'en')
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        history = ticker.history(start=start_date, end=end_date)
        
        # Process company data
        company_data = {
            'Company Description': translate_text(info.get('longBusinessSummary', ''), lang),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Profit Margin': f"{info.get('profitMargins', 0) * 100:.2f}%",
            'Revenue Growth': f"{info.get('revenueGrowth', 0) * 100:.2f}%",
            'Operating Margin': f"{info.get('operatingMargins', 0) * 100:.2f}%",
            'Trailing P/E': info.get('trailingPE', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A'
        }
        
        # Process historical data
        history_data = []
        for date, row in history.iterrows():
            history_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Close': row['Close']
            })
        
        # Generate analysis summary
        summary = generate_analysis_summary(info, history, lang)
        
        return jsonify({
            'company_data': company_data,
            'stock_history': history_data,
            'summary': summary
        })
    
    except Exception as e:
        error_message = str(e)
        if lang != 'en':
            error_message = translate_text(error_message, lang)
        return jsonify({'error': error_message}), 500

def generate_analysis_summary(info, history, lang):
    try:
        # Calculate basic metrics
        current_price = history['Close'][-1]
        price_change = ((current_price - history['Close'][0]) / history['Close'][0]) * 100
        
        summary = f"{'Company shows ' if lang == 'en' else ''}"
        
        # Analyze price trend
        if price_change > 0:
            trend = f"positive growth of {price_change:.1f}%" if lang == 'en' else f"{price_change:.1f}% 상승"
        else:
            trend = f"decline of {abs(price_change):.1f}%" if lang == 'en' else f"{abs(price_change):.1f}% 하락"
        
        summary += trend
        
        return translate_text(summary, lang)
    except:
        return translate_text("Unable to generate analysis summary", lang)

if __name__ == '__main__':
    app.run(debug=True)
