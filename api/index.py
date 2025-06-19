"""
회사 정보 조회 API
"""

import logging
import os

from flasgger import Swagger
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from .services.company_service import CompanyService, CompanyServiceError
from .services.translation_service import TranslationService, TranslationServiceError


def create_app():
    app = Flask(__name__)
    CORS(app)
    Swagger(app)

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # 서비스 인스턴스 생성
    company_service = CompanyService()
    translation_service = TranslationService()

    with app.app_context():

        @app.route("/api/search")
        def search_company():
            """
            회사 검색 API
            ---
            parameters:
              - name: query
                in: query
                type: string
                required: true
                description: 검색할 회사명 또는 심볼
              - name: lang
                in: query
                type: string
                required: false
                default: en
                description: 결과 언어 코드
            responses:
              200:
                description: 검색 결과 리스트
                schema:
                  type: object
                  properties:
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          symbol:
                            type: string
                          name:
                            type: string
                          marketCap:
                            type: integer
                          profitMargins:
                            type: number
                          revenueGrowth:
                            type: number
                          operatingMargins:
                            type: number
                          trailingPE:
                            type: number
                          forwardPE:
                            type: number
                          dividendYield:
                            type: number
              400:
                description: 잘못된 요청
                schema:
                  type: object
                  properties:
                    error:
                      type: string
              500:
                description: 서버 오류
                schema:
                  type: object
                  properties:
                    error:
                      type: string
            """
            query = request.args.get("query", "")
            lang = request.args.get("lang", "en")

            logger.info(f"Search request received: query={query}, lang={lang}")

            if not query:
                logger.warning("Empty query received")
                return jsonify({"data": []}), 200

            try:
                results = company_service.search_companies(query)
                if lang != "en" and results:
                    results = [
                        translation_service.translate_dict(item, lang)
                        for item in results
                    ]
                logger.info(f"Search successful: {len(results)} results found")
                return jsonify({"data": results}), 200
            except CompanyServiceError as e:
                logger.error(f"Company service error: {str(e)}")
                return jsonify({"error": str(e)}), 500
            except TranslationServiceError as e:
                logger.error(f"Translation service error: {str(e)}")
                return jsonify({"error": str(e)}), 500
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Unexpected error: {error_msg}")
                if "resource_exhausted" in error_msg.lower():
                    return (
                        jsonify(
                            {
                                "error": "Service is temporarily unavailable due to high"
                                " demand. Please try again in a few minutes."
                            }
                        ),
                        429,
                    )
                return jsonify({"error": error_msg}), 500

        @app.route("/api/analyze/<symbol>")
        def analyze_company(symbol):
            """
            회사 분석 API
            ---
            parameters:
              - name: symbol
                in: path
                type: string
                required: true
                description: 분석할 회사 심볼
              - name: lang
                in: query
                type: string
                required: false
                default: en
                description: 결과 언어 코드
              - name: period
                in: query
                type: string
                required: false
                default: 1y
                description: 주가 히스토리 기간(예: 1mo, 3mo, 6mo, 1y, 3y)
            responses:
              200:
                description: 분석 결과
                schema:
                  type: object
                  properties:
                    data:
                      type: object
                      properties:
                        Company Description:
                          type: string
                        Market Cap:
                          type: integer
                        Profit Margin:
                          type: number
                        Revenue Growth:
                          type: number
                        Operating Margin:
                          type: number
                        Trailing P/E:
                          type: number
                        Forward P/E:
                          type: number
                        Dividend Yield:
                          type: number
                        Price Change:
                          type: number
                        Stock History:
                          type: array
                          items:
                            type: object
                            properties:
                              date:
                                type: string
                              close:
                                type: number
              400:
                description: 잘못된 요청
                schema:
                  type: object
                  properties:
                    error:
                      type: string
              500:
                description: 서버 오류
                schema:
                  type: object
                  properties:
                    error:
                      type: string
            """
            lang = request.args.get("lang", "en")
            period = request.args.get("period", "1y")

            logger.info(
                f"Analysis request received: symbol={symbol}, lang={lang}, period={period}"
            )

            try:
                analysis = company_service.analyze_company(symbol, period=period)
                if lang != "en":
                    analysis = translation_service.translate_dict(analysis, lang)
                logger.info(f"Analysis successful for symbol: {symbol}")
                return jsonify({"data": analysis}), 200
            except CompanyServiceError as e:
                logger.error(f"Company service error: {str(e)}")
                return jsonify({"error": str(e)}), 500
            except TranslationServiceError as e:
                logger.error(f"Translation service error: {str(e)}")
                return jsonify({"error": str(e)}), 500
            except Exception as e:
                error_message = str(e)
                logger.error(f"Unexpected error: {error_message}")
                if lang != "en":
                    error_message = translation_service.translate(error_message, lang)
                if "resource_exhausted" in error_message.lower():
                    return (
                        jsonify(
                            {
                                "error": "Service is temporarily unavailable due to high"
                                " demand. Please try again in a few minutes."
                            }
                        ),
                        429,
                    )
                return jsonify({"error": error_message}), 500

        @app.route("/api/analyze-multi", methods=["POST"])
        def analyze_multi():
            """
            여러 기업 주요 지표 비교 API
            ---
            parameters:
              - name: symbols
                in: body
                type: array
                required: true
                description: 분석할 회사 심볼 리스트
              - name: period
                in: body
                type: string
                required: false
                default: 1y
                description: 주가 히스토리 기간(예: 1mo, 3mo, 6mo, 1y, 3y)
            responses:
              200:
                description: 분석 결과 리스트
                schema:
                  type: object
                  properties:
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          symbol:
                            type: string
                          name:
                            type: string
                          Market Cap:
                            type: integer
                          Trailing P/E:
                            type: number
                          Forward P/E:
                            type: number
                          Profit Margin:
                            type: number
                          Operating Margin:
                            type: number
                          Revenue Growth:
                            type: number
                          Dividend Yield:
                            type: number
              400:
                description: 잘못된 요청
                schema:
                  type: object
                  properties:
                    error:
                      type: string
              500:
                description: 서버 오류
                schema:
                  type: object
                  properties:
                    error:
                      type: string
            """
            try:
                req = request.get_json()
                symbols = req.get("symbols", [])
                period = req.get("period", "1y")
                if not symbols or not isinstance(symbols, list):
                    return jsonify({"error": "symbols 파라미터가 필요합니다."}), 400
                results = []
                for symbol in symbols:
                    try:
                        analysis = company_service.analyze_company(
                            symbol, period=period
                        )
                        results.append(
                            {
                                "symbol": symbol,
                                "name": analysis.get("Company Description", "")[:40],
                                "Market Cap": analysis.get("Market Cap", "N/A"),
                                "Trailing P/E": analysis.get("Trailing P/E", "N/A"),
                                "Forward P/E": analysis.get("Forward P/E", "N/A"),
                                "Profit Margin": analysis.get("Profit Margin", "N/A"),
                                "Operating Margin": analysis.get(
                                    "Operating Margin", "N/A"
                                ),
                                "Revenue Growth": analysis.get("Revenue Growth", "N/A"),
                                "Dividend Yield": analysis.get("Dividend Yield", "N/A"),
                            }
                        )
                    except Exception as e:
                        results.append({"symbol": symbol, "error": str(e)})
                return jsonify({"data": results}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route("/")
        def home():
            """홈페이지 리다이렉트"""
            return send_from_directory("../docs", "index.html")

        @app.route("/docs/<path:path>")
        def serve_docs(path):
            """정적 파일 제공"""
            docs_path = os.path.join(os.path.dirname(__file__), "..", "docs")
            return send_from_directory(docs_path, path)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
