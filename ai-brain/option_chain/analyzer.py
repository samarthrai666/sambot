"""
NSE Option Chain Analyzer

This module provides analytics for option chain data, including
PCR, max pain, OI analysis, and other option-specific metrics.
"""

import numpy as np
import pandas as pd


class OptionChainAnalyzer:
    """Analyzes option chain data for insights and metrics."""
    
    def __init__(self, fetcher=None):
        """
        Initialize the analyzer.
        
        Args:
            fetcher (OptionChainFetcher, optional): Fetcher instance to use
        """
        self.fetcher = fetcher
        self.pcr = None
        self.max_pain = None
        self.strike_distribution = None
        
    def set_fetcher(self, fetcher):
        """Set the fetcher to use for data access."""
        self.fetcher = fetcher
    
    def calculate_basic_metrics(self, df=None):
        """
        Calculate basic metrics for the option chain.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze or None to use fetcher
            
        Returns:
            dict: Calculated metrics
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return None
            
        # Calculate additional metrics
        df['oi_diff'] = df['pe_oi'] - df['ce_oi']
        df['call_put_ratio'] = df['pe_oi'] / df['ce_oi'].replace(0, 1)
        df['total_oi'] = df['ce_oi'] + df['pe_oi']
            
        # Calculate intrinsic values if we have underlying price
        underlying_value = self.fetcher.underlying_value if self.fetcher else None
        if underlying_value:
            df['ce_intrinsic'] = np.maximum(underlying_value - df['strike'], 0)
            df['pe_intrinsic'] = np.maximum(df['strike'] - underlying_value, 0)
            df['ce_extrinsic'] = df['ce_ltp'] - df['ce_intrinsic']
            df['pe_extrinsic'] = df['pe_ltp'] - df['pe_intrinsic']
            
        # Calculate volume metrics
        df['ce_volume_weight'] = df['ce_volume'] / df['ce_volume'].sum() if df['ce_volume'].sum() > 0 else 0
        df['pe_volume_weight'] = df['pe_volume'] / df['pe_volume'].sum() if df['pe_volume'].sum() > 0 else 0
            
        # Basic statistics
        total_ce_oi = df['ce_oi'].sum()
        total_pe_oi = df['pe_oi'].sum()
        total_ce_volume = df['ce_volume'].sum()
        total_pe_volume = df['pe_volume'].sum()
        
        # Put-Call Ratio (PCR)
        pcr_oi = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        pcr_volume = round(total_pe_volume / total_ce_volume, 2) if total_ce_volume > 0 else 0
        
        # Store PCR for later use
        self.pcr = pcr_oi
        
        # Find ATM strike
        if underlying_value:
            atm_index = (df['strike'] - underlying_value).abs().idxmin()
            atm_strike = df.loc[atm_index, 'strike']
        else:
            atm_strike = None
            
        # Return calculated metrics
        return {
            'total_ce_oi': total_ce_oi,
            'total_pe_oi': total_pe_oi,
            'total_oi': total_ce_oi + total_pe_oi,
            'pcr_oi': pcr_oi,
            'pcr_volume': pcr_volume,
            'atm_strike': atm_strike,
            'processed_df': df
        }
        
    def calculate_max_pain(self, df=None):
        """
        Calculate the max pain point - the strike price where option writers have minimal loss.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze or None to use fetcher
            
        Returns:
            float: Max pain strike price
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return None
            
        strikes = df['strike'].unique()
        pain_values = []
        
        for strike in strikes:
            # Calculate the pain (loss to option writers) at this strike
            pain = 0
            for _, row in df.iterrows():
                # For calls, loss = max(0, underlying - strike)
                if row['strike'] < strike:
                    pain += row['ce_oi'] * (row['strike'] - strike)
                # For puts, loss = max(0, strike - underlying)
                if row['strike'] > strike:
                    pain += row['pe_oi'] * (strike - row['strike'])
            
            pain_values.append({'strike': strike, 'pain': abs(pain)})
            
        # Find the strike with minimum pain
        pain_df = pd.DataFrame(pain_values)
        if pain_df.empty:
            return None
            
        # Store max pain for later use
        self.max_pain = pain_df.loc[pain_df['pain'].idxmin()]['strike']
        return self.max_pain

    def calculate_pcr(self, df=None):
        """
        Calculate the overall Put-Call Ratio.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze or None to use fetcher
            
        Returns:
            float: Calculated PCR
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return None
            
        total_pe_oi = df['pe_oi'].sum()
        total_ce_oi = df['ce_oi'].sum()
        
        self.pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
        return self.pcr

    def get_strike_distribution(self, df=None, range_percent=5):
        """
        Analyze the distribution of OI around the underlying price.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            range_percent (float): Percentage range around current price
            
        Returns:
            dict: Strike distribution data
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        underlying_value = self.fetcher.underlying_value if self.fetcher else None
            
        if df is None or df.empty or not underlying_value:
            return None
            
        # Define range around current price (e.g., ±5%)
        lower_bound = underlying_value * (1 - range_percent/100)
        upper_bound = underlying_value * (1 + range_percent/100)
        
        # Filter strikes within range
        range_df = df[(df['strike'] >= lower_bound) & (df['strike'] <= upper_bound)]
        
        # Calculate distribution data
        self.strike_distribution = {
            'range': f"{lower_bound:.2f} - {upper_bound:.2f}",
            'ce_oi_within_range': range_df['ce_oi'].sum(),
            'pe_oi_within_range': range_df['pe_oi'].sum(),
            'total_oi_within_range': range_df['ce_oi'].sum() + range_df['pe_oi'].sum(),
            'max_call_oi_strike': range_df.loc[range_df['ce_oi'].idxmax()]['strike'] if not range_df.empty else None,
            'max_put_oi_strike': range_df.loc[range_df['pe_oi'].idxmax()]['strike'] if not range_df.empty else None
        }
        
        return self.strike_distribution
    
    def get_implied_volatility_skew(self, df=None):
        """
        Analyze the implied volatility skew.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: IV skew data
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        underlying_value = self.fetcher.underlying_value if self.fetcher else None
            
        if df is None or df.empty or not underlying_value:
            return None
            
        # Find the ATM strike price (closest to underlying value)
        df['distance'] = abs(df['strike'] - underlying_value)
        atm_index = df['distance'].idxmin()
        atm_strike = df.loc[atm_index, 'strike']
        
        # Get IV for ATM options
        atm_ce_iv = df.loc[atm_index, 'ce_iv']
        atm_pe_iv = df.loc[atm_index, 'pe_iv']
        
        # Calculate IV skew (OTM puts vs OTM calls)
        otm_puts = df[df['strike'] < atm_strike].sort_values('strike', ascending=False)
        otm_calls = df[df['strike'] > atm_strike].sort_values('strike')
        
        # Get the first few OTM options on each side
        skew_data = {
            'atm_strike': atm_strike,
            'atm_call_iv': atm_ce_iv,
            'atm_put_iv': atm_pe_iv,
            'otm_calls': [],
            'otm_puts': []
        }
        
        for i, row in otm_calls.head(3).iterrows():
            skew_data['otm_calls'].append({
                'strike': row['strike'],
                'iv': row['ce_iv'],
                'delta_from_atm': row['ce_iv'] - atm_ce_iv
            })
            
        for i, row in otm_puts.head(3).iterrows():
            skew_data['otm_puts'].append({
                'strike': row['strike'],
                'iv': row['pe_iv'],
                'delta_from_atm': row['pe_iv'] - atm_pe_iv
            })
            
        return skew_data
    
    def identify_key_levels(self, df=None):
        """
        Identify key support and resistance levels based on option OI.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: Key level data
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return None
            
        # Identify significant put support (high put OI)
        put_support = df.sort_values('pe_oi', ascending=False).head(3)
        
        # Identify significant call resistance (high call OI)
        call_resistance = df.sort_values('ce_oi', ascending=False).head(3)
        
        # Look for strikes with significant changes in OI
        pe_oi_change = df.sort_values('pe_change_oi', ascending=False).head(3)
        ce_oi_change = df.sort_values('ce_change_oi', ascending=False).head(3)
        
        support_resistance = {
            'put_support': put_support[['strike', 'pe_oi', 'pe_change_oi']].to_dict('records'),
            'call_resistance': call_resistance[['strike', 'ce_oi', 'ce_change_oi']].to_dict('records'),
            'significant_pe_change': pe_oi_change[['strike', 'pe_change_oi']].to_dict('records'),
            'significant_ce_change': ce_oi_change[['strike', 'ce_change_oi']].to_dict('records')
        }
        
        return support_resistance
        
    def calculate_momentum_indicators(self, df=None):
        """
        Calculate momentum indicators from option chain data.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: Momentum indicators
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return None
            
        # Calculate OI momentum
        total_ce_change = df['ce_change_oi'].sum()
        total_pe_change = df['pe_change_oi'].sum()
        
        # Calculate volume momentum
        total_ce_volume = df['ce_volume'].sum()
        total_pe_volume = df['pe_volume'].sum()
        
        return {
            'ce_oi_change': total_ce_change,
            'pe_oi_change': total_pe_change,
            'net_oi_change': total_pe_change - total_ce_change,
            'oi_momentum': 'Bullish' if total_pe_change > total_ce_change else 'Bearish',
            'ce_volume': total_ce_volume,
            'pe_volume': total_pe_volume,
            'pcr_volume': round(total_pe_volume / total_ce_volume, 2) if total_ce_volume > 0 else 0,
            'volume_momentum': 'Bullish' if total_pe_volume > total_ce_volume else 'Bearish'
        }
        
    def get_vix_impact(self, vix_value=None):
        """
        Analyze the impact of VIX on option chain data.
        
        Args:
            vix_value (float, optional): Current VIX value
            
        Returns:
            dict: VIX impact analysis
        """
        if not vix_value:
            # Default to placeholder logic if no VIX provided
            return {
                'vix_level': 'Unknown',
                'expected_impact': 'Unknown without VIX data'
            }
            
        # VIX impact analysis
        vix_level = 'Low' if vix_value < 15 else 'Moderate' if vix_value < 25 else 'High'
        
        if vix_value < 15:
            expected_impact = "Low volatility environment. Option premiums may be cheaper. Consider long strategies that benefit from volatility expansion."
        elif vix_value < 25:
            expected_impact = "Moderate volatility environment. Option premiums fairly priced. Balance between directional and volatility strategies."
        else:
            expected_impact = "High volatility environment. Option premiums expensive. Consider strategies that benefit from volatility contraction."
            
        return {
            'vix_value': vix_value,
            'vix_level': vix_level,
            'expected_impact': expected_impact
        }
        
    def analyze_option_chain(self, df=None):
        """
        Perform comprehensive analysis on option chain data.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to analyze
            
        Returns:
            dict: Comprehensive analysis results
        """
        if df is None and self.fetcher:
            df = self.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            return {"error": "No data available for analysis"}
            
        # Perform all analyses
        basic_metrics = self.calculate_basic_metrics(df)
        if not basic_metrics:
            return {"error": "Error calculating basic metrics"}
            
        max_pain = self.calculate_max_pain(df)
        
        # Calculate PCR if not already calculated
        if self.pcr is None:
            self.calculate_pcr(df)
            
        # Get strike distribution around current price
        strike_dist = self.get_strike_distribution(df)
        
        # Get IV skew analysis
        iv_skew = self.get_implied_volatility_skew(df)
        
        # Identify key support and resistance levels
        key_levels = self.identify_key_levels(df)
        
        # Calculate momentum indicators
        momentum = self.calculate_momentum_indicators(df)
        
        # Combine all results
        return {
            "index": self.fetcher.index if self.fetcher else None,
            "timestamp": self.fetcher.last_fetch_time.strftime("%Y-%m-%d %H:%M:%S") if self.fetcher and self.fetcher.last_fetch_time else None,
            "underlying_value": self.fetcher.underlying_value if self.fetcher else None,
            "expiry": self.fetcher.selected_expiry if self.fetcher else None,
            "pcr": self.pcr,
            "max_pain": max_pain,
            "basic_metrics": basic_metrics,
            "strike_distribution": strike_dist,
            "iv_skew": iv_skew,
            "key_levels": key_levels,
            "momentum": momentum
        }