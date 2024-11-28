from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from googletrans import Translator
import numpy as np
from datetime import datetime, timedelta
from functools import lru_cache
import time

app = Flask(__name__)
CORS(app)
translator = Translator()

# Add caching to reduce API calls
@lru_cache(maxsize=100)
def translate_text(text, dest_lang='en'):
    if not text or dest_lang == 'en':
        return text
    try:
        time.sleep(0.5)
        return translator.translate(text, dest=dest_lang).text
    except:
        return text

@app.route('/api/search', methods=['GET'])
def search_company():
    query = request.args.get('query', '')
    lang = request.args.get('lang', 'en')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        ticker = yf.Ticker(query)
        info = ticker.info
        
        if not info:
            return jsonify({'error': 'Company not found'}), 404
            
        history = ticker.history(period='1y')
        if not history.empty:
            prices = history['Close'].tolist()
            dates = history.index.strftime('%Y-%m-%d').tolist()
        else:
            prices = []
            dates = []
            
        analysis = generate_analysis_summary(info, history, lang)
        
        return jsonify({
            'symbol': query.upper(),
            'name': info.get('longName', ''),
            'description': translate_text(info.get('longBusinessSummary', ''), lang),
            'prices': prices,
            'dates': dates,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['GET'])
def analyze_company():
    symbol = request.args.get('symbol', '')
    lang = request.args.get('lang', 'en')
    
    if not symbol:
        return jsonify({'error': 'No symbol provided'}), 400
        
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            return jsonify({'error': 'Company not found'}), 404
            
        history = ticker.history(period='1y')
        analysis = generate_analysis_summary(info, history, lang)
        
        return jsonify({
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_analysis_summary(info, history, lang='en'):
    if history.empty:
        return translate_text("Insufficient data for analysis", lang)
        
    current_price = history['Close'][-1]
    year_high = np.max(history['High'])
    year_low = np.min(history['Low'])
    
    pe_ratio = info.get('forwardPE', 0)
    profit_margins = info.get('profitMargins', 0)
    
    analysis = []
    
    if pe_ratio > 0:
        if pe_ratio < 15:
            analysis.append("The stock appears to be potentially undervalued based on its P/E ratio.")
        elif pe_ratio > 30:
            analysis.append("The stock appears to be potentially overvalued based on its P/E ratio.")
            
    if profit_margins:
        if profit_margins > 0.2:
            analysis.append("The company shows strong profit margins above 20%.")
        elif profit_margins < 0:
            analysis.append("The company is currently operating at a loss.")
            
    price_range = f"The stock has traded between ${year_low:.2f} and ${year_high:.2f} over the past year."
    analysis.append(price_range)
    
    summary = " ".join(analysis)
    return translate_text(summary, lang)

if __name__ == '__main__':
    app.run(debug=True)
