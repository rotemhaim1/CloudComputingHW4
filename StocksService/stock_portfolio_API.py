from stock_portfolio import *
from flask import Flask, jsonify, request, make_response
import json
import uuid
import numbers
import re
from flask_restful import Resource, Api, reqparse
import requests
import os
from datetime import datetime


class Stocks(Resource):


    def __init__(self, portfolio):
        self.portfolio = portfolio

    def post(self):
        """
        Handles the POST request to add a new stock to the portfolio.

        Returns:
            dict: A response containing the stock ID if created successfully.
            int: HTTP status code (201 for success, 400 for malformed data).
        """
        try:
            content_type = request.headers.get('Content-Type')
            if content_type != 'application/json':
                return {"error": "Expected application/json media type"}, 415
            
            raw_payload = request.get_json()
            unexpected_fields = [field for field in raw_payload.keys() if field not in self.portfolio.STOCKS_FIELDS]
            if unexpected_fields:
                return {"error": "Malformed data"}, 400
            
            expected_fields = [field for field in raw_payload.keys()]
            if not all(field in expected_fields for field in ["symbol", "shares", "purchase price"]):
                return {"error": "Malformed data"}, 400
            if ("purchase date" in raw_payload.keys()):
                if raw_payload["purchase date"] == "NA":
                    return {"error": "Malformed data"}, 400
                
            parser = reqparse.RequestParser()
            parser.add_argument('purchase price', type=str, required=True, location='json')
            parser.add_argument('symbol', type=str, required=True, location='json')
            parser.add_argument('shares', type=str, required=True, location='json')
            parser.add_argument('name', type=str, location='json', default = 'NA')
            parser.add_argument('purchase date', type=str, location='json', default = 'NA')
            args = parser.parse_args()

            name = args['name']
            symbol = args['symbol'].upper()
            purchase_price = args['purchase price']
            purchase_date = args['purchase date']
            shares = args['shares']
        except Exception as e:
            return {"server error": str(e)}, 500
        try:
            shares = int(shares)
            purchase_price = float(purchase_price)
        except ValueError:
            return {"error": "Malformed data"}, 400
        except TypeError:
            return {"error": "Malformed data"}, 400
        request_status, stock_id = self.portfolio.insert_stock(name, symbol, purchase_price, purchase_date, shares)
        if request_status == 201:
            return {'id': stock_id}, 201
        elif request_status == 400:
            return {"error": "Malformed data"}, 400
    
    def get(self):
        """
        Handles the GET request to retrieve all stocks or filter stocks based on query parameters.

        Returns:
            list: A list of stock dictionaries matching the query or all stocks.
            int: HTTP status code (200 for success).
        """
        try:
            request_status, stocks = self.portfolio.retrieve_stocks()
            query_params = dict(request.args)
            if not query_params:
                return stocks, 200
            filtered_stocks = [
            stock for stock in stocks
            if all(str(stock.get(field, "")).lower() == value.lower() for field, value in query_params.items())
        ]
        except Exception as e:
            return {"server error": str(e)}, 500

        return filtered_stocks, 200

