"""
NSE Option Chain Strategy Recommender

This module provides recommendations for option strategies based on
option chain analysis and market conditions.
"""

import pandas as pd
import numpy as np


class StrategyRecommender:
    """Recommends option strategies based on market analysis."""
    
    def __init__(self, analyzer=None):
        """
        Initialize the strategy recommender.
        
        Args:
            analyzer (OptionChainAnalyzer, optional): Analyzer to use for data
        """
        self.analyzer = analyzer
        
    def set_analyzer(self, analyzer):
        """Set the analyzer to use for data."""
        self.analyzer = analyzer
        
    def get_optimal_strike(self, df=None, strategy="straddle"):
        """
        Recommend optimal strikes for different option strategies.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            strategy (str): Strategy type (straddle, strangle, etc.)
            
        Returns:
            dict: Optimal strategy parameters
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return {"error": "No data available for analysis"}
            
        # Get underlying value
        underlying_value = None
        if self.analyzer and hasattr(self.analyzer, 'fetcher'):
            underlying_value = self.analyzer.fetcher.underlying_value
            
        if not underlying_value:
            return {"error": "No underlying value available"}
            
        # Find ATM strike
        df['distance'] = abs(df['strike'] - underlying_value)
        atm_index = df['distance'].idxmin()
        atm_strike = df.loc[atm_index, 'strike']
        
        if strategy == "straddle":
            # For straddle, find strike with lowest combined IV (usually ATM)
            df['combined_iv'] = df['ce_iv'] + df['pe_iv']
            optimal_index = df['combined_iv'].idxmin()
            optimal_strike = df.loc[optimal_index, 'strike']
            
            return {
                'strategy': 'Straddle',
                'description': 'Buy both a call and put at the same strike price',
                'market_outlook': 'Expecting significant move but direction uncertain',
                'iv_outlook': 'Expecting volatility to increase',
                'optimal_strike': optimal_strike,
                'call_iv': df.loc[optimal_index, 'ce_iv'],
                'put_iv': df.loc[optimal_index, 'pe_iv'],
                'call_price': df.loc[optimal_index, 'ce_ltp'],
                'put_price': df.loc[optimal_index, 'pe_ltp'],
                'total_cost': df.loc[optimal_index, 'ce_ltp'] + df.loc[optimal_index, 'pe_ltp'],
                'break_even_up': optimal_strike + df.loc[optimal_index, 'ce_ltp'] + df.loc[optimal_index, 'pe_ltp'],
                'break_even_down': optimal_strike - (df.loc[optimal_index, 'ce_ltp'] + df.loc[optimal_index, 'pe_ltp'])
            }
            
        elif strategy == "strangle":
            # For strangle, find OTM call and put with good risk/reward
            otm_calls = df[df['strike'] > atm_strike].sort_values('strike')
            otm_puts = df[df['strike'] < atm_strike].sort_values('strike', ascending=False)
            
            if len(otm_calls) < 1 or len(otm_puts) < 1:
                return {'strategy': 'Strangle', 'error': 'Not enough OTM strikes for analysis'}
                
            # Find suitable OTM options (approximately 5% away from ATM)
            target_call_strike = underlying_value * 1.05
            target_put_strike = underlying_value * 0.95
            
            call_index = (otm_calls['strike'] - target_call_strike).abs().idxmin()
            put_index = (otm_puts['strike'] - target_put_strike).abs().idxmin()
            
            call_strike = df.loc[call_index, 'strike']
            put_strike = df.loc[put_index, 'strike']
            
            return {
                'strategy': 'Strangle',
                'description': 'Buy OTM call and OTM put',
                'market_outlook': 'Expecting significant move but direction uncertain',
                'iv_outlook': 'Expecting volatility to increase',
                'call_strike': call_strike,
                'put_strike': put_strike,
                'call_iv': df.loc[call_index, 'ce_iv'],
                'put_iv': df.loc[put_index, 'pe_iv'],
                'call_price': df.loc[call_index, 'ce_ltp'],
                'put_price': df.loc[put_index, 'pe_ltp'],
                'total_cost': df.loc[call_index, 'ce_ltp'] + df.loc[put_index, 'pe_ltp'],
                'break_even_up': call_strike + df.loc[call_index, 'ce_ltp'] + df.loc[put_index, 'pe_ltp'],
                'break_even_down': put_strike - (df.loc[call_index, 'ce_ltp'] + df.loc[put_index, 'pe_ltp'])
            }
            
        elif strategy == "bull_call_spread":
            # For bull call spread, find strikes above ATM with good risk/reward
            otm_calls = df[df['strike'] > atm_strike].sort_values('strike')
            if len(otm_calls) < 2:
                return {'strategy': 'Bull Call Spread', 'error': 'Not enough OTM strikes for analysis'}
                
            spreads = []
            for i in range(len(otm_calls) - 1):
                lower_strike = otm_calls.iloc[i]['strike']
                upper_strike = otm_calls.iloc[i+1]['strike']
                lower_price = otm_calls.iloc[i]['ce_ltp']
                upper_price = otm_calls.iloc[i+1]['ce_ltp']
                
                # Calculate max profit and max loss
                max_profit = (upper_strike - lower_strike) - (lower_price - upper_price)
                max_loss = lower_price - upper_price
                
                if max_loss > 0:  # Avoid invalid spreads
                    risk_reward = max_profit / max_loss
                    
                    spreads.append({
                        'lower_strike': lower_strike,
                        'upper_strike': upper_strike,
                        'lower_price': lower_price,
                        'upper_price': upper_price,
                        'max_profit': max_profit,
                        'max_loss': max_loss,
                        'risk_reward': risk_reward
                    })
            
            if not spreads:
                return {'strategy': 'Bull Call Spread', 'error': 'No valid spreads found'}
                
            # Find the spread with the best risk/reward ratio
            best_spread = max(spreads, key=lambda x: x['risk_reward'])
            best_spread['strategy'] = 'Bull Call Spread'
            best_spread['description'] = 'Buy lower strike call, sell higher strike call'
            best_spread['market_outlook'] = 'Moderately bullish'
            best_spread['iv_outlook'] = 'Neutral to slightly bearish on volatility'
            
            return best_spread
            
        elif strategy == "bear_put_spread":
            # For bear put spread, find strikes below ATM with good risk/reward
            otm_puts = df[df['strike'] < atm_strike].sort_values('strike', ascending=False)
            if len(otm_puts) < 2:
                return {'strategy': 'Bear Put Spread', 'error': 'Not enough OTM strikes for analysis'}
                
            spreads = []
            for i in range(len(otm_puts) - 1):
                upper_strike = otm_puts.iloc[i]['strike']
                lower_strike = otm_puts.iloc[i+1]['strike']
                upper_price = otm_puts.iloc[i]['pe_ltp']
                lower_price = otm_puts.iloc[i+1]['pe_ltp']
                
                # Calculate max profit and max loss
                max_profit = (upper_strike - lower_strike) - (upper_price - lower_price)
                max_loss = upper_price - lower_price
                
                if max_loss > 0:  # Avoid invalid spreads
                    risk_reward = max_profit / max_loss
                    
                    spreads.append({
                        'upper_strike': upper_strike,
                        'lower_strike': lower_strike,
                        'upper_price': upper_price,
                        'lower_price': lower_price,
                        'max_profit': max_profit,
                        'max_loss': max_loss,
                        'risk_reward': risk_reward
                    })
            
            if not spreads:
                return {'strategy': 'Bear Put Spread', 'error': 'No valid spreads found'}
                
            # Find the spread with the best risk/reward ratio
            best_spread = max(spreads, key=lambda x: x['risk_reward'])
            best_spread['strategy'] = 'Bear Put Spread'
            best_spread['description'] = 'Buy higher strike put, sell lower strike put'
            best_spread['market_outlook'] = 'Moderately bearish'
            best_spread['iv_outlook'] = 'Neutral to slightly bearish on volatility'
            
            return best_spread
            
        elif strategy == "iron_condor":
            # For iron condor, find strikes with stable IVs and good premium
            put_strikes = df[df['strike'] < atm_strike].sort_values('strike', ascending=False)
            call_strikes = df[df['strike'] > atm_strike].sort_values('strike')
            
            if len(put_strikes) < 2 or len(call_strikes) < 2:
                return {'strategy': 'Iron Condor', 'error': 'Not enough strikes for analysis'}
                
            # Find put spread (for lower wing)
            put_spread = {
                'short_strike': put_strikes.iloc[0]['strike'],
                'short_premium': put_strikes.iloc[0]['pe_ltp'],
                'long_strike': put_strikes.iloc[1]['strike'],
                'long_premium': put_strikes.iloc[1]['pe_ltp']
            }
            
            # Find call spread (for upper wing)
            call_spread = {
                'short_strike': call_strikes.iloc[0]['strike'],
                'short_premium': call_strikes.iloc[0]['ce_ltp'],
                'long_strike': call_strikes.iloc[1]['strike'],
                'long_premium': call_strikes.iloc[1]['ce_ltp']
            }
            
            # Calculate net premium and max risk
            net_premium = (put_spread['short_premium'] - put_spread['long_premium']) + (call_spread['short_premium'] - call_spread['long_premium'])
            max_risk_put = put_spread['short_strike'] - put_spread['long_strike'] - (put_spread['short_premium'] - put_spread['long_premium'])
            max_risk_call = call_spread['long_strike'] - call_spread['short_strike'] - (call_spread['short_premium'] - call_spread['long_premium'])
            max_risk = max(max_risk_put, max_risk_call)
            
            return {
                'strategy': 'Iron Condor',
                'description': 'Sell OTM put and call, buy further OTM put and call for protection',
                'market_outlook': 'Neutral, expecting consolidation',
                'iv_outlook': 'Expecting volatility to decrease',
                'put_short_strike': put_spread['short_strike'],
                'put_long_strike': put_spread['long_strike'],
                'call_short_strike': call_spread['short_strike'],
                'call_long_strike': call_spread['long_strike'],
                'net_premium': net_premium,
                'max_risk': max_risk,
                'risk_reward': max_risk / net_premium if net_premium > 0 else 0,
                'break_even_lower': put_spread['short_strike'] - net_premium,
                'break_even_upper': call_spread['short_strike'] + net_premium
            }
            
        elif strategy == "butterfly":
            # For butterfly, find strikes centered around ATM
            if len(df) < 3:
                return {'strategy': 'Butterfly', 'error': 'Not enough strikes for analysis'}
                
            # Find the middle strike (closest to ATM)
            middle_index = atm_index
            middle_strike = df.loc[middle_index, 'strike']
            
            # Find wing strikes (approximately equidistant from middle)
            wing_width = df['strike'].diff().median() * 2  # Typically 2 strikes away
            lower_target = middle_strike - wing_width
            upper_target = middle_strike + wing_width
            
            # Find closest actual strikes
            lower_index = (df['strike'] - lower_target).abs().idxmin()
            upper_index = (df['strike'] - upper_target).abs().idxmin()
            
            lower_strike = df.loc[lower_index, 'strike']
            upper_strike = df.loc[upper_index, 'strike']
            
            # Calculate prices and metrics for a call butterfly
            lower_call_price = df.loc[lower_index, 'ce_ltp']
            middle_call_price = df.loc[middle_index, 'ce_ltp']
            upper_call_price = df.loc[upper_index, 'ce_ltp']
            
            # Net debit = buy lower + buy upper - (2 * sell middle)
            net_debit = lower_call_price + upper_call_price - (2 * middle_call_price)
            max_profit = middle_strike - lower_strike - net_debit
            
            return {
                'strategy': 'Call Butterfly',
                'description': 'Buy lower and upper strikes, sell 2x middle strike',
                'market_outlook': 'Highly neutral, expecting price to stay near middle strike',
                'iv_outlook': 'Neutral to slightly bearish on volatility',
                'lower_strike': lower_strike,
                'middle_strike': middle_strike,
                'upper_strike': upper_strike,
                'lower_price': lower_call_price,
                'middle_price': middle_call_price,
                'upper_price': upper_call_price,
                'net_debit': net_debit,
                'max_profit': max_profit,
                'risk_reward': max_profit / net_debit if net_debit > 0 else 0,
                'break_even_lower': lower_strike + net_debit,
                'break_even_upper': upper_strike - net_debit
            }
        
        return {"error": f"Strategy '{strategy}' not supported"}
        
    def get_strategy_recommendation(self, market_view=None):
        """
        Get strategy recommendations based on market view and option chain analysis.
        
        Args:
            market_view (str, optional): User's market view 
                ('bullish', 'bearish', 'neutral', 'volatile')
            
        Returns:
            list: Recommended strategies with parameters
        """
        if not self.analyzer:
            return [{"error": "Analyzer not available"}]
            
        # Get market data
        df = None
        if hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return [{"error": "No data available for analysis"}]
            
        # Get analysis results
        analysis_results = self.analyzer.analyze_option_chain(df)
        
        # If no market view provided, infer from analysis
        if not market_view:
            pcr = analysis_results.get('pcr', 1.0)
            
            if pcr > 1.2:
                # High PCR often indicates bearish sentiment
                market_view = 'bearish'
            elif pcr < 0.8:
                # Low PCR often indicates bullish sentiment
                market_view = 'bullish'
            else:
                # PCR around 1 suggests neutral sentiment
                market_view = 'neutral'
                
        # Get IV analysis to gauge volatility expectations
        iv_skew = analysis_results.get('iv_skew', {})
        avg_iv = df['ce_iv'].mean() if 'ce_iv' in df else None
        
        high_iv = avg_iv > 25 if avg_iv else False
        
        recommendations = []
        
        # Based on market view, recommend appropriate strategies
        if market_view == 'bullish':
            # Strong bullish: Long Call
            atm_call = self.get_optimal_strike(df, "straddle")  # Use straddle finder to get ATM
            if "error" not in atm_call:
                recommendations.append({
                    'strategy': 'Long Call',
                    'description': 'Buy a call option to profit from upward movement',
                    'market_outlook': 'Bullish',
                    'iv_outlook': 'Neutral to bullish on volatility',
                    'strike': atm_call['optimal_strike'],
                    'premium': atm_call['call_price'],
                    'break_even': atm_call['optimal_strike'] + atm_call['call_price'],
                    'confidence': 'High' if pcr < 0.7 else 'Medium'
                })
                
            # Moderately bullish: Bull Call Spread
            bull_spread = self.get_optimal_strike(df, "bull_call_spread")
            if "error" not in bull_spread:
                recommendations.append(bull_spread)
                
        elif market_view == 'bearish':
            # Strong bearish: Long Put
            atm_put = self.get_optimal_strike(df, "straddle")  # Use straddle finder to get ATM
            if "error" not in atm_put:
                recommendations.append({
                    'strategy': 'Long Put',
                    'description': 'Buy a put option to profit from downward movement',
                    'market_outlook': 'Bearish',
                    'iv_outlook': 'Neutral to bullish on volatility',
                    'strike': atm_put['optimal_strike'],
                    'premium': atm_put['put_price'],
                    'break_even': atm_put['optimal_strike'] - atm_put['put_price'],
                    'confidence': 'High' if pcr > 1.3 else 'Medium'
                })
                
            # Moderately bearish: Bear Put Spread
            bear_spread = self.get_optimal_strike(df, "bear_put_spread")
            if "error" not in bear_spread:
                recommendations.append(bear_spread)
                
        elif market_view == 'neutral':
            # Range-bound: Iron Condor
            iron_condor = self.get_optimal_strike(df, "iron_condor")
            if "error" not in iron_condor:
                recommendations.append(iron_condor)
                
            # Highly neutral: Butterfly
            butterfly = self.get_optimal_strike(df, "butterfly")
            if "error" not in butterfly:
                recommendations.append(butterfly)
                
        elif market_view == 'volatile':
            # Expecting big move in either direction: Straddle
            straddle = self.get_optimal_strike(df, "straddle")
            if "error" not in straddle:
                recommendations.append(straddle)
                
            # Cheaper alternative to straddle: Strangle
            strangle = self.get_optimal_strike(df, "strangle")
            if "error" not in strangle:
                recommendations.append(strangle)
        
        # Add metadata about current market conditions
        market_context = {
            'pcr': analysis_results.get('pcr'),
            'max_pain': analysis_results.get('max_pain'),
            'iv_environment': 'High' if high_iv else 'Normal',
            'market_view': market_view,
            'timestamp': analysis_results.get('timestamp')
        }
        
        return {
            'market_context': market_context,
            'recommendations': recommendations
        }