"""
NSE Option Chain Signal Generator

This module generates trading signals based on option chain analysis,
focusing on directional and volatility-based signals.
"""

import pandas as pd
import numpy as np


class SignalGenerator:
    """Generates trading signals from option chain data."""
    
    def __init__(self, analyzer=None):
        """
        Initialize the signal generator.
        
        Args:
            analyzer (OptionChainAnalyzer, optional): Analyzer to use for data
        """
        self.analyzer = analyzer
        
    def set_analyzer(self, analyzer):
        """Set the analyzer to use for data."""
        self.analyzer = analyzer
        
    def get_intraday_signals(self, df=None):
        """
        Generate intraday trading signals based on option chain analysis.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: Generated trading signals
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return {"error": "No data available for signal generation"}
            
        # Get analysis results
        analysis_results = self.analyzer.analyze_option_chain(df)
        if not analysis_results or "error" in analysis_results:
            return {"error": f"Analysis failed: {analysis_results.get('error', 'Unknown error')}"}
            
        # Extract key metrics
        pcr = analysis_results.get('pcr')
        max_pain = analysis_results.get('max_pain')
        underlying_value = analysis_results.get('underlying_value')
        momentum = analysis_results.get('momentum', {})
        key_levels = analysis_results.get('key_levels', {})
        
        # Generate trading signals
        signals = []
        
        # Signal 1: PCR extreme levels
        if pcr > 1.5:
            signals.append({
                'signal': 'BUY CALL',
                'reason': f'Extremely high PCR ({pcr}) indicates potential reversal (contrarian)',
                'confidence': 0.7,
                'timeframe': 'Intraday'
            })
        elif pcr < 0.5:
            signals.append({
                'signal': 'BUY PUT',
                'reason': f'Extremely low PCR ({pcr}) indicates potential reversal (contrarian)',
                'confidence': 0.7,
                'timeframe': 'Intraday'
            })
            
        # Signal 2: OI analysis - significant buildup
        if 'significant_ce_change' in key_levels and key_levels['significant_ce_change']:
            highest_ce_change = key_levels['significant_ce_change'][0]
            highest_ce_strike = highest_ce_change.get('strike')
            highest_ce_oi_change = highest_ce_change.get('ce_change_oi', 0)
            
            # If highest call OI buildup is above current price = resistance
            if highest_ce_strike and highest_ce_strike > underlying_value and highest_ce_oi_change > 100000:
                signals.append({
                    'signal': 'BUY PUT',
                    'reason': f'Strong call writing at {highest_ce_strike} creating resistance',
                    'confidence': 0.65,
                    'target': highest_ce_strike,
                    'timeframe': 'Intraday'
                })
        
        if 'significant_pe_change' in key_levels and key_levels['significant_pe_change']:
            highest_pe_change = key_levels['significant_pe_change'][0]
            highest_pe_strike = highest_pe_change.get('strike')
            highest_pe_oi_change = highest_pe_change.get('pe_change_oi', 0)
            
            # If highest put OI buildup is below current price = support
            if highest_pe_strike and highest_pe_strike < underlying_value and highest_pe_oi_change > 100000:
                signals.append({
                    'signal': 'BUY CALL',
                    'reason': f'Strong put writing at {highest_pe_strike} creating support',
                    'confidence': 0.65,
                    'target': highest_pe_strike,
                    'timeframe': 'Intraday'
                })
            
        # Signal 3: Distance from max pain
        if max_pain and underlying_value:
            max_pain_percent = (max_pain - underlying_value) / underlying_value * 100
            
            if max_pain_percent > 1:  # If max pain is significantly above current price
                signals.append({
                    'signal': 'BUY CALL',
                    'reason': f'Price ({underlying_value}) below max pain ({max_pain}), potential upward movement',
                    'confidence': 0.6,
                    'timeframe': 'Intraday to Swing'
                })
            elif max_pain_percent < -1:  # If max pain is significantly below current price
                signals.append({
                    'signal': 'BUY PUT',
                    'reason': f'Price ({underlying_value}) above max pain ({max_pain}), potential downward movement',
                    'confidence': 0.6,
                    'timeframe': 'Intraday to Swing'
                })
                
        # Signal 4: IV skew analysis
        iv_skew = analysis_results.get('iv_skew', {})
        if iv_skew:
            # Check if OTM put IVs are much higher than OTM call IVs
            if 'otm_puts' in iv_skew and 'otm_calls' in iv_skew and iv_skew['otm_puts'] and iv_skew['otm_calls']:
                avg_put_iv_delta = sum(p['delta_from_atm'] for p in iv_skew['otm_puts']) / len(iv_skew['otm_puts'])
                avg_call_iv_delta = sum(c['delta_from_atm'] for c in iv_skew['otm_calls']) / len(iv_skew['otm_calls'])
                
                if avg_put_iv_delta > 5 and avg_put_iv_delta > avg_call_iv_delta * 1.5:
                    signals.append({
                        'signal': 'BUY CALL',
                        'reason': 'Steep put IV skew indicates market fear and potential reversal',
                        'confidence': 0.55,
                        'timeframe': 'Swing'
                    })
                elif avg_call_iv_delta > 5 and avg_call_iv_delta > avg_put_iv_delta * 1.5:
                    signals.append({
                        'signal': 'BUY PUT',
                        'reason': 'Steep call IV skew indicates excessive optimism and potential reversal',
                        'confidence': 0.55,
                        'timeframe': 'Swing'
                    })
        
        # Signal 5: OI momentum analysis
        if momentum:
            ce_oi_change = momentum.get('ce_oi_change', 0)
            pe_oi_change = momentum.get('pe_oi_change', 0)
            
            # Significant call writing (bearish)
            if ce_oi_change > 500000 and ce_oi_change > pe_oi_change * 2:
                signals.append({
                    'signal': 'BUY PUT',
                    'reason': 'Heavy call writing indicating bearish sentiment',
                    'confidence': 0.6,
                    'timeframe': 'Intraday'
                })
                
            # Significant put writing (bullish)
            if pe_oi_change > 500000 and pe_oi_change > ce_oi_change * 2:
                signals.append({
                    'signal': 'BUY CALL',
                    'reason': 'Heavy put writing indicating bullish sentiment',
                    'confidence': 0.6,
                    'timeframe': 'Intraday'
                })
        
        # Determine the final recommendation based on signal weights
        final_signal = self._determine_final_signal(signals)
        
        return {
            'index': analysis_results.get('index'),
            'timestamp': analysis_results.get('timestamp'),
            'underlying_value': underlying_value,
            'pcr': pcr,
            'max_pain': max_pain,
            'signals': signals,
            'final_signal': final_signal
        }
    
    def _determine_final_signal(self, signals):
        """
        Determine the final signal based on weighted confidence.
        
        Args:
            signals (list): List of signal dictionaries
            
        Returns:
            dict: Final signal recommendation
        """
        if not signals:
            return {
                'signal': 'WAIT',
                'reason': 'No clear signals detected',
                'confidence': 0.0
            }
            
        # Group signals by type (BUY CALL vs BUY PUT)
        call_signals = [s for s in signals if s['signal'] == 'BUY CALL']
        put_signals = [s for s in signals if s['signal'] == 'BUY PUT']
        
        # Calculate weighted confidence for each direction
        call_confidence = sum(s['confidence'] for s in call_signals) / 5  # Normalize to 0-1 scale
        put_confidence = sum(s['confidence'] for s in put_signals) / 5
        
        # Determine final signal based on highest confidence
        if call_confidence > put_confidence and call_confidence > 0.65:
            # Find the call signal with highest confidence
            best_call = max(call_signals, key=lambda x: x['confidence'])
            return {
                'signal': 'BUY CALL',
                'reason': best_call['reason'],
                'confidence': round(call_confidence, 2),
                'target': best_call.get('target'),
                'timeframe': best_call['timeframe']
            }
        elif put_confidence > call_confidence and put_confidence > 0.65:
            # Find the put signal with highest confidence
            best_put = max(put_signals, key=lambda x: x['confidence'])
            return {
                'signal': 'BUY PUT',
                'reason': best_put['reason'],
                'confidence': round(put_confidence, 2),
                'target': best_put.get('target'),
                'timeframe': best_put['timeframe']
            }
        else:
            return {
                'signal': 'WAIT',
                'reason': 'Conflicting signals or low confidence',
                'confidence': round(max(call_confidence, put_confidence), 2)
            }
    
    def get_position_suggestions(self, df=None):
        """
        Generate position size and strike suggestions for signals.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: Position suggestions
        """
        # Get intraday signals first
        signal_data = self.get_intraday_signals(df)
        if "error" in signal_data:
            return signal_data
            
        final_signal = signal_data.get('final_signal', {})
        if not final_signal or final_signal.get('signal') == 'WAIT':
            return {
                'message': 'No actionable signal detected',
                'action': 'WAIT'
            }
            
        # Get underlying value
        underlying_value = signal_data.get('underlying_value')
        if not underlying_value:
            return {
                'message': 'Missing underlying value',
                'action': 'ERROR'
            }
            
        # Get the nearest expiry
        expiry = None
        if self.analyzer and hasattr(self.analyzer, 'fetcher'):
            expiry = self.analyzer.fetcher.selected_expiry
            
        # Determine appropriate strike price based on signal
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return {
                'message': 'No option chain data available',
                'action': 'ERROR'
            }
            
        # Find ATM strike
        df['distance'] = abs(df['strike'] - underlying_value)
        atm_index = df['distance'].idxmin()
        atm_strike = df.loc[atm_index, 'strike']
        
        # Recommendation varies based on signal type
        signal_type = final_signal.get('signal')
        confidence = final_signal.get('confidence', 0)
        
        if signal_type == 'BUY CALL':
            # For calls, slightly OTM often offers better risk/reward
            strike_index = df[df['strike'] >= atm_strike].iloc[0:2].index[0]
            strike = df.loc[strike_index, 'strike']
            premium = df.loc[strike_index, 'ce_ltp']
            
            # Suggest stop loss and target
            stop_loss = underlying_value - (underlying_value * 0.01)  # 1% below current price
            target = underlying_value + (underlying_value * 0.02)  # 2% above current price
            
            # Suggest lot size based on confidence
            lots = 1
            if confidence > 0.8:
                lots = 3
            elif confidence > 0.7:
                lots = 2
                
            return {
                'index': signal_data.get('index'),
                'signal': signal_type,
                'confidence': confidence,
                'reason': final_signal.get('reason'),
                'entry': underlying_value,
                'strike': strike,
                'premium': premium,
                'stop_loss': stop_loss,
                'target': target,
                'lots': lots,
                'expiry': expiry,
                'risk_reward': (target - underlying_value) / (underlying_value - stop_loss) if (underlying_value - stop_loss) > 0 else 0,
                'action': 'EXECUTE' if confidence > 0.7 else 'MONITOR'
            }
            
        elif signal_type == 'BUY PUT':
            # For puts, slightly OTM often offers better risk/reward
            strike_index = df[df['strike'] <= atm_strike].iloc[0:2].index[0]
            strike = df.loc[strike_index, 'strike']
            premium = df.loc[strike_index, 'pe_ltp']
            
            # Suggest stop loss and target
            stop_loss = underlying_value + (underlying_value * 0.01)  # 1% above current price
            target = underlying_value - (underlying_value * 0.02)  # 2% below current price
            
            # Suggest lot size based on confidence
            lots = 1
            if confidence > 0.8:
                lots = 3
            elif confidence > 0.7:
                lots = 2
                
            return {
                'index': signal_data.get('index'),
                'signal': signal_type,
                'confidence': confidence,
                'reason': final_signal.get('reason'),
                'entry': underlying_value,
                'strike': strike,
                'premium': premium,
                'stop_loss': stop_loss,
                'target': target,
                'lots': lots,
                'expiry': expiry,
                'risk_reward': (underlying_value - target) / (stop_loss - underlying_value) if (stop_loss - underlying_value) > 0 else 0,
                'action': 'EXECUTE' if confidence > 0.7 else 'MONITOR'
            }
            
        return {
            'message': 'Unsupported signal type',
            'action': 'ERROR'
        }