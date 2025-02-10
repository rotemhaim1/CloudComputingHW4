from flask_pymongo import PyMongo
from flask import Flask, jsonify, request, make_response
import json
import uuid
import numbers
import re
from flask_restful import Resource, Api, reqparse
import requests
import os
from pymongo import MongoClient
from datetime import datetime
from stock_portfolio import *
from stock_portfolio_API import *

app = Flask(__name__)
api = Api(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/stocks_db'
client = MongoClient("mongodb://mongodb:27017/")  # Connect to MongoDB Docker container
db = client['stocks_db']  # Use 'stocks_db' database
portfolio_name = os.getenv('PORTFOLIO', 'stocks1a')
collection = db[portfolio_name]
portfolio = StockPortfolio(collection)

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)

if __name__ == "__main__":
    api.add_resource(Stocks, '/stocks', resource_class_args = [portfolio])
    api.add_resource(StocksID, '/stocks/<string:id>', resource_class_args = [portfolio])
    api.add_resource(stockValueID, '/stock-value/<string:id>', resource_class_args = [portfolio])
    api.add_resource(portfolioValue, '/portfolio-value', resource_class_args = [portfolio])
    # run Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)