# import pytest
# import requests

# # Base URLs for your services.
# STOCKS_BASE_URL = "http://localhost:5001"  # Stocks service endpoint

# # Sample stock payloads
# stock1 = {
#     "name": "NVIDIA Corporation",
#     "symbol": "NVDA",
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock2 = {
#     "name": "Apple Inc.",
#     "symbol": "AAPL",
#     "purchase price": 183.63,
#     "purchase date": "22-02-2024",
#     "shares": 19
# }

# stock3 = {
#     "name": "Alphabet Inc.",
#     "symbol": "GOOG",
#     "purchase price": 140.12,
#     "purchase date": "24-10-2024",
#     "shares": 14
# }

# stock7 = {
#     "name": "Amazon.com, Inc.",
#     # Missing "symbol" field to trigger 400 error
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock8 = {
#     "name": "Amazon.com, Inc.",
#     "symbol": "AMZN",
#     "purchase price": 134.66,
#     # Incorrect date format to trigger 400 error
#     "purchase date": "Tuesday, June 18, 2024",
#     "shares": 7
# }


# @pytest.fixture(scope="module")
# def test_data():
#     """
#     Fixture to store shared data between tests.
#     """
#     return {}


# def test_post_stocks(test_data):
#     # POST stock1
#     response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock1)
#     assert response.status_code == 201, "POST stock1 did not return status 201"
#     stock1_id = response.json().get("id")
#     test_data['stock1_id'] = stock1_id

#     # POST stock2
#     response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock2)
#     assert response.status_code == 201, "POST stock2 did not return status 201"
#     stock2_id = response.json().get("id")
#     test_data['stock2_id'] = stock2_id

#     # POST stock3
#     response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock3)
#     assert response.status_code == 201, "POST stock3 did not return status 201"
#     stock3_id = response.json().get("id")
#     test_data['stock3_id'] = stock3_id

#     assert stock1_id != stock2_id != stock3_id, "Stock IDs are not unique"

# def test_get_stock1(test_data):
#     stock1_id = test_data.get('stock1_id')
#     response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock1_id}")
#     assert response.status_code == 200, "GET stock1 did not return status 200"
#     assert response.json().get("symbol") == "NVDA", "Stock1 symbol is not NVDA"


# def test_get_all_stocks(test_data):
#     response = requests.get(f"{STOCKS_BASE_URL}/stocks")
#     assert response.status_code == 200, "GET all stocks did not return status 200"
#     stocks = response.json()
#     assert isinstance(stocks, list) and len(
#         stocks) == 3, "Expected exactly 3 stocks"


# def test_get_stock_values(test_data):
#     stock1_id = test_data.get('stock1_id')
#     stock2_id = test_data.get('stock2_id')
#     stock3_id = test_data.get('stock3_id')

#     response1 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock1_id}")
#     assert response1.status_code == 200, "GET stock-value for stock1 did not return status 200"
#     assert response1.json().get("symbol") == "NVDA", "Stock1 value response symbol mismatch"

#     response2 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock2_id}")
#     assert response2.status_code == 200, "GET stock-value for stock2 did not return status 200"
#     assert response2.json().get("symbol") == "AAPL", "Stock2 value response symbol mismatch"

#     response3 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock3_id}")
#     assert response3.status_code == 200, "GET stock-value for stock3 did not return status 200"
#     assert response3.json().get("symbol") == "GOOG", "Stock3 value response symbol mismatch"


# def test_get_portfolio_value(test_data):
#     stock1_id = test_data.get('stock1_id')
#     stock2_id = test_data.get('stock2_id')
#     stock3_id = test_data.get('stock3_id')

#     sv1 = requests.get(
#         f"{STOCKS_BASE_URL}/stock-value/{stock1_id}").json().get("stock value")
#     sv2 = requests.get(
#         f"{STOCKS_BASE_URL}/stock-value/{stock2_id}").json().get("stock value")
#     sv3 = requests.get(
#         f"{STOCKS_BASE_URL}/stock-value/{stock3_id}").json().get("stock value")
#     total_value = sv1 + sv2 + sv3

#     response = requests.get(f"{STOCKS_BASE_URL}/portfolio-value")
#     assert response.status_code == 200, "GET portfolio-value did not return status 200"
#     portfolio_value = response.json().get("portfolio value")
#     lower_bound = total_value * 0.97
#     upper_bound = total_value * 1.03
#     assert lower_bound <= portfolio_value <= upper_bound, "Portfolio value not within expected range"


# def test_post_stock7_invalid(test_data):
#     # POST stock7 (missing 'symbol')
#     response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock7)
#     assert response.status_code == 400, "POST stock7 did not return status 400 as expected"


# def test_delete_stock2(test_data):
#     stock2_id = test_data.get('stock2_id')
#     response = requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock2_id}")
#     assert response.status_code == 204, "DELETE stock2 did not return status 204"


# def test_get_deleted_stock2(test_data):
#     stock2_id = test_data.get('stock2_id')
#     response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock2_id}")
#     assert response.status_code == 404, "GET deleted stock2 did not return status 404"


# def test_post_stock8_invalid(test_data):
#     # POST stock8 (incorrect date format)
#     response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock8)
#     assert response.status_code == 400, "POST stock8 did not return status 400 as expected"
import requests
import pytest

BASE_URL = "http://localhost:5001" 

# Stock data
stock1 = { "name": "NVIDIA Corporation", "symbol": "NVDA", "purchase price": 134.66, "purchase date": "18-06-2024", "shares": 7 }
stock2 = { "name": "Apple Inc.", "symbol": "AAPL", "purchase price": 183.63, "purchase date": "22-02-2024", "shares": 19 }
stock3 = { "name": "Alphabet Inc.", "symbol": "GOOG", "purchase price": 140.12, "purchase date": "24-10-2024", "shares": 14 }

def test_post_stocks():
    response1 = requests.post(f"{BASE_URL}/stocks", json=stock1)
    response2 = requests.post(f"{BASE_URL}/stocks", json=stock2)
    response3 = requests.post(f"{BASE_URL}/stocks", json=stock3)
    
    assert response1.status_code == 207
    assert response2.status_code == 201
    assert response3.status_code == 201

    # Ensure unique IDs
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert data1['id'] != data2['id']
    assert data1['id'] != data3['id']
    assert data2['id'] != data3['id']

def test_get_stocks():
    response = requests.get(f"{BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) == 3 
    
def test_get_portfolio_value():
    response = requests.get(f"{BASE_URL}/portfolio-value")
    assert response.status_code == 200
    portfolio_value = response.json()
    assert portfolio_value['portfolio value'] > 0  # Portfolio value should be greater than 0

def test_post_stocks_invalid_data():
    stock_invalid = { "name": "Amazon", "purchase price": 100.50, "purchase date": "15-03-2025", "shares": 50 }
    response = requests.post(f"{BASE_URL}/stocks", json=stock_invalid)
    assert response.status_code == 400


