"""
Decision Fusion Module for SAMBOT trading system.
Combines signals from technical indicators, ML predictions, and LLM recommendations
to make final trading decisions.
"""

import json
import numpy as np
from datetime import datetime


def fuse_signals(ml_signal, indicator_signal, llm_signal=None, risk_profile="moderate"):
    """
    Fuse signals from multiple sources to make a final decision.
    
    Args:
        ml_signal (dict): Signal from ML prediction with confidence
        indicator_signal (dict): Signal from technical indicators
        llm_signal (dict): Signal from LLM (optional)
        risk_profile (str): Risk profile ("conservative", "moderate", "aggressive")
        
    Returns:
        dict: Final decision with confidence and details
    """
    # Extract core signals and confidences
    ml_decision = ml_signal.get("signal", "WAIT")
    ml_confidence = ml_signal.get("confidence", 0.5)
    
    indicator_decision = indicator_signal.get("signal", "WAIT")
    indicator_confidence = indicator_signal.get("confidence", 0.5)
    
    llm_decision = "WAIT"
    llm_confidence = 0.5
    if llm_signal:
        llm_decision = llm_signal.get("decision", "WAIT")
        llm_confidence = llm_signal.get("confidence", 0.5)
    
    # Set signal weights based on risk profile
    if risk_profile == "conservative":
        # Conservative profile relies more on technical signals
        weights = {
            "ml": 0.3,
            "indicator": 0.5,
            "llm": 0.2
        }
        # Higher threshold for trade execution
        confidence_threshold = 0.8
    elif risk_profile == "aggressive":
        # Aggressive profile relies more on ML prediction
        weights = {
            "ml": 0.5,
            "indicator": 0.3,
            "llm": 0.2
        }
        # Lower threshold for trade execution
        confidence_threshold = 0.65
    else:  # moderate
        # Balanced approach
        weights = {
            "ml": 0.4,
            "indicator": 0.4,
            "llm": 0.2
        }
        # Moderate threshold for trade execution
        confidence_threshold = 0.75
    
    # Normalize weights if LLM signal is not provided
    if not llm_signal:
        weights["ml"] = weights["ml"] / (weights["ml"] + weights["indicator"])
        weights["indicator"] = weights["indicator"] / (weights["ml"] + weights["indicator"])
        weights["llm"] = 0.0
    
    # Calculate signal scores
    signal_scores = {
        "BUY CALL": 0.0,
        "WAIT": 0.0,
        "BUY PUT": 0.0
    }
    
    # Add ML score
    signal_scores[ml_decision] += weights["ml"] * ml_confidence
    
    # Add indicator score
    signal_scores[indicator_decision] += weights["indicator"] * indicator_confidence
    
    # Add LLM score if available
    if llm_signal:
        signal_scores[llm_decision] += weights["llm"] * llm_confidence
    
    # Find the highest scoring signal
    final_signal = max(signal_scores, key=signal_scores.get)
    final_confidence = signal_scores[final_signal]
    
    # Check agreement between sources
    sources_agree = False
    if llm_signal:
        sources_agree = (ml_decision == indicator_decision == llm_decision)
    else:
        sources_agree = (ml_decision == indicator_decision)
    
    # Boost confidence when sources agree
    if sources_agree:
        final_confidence = min(final_confidence + 0.1, 0.98)
    
    # Determine if we should execute the trade or just suggest it
    action = "EXECUTE TRADE" if final_confidence >= confidence_threshold else "SUGGEST TRADE"
    if final_signal == "WAIT":
        action = "NO ACTION"
    
    # Determine option details
    strike = ml_signal.get("strike", 0)
    expiry = ml_signal.get("expiry", None)
    current_price = ml_signal.get("entry", 0)
    
    # Generate reasoning text
    if sources_agree:
        reasoning = f"All sources agree on {final_signal} with high confidence"
    else:
        # If sources disagree, explain the decision
        ml_text = f"ML: {ml_decision} ({ml_confidence:.2f})"
        ind_text = f"Indicators: {indicator_decision} ({indicator_confidence:.2f})"
        llm_text = f"AI: {llm_decision} ({llm_confidence:.2f})" if llm_signal else ""
        
        sources_text = [ml_text, ind_text]
        if llm_signal:
            sources_text.append(llm_text)
            
        reasoning = f"Mixed signals: {', '.join(sources_text)}. Choosing {final_signal} based on weighted confidence."
    
    # For Indian market, determine lots based on confidence
    lots = 1  # Default
    if final_confidence > 0.9:
        lots = 3
    elif final_confidence > 0.8:
        lots = 2
    
    # Return final decision
    return {
        "signal": final_signal,
        "confidence": round(final_confidence, 2),
        "action": action,
        "lots": lots,
        "strike": strike,
        "expiry": expiry,
        "current_price": current_price,
        "timestamp": datetime.now().isoformat(),
        "reasoning": reasoning,
        "risk_profile": risk_profile,
        "source_signals": {
            "ml_signal": ml_decision,
            "ml_confidence": ml_confidence,
            "indicator_signal": indicator_decision,
            "indicator_confidence": indicator_confidence,
            "llm_signal": llm_decision if llm_signal else None,
            "llm_confidence": llm_confidence if llm_signal else None
        }
    }


