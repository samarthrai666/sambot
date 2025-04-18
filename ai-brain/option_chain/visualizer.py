"""
NSE Option Chain Visualizer

This module provides visualization tools for option chain data analysis,
including OI distribution, PCR trends, IV skew, and more.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime
import os


class OptionChainVisualizer:
    """Visualizes option chain data analysis results."""
    
    def __init__(self, analyzer=None):
        """
        Initialize the visualizer.
        
        Args:
            analyzer (OptionChainAnalyzer, optional): Analyzer to use for data
        """
        self.analyzer = analyzer
        self.figures = {}
        self.output_dir = "option_charts"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def set_analyzer(self, analyzer):
        """Set the analyzer to use for data."""
        self.analyzer = analyzer
        
    def set_output_directory(self, directory):
        """Set the output directory for saved charts."""
        self.output_dir = directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def plot_option_chain(self, df=None, save_path=None, show_plot=False):
        """
        Generate a visual representation of the option chain.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to visualize
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            print("No data available for visualization")
            return None
            
        # Get underlying value and max pain
        underlying_value = None
        max_pain = None
        
        if self.analyzer:
            if hasattr(self.analyzer, 'fetcher') and self.analyzer.fetcher:
                underlying_value = self.analyzer.fetcher.underlying_value
            max_pain = self.analyzer.max_pain
        
        # Set up the figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot the OI distribution
        ax1.bar(df['strike'], df['ce_oi'], width=10, alpha=0.7, color='green', label='Call OI')
        ax1.bar(df['strike'], df['pe_oi'], width=10, alpha=0.7, color='red', label='Put OI')
        
        # Add the current price line if we have it
        if underlying_value:
            ax1.axvline(x=underlying_value, color='blue', linestyle='--', alpha=0.7, 
                      label=f'Current Price: {underlying_value}')
        
        # Add max pain if calculated
        if max_pain:
            ax1.axvline(x=max_pain, color='purple', linestyle='-.', alpha=0.7, 
                      label=f'Max Pain: {max_pain}')
        
        # Format the plot
        index_name = self.analyzer.fetcher.index if self.analyzer and hasattr(self.analyzer, 'fetcher') else "Option Chain"
        expiry = self.analyzer.fetcher.selected_expiry if self.analyzer and hasattr(self.analyzer, 'fetcher') else ""
        
        ax1.set_title(f'{index_name} Option Chain Analysis - {expiry}')
        ax1.set_xlabel('Strike Price')
        ax1.set_ylabel('Open Interest')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Plot the IV skew
        ax2.plot(df['strike'], df['ce_iv'], marker='o', color='green', alpha=0.7, label='Call IV')
        ax2.plot(df['strike'], df['pe_iv'], marker='o', color='red', alpha=0.7, label='Put IV')
        
        if underlying_value:
            ax2.axvline(x=underlying_value, color='blue', linestyle='--', alpha=0.5)
            
        ax2.set_xlabel('Strike Price')
        ax2.set_ylabel('Implied Volatility (%)')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['option_chain'] = fig
        return fig
        
    def plot_oi_buildup(self, df=None, save_path=None, show_plot=False):
        """
        Plot the OI buildup for call and put options.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to visualize
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            print("No data available for visualization")
            return None
            
        # Get underlying value
        underlying_value = None
        if self.analyzer and hasattr(self.analyzer, 'fetcher'):
            underlying_value = self.analyzer.fetcher.underlying_value
            
        # Set up the figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the OI change
        ax.bar(df['strike'], df['ce_change_oi'], width=10, alpha=0.7, color='green', label='Call OI Change')
        ax.bar(df['strike'], df['pe_change_oi'], width=10, alpha=0.7, color='red', label='Put OI Change')
        
        # Add the current price line if we have it
        if underlying_value:
            ax.axvline(x=underlying_value, color='blue', linestyle='--', alpha=0.7, 
                      label=f'Current Price: {underlying_value}')
        
        # Format the plot
        index_name = self.analyzer.fetcher.index if self.analyzer and hasattr(self.analyzer, 'fetcher') else "Option Chain"
        expiry = self.analyzer.fetcher.selected_expiry if self.analyzer and hasattr(self.analyzer, 'fetcher') else ""
        
        ax.set_title(f'{index_name} OI Buildup Analysis - {expiry}')
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('Change in Open Interest')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Add a zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['oi_buildup'] = fig
        return fig
    
    def plot_pcr_chart(self, pcr_data, save_path=None, show_plot=False):
        """
        Plot PCR trend over time.
        
        Args:
            pcr_data (list): List of {timestamp, pcr} dictionaries
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if not pcr_data or len(pcr_data) < 2:
            print("Not enough PCR data points for visualization")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(pcr_data)
        
        # Convert timestamps to datetime if they're not already
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Set up the figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the PCR
        ax.plot(df['timestamp'], df['pcr'], marker='o', color='blue', linewidth=2)
        
        # Add threshold lines
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Neutral (PCR=1.0)')
        ax.axhline(y=0.8, color='green', linestyle=':', alpha=0.5, label='Bullish (PCR<0.8)')
        ax.axhline(y=1.2, color='red', linestyle=':', alpha=0.5, label='Bearish (PCR>1.2)')
        
        # Format the plot
        index_name = self.analyzer.fetcher.index if self.analyzer and hasattr(self.analyzer, 'fetcher') else "Option Chain"
        
        ax.set_title(f'{index_name} Put-Call Ratio Trend')
        ax.set_xlabel('Time')
        ax.set_ylabel('Put-Call Ratio')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Format x-axis as time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['pcr_trend'] = fig
        return fig
    
    def plot_iv_skew(self, df=None, save_path=None, show_plot=False):
        """
        Plot the implied volatility skew.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to visualize
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            print("No data available for visualization")
            return None
            
        # Get underlying value
        underlying_value = None
        if self.analyzer and hasattr(self.analyzer, 'fetcher'):
            underlying_value = self.analyzer.fetcher.underlying_value
            
        if not underlying_value:
            print("No underlying value available for IV skew analysis")
            return None
            
        # Calculate moneyness (% distance from ATM)
        df['moneyness'] = ((df['strike'] - underlying_value) / underlying_value) * 100
        
        # Set up the figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the IV skew
        ax.plot(df['moneyness'], df['ce_iv'], marker='o', color='green', alpha=0.7, label='Call IV')
        ax.plot(df['moneyness'], df['pe_iv'], marker='o', color='red', alpha=0.7, label='Put IV')
        
        # Add the ATM line
        ax.axvline(x=0, color='blue', linestyle='--', alpha=0.7, label='At-The-Money')
        
        # Format the plot
        index_name = self.analyzer.fetcher.index if self.analyzer and hasattr(self.analyzer, 'fetcher') else "Option Chain"
        expiry = self.analyzer.fetcher.selected_expiry if self.analyzer and hasattr(self.analyzer, 'fetcher') else ""
        
        ax.set_title(f'{index_name} IV Skew Analysis - {expiry}')
        ax.set_xlabel('Moneyness (% from ATM)')
        ax.set_ylabel('Implied Volatility (%)')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Set x-axis limits for better visualization
        ax.set_xlim(-20, 20)
        
        plt.tight_layout()
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['iv_skew'] = fig
        return fig
        
    def plot_support_resistance(self, df=None, key_levels=None, save_path=None, show_plot=False):
        """
        Plot support and resistance levels based on option OI.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame to visualize
            key_levels (dict, optional): Key levels from analyzer
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if df is None and self.analyzer and hasattr(self.analyzer, 'fetcher'):
            df = self.analyzer.fetcher.prepare_dataframe()
            
        if df is None or df.empty:
            print("No data available for visualization")
            return None
            
        # Get underlying value
        underlying_value = None
        if self.analyzer and hasattr(self.analyzer, 'fetcher'):
            underlying_value = self.analyzer.fetcher.underlying_value
            
        # Get key levels if not provided
        if key_levels is None and self.analyzer:
            key_levels = self.analyzer.identify_key_levels(df)
            
        if not key_levels:
            print("No key levels available for visualization")
            return None
            
        # Set up the figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the OI
        ax.bar(df['strike'], df['ce_oi'], width=10, alpha=0.5, color='green', label='Call OI')
        ax.bar(df['strike'], df['pe_oi'], width=10, alpha=0.5, color='red', label='Put OI')
        
        # Add the current price line if we have it
        if underlying_value:
            ax.axvline(x=underlying_value, color='blue', linestyle='--', alpha=0.7, 
                      label=f'Current Price: {underlying_value}')
        
        # Add support levels
        for i, level in enumerate(key_levels['put_support']):
            strike = level['strike']
            ax.axvline(x=strike, color='green', linestyle='-.', alpha=0.5 + (0.2 * (3-i)), 
                      label=f"Support: {strike}")
            
        # Add resistance levels
        for i, level in enumerate(key_levels['call_resistance']):
            strike = level['strike']
            ax.axvline(x=strike, color='red', linestyle='-.', alpha=0.5 + (0.2 * (3-i)), 
                      label=f"Resistance: {strike}")
        
        # Format the plot
        index_name = self.analyzer.fetcher.index if self.analyzer and hasattr(self.analyzer, 'fetcher') else "Option Chain"
        expiry = self.analyzer.fetcher.selected_expiry if self.analyzer and hasattr(self.analyzer, 'fetcher') else ""
        
        ax.set_title(f'{index_name} Support & Resistance Analysis - {expiry}')
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('Open Interest')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['support_resistance'] = fig
        return fig
        
    def create_dashboard(self, save_path=None, show_plot=False):
        """
        Create a comprehensive dashboard with multiple charts.
        
        Args:
            save_path (str, optional): Path to save the figure
            show_plot (bool): Whether to display the plot
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if not self.analyzer or not hasattr(self.analyzer, 'fetcher'):
            print("Analyzer with fetcher required for dashboard")
            return None
            
        # Get the data
        df = self.analyzer.fetcher.prepare_dataframe()
        if df is None or df.empty:
            print("No data available for dashboard")
            return None
            
        # Get analysis results
        analysis = self.analyzer.analyze_option_chain(df)
        if not analysis or "error" in analysis:
            print(f"Error in analysis: {analysis.get('error', 'Unknown error')}")
            return None
            
        # Create a figure with subplots
        fig = plt.figure(figsize=(16, 12))
        
        # Define grid layout
        gs = fig.add_gridspec(3, 2)
        
        # Add title to the figure
        index_name = self.analyzer.fetcher.index
        expiry = self.analyzer.fetcher.selected_expiry
        underlying = self.analyzer.fetcher.underlying_value
        pcr = analysis.get('pcr', 'N/A')
        max_pain = analysis.get('max_pain', 'N/A')
        
        fig.suptitle(f"{index_name} Option Chain Dashboard\n"
                    f"Expiry: {expiry} | LTP: {underlying} | PCR: {pcr} | Max Pain: {max_pain}",
                    fontsize=16)
        
        # 1. OI Distribution (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(df['strike'], df['ce_oi'], width=10, alpha=0.7, color='green', label='Call OI')
        ax1.bar(df['strike'], df['pe_oi'], width=10, alpha=0.7, color='red', label='Put OI')
        if underlying:
            ax1.axvline(x=underlying, color='blue', linestyle='--', alpha=0.7)
        if max_pain:
            ax1.axvline(x=max_pain, color='purple', linestyle='-.', alpha=0.7)
        ax1.set_title('Open Interest Distribution')
        ax1.set_xlabel('Strike Price')
        ax1.set_ylabel('Open Interest')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. OI Change (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(df['strike'], df['ce_change_oi'], width=10, alpha=0.7, color='green', label='Call OI Change')
        ax2.bar(df['strike'], df['pe_change_oi'], width=10, alpha=0.7, color='red', label='Put OI Change')
        if underlying:
            ax2.axvline(x=underlying, color='blue', linestyle='--', alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Open Interest Change')
        ax2.set_xlabel('Strike Price')
        ax2.set_ylabel('OI Change')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        # 3. IV Skew (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(df['strike'], df['ce_iv'], marker='o', color='green', alpha=0.7, label='Call IV')
        ax3.plot(df['strike'], df['pe_iv'], marker='o', color='red', alpha=0.7, label='Put IV')
        if underlying:
            ax3.axvline(x=underlying, color='blue', linestyle='--', alpha=0.7)
        ax3.set_title('Implied Volatility Skew')
        ax3.set_xlabel('Strike Price')
        ax3.set_ylabel('IV (%)')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # 4. Volume Distribution (middle right)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.bar(df['strike'], df['ce_volume'], width=10, alpha=0.7, color='green', label='Call Volume')
        ax4.bar(df['strike'], df['pe_volume'], width=10, alpha=0.7, color='red', label='Put Volume')
        if underlying:
            ax4.axvline(x=underlying, color='blue', linestyle='--', alpha=0.7)
        ax4.set_title('Trading Volume')
        ax4.set_xlabel('Strike Price')
        ax4.set_ylabel('Volume')
        ax4.legend()
        ax4.grid(alpha=0.3)
        
        # 5. Support & Resistance (bottom)
        ax5 = fig.add_subplot(gs[2, :])
        
        # Use OI difference to find resistance (positive) and support (negative)
        df['oi_diff'] = df['ce_oi'] - df['pe_oi']
        
        # Plot the OI difference
        bars = ax5.bar(df['strike'], df['oi_diff'], width=10, alpha=0.7, color='blue')
        
        # Color code bars: green for support (negative), red for resistance (positive)
        for i, bar in enumerate(bars):
            if df.iloc[i]['oi_diff'] < 0:
                bar.set_color('green')
            else:
                bar.set_color('red')
                
        if underlying:
            ax5.axvline(x=underlying, color='blue', linestyle='--', alpha=0.7, label='Current Price')
        ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax5.set_title('Support & Resistance (Call OI - Put OI)')
        ax5.set_xlabel('Strike Price')
        ax5.set_ylabel('OI Difference')
        ax5.legend()
        ax5.grid(alpha=0.3)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for the figure title
        
        # Save the figure if requested
        if save_path:
            plt.savefig(save_path)
            print(f"Dashboard saved to {save_path}")
        
        # Show the plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Store the figure for later use
        self.figures['dashboard'] = fig
        return fig