def execute_vertical_spread(index, direction, expiry, width=100):
    """
    Creates a vertical spread (bull call or bear put spread)
    Requires manual confirmation before execution
    
    Parameters:
    - index: The index to trade (NIFTY, BANKNIFTY)
    - direction: 'BULL' or 'BEAR'
    - expiry: Expiry date string
    - width: Strike width between long and short legs
    """
    current_price = get_current_price(index)
    atm_strike = round(current_price / 50) * 50
    
    if direction == 'BULL':  # Bull Call Spread
        buy_strike = atm_strike
        sell_strike = atm_strike + width
        strategy_type = "BULL CALL SPREAD"
    else:  # Bear Put Spread
        buy_strike = atm_strike
        sell_strike = atm_strike - width
        strategy_type = "BEAR PUT SPREAD"
    
    # Calculate prices, max profit, max loss, breakeven
    # ...
    
    # Create order payload but don't execute
    order = {
        "strategy": strategy_type,
        "index": index,
        "buy_leg": f"{index}{expiry}{buy_strike}{'CE' if direction == 'BULL' else 'PE'}",
        "sell_leg": f"{index}{expiry}{sell_strike}{'CE' if direction == 'BULL' else 'PE'}",
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakeven": breakeven
    }
    
    # Return for manual confirmation
    return order