class StocksID(Resource):
    
    def __init__(self, portfolio):
        self.portfolio = portfolio

    """
    Handles operations for specific stocks by ID at the '/stocks/<id>' endpoint.
    """
    def put(self, id):
        """
        Handles the PUT request to update a specific stock.

        Args:
            id (str): The stock ID.

        Returns:
            dict: Response containing the updated stock ID or error details.
            int: HTTP status code (200 for success, 400 for malformed data, 404 if not found).
        """
        try:
            content_type = request.headers.get('Content-Type')
            if content_type != 'application/json':
                return {"error": "Expected application/json media type"}, 415
            if not self.portfolio.stock_exists(id):
                return {"error": "Not found"}, 404

            raw_payload = request.get_json()
            unexpected_fields = [field for field in raw_payload.keys() if field not in self.portfolio.STOCKS_FIELDS]
            if unexpected_fields:
                return {"error": "Malformed data"}, 400
            
            expected_fields = [field for field in raw_payload.keys()]
            if not all(field in expected_fields for field in self.portfolio.STOCKS_FIELDS):
                return {"error": "Malformed data"}, 400
                    
            parser = reqparse.RequestParser()
            parser.add_argument('purchase price', type=str, required=True, location='json')
            parser.add_argument('symbol', type=str, required=True, location='json') #Check whether we should use the require = true
            parser.add_argument('shares', type=str, required=True, location='json')
            parser.add_argument('name', type=str, required=True, location='json')
            parser.add_argument('purchase date', type=str, required=True, location='json')
            parser.add_argument('id', type=str, required=True, location='json')
            args = parser.parse_args()
            if not (id == args['id']):
                return {"error": "Malformed data"}, 400
            name = args['name']
            symbol = args['symbol'].upper()
            purchase_price = args['purchase price']
            purchase_date = args['purchase date']
            shares = args['shares']
        except Exception as e:
            return {"server error": str(e)}, 500
        try:
            shares = int(shares)
            purchase_price = float(purchase_price)
        except ValueError:
            return {"error": "Malformed data"}, 400
        except TypeError:
            return {"error": "Malformed data"}, 400

        request_status, stock = self.portfolio.update_stock(id, name, symbol, purchase_price, purchase_date, shares)
        if request_status == 200:
            return {'id': id}, 200
        elif request_status == 400:
            return {"error": "Malformed data"}, request_status
        elif request_status == 404:
            return {"error": "Not found"}, 404
        
    def get(self, id):
        """
        Handles the GET request to retrieve a specific stock by ID.

        Args:
            id (str): The stock ID.

        Returns:
            dict: The stock data if found.
            int: HTTP status code (200 for success, 404 if not found).
        """
        try:
            request_status, stock = self.portfolio.get_stock(id)
            if request_status == 200:
                return stock, 200
            elif request_status == 404:
                return {"error": "Not found"}, 404
        except Exception as e:
            return {"server error": str(e)}, 500

    def delete(self, id):
        """
        Handles the DELETE request to remove a specific stock by ID.

        Args:
            id (str): The stock ID.

        Returns:
            int: HTTP status code (204 for success, 500 for server error).
        """
        try:
            request_status, stock = self.portfolio.delete_stock(id)
            if request_status == 204:
                return "", request_status
            elif request_status == 404:
                return {"error": "Not found"}, 404
        except Exception as e:
            return {"server error": str(e)}, 500

API_KEY = 'T6x6QsSBjaxT+BssCEg4VQ==wwU7bHC7P9hlXitc'
class stockValueID(Resource):

    def __init__(self, portfolio):
        self.portfolio = portfolio

    """
    Handles operations for retrieving the current value of a specific stock by ID at the '/stock-value/<id>' endpoint.
    """
    def get(self, id):
        """
        Handles the GET request to calculate the stock value using live data from an external API.

        Args:
            id (str): The stock ID.

        Returns:
            dict: The stock symbol, ticker, and calculated value if successful.
            int: HTTP status code (200 for success, 404 if not found, 500 for server error).
        """
        try:
            if not self.portfolio.stock_exists(id):  # CHANGED
                return {"error": "Not found"}, 404

            stock = self.portfolio.get_stock(id)[1]
            symbol = stock['symbol']
            url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
            response = requests.get(url, headers={'X-Api-Key': API_KEY})
            print(f"External API status: {response.status_code}")
            print(f"External API response: {response.text}")
            data = response.json()
            if not data:
                return {"error": "Not found"}, 404
            price_per_stock = data['price']
        except Exception as e:
            return {"server error": str(e)}, 500
        request_status, stock_symbol, ticker, value = self.portfolio.stock_value(id=id, ticker=price_per_stock)
        if request_status == 200:
            return {
                "symbol": stock_symbol,
                "ticker": ticker,
                "stock value": value
            }, 200
        if request_status == 404:
            return {"error": "Not found"}, 404
        

class portfolioValue(Resource):

    def __init__(self, portfolio):
        self.portfolio = portfolio

    """
    Handles operations for retrieving the total value of the portfolio at the '/portfolio-value' endpoint.
    """
    
    def get(self):
        """
        Handles the GET request to calculate the total value of the portfolio using live stock data.

        Returns:
            dict: The total portfolio value and the current date.
            int: HTTP status code (200 for success, 500 for server error).
        """
        portfolio_value = 0
        try:
            request_status, stocks = self.portfolio.retrieve_stocks()
            if request_status == 404 or not stocks:
                return {"error": "No stocks found"}, 404
            for stock in stocks:
                url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(stock['symbol'])
                response = requests.get(url, headers={'X-Api-Key': API_KEY})
                data = response.json()
                if not data:
                    return {"error": "Not found"}, 404
                price_per_stock = data['price']
                num_of_shares = stock['shares']
                portfolio_value += price_per_stock*num_of_shares
        except Exception as e:
            return {"server error": str(e)}, 500

        current_date = datetime.now()
        formatted_date = current_date.strftime("%d-%m-%Y")

        return {
            "date": formatted_date,
            "portfolio value": portfolio_value}, 200

