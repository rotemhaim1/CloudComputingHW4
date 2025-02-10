"""
assn4_tests.py

This file contains the pytest tests for the CI/CD pipeline assignment.
It verifies that the stocks service is functioning correctly by performing:
1. POST requests to add stocks (stock1, stock2, stock3) and checking for unique IDs.
2. GET requests to retrieve individual stocks and a list of all stocks.
3. GET requests to obtain stock values and the overall portfolio value.
4. Negative tests including:
   - POSTing a stock (stock7) missing the required "symbol" field.
   - DELETEing a stock (stock2) and then confirming it’s gone.
   - POSTing a stock (stock8) with an improperly formatted purchase date.
   
Assumptions:
- The stocks service is accessible at http://localhost:5001.
- Endpoints used:
    * POST   /stocks           to create a new stock.
    * GET    /stocks/{id}      to get a stock by its ID.
    * GET    /stocks           to list all stocks.
    * GET    /stock-value/{id} to get the value of a stock (returns JSON with a "symbol" and "stock_value" field).
    * GET    /portfolio-value  to get the overall portfolio value (returns JSON with a "portfolio value" or "portfolio_value" field).
    * DELETE /stocks/{id}      to delete a stock.
- The responses return JSON data. Adjust JSON key names if your implementation differs.
"""

import requests
import pytest

# Base URL for the stocks service (adjust if needed)
BASE_URL = "http://localhost:5001"

# Global dictionaries to hold created stock IDs and computed stock values
stock_ids = {}
stock_values = {}

# ----- Test Data -----

# Valid stocks data for tests 1-5.
stock1 = {
    "name": "NVIDIA Corporation",
    "symbol": "NVDA",
    "purchase price": 134.66,
    "purchase date": "18-06-2024",
    "shares": 7
}

stock2 = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "purchase price": 183.63,
    "purchase date": "22-02-2024",
    "shares": 19
}

stock3 = {
    "name": "Alphabet Inc.",
    "symbol": "GOOG",
    "purchase price": 140.12,
    "purchase date": "24-10-2024",
    "shares": 14
}

# Invalid stock (missing the required "symbol" field)
stock7 = {
    "name": "Amazon.com, Inc.",
    # "symbol" is intentionally missing
    "purchase price": 134.66,
    "purchase date": "18-06-2024",
    "shares": 7
}

# Invalid stock (incorrect purchase date format)
stock8 = {
    "name": "Amazon.com, Inc.",
    "symbol": "AMZN",
    "purchase price": 134.66,
    "purchase date": "Tuesday, June 18, 2024",  # Incorrect format
    "shares": 7
}


# ----- Test Functions -----

def test_1_create_stocks():
    """
    Test 1:
    Execute three POST /stocks requests to add stock1, stock2, and stock3.
    Verify that each returns status code 201 and a unique ID.
    """
    global stock_ids

    # POST stock1
    response1 = requests.post(f"{BASE_URL}/stocks", json=stock1)
    assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
    data1 = response1.json()
    assert "id" in data1, "Response for stock1 does not include 'id'"
    stock_ids["stock1"] = data1["id"]

    # POST stock2
    response2 = requests.post(f"{BASE_URL}/stocks", json=stock2)
    assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
    data2 = response2.json()
    assert "id" in data2, "Response for stock2 does not include 'id'"
    stock_ids["stock2"] = data2["id"]

    # POST stock3
    response3 = requests.post(f"{BASE_URL}/stocks", json=stock3)
    assert response3.status_code == 201, f"Expected 201, got {response3.status_code}"
    data3 = response3.json()
    assert "id" in data3, "Response for stock3 does not include 'id'"
    stock_ids["stock3"] = data3["id"]

    # Verify that all three IDs are unique
    unique_ids = {stock_ids["stock1"], stock_ids["stock2"], stock_ids["stock3"]}
    assert len(unique_ids) == 3, "The returned IDs are not unique"


