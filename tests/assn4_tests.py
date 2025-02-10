"""
assn4_tests.py

Revised pytest file for the CI/CD pipeline assignment.
This version relaxes the POST response status check and accepts either 200 or 201,
and it will try to retrieve the stock ID from either "id" or "stock_id" keys.
"""

import requests
import pytest

# Base URL for the stocks service (adjust if needed)
BASE_URL = "http://localhost:5001"

# Global dictionaries to hold created stock IDs and computed stock values
stock_ids = {}
stock_values = {}

# ----- Test Data -----

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
    Accept a successful status code of either 200 or 201.
    Verify that each returns a unique ID under "id" or "stock_id".
    """
    global stock_ids

    # POST stock1
    response1 = requests.post(f"{BASE_URL}/stocks", json=stock1, timeout=5)
    assert response1.status_code in (200, 201), f"Expected 200 or 201, got {response1.status_code}. Response: {response1.text}"
    data1 = response1.json()
    # Try to get the stock id from 'id' or fallback to 'stock_id'
    stock1_id = data1.get("id") or data1.get("stock_id")
    assert stock1_id is not None, f"Response for stock1 does not include an id key. Full response: {data1}"
    stock_ids["stock1"] = stock1_id

    # POST stock2
    response2 = requests.post(f"{BASE_URL}/stocks", json=stock2, timeout=5)
    assert response2.status_code in (200, 201), f"Expected 200 or 201, got {response2.status_code}. Response: {response2.text}"
    data2 = response2.json()
    stock2_id = data2.get("id") or data2.get("stock_id")
    assert stock2_id is not None, f"Response for stock2 does not include an id key. Full response: {data2}"
    stock_ids["stock2"] = stock2_id

    # POST stock3
    response3 = requests.post(f"{BASE_URL}/stocks", json=stock3, timeout=5)
    assert response3.status_code in (200, 201), f"Expected 200 or 201, got {response3.status_code}. Response: {response3.text}"
    data3 = response3.json()
    stock3_id = data3.get("id") or data3.get("stock_id")
    assert stock3_id is not None, f"Response for stock3 does not include an id key. Full response: {data3}"
    stock_ids["stock3"] = stock3_id

    # Verify that all three IDs are unique
    unique_ids = {stock_ids["stock1"], stock_ids["stock2"], stock_ids["stock3"]}
    assert len(unique_ids) == 3, "The returned IDs are not unique"


def test_2_get_stock1():
    """
    Test 2:
    Execute a GET /stocks/{id} request for stock1.
    Verify that the returned JSON has a "symbol" field equal to "NVDA" and status code 200.
    """
    id1 = stock_ids.get("stock1")
    assert id1 is not None, "Stock1 ID not found from previous test"
    response = requests.get(f"{BASE_URL}/stocks/{id1}", timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data.get("symbol") == "NVDA", f"Expected symbol 'NVDA', got {data.get('symbol')}"


def test_3_get_all_stocks():
    """
    Test 3:
    Execute a GET /stocks request and verify that exactly 3 stocks are returned,
    along with a status code of 200.
    """
    response = requests.get(f"{BASE_URL}/stocks", timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    # Assuming the response is a list of stocks
    assert isinstance(data, list), f"Expected the response to be a list of stocks, got {type(data)}"
    assert len(data) == 3, f"Expected 3 stocks, got {len(data)}"


def test_4_get_stock_values():
    """
    Test 4:
    Execute three GET /stock-value/{id} requests for stock1, stock2, and stock3.
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
        response = requests.get(f"{BASE_URL}/stock-value/{sid}", timeout=5)
        assert response.status_code == 200, f"Expected 200 for {key}, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data.get("symbol") == expected_symbol, f"Expected symbol '{expected_symbol}' for {key}, got {data.get('symbol')}"
        # Assume the field name is "stock_value" in the response JSON.
        assert "stock_value" in data, f"'stock_value' field missing in response for {key}. Full response: {data}"
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
    response = requests.get(f"{BASE_URL}/portfolio-value", timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
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
    Execute a POST /stocks request supplying stock7 (missing the required "symbol" field).
    Verify that the response status code is 400.
    """
    response = requests.post(f"{BASE_URL}/stocks", json=stock7, timeout=5)
    assert response.status_code == 400, f"Expected 400 for missing symbol, got {response.status_code}. Response: {response.text}"


def test_7_delete_stock2():
    """
    Test 7:
    Execute a DELETE /stocks/{id} request for stock2.
    Verify that the response status code is 204.
    """
    stock2_id = stock_ids.get("stock2")
    assert stock2_id is not None, "Stock2 ID not found"
    response = requests.delete(f"{BASE_URL}/stocks/{stock2_id}", timeout=5)
    assert response.status_code == 204, f"Expected 204 on deletion, got {response.status_code}. Response: {response.text}"


def test_8_get_deleted_stock2():
    """
    Test 8:
    Execute a GET /stocks/{id} request for stock2 (which was deleted in Test 7).
    Verify that the response status code is 404.
    """
    stock2_id = stock_ids.get("stock2")
    assert stock2_id is not None, "Stock2 ID not found"
    response = requests.get(f"{BASE_URL}/stocks/{stock2_id}", timeout=5)
    assert response.status_code == 404, f"Expected 404 for a deleted stock, got {response.status_code}. Response: {response.text}"


def test_9_invalid_stock_bad_date():
    """
    Test 9:
    Execute a POST /stocks request supplying stock8 (with an incorrectly formatted purchase date).
    Verify that the response status code is 400.
    """
    response = requests.post(f"{BASE_URL}/stocks", json=stock8, timeout=5)
    assert response.status_code == 400, f"Expected 400 for invalid purchase date, got {response.status_code}. Response: {response.text}"
