def place_order(index, strike, direction, lots, expiry):
    symbol = f"NSE:{index}{expiry}{strike}{'CE' if direction == 'BUY CALL' else 'PE'}"

    order_payload = {
        "symbol": symbol,
        "qty": lots * 15,
        "type": 2,  # Market order
        "side": 1 if direction == "BUY CALL" else -1,
        "productType": "INTRADAY",
        "validity": "DAY",
        "disclosedQty": 0
    }

    try:
        from fyers_api import fyers_model  # hypothetical
        response = fyers_model.place_order(order_payload)
        return response
    except Exception as e:
        return {"error": str(e)}
