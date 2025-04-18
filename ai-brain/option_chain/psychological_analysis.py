"""
Market Psychology Analysis Module

This module analyzes market psychology and sentiment using option chain data,
focusing on fear & greed indicators, smart money vs retail positioning, and
contrarian signals.
"""

import numpy as np
import pandas as pd
from datetime import datetime


class MarketPsychologyAnalyzer:
    """Analyzes market psychology based on option chain data."""
    
    def __init__(self, analyzer=None):
        """
        Initialize the market psychology analyzer.
        
        Args:
            analyzer (OptionChainAnalyzer, optional): Analyzer to use for data
        """
        self.analyzer = analyzer
        
    def set_analyzer(self, analyzer):
        """Set the analyzer to use for data."""
        self.analyzer = analyzer
    
    def get_fear_greed_index(self, analysis_results=None):
        """
        Calculate the Fear & Greed Index (0-100).
        
        Args:
            analysis_results (dict, optional): Pre-computed analysis results
            
        Returns:
            dict: Fear & Greed Index information
        """
        if not analysis_results and self.analyzer:
            # Get analysis results from the analyzer
            df = self.analyzer.fetcher.prepare_dataframe() if hasattr(self.analyzer, 'fetcher') else None
            analysis_results = self.analyzer.analyze_option_chain(df) if df is not None else None
        
        if not analysis_results:
            return {
                "error": "No analysis results available",
                "score": 50,  # Default to neutral
                "interpretation": "Neutral (Default)",
                "description": "Insufficient data to determine market sentiment"
            }
            
        # Extract key metrics
        pcr = analysis_results.get('pcr')
        max_pain = analysis_results.get('max_pain')
        underlying_value = analysis_results.get('underlying_value')
        momentum = analysis_results.get('momentum', {})
        iv_skew = analysis_results.get('iv_skew', {})
        
        # Start with a neutral score
        fear_greed_score = 50
        
        # Factor 1: PCR impact (-20 to +20)
        if pcr:
            if pcr > 1.5:
                fear_greed_score -= 20  # High PCR = Fear
            elif pcr > 1.2:
                fear_greed_score -= 10  # Above average PCR = Mild fear
            elif pcr < 0.5:
                fear_greed_score += 20  # Very low PCR = Greed
            elif pcr < 0.8:
                fear_greed_score += 10  # Below average PCR = Mild greed
                
        # Factor 2: OI momentum impact (-10 to +10)
        oi_momentum = momentum.get('oi_momentum')
        if oi_momentum:
            if oi_momentum == 'Bullish':
                fear_greed_score += 10
            elif oi_momentum == 'Bearish':
                fear_greed_score -= 10
                
        # Factor 3: Max pain vs current price impact (-10 to +10)
        if max_pain and underlying_value:
            percent_diff = (max_pain - underlying_value) / underlying_value * 100
            if percent_diff > 1:
                fear_greed_score += 5  # Max pain above price = Positive
            elif percent_diff < -1:
                fear_greed_score -= 5  # Max pain below price = Negative
                
        # Factor 4: IV skew impact (-10 to +10)
        if iv_skew and 'otm_puts' in iv_skew and 'otm_calls' in iv_skew:
            # Average IV delta for OTM puts and calls
            avg_put_iv_delta = None
            avg_call_iv_delta = None
            
            if iv_skew['otm_puts'] and len(iv_skew['otm_puts']) > 0:
                avg_put_iv_delta = sum(p.get('delta_from_atm', 0) for p in iv_skew['otm_puts']) / len(iv_skew['otm_puts'])
                
            if iv_skew['otm_calls'] and len(iv_skew['otm_calls']) > 0:
                avg_call_iv_delta = sum(c.get('delta_from_atm', 0) for c in iv_skew['otm_calls']) / len(iv_skew['otm_calls'])
                
            # High put skew indicates fear
            if avg_put_iv_delta and avg_call_iv_delta:
                if avg_put_iv_delta > avg_call_iv_delta * 1.5:
                    fear_greed_score -= 10
                # High call skew indicates greed
                elif avg_call_iv_delta > avg_put_iv_delta * 1.5:
                    fear_greed_score += 10
        
        # Clamp the score between 0 and 100
        fear_greed_score = max(0, min(100, fear_greed_score))
        
        # Determine the sentiment category
        if fear_greed_score >= 75:
            sentiment = "Extreme Greed"
            sentiment_desc = "Market shows excessive optimism, potentially overvalued. Contrarian traders might consider defensive positions."
        elif fear_greed_score >= 60:
            sentiment = "Greed"
            sentiment_desc = "Bullish sentiment with increasing risk appetite. Be cautious about chasing momentum at this stage."
        elif fear_greed_score >= 45:
            sentiment = "Neutral to Bullish"
            sentiment_desc = "Balanced sentiment with slight bullish bias. Favorable for measured position building."
        elif fear_greed_score >= 30:
            sentiment = "Neutral to Bearish"
            sentiment_desc = "Balanced sentiment with slight bearish bias. Consider protection strategies."
        elif fear_greed_score >= 15:
            sentiment = "Fear"
            sentiment_desc = "Bearish sentiment with increasing risk aversion. Potential opportunity for contrarians."
        else:
            sentiment = "Extreme Fear"
            sentiment_desc = "Market shows excessive pessimism, potentially oversold. Contrarian opportunity for the brave."
            
        return {
            "score": fear_greed_score,
            "interpretation": sentiment,
            "description": sentiment_desc,
            "pcr_contribution": "Bearish" if pcr and pcr > 1.2 else "Bullish" if pcr and pcr < 0.8 else "Neutral",
            "iv_skew_contribution": "Fearful" if 'avg_put_iv_delta' in locals() and avg_put_iv_delta and avg_call_iv_delta and avg_put_iv_delta > avg_call_iv_delta else "Complacent" if 'avg_call_iv_delta' in locals() and avg_call_iv_delta and avg_put_iv_delta and avg_call_iv_delta > avg_put_iv_delta else "Neutral"
        }
    
    def analyze_smart_money(self, analysis_results=None):
        """
        Analyze smart money vs retail positioning.
        
        Args:
            analysis_results (dict, optional): Pre-computed analysis results
            
        Returns:
            dict: Smart money analysis
        """
        if not analysis_results and self.analyzer:
            # Get analysis results from the analyzer
            df = self.analyzer.fetcher.prepare_dataframe() if hasattr(self.analyzer, 'fetcher') else None
            analysis_results = self.analyzer.analyze_option_chain(df) if df is not None else None
        
        if not analysis_results:
            return {"error": "No analysis results available"}
            
        # Extract key data
        iv_skew = analysis_results.get('iv_skew', {})
        key_levels = analysis_results.get('key_levels', {})
        underlying_value = analysis_results.get('underlying_value')
        
        smart_money_indications = []
        
        # Check for IV skew patterns that might indicate smart money positioning
        if iv_skew and 'otm_puts' in iv_skew and 'otm_calls' in iv_skew:
            if iv_skew['otm_puts'] and len(iv_skew['otm_puts']) > 0:
                # Steep put skew often indicates institutional hedging
                avg_put_iv_delta = sum(p.get('delta_from_atm', 0) for p in iv_skew['otm_puts']) / len(iv_skew['otm_puts'])
                if avg_put_iv_delta > 5:
                    smart_money_indications.append({
                        "pattern": "Institutional Hedging",
                        "indication": "Smart money adding downside protection",
                        "implication": "Potential caution while maintaining long positions"
                    })
                    
        # OI changes in specific strikes can indicate smart vs retail money
        if key_levels:
            # Major put support can indicate smart money
            if 'put_support' in key_levels and key_levels['put_support']:
                for level in key_levels['put_support'][:2]:  # Top 2 support levels
                    if underlying_value and level.get('strike') and level.get('strike') < underlying_value:
                        smart_money_indications.append({
                            "pattern": "Strong Put Support",
                            "level": level.get('strike'),
                            "oi": level.get('pe_oi'),
                            "indication": "Significant put writing at key level",
                            "implication": "Smart money providing price support / selling insurance"
                        })
                
            # Major call resistance can indicate smart money
            if 'call_resistance' in key_levels and key_levels['call_resistance']:
                for level in key_levels['call_resistance'][:2]:  # Top 2 resistance levels
                    if underlying_value and level.get('strike') and level.get('strike') > underlying_value:
                        smart_money_indications.append({
                            "pattern": "Strong Call Resistance",
                            "level": level.get('strike'),
                            "oi": level.get('ce_oi'),
                            "indication": "Significant call writing at key level",
                            "implication": "Smart money creating price ceiling / selling insurance"
                        })
            
            # Significant change in OI can indicate institutional activity
            if 'significant_pe_change' in key_levels and key_levels['significant_pe_change']:
                for change in key_levels['significant_pe_change'][:1]:  # Top change
                    if change.get('pe_change_oi', 0) > 200000:  # Large OI change
                        smart_money_indications.append({
                            "pattern": "Large Put OI Change",
                            "level": change.get('strike'),
                            "change": change.get('pe_change_oi'),
                            "indication": "Significant put position change",
                            "implication": "Institutional activity at this strike"
                        })
                        
            if 'significant_ce_change' in key_levels and key_levels['significant_ce_change']:
                for change in key_levels['significant_ce_change'][:1]:  # Top change
                    if change.get('ce_change_oi', 0) > 200000:  # Large OI change
                        smart_money_indications.append({
                            "pattern": "Large Call OI Change",
                            "level": change.get('strike'),
                            "change": change.get('ce_change_oi'),
                            "indication": "Significant call position change",
                            "implication": "Institutional activity at this strike"
                        })
        
        # Determine if retail is likely chasing momentum
        retail_activity = "Neutral"
        retail_implications = "No clear retail positioning detected"
        
        if analysis_results.get('pcr'):
            pcr = analysis_results.get('pcr')
            if pcr < 0.6:
                retail_activity = "Bullish Chasing"
                retail_implications = "Retail traders likely chasing bullish momentum, potentially overextended"
            elif pcr > 1.4:
                retail_activity = "Excessive Fear"
                retail_implications = "Retail traders showing excessive fear, potentially oversold"
                
        return {
            "smart_money_signs": smart_money_indications,
            "retail_positioning": {
                "activity": retail_activity,
                "implications": retail_implications
            },
            "institutional_hedging_level": "High" if smart_money_indications and any("Institutional Hedging" in indication.get('pattern', '') for indication in smart_money_indications) else "Normal"
        }
    
    def get_contrarian_signals(self, analysis_results=None):
        """
        Identify contrarian trading signals.
        
        Args:
            analysis_results (dict, optional): Pre-computed analysis results
            
        Returns:
            dict: Contrarian signals
        """
        if not analysis_results and self.analyzer:
            # Get analysis results from the analyzer
            df = self.analyzer.fetcher.prepare_dataframe() if hasattr(self.analyzer, 'fetcher') else None
            analysis_results = self.analyzer.analyze_option_chain(df) if df is not None else None
        
        if not analysis_results:
            return {"error": "No analysis results available"}
            
        # Get fear & greed score
        fear_greed = self.get_fear_greed_index(analysis_results)
        fear_greed_score = fear_greed.get('score', 50)
        
        # Extract key metrics
        pcr = analysis_results.get('pcr')
        max_pain = analysis_results.get('max_pain')
        underlying_value = analysis_results.get('underlying_value')
        
        contrarian_signals = []
        
        # Extreme fear/greed levels are contrarian signals
        if fear_greed_score <= 15:
            contrarian_signals.append({
                "signal": "Potential Bullish Reversal",
                "strength": "Strong",
                "reason": f"Extreme fear (score: {fear_greed_score}) often precedes market bottoms",
                "strategy": "Consider bullish positions against the prevailing sentiment"
            })
        elif fear_greed_score >= 85:
            contrarian_signals.append({
                "signal": "Potential Bearish Reversal",
                "strength": "Strong",
                "reason": f"Extreme greed (score: {fear_greed_score}) often precedes market tops",
                "strategy": "Consider bearish positions against the prevailing sentiment"
            })
            
        # High PCR is contrarian bullish
        if pcr and pcr > 1.5:
            contrarian_signals.append({
                "signal": "Contrarian Bullish Signal",
                "strength": "Moderate to Strong",
                "reason": f"Very high PCR ({pcr}) indicates excessive fear or hedging",
                "strategy": "Consider bullish positions, especially if technical support is present"
            })
        
        # Low PCR is contrarian bearish
        elif pcr and pcr < 0.5:
            contrarian_signals.append({
                "signal": "Contrarian Bearish Signal",
                "strength": "Moderate to Strong",
                "reason": f"Very low PCR ({pcr}) indicates excessive complacency or euphoria",
                "strategy": "Consider bearish positions, especially if technical resistance is present"
            })
            
        # Max pain divergence can be a contrarian signal
        if max_pain and underlying_value:
            percent_diff = (max_pain - underlying_value) / underlying_value * 100
            if percent_diff > 3:
                contrarian_signals.append({
                    "signal": "Potential Upward Reversion",
                    "strength": "Moderate",
                    "reason": f"Price ({underlying_value}) significantly below max pain ({max_pain})",
                    "strategy": "Consider bullish positions anticipating mean reversion to max pain"
                })
            elif percent_diff < -3:
                contrarian_signals.append({
                    "signal": "Potential Downward Reversion",
                    "strength": "Moderate",
                    "reason": f"Price ({underlying_value}) significantly above max pain ({max_pain})",
                    "strategy": "Consider bearish positions anticipating mean reversion to max pain"
                })
                
        # Analyze momentum indicators for potential exhaustion
        if 'momentum' in analysis_results:
            momentum = analysis_results['momentum']
            ce_oi_change = momentum.get('ce_oi_change', 0)
            pe_oi_change = momentum.get('pe_oi_change', 0)
            
            # Extremely one-sided OI changes can signal exhaustion
            if ce_oi_change and pe_oi_change and ce_oi_change > 500000 and ce_oi_change > pe_oi_change * 3:
                contrarian_signals.append({
                    "signal": "Potential Call Exhaustion",
                    "strength": "Moderate",
                    "reason": f"Extremely high call OI buildup (change: {ce_oi_change})",
                    "strategy": "Be cautious of buying calls at these levels, potential reversal"
                })
                
            if ce_oi_change and pe_oi_change and pe_oi_change > 500000 and pe_oi_change > ce_oi_change * 3:
                contrarian_signals.append({
                    "signal": "Potential Put Exhaustion",
                    "strength": "Moderate",
                    "reason": f"Extremely high put OI buildup (change: {pe_oi_change})",
                    "strategy": "Be cautious of buying puts at these levels, potential reversal"
                })
                
        return {
            "signals": contrarian_signals,
            "fear_greed_score": fear_greed_score,
            "overall_contrarian_bias": "Bullish" if fear_greed_score < 30 else "Bearish" if fear_greed_score > 70 else "Neutral"
        }
        
    def analyze_market_psychology(self, analysis_results=None):
        """
        Perform a comprehensive market psychology analysis.
        
        Args:
            analysis_results (dict, optional): Pre-computed analysis results
            
        Returns:
            dict: Complete market psychology analysis
        """
        if not analysis_results and self.analyzer:
            # Get analysis results from the analyzer
            df = self.analyzer.fetcher.prepare_dataframe() if hasattr(self.analyzer, 'fetcher') else None
            analysis_results = self.analyzer.analyze_option_chain(df) if df is not None else None
        
        if not analysis_results:
            return {"error": "No analysis results available"}
            
        # Get all psychology components
        fear_greed = self.get_fear_greed_index(analysis_results)
        smart_money = self.analyze_smart_money(analysis_results)
        contrarian = self.get_contrarian_signals(analysis_results)
        
        # Extract some key metrics for summary
        pcr = analysis_results.get('pcr', 0)
        max_pain = analysis_results.get('max_pain', 0)
        underlying_value = analysis_results.get('underlying_value', 0)
        
        # Generate market psychology summary
        summary = []
        
        # Fear & Greed summary
        if fear_greed.get('score', 50) < 30:
            summary.append("Market sentiment is fearful, with psychological indicators suggesting pessimism.")
        elif fear_greed.get('score', 50) > 70:
            summary.append("Market sentiment is greedy, with psychological indicators suggesting optimism.")
        else:
            summary.append("Market sentiment is relatively balanced between fear and greed.")
            
        # Smart money summary
        if smart_money.get('smart_money_signs'):
            summary.append("Institutional activity detected at key strike prices, suggesting smart money positioning.")
            
        # Contrarian summary
        if contrarian.get('signals'):
            if contrarian.get('overall_contrarian_bias') == "Bullish":
                summary.append("Contrarian indicators suggest potential bullish reversal against prevailing bearish sentiment.")
            elif contrarian.get('overall_contrarian_bias') == "Bearish":
                summary.append("Contrarian indicators suggest potential bearish reversal against prevailing bullish sentiment.")
                
        # Max pain insight
        if max_pain and underlying_value:
            percent_diff = (max_pain - underlying_value) / underlying_value * 100
            if abs(percent_diff) > 1:
                summary.append(f"Current price is {abs(percent_diff):.2f}% {'below' if percent_diff > 0 else 'above'} max pain ({max_pain}), suggesting potential {'upward' if percent_diff > 0 else 'downward'} pressure.")
                
        # PCR insight
        if pcr:
            if pcr > 1.2:
                summary.append(f"Put-Call Ratio of {pcr} indicates elevated hedging or bearish positioning.")
            elif pcr < 0.8:
                summary.append(f"Put-Call Ratio of {pcr} indicates low hedging or bullish positioning.")
                
        # Combine everything into a complete analysis
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "index": self.analyzer.fetcher.index if hasattr(self.analyzer, 'fetcher') else None,
            "underlying_value": underlying_value,
            "fear_greed_index": fear_greed,
            "smart_money_analysis": smart_money,
            "contrarian_signals": contrarian,
            "summary": summary,
            "trading_psychology_tips": [
                "Be aware of your own psychological biases and how they may align with the current market sentiment",
                "Consider contrarian positions when sentiment reaches extremes",
                "Watch smart money positioning for clues about institutional outlook",
                "Remember that max pain theory suggests prices often gravitate toward max pain at expiration",
                "Extremely high PCR can indicate a bottom is forming (contrarian bullish)",
                "Extremely low PCR can indicate a top is forming (contrarian bearish)"
            ]
        }
        
    def analyze_volume_profile(self, analysis_results=None):
        """
        Analyze volume distribution by strike price.
        
        Args:
            analysis_results (dict, optional): Pre-computed analysis results
            
        Returns:
            dict: Volume profile analysis
        """
        if not analysis_results and self.analyzer:
            # Get analysis results from the analyzer
            df = self.analyzer.fetcher.prepare_dataframe() if hasattr(self.analyzer, 'fetcher') else None
            analysis_results = self.analyzer.analyze_option_chain(df) if df is not None else None
        
        if not analysis_results:
            return {"error": "No analysis results available"}
            
        # We need the raw dataframe for volume analysis
        if not hasattr(self.analyzer, 'fetcher'):
            return {"error": "Fetcher not available"}
            
        df = self.analyzer.fetcher.prepare_dataframe()
        if df is None or df.empty:
            return {"error": "No dataframe available for volume analysis"}
            
        # Check if volume data exists in the dataframe
        if 'ce_volume' not in df.columns or 'pe_volume' not in df.columns:
            return {"error": "Volume data not available in the dataframe"}
            
        # Get underlying value
        underlying_value = self.analyzer.fetcher.underlying_value
        if not underlying_value:
            return {"error": "Underlying value not available"}
            
        try:
            # Calculate volume distribution
            total_ce_volume = df['ce_volume'].sum()
            total_pe_volume = df['pe_volume'].sum()
            
            # Find strikes with highest volume
            highest_ce_volume_idx = df['ce_volume'].idxmax() if not df['ce_volume'].empty else None
            highest_pe_volume_idx = df['pe_volume'].idxmax() if not df['pe_volume'].empty else None
            
            highest_ce_volume = df.loc[highest_ce_volume_idx] if highest_ce_volume_idx is not None else None
            highest_pe_volume = df.loc[highest_pe_volume_idx] if highest_pe_volume_idx is not None else None
            
            # Calculate volume distribution above and below current price
            above_price = df[df['strike'] > underlying_value]
            below_price = df[df['strike'] <= underlying_value]
            
            above_ce_volume = above_price['ce_volume'].sum()
            below_ce_volume = below_price['ce_volume'].sum()
            above_pe_volume = above_price['pe_volume'].sum()
            below_pe_volume = below_price['pe_volume'].sum()
            
            # Calculate call-put volume ratio
            cp_volume_ratio = round(total_ce_volume / total_pe_volume, 2) if total_pe_volume > 0 else float('inf')
            
            # Psychological interpretation
            if cp_volume_ratio > 2.0:
                volume_bias = "Extremely Bullish"
                volume_interpretation = "Significantly more call volume than put volume indicates strong bullish sentiment or FOMO"
            elif cp_volume_ratio > 1.5:
                volume_bias = "Bullish"
                volume_interpretation = "More call volume than put volume indicates bullish sentiment"
            elif cp_volume_ratio > 1.0:
                volume_bias = "Slightly Bullish"
                volume_interpretation = "Slightly more call volume than put volume indicates mildly bullish sentiment"
            elif cp_volume_ratio > 0.7:
                volume_bias = "Neutral"
                volume_interpretation = "Roughly balanced call and put volume indicates neutral sentiment"
            elif cp_volume_ratio > 0.5:
                volume_bias = "Slightly Bearish"
                volume_interpretation = "Slightly more put volume than call volume indicates mildly bearish sentiment"
            elif cp_volume_ratio > 0.3:
                volume_bias = "Bearish"
                volume_interpretation = "More put volume than call volume indicates bearish sentiment"
            else:
                volume_bias = "Extremely Bearish"
                volume_interpretation = "Significantly more put volume than call volume indicates strong bearish sentiment or panic"
            
            # OTM vs ITM volume analysis
            otm_calls = above_price['ce_volume'].sum()
            itm_calls = below_price['ce_volume'].sum()
            otm_puts = below_price['pe_volume'].sum()
            itm_puts = above_price['pe_volume'].sum()
            
            # Psychological insights
            insights = []
            
            # Insight from volume distribution
            if otm_calls > itm_calls * 3 and itm_calls > 0:
                insights.append({
                    "insight": "Heavy OTM Call Buying",
                    "interpretation": "Significant speculative bullish activity or anticipation of a large upward move",
                    "psychological_bias": "FOMO (Fear of Missing Out) or strong optimism"
                })
                
            if otm_puts > itm_puts * 3 and itm_puts > 0:
                insights.append({
                    "insight": "Heavy OTM Put Buying",
                    "interpretation": "Significant hedging or anticipation of a market decline",
                    "psychological_bias": "Fear or strong pessimism"
                })
                
            # Insight from volume clustering
            if highest_ce_volume is not None and 'ce_volume' in highest_ce_volume and highest_ce_volume['ce_volume'] > total_ce_volume * 0.2 and total_ce_volume > 0:
                insights.append({
                    "insight": "Call Volume Clustering",
                    "strike": highest_ce_volume['strike'],
                    "interpretation": f"Significant focus on strike {highest_ce_volume['strike']} for calls",
                    "psychological_bias": "Anchoring to a specific price target"
                })
                
            if highest_pe_volume is not None and 'pe_volume' in highest_pe_volume and highest_pe_volume['pe_volume'] > total_pe_volume * 0.2 and total_pe_volume > 0:
                insights.append({
                    "insight": "Put Volume Clustering",
                    "strike": highest_pe_volume['strike'],
                    "interpretation": f"Significant focus on strike {highest_pe_volume['strike']} for puts",
                    "psychological_bias": "Anchoring to a specific support level"
                })
                
            # Volume skew insight
            if above_ce_volume > below_ce_volume * 2 and below_ce_volume > 0:
                insights.append({
                    "insight": "Upside Call Skew",
                    "interpretation": "Traders focusing on upside calls far above current price",
                    "psychological_bias": "Optimism or speculation on a large upward move"
                })
                
            if below_pe_volume > above_pe_volume * 2 and above_pe_volume > 0:
                insights.append({
                    "insight": "Downside Put Skew",
                    "interpretation": "Traders focusing on downside puts far below current price",
                    "psychological_bias": "Pessimism or hedging against a large downward move"
                })
                
            return {
                "volume_metrics": {
                    "total_call_volume": total_ce_volume,
                    "total_put_volume": total_pe_volume,
                    "call_put_volume_ratio": cp_volume_ratio,
                    "above_price_call_volume": above_ce_volume,
                    "below_price_call_volume": below_ce_volume,
                    "above_price_put_volume": above_pe_volume,
                    "below_price_put_volume": below_pe_volume,
                    "otm_call_volume": otm_calls,
                    "itm_call_volume": itm_calls,
                    "otm_put_volume": otm_puts,
                    "itm_put_volume": itm_puts
                },
                "highest_volume_strikes": {
                    "call": highest_ce_volume['strike'] if highest_ce_volume is not None else None,
                    "put": highest_pe_volume['strike'] if highest_pe_volume is not None else None
                } if highest_ce_volume is not None or highest_pe_volume is not None else {},
                "volume_sentiment": {
                    "bias": volume_bias,
                    "interpretation": volume_interpretation
                },
                "psychological_insights": insights
            }
        except Exception as e:
            return {"error": f"Error in volume profile analysis: {str(e)}"}