def test_2_get_stock1():
    """
    Test 2:
    Execute a GET /stocks/{ID} request for stock1.
    Verify that the returned JSON has a "symbol" field equal to "NVDA" and status code 200.
    """
    id1 = stock_ids.get("stock1")
    assert id1 is not None, "Stock1 ID not found from previous test"
    response = requests.get(f"{BASE_URL}/stocks/{id1}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("symbol") == "NVDA", f"Expected symbol 'NVDA', got {data.get('symbol')}"


def test_3_get_all_stocks():
    """
    Test 3:
    Execute a GET /stocks request and verify that exactly 3 stocks are returned,
    along with a status code of 200.
    """
    response = requests.get(f"{BASE_URL}/stocks")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # Assuming the response is a list of stocks
    assert isinstance(data, list), "Expected the response to be a list of stocks"
    assert len(data) == 3, f"Expected 3 stocks, got {len(data)}"


def test_4_get_stock_values():
    """
    Test 4:
    Execute three GET /stock-value/{ID} requests for stock1, stock2, and stock3.
    Verify that:
      - Each response returns status code 200.
      - The "symbol" field in each response equals "NVDA", "AAPL", and "GOOG" respectively.
    Also, store the "stock_value" from each response for use in Test 5.
    """
    global stock_ids, stock_values

    stock_tests = [
        ("stock1", "NVDA"),
        ("stock2", "AAPL"),
        ("stock3", "GOOG")
    ]

    for key, expected_symbol in stock_tests:
        sid = stock_ids.get(key)
        assert sid is not None, f"{key} ID not found"
        response = requests.get(f"{BASE_URL}/stock-value/{sid}")
        assert response.status_code == 200, f"Expected 200 for {key}, got {response.status_code}"
        data = response.json()
        assert data.get("symbol") == expected_symbol, f"Expected symbol '{expected_symbol}' for {key}, got {data.get('symbol')}"
        # Assume the field name is "stock_value" in the response JSON.
        assert "stock_value" in data, f"'stock_value' field missing in response for {key}"
        stock_values[key] = data["stock_value"]


def test_5_get_portfolio_value():
    """
    Test 5:
    Execute a GET /portfolio-value request.
    Verify that:
      - The response returns a status code of 200.
      - The sum of the stock values from Test 4 is within ±3% of the portfolio value.
    """
    total_stock_value = sum(stock_values.get(key, 0) for key in ["stock1", "stock2", "stock3"])
    response = requests.get(f"{BASE_URL}/portfolio-value")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # The portfolio value might be returned under "portfolio value" or "portfolio_value"
    pv = data.get("portfolio value") or data.get("portfolio_value")
    assert pv is not None, "Portfolio value field missing in response"

    lower_bound = pv * 0.97
    upper_bound = pv * 1.03
    assert lower_bound <= total_stock_value <= upper_bound, (
        f"Sum of stock values ({total_stock_value}) not within 3% of portfolio value ({pv})"
    )


def test_6_invalid_stock_missing_symbol():
    """
    Test 6:
    Execute a POST /stocks request supplying stock7 (which is missing the required "symbol" field).
    Verify that the response status code is 400.
    """
    response = requests.post(f"{BASE_URL}/stocks", json=stock7)
    assert response.status_code == 400, f"Expected 400 for missing symbol, got {response.status_code}"


def test_7_delete_stock2():
    """
    Test 7:
    Execute a DELETE /stocks/{ID} request for stock2.
    Verify that the response status code is 204.
    """
    stock2_id = stock_ids.get("stock2")
    assert stock2_id is not None, "Stock2 ID not found"
    response = requests.delete(f"{BASE_URL}/stocks/{stock2_id}")
    assert response.status_code == 204, f"Expected 204 on deletion, got {response.status_code}"


def test_8_get_deleted_stock2():
    """
    Test 8:
    Execute a GET /stocks/{ID} request for stock2 (which was deleted in Test 7).
    Verify that the response status code is 404.
    """
    stock2_id = stock_ids.get("stock2")
    assert stock2_id is not None, "Stock2 ID not found"
    response = requests.get(f"{BASE_URL}/stocks/{stock2_id}")
    assert response.status_code == 404, f"Expected 404 for a deleted stock, got {response.status_code}"


def test_9_invalid_stock_bad_date():
    """
    Test 9:
    Execute a POST /stocks request supplying stock8 (with an incorrectly formatted purchase date).
    Verify that the response status code is 400.
    """
    response = requests.post(f"{BASE_URL}/stocks", json=stock8)
    assert response.status_code == 400, f"Expected 400 for invalid purchase date, got {response.status_code}"