def should_take_trade(signal, confidence, technical_factors, risk_profile="moderate"):
    """
    Additional decision layer to determine if a trade should be taken
    based on market conditions and technical factors.
    
    Args:
        signal (str): Trading signal (BUY CALL, BUY PUT, WAIT)
        confidence (float): Signal confidence
        technical_factors (dict): Technical market factors
        risk_profile (str): Risk profile ("conservative", "moderate", "aggressive")
        
    Returns:
        bool: Whether to take the trade
    """
    # Don't take trades with WAIT signal or low confidence
    if signal == "WAIT" or confidence < 0.6:
        return False
    
    # Set thresholds based on risk profile
    if risk_profile == "conservative":
        min_rr_ratio = 2.0  # Minimum risk-reward ratio
        max_volatility = 1.5  # Maximum allowed volatility (ATR%)
        min_adx = 25  # Minimum ADX (trend strength)
    elif risk_profile == "aggressive":
        min_rr_ratio = 1.2
        max_volatility = 2.5
        min_adx = 15
    else:  # moderate
        min_rr_ratio = 1.5
        max_volatility = 2.0
        min_adx = 20
    
    # Extract technical factors
    risk_reward = technical_factors.get("risk_reward", 0)
    volatility = technical_factors.get("volatility", 0)
    adx = technical_factors.get("adx", 0)
    
    # Check risk-reward ratio
    if risk_reward < min_rr_ratio:
        return False
    
    # Check volatility (too volatile markets can be unpredictable)
    if volatility > max_volatility:
        return False
    
    # Check trend strength (ADX)
    if adx < min_adx:
        return False
    
    # All checks passed
    return True


def determine_lot_size(balance, risk_per_trade, entry, stop_loss, index="NIFTY"):
    """
    Determine appropriate lot size based on available balance and risk parameters.
    
    Args:
        balance (float): Available trading balance
        risk_per_trade (float): Maximum risk per trade (0-1)
        entry (float): Entry price
        stop_loss (float): Stop loss price
        index (str): Index name (NIFTY, BANKNIFTY, etc.)
        
    Returns:
        int: Number of lots to trade
    """
    # Define lot sizes for different indices (Indian market specific)
    lot_sizes = {
        "NIFTY": 50,
        "BANKNIFTY": 25,
        "FINNIFTY": 40,
        "SENSEX": 10,
        "MIDCPNIFTY": 75
    }
    
    # Get lot size for the index
    lot_size = lot_sizes.get(index.upper(), 50)  # Default to NIFTY lot size
    
    # Calculate risk amount
    risk_amount = balance * risk_per_trade
    
    # Calculate risk per lot
    risk_per_point = abs(entry - stop_loss)
    risk_per_lot = risk_per_point * lot_size
    
    # Calculate maximum lots
    max_lots = int(risk_amount / risk_per_lot)
    
    # Ensure at least 1 lot, but not more than affordable
    return max(1, max_lots)


def choose_expiry_strategy(signal, days_to_expiry, risk_profile="moderate"):
    """
    Choose the appropriate options expiry based on the signal and risk profile.
    
    Args:
        signal (str): Trading signal (BUY CALL, BUY PUT, WAIT)
        days_to_expiry (int): Days to the nearest expiry
        risk_profile (str): Risk profile ("conservative", "moderate", "aggressive")
        
    Returns:
        str: Expiry strategy recommendation
    """
    # For Indian market, weekly and monthly expiries are common
    
    # If very close to expiry (1-2 days), consider next week
    if days_to_expiry <= 1:
        return "next_weekly"
    
    # Conservative risk profile prefers longer expiry for more time
    if risk_profile == "conservative":
        if days_to_expiry < 3:
            return "next_weekly"  # Avoid expiry week
        else:
            return "current_weekly"
    
    # Aggressive risk profile may be ok with shorter expiry
    elif risk_profile == "aggressive":
        if days_to_expiry < 1:
            return "next_weekly"  # Only avoid day of expiry
        else:
            return "current_weekly"
    
    # Moderate risk profile
    else:
        if days_to_expiry < 2:
            return "next_weekly"  # Avoid last two days
        else:
            return "current_weekly"


def main():
    """
    Main function for standalone testing
    """
    # Example ML signal
    ml_signal = {
        "signal": "BUY CALL",
        "confidence": 0.85,
        "entry": 22500,
        "stop_loss": 22400,
        "target": 22650,
        "strike": 22450
    }
    
    # Example indicator signal
    indicator_signal = {
        "signal": "BUY CALL",
        "confidence": 0.75,
        "trend": "UPTREND",
        "trend_strength": 0.8,
        "bullish_signals": ["RSI Bullish", "MACD Crossover"],
        "bearish_signals": []
    }
    
    # Example LLM signal
    llm_signal = {
        "decision": "BUY CALL",
        "confidence": 0.7,
        "reason": "Strong bullish momentum with increasing volume"
    }
    
    # Fuse the signals
    result = fuse_signals(ml_signal, indicator_signal, llm_signal, "moderate")
    
    # Print the result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()