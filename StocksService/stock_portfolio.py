from flask import Flask, jsonify, request, make_response
import json
import uuid
import numbers
import re
from flask_restful import Resource, Api, reqparse
import requests
import os
from datetime import datetime
from flask_pymongo import PyMongo


API_KEY = os.getenv("NINJA_API_KEY")

class StockPortfolio:
    """
    Represents a stock portfolio that allows operations on stocks.
    Includes validation methods for stock attributes.
    """
    STOCKS_FIELDS = ["id", "name", "symbol", "purchase price", "purchase date", "shares"]
    def __init__(self, stocks_collection):
        self.stocks = stocks_collection

    def purchase_price_validation(self, purchase_price):
        """
        Validates if the purchase price is a valid number.

        Args:
            purchase_price (float): The purchase price of the stock.

        Returns:
            bool: True if valid, False otherwise.
        """
        if isinstance(purchase_price, numbers.Number):
            return True
        else:
            return False
        
    def purchase_date_validation(self, purchase_date):
        """
        Validates if the purchase date follows the format DD-MM-YYYY or is 'NA'.

        Args:
            purchase_date (str): The purchase date of the stock.

        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r'^\d{2}-\d{2}-\d{4}$'
        if not (re.match(pattern, purchase_date) or purchase_date == "NA"):
            return False
        return True
    
    def shares_validation(self, shares):
        """
        Validates if the shares are non-negative.

        Args:
            shares (int): The number of shares.

        Returns:
            bool: True if shares are >= 0, False otherwise.
        """
        return shares >= 0 
    
    def fields_validation(self, purchase_price, purchase_date, shares):
        """
        Validates all fields for a stock.

        Args:
            purchase_price (float): The purchase price.
            purchase_date (str): The purchase date.
            shares (int): The number of shares.

        Returns:
            bool: True if all fields are valid, False otherwise.
        """
        return self.purchase_price_validation(purchase_price = purchase_price) and self.purchase_date_validation(purchase_date = purchase_date) and self.shares_validation(shares = shares)

    def insert_stock(self, name: str, symbol: str, purchase_price: float, purchase_date: str, shares: int):
        """
        Inserts a new stock into the portfolio.

        Args:
            name (str): The name of the stock.
            symbol (str): The stock symbol.
            purchase_price (float): The purchase price.
            purchase_date (str): The purchase date.
            shares (int): The number of shares.

        Returns:
            tuple: (status code, stock ID or -1 if insertion failed).
        """
        # Check if symbol already exists as a key
        if self.stocks.find_one({"symbol": symbol}):  # CHANGED
            return 400, -1
        # The symbol already exists
        # Validate the fields
        if not self.fields_validation(purchase_price, purchase_date, shares):
            return 400, -1  # Validation failed, unprocessable entity

        # Generate a unique ID
        stock_id = str(uuid.uuid4())

        # Add the stock to the portfolio
        stock_data = {
            '_id': stock_id,
            'id': stock_id,
            'name': name,
            'symbol': symbol,
            'purchase price': purchase_price,
            'purchase date': purchase_date,
            'shares': shares,
        }
        self.stocks.insert_one(stock_data)
        return 201, stock_id
    
    def retrieve_stocks(self):
        """
        Retrieves all stocks in the portfolio.

        Returns:
            tuple: (status code, dictionary of all stocks).
        """
        stocks = list(self.stocks.find({}, {'_id': 0}))
        return 200, stocks

    def get_stock(self, id):
        """
        Retrieves a stock by ID.

        Args:
            id (str): The stock ID.

        Returns:
            tuple: (status code, stock data or None if not found).
        """
        stock = self.stocks.find_one({"_id": id}, {'_id': 0})
        if stock:
            return 200, stock
        return 404, None

    def delete_stock(self, id):
        """
        Deletes a stock by ID.

        Args:
            id (str): The stock ID.

        Returns:
            tuple: (status code, deleted stock data or None if not found).
        """
        result = self.stocks.delete_one({"_id": id})  # CHANGED
        if result.deleted_count == 1:
            return 204, None
        return 404, None

    def update_stock(self, id, name, symbol, purchase_price, purchase_date, shares):
        """
        Updates a stock by ID.

        Args:
            id (str): The stock ID.
            name (str): The updated stock name.
            symbol (str): The updated stock symbol.
            purchase_price (float): The updated purchase price.
            purchase_date (str): The updated purchase date.
            shares (int): The updated number of shares.

        Returns:
            tuple: (status code, stock ID or -1 if update failed).
        """
        if not self.stock_exists(id):
            return 404, -1
        symbol_conflict = self.stocks.find_one({"symbol": symbol, "_id": {"$ne": id}})
        if symbol_conflict:
            return 400, -1
        if not self.fields_validation(purchase_price = purchase_price, purchase_date = purchase_date, shares = shares):
            return 400, -1
        update_result = self.stocks.update_one(
            {"_id": id},
            {
                "$set": {
                    "name": name,
                    "symbol": symbol,
                    "purchase price": round(float(purchase_price), 2),
                    "purchase date": purchase_date,
                    "shares": shares,
                }
            }
        )
        return 200, id # Success - status code is 200

    def stock_exists(self, id):
        """
        Checks if a stock exists by ID.

        Args:
            id (str): The stock ID.

        Returns:
            bool: True if the stock exists, False otherwise.
        """
        return self.stocks.find_one({"_id": id}) is not None

    def stock_value(self, id, ticker):
        """
        Calculates the value of a stock.

        Args:
            id (str): The stock ID.
            ticker (float): The current price per share.

        Returns:
            tuple: (status code, stock symbol, ticker, calculated value).
        """
        stock = self.stocks.find_one({"_id": id})
        if not stock:
            return 404, None, None, None
        stock_symbol = stock['symbol']
        stock_shares = stock['shares']
        value = stock_shares * ticker
        return 200 ,stock_symbol, ticker, value
        
    def search_by_field(self, field: str, value: str):
        """
        Searches stocks by a specific field and value.

        Args:
            field (str): The field name to search.
            value (str): The value to match.

        Returns:
            list or int: A list of matching stocks, or -1 if none are found.
        """
        query = {field: value}
        stocks = list(self.stocks.find(query, {'_id': 0}))
        if not stocks:
            return False
        if len(stocks) == 1:
            return stocks[0]
        return stocks
    


