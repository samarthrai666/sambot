"""
NSE Option Chain Manager

This is the main module that integrates all the components:
- Fetcher for data retrieval
- Analyzer for calculations and metrics
- Visualizer for charts and graphical representation
- Strategies for recommendations
- Signals for trading signals
- Psychological Analysis for market sentiment
"""

import os
import json
from datetime import datetime
from .fetcher import OptionChainFetcher
from .analyzer import OptionChainAnalyzer
from .visualizer import OptionChainVisualizer
from .strategies import StrategyRecommender
from .signals import SignalGenerator
from .psychological_analysis import MarketPsychologyAnalyzer


class OptionChainManager:
    """
    Main class for managing option chain analysis.
    
    This class integrates all the components and provides a simplified
    interface for working with option chain data.
    """
    
    def __init__(self, index="NIFTY", output_dir="option_charts"):
        """
        Initialize the option chain manager.
        
        Args:
            index (str): Index to analyze (NIFTY, BANKNIFTY, etc.)
            output_dir (str): Directory for saving charts and reports
        """
        self.fetcher = OptionChainFetcher(index)
        self.analyzer = OptionChainAnalyzer(self.fetcher)
        self.visualizer = OptionChainVisualizer(self.analyzer)
        self.strategy = StrategyRecommender(self.analyzer)
        self.signals = SignalGenerator(self.analyzer)
        self.psychology = MarketPsychologyAnalyzer(self.analyzer)
        
        self.output_dir = output_dir
        self.analysis_results = None
        self.history = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def set_index(self, index):
        """
        Change the index being analyzed.
        
        Args:
            index (str): New index to analyze
        """
        self.fetcher = OptionChainFetcher(index)
        self.analyzer.set_fetcher(self.fetcher)
        self.visualizer.set_analyzer(self.analyzer)
        self.strategy.set_analyzer(self.analyzer)
        self.signals.set_analyzer(self.analyzer)
        self.psychology.set_analyzer(self.analyzer)
        
    def fetch_data(self, expiry=None):
        """
        Fetch option chain data.
        
        Args:
            expiry (str, optional): Specific expiry date to fetch
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.fetcher.fetch_option_chain(expiry)
        
    def analyze(self):
        """
        Perform comprehensive analysis on the option chain data.
        
        Returns:
            dict: Analysis results
        """
        df = self.fetcher.prepare_dataframe()
        if df is None or df.empty:
            return {"error": "No data available for analysis"}
            
        # Perform the analysis
        self.analysis_results = self.analyzer.analyze_option_chain(df)
        
        # Add to history
        self.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'index': self.fetcher.index,
            'underlying': self.fetcher.underlying_value,
            'pcr': self.analysis_results.get('pcr'),
            'max_pain': self.analysis_results.get('max_pain')
        })
        
        return self.analysis_results
        
    def get_trading_signals(self):
        """
        Get trading signals based on option chain analysis.
        
        Returns:
            dict: Trading signals
        """
        return self.signals.get_intraday_signals()
        
    def get_trade_suggestions(self):
        """
        Get detailed trade suggestions including position sizing.
        
        Returns:
            dict: Trade suggestions
        """
        return self.signals.get_position_suggestions()
        
    def get_strategy_recommendations(self, market_view=None):
        """
        Get strategy recommendations based on market view.
        
        Args:
            market_view (str, optional): Market outlook - bullish, bearish, neutral, volatile
            
        Returns:
            dict: Strategy recommendations
        """
        return self.strategy.get_strategy_recommendation(market_view)
        
    def create_dashboard(self, save=True, show=False):
        """
        Create a comprehensive visual dashboard.
        
        Args:
            save (bool): Whether to save the dashboard
            show (bool): Whether to display the dashboard
            
        Returns:
            matplotlib.figure.Figure: The dashboard figure
        """
        save_path = None
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"{self.fetcher.index}_dashboard_{timestamp}.png")
            
        return self.visualizer.create_dashboard(save_path, show)
        
    def generate_report(self, include_signals=True, include_strategies=True, include_psychology=True, include_visualizations=True):
        """
        Generate a comprehensive report with analysis results.
        
        Args:
            include_signals (bool): Include trading signals
            include_strategies (bool): Include strategy recommendations
            include_psychology (bool): Include psychological analysis
            include_visualizations (bool): Include visualizations
            
        Returns:
            dict: Complete report
        """
        if not self.analysis_results:
            self.analyze()
            
        if not self.analysis_results or "error" in self.analysis_results:
            return {"error": f"Analysis failed: {self.analysis_results.get('error', 'Unknown error')}"}
            
        report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'index': self.fetcher.index,
            'expiry': self.fetcher.selected_expiry,
            'underlying_value': self.fetcher.underlying_value,
            'analysis': self.analysis_results
        }
        
        # Add trading signals if requested
        if include_signals:
            report['signals'] = self.get_trading_signals()
            report['trade_suggestions'] = self.get_trade_suggestions()
            
        # Add strategy recommendations if requested
        if include_strategies:
            report['strategy_recommendations'] = self.get_strategy_recommendations()
            
        # Add psychological analysis if requested
        if include_psychology:
            report['psychology'] = self.run_psychological_analysis()
            
        # Generate visualizations if requested
        if include_visualizations:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate and save visualization files
            visualization_files = {}
            
            # Main option chain visualization
            chart_path = os.path.join(self.output_dir, f"{self.fetcher.index}_option_chain_{timestamp}.png")
            self.visualizer.plot_option_chain(save_path=chart_path)
            visualization_files['option_chain'] = chart_path
            
            # OI buildup visualization
            buildup_path = os.path.join(self.output_dir, f"{self.fetcher.index}_oi_buildup_{timestamp}.png")
            self.visualizer.plot_oi_buildup(save_path=buildup_path)
            visualization_files['oi_buildup'] = buildup_path
            
            # Dashboard with all charts
            dashboard_path = os.path.join(self.output_dir, f"{self.fetcher.index}_dashboard_{timestamp}.png")
            self.visualizer.create_dashboard(save_path=dashboard_path)
            visualization_files['dashboard'] = dashboard_path
            
            report['visualization_files'] = visualization_files
            
        # Save report to JSON file
        report_filename = f"{self.fetcher.index}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        report['report_file'] = report_path
        
        return report
        
    def save_history(self, filename=None):
        """
        Save analysis history to a file.
        
        Args:
            filename (str, optional): Custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            filename = f"option_chain_history_{datetime.now().strftime('%Y%m%d')}.json"
            
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(self.history, f, indent=2)
            
        return file_path
        
    def get_pcr_history(self):
        """
        Get PCR history for plotting trends.
        
        Returns:
            list: List of PCR history data points
        """
        return [{'timestamp': item['timestamp'], 'pcr': item['pcr']} for item in self.history if 'pcr' in item]
    
    def run_psychological_analysis(self):
        """
        Perform psychological analysis of market sentiment based on option data.
        
        Returns:
            dict: Psychological analysis results
        """
        if not self.analysis_results:
            self.analyze()
            
        if not self.analysis_results or "error" in self.analysis_results:
            return {"error": "Analysis must be run before psychological analysis"}
            
        # Run the comprehensive psychological analysis
        psych_analysis = self.psychology.analyze_market_psychology(self.analysis_results)
        
        # Add volume profile analysis
        volume_profile = self.psychology.analyze_volume_profile(self.analysis_results)
        if "error" not in volume_profile:
            psych_analysis["volume_profile"] = volume_profile
            
        return psych_analysis
        
    def example_usage(self):
        """
        Show example usage of the OptionChainManager.
        
        Returns:
            str: Example usage text
        """
        return """
# Example usage of OptionChainManager

# Initialize manager for NIFTY
manager = OptionChainManager(index="NIFTY")

# Fetch the latest data
if manager.fetch_data():
    # Analyze the data
    analysis = manager.analyze()
    
    # Get trading signals
    signals = manager.get_trading_signals()
    
    # Get psychological analysis
    psych_analysis = manager.run_psychological_analysis()
    
    # Get strategy recommendations
    strategies = manager.get_strategy_recommendations(market_view="bullish")
    
    # Create a visual dashboard
    manager.create_dashboard(save=True)
    
    # Generate a comprehensive report
    report = manager.generate_report()
        """