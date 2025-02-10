from flask import Flask, request, jsonify
from flask_restful import Resource
import requests
import os

STOCKS1_URL = "http://stocks-1a:8000"
API_KEY = os.getenv("NINJA_API_KEY")

class CapitalGains(Resource):
    def get(self):
        """
        GET /capital-gains
        Calculates capital gains for all stocks or based on query filters.
        """
        try:
            # Get query parameters
            query_params = request.args
            portfolio = query_params.get("portfolio", None)
            numsharesgt = query_params.get("numsharesgt", None)
            numshareslt = query_params.get("numshareslt", None)

            # Determine which stock service to query
            stocks_url = f"{STOCKS1_URL}/stocks"
            stocks1_response = requests.get(f"{STOCKS1_URL}/stocks")
            stocks = stocks1_response.json()

            # If filtering by portfolio
            if portfolio:
                response = requests.get(stocks_url)
                stocks = response.json()

            # Apply additional filters for shares
            if numsharesgt:
                stocks = [stock for stock in stocks if stock['shares'] > int(numsharesgt)]
            if numshareslt:
                stocks = [stock for stock in stocks if stock['shares'] < int(numshareslt)]

            # Calculate capital gains
            total_capital_gain = 0
            for stock in stocks:
                symbol = stock['symbol']
                shares = stock['shares']
                purchase_price = stock['purchase price']

                # Fetch live price from external API
                price_url = f'https://api.api-ninjas.com/v1/stockprice?ticker={symbol}'
                response = requests.get(price_url, headers={'X-Api-Key': API_KEY})
                json_price = response.json()
                current_price = json_price['price']

                if current_price is not None:
                    stock_value = shares * current_price
                    gain = stock_value - (shares * purchase_price)
                    total_capital_gain += gain

            return round(total_capital_gain, 2)

        except Exception as e:
            return {"error": str(e)}, 500
