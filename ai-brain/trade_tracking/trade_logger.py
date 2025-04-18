"""
Trade Logging Module

This module handles trade logging, tracking, and performance analysis for Sambot.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict


class TradeLogger:
    """
    Comprehensive trade logging and performance tracking system.
    """
    
    def __init__(self, log_dir="trade_logs"):
        """
        Initialize the trade logger.
        
        Args:
            log_dir (str): Directory to store logs and reports
        """
        self.log_dir = log_dir
        self.trades_file = os.path.join(log_dir, "trades.json")
        self.performance_file = os.path.join(log_dir, "performance.json")
        self.stats_file = os.path.join(log_dir, "stats.json")
        self.trades = []
        self.performance = {}
        self.stats = {}
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Load existing data if available
        self._load_data()
        
    def _load_data(self):
        """Load existing log data if available."""
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    self.trades = json.load(f)
            
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    self.performance = json.load(f)
                    
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
                    
        except Exception as e:
            print(f"Error loading log data: {str(e)}")
            # Initialize with empty data
            self.trades = []
            self.performance = {}
            self.stats = {}
    
    def _save_data(self):
        """Save log data to files."""
        try:
            with open(self.trades_file, 'w') as f:
                json.dump(self.trades, f, indent=2)
                
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance, f, indent=2)
                
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
                
        except Exception as e:
            print(f"Error saving log data: {str(e)}")
    
    def log_trade(self, trade_data):
        """
        Log a new trade.
        
        Args:
            trade_data (dict): Trade details including:
                - index: Index symbol (NIFTY, BANKNIFTY, etc.)
                - signal: Trade signal (BUY CALL, BUY PUT, etc.)
                - entry_time: Entry timestamp
                - entry_price: Entry price
                - exit_time: Exit timestamp (if completed)
                - exit_price: Exit price (if completed)
                - quantity: Number of contracts
                - strike: Strike price
                - expiry: Option expiry date
                - status: Trade status (OPEN, CLOSED, CANCELLED)
                - pnl: Profit/Loss (if completed)
                - stop_loss: Stop loss level
                - target: Target level
                - psychology: Market psychology at entry (optional)
                - confidence: Trade confidence level
                
        Returns:
            str: Trade ID
        """
        # Generate a unique trade ID
        trade_id = f"TRADE_{len(self.trades) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Ensure required fields
        required_fields = ['index', 'signal', 'entry_time', 'entry_price', 'quantity', 'strike', 'expiry']
        for field in required_fields:
            if field not in trade_data:
                raise ValueError(f"Required field missing in trade data: {field}")
        
        # Add trade ID and tracking fields
        trade = {
            'trade_id': trade_id,
            'log_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': trade_data.get('status', 'OPEN'),
            **trade_data
        }
        
        # Calculate PnL if complete
        if 'exit_price' in trade_data and 'exit_time' in trade_data:
            if 'pnl' not in trade_data:
                # Calculate PnL based on direction
                direction = 1 if trade_data['signal'] == 'BUY CALL' else -1 if trade_data['signal'] == 'BUY PUT' else 0
                trade['pnl'] = direction * (trade_data['exit_price'] - trade_data['entry_price']) * trade_data['quantity']
                trade['status'] = 'CLOSED'
        
        # Add to trades list
        self.trades.append(trade)
        
        # Save updated data
        self._save_data()
        
        # Update performance metrics
        self.update_performance()
        
        return trade_id
    
    def update_trade(self, trade_id, update_data):
        """
        Update an existing trade.
        
        Args:
            trade_id (str): ID of the trade to update
            update_data (dict): Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        for i, trade in enumerate(self.trades):
            if trade['trade_id'] == trade_id:
                # Update fields
                self.trades[i].update(update_data)
                
                # If exiting the trade, update status and calculate PnL
                if 'exit_price' in update_data and 'exit_time' in update_data:
                    if self.trades[i]['status'] != 'CLOSED':
                        self.trades[i]['status'] = 'CLOSED'
                        
                        # Calculate PnL
                        direction = 1 if self.trades[i]['signal'] == 'BUY CALL' else -1 if self.trades[i]['signal'] == 'BUY PUT' else 0
                        self.trades[i]['pnl'] = direction * (self.trades[i]['exit_price'] - self.trades[i]['entry_price']) * self.trades[i]['quantity']
                
                # Save updated data
                self._save_data()
                
                # Update performance metrics
                self.update_performance()
                
                return True
        
        print(f"Trade ID not found: {trade_id}")
        return False
    
    def get_trade(self, trade_id):
        """
        Get details of a specific trade.
        
        Args:
            trade_id (str): ID of the trade
            
        Returns:
            dict: Trade details or None if not found
        """
        for trade in self.trades:
            if trade['trade_id'] == trade_id:
                return trade
        
        return None
    
    def get_open_trades(self):
        """
        Get all open trades.
        
        Returns:
            list: List of open trades
        """
        return [trade for trade in self.trades if trade['status'] == 'OPEN']
    
    def get_trades_by_index(self, index):
        """
        Get all trades for a specific index.
        
        Args:
            index (str): Index symbol (NIFTY, BANKNIFTY, etc.)
            
        Returns:
            list: List of trades for the index
        """
        return [trade for trade in self.trades if trade['index'] == index]
    
    def get_trades_by_date_range(self, start_date, end_date=None):
        """
        Get trades within a date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format. If None, uses today.
            
        Returns:
            list: List of trades in the date range
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end date
        
        return [
            trade for trade in self.trades 
            if datetime.strptime(trade['entry_time'].split()[0], '%Y-%m-%d') >= start
            and datetime.strptime(trade['entry_time'].split()[0], '%Y-%m-%d') < end
        ]
    
    def update_performance(self):
        """
        Update performance metrics based on all trades.
        """
        if not self.trades:
            self.performance = {
                'total_trades': 0,
                'win_rate': 0,
                'win_loss_ratio': 0,
                'total_pnl': 0,
                'avg_pnl_per_trade': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self._save_data()
            return
        
        # Get all closed trades
        closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']
        
        if not closed_trades:
            self.performance = {
                'total_trades': 0,
                'closed_trades': 0,
                'open_trades': len(self.trades),
                'win_rate': 0,
                'win_loss_ratio': 0,
                'total_pnl': 0,
                'avg_pnl_per_trade': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self._save_data()
            return
        
        # Calculate basic metrics
        total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]
        
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        win_loss_ratio = len(winning_trades) / len(losing_trades) if losing_trades else float('inf')
        avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0
        
        # Calculate max drawdown
        if len(closed_trades) > 1:
            # Sort trades by exit time
            sorted_trades = sorted(closed_trades, key=lambda x: x.get('exit_time', x.get('entry_time')))
            
            # Calculate cumulative PnL
            cumulative_pnl = []
            current_pnl = 0
            for trade in sorted_trades:
                current_pnl += trade.get('pnl', 0)
                cumulative_pnl.append(current_pnl)
            
            # Calculate max drawdown
            peak = cumulative_pnl[0]
            max_drawdown = 0
            
            for pnl in cumulative_pnl:
                if pnl > peak:
                    peak = pnl
                drawdown = peak - pnl
                max_drawdown = max(max_drawdown, drawdown)
        else:
            max_drawdown = 0
        
        # Calculate daily returns for Sharpe ratio
        if len(closed_trades) > 5:
            # Group trades by day
            trades_by_day = defaultdict(list)
            for trade in closed_trades:
                exit_day = trade.get('exit_time', trade.get('entry_time')).split()[0]
                trades_by_day[exit_day].append(trade.get('pnl', 0))
            
            # Calculate daily returns
            daily_returns = [sum(pnls) for day, pnls in trades_by_day.items()]
            
            # Calculate Sharpe ratio (simplified)
            if len(daily_returns) > 1:
                avg_return = np.mean(daily_returns)
                std_return = np.std(daily_returns)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Create performance data
        self.performance = {
            'total_trades': len(self.trades),
            'closed_trades': len(closed_trades),
            'open_trades': len(self.trades) - len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'win_loss_ratio': win_loss_ratio,
            'total_pnl': total_pnl,
            'avg_pnl_per_trade': avg_pnl,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Calculate performance by index
        indices = set(t['index'] for t in self.trades)
        index_performance = {}
        
        for index in indices:
            index_trades = [t for t in closed_trades if t['index'] == index]
            if not index_trades:
                continue
                
            index_pnl = sum(t.get('pnl', 0) for t in index_trades)
            index_winners = len([t for t in index_trades if t.get('pnl', 0) > 0])
            
            index_performance[index] = {
                'trades': len(index_trades),
                'win_rate': index_winners / len(index_trades) if index_trades else 0,
                'total_pnl': index_pnl,
                'avg_pnl': index_pnl / len(index_trades) if index_trades else 0
            }
            
        self.performance['by_index'] = index_performance
        
        # Calculate performance by signal type
        signal_types = set(t['signal'] for t in self.trades)
        signal_performance = {}
        
        for signal in signal_types:
            signal_trades = [t for t in closed_trades if t['signal'] == signal]
            if not signal_trades:
                continue
                
            signal_pnl = sum(t.get('pnl', 0) for t in signal_trades)
            signal_winners = len([t for t in signal_trades if t.get('pnl', 0) > 0])
            
            signal_performance[signal] = {
                'trades': len(signal_trades),
                'win_rate': signal_winners / len(signal_trades) if signal_trades else 0,
                'total_pnl': signal_pnl,
                'avg_pnl': signal_pnl / len(signal_trades) if signal_trades else 0
            }
            
        self.performance['by_signal'] = signal_performance
        
        # Calculate monthly performance
        monthly_performance = {}
        
        for trade in closed_trades:
            exit_month = trade.get('exit_time', trade.get('entry_time')).split()[0][:7]  # YYYY-MM
            if exit_month not in monthly_performance:
                monthly_performance[exit_month] = {
                    'trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'pnl': 0
                }
                
            monthly_performance[exit_month]['trades'] += 1
            monthly_performance[exit_month]['pnl'] += trade.get('pnl', 0)
            
            if trade.get('pnl', 0) > 0:
                monthly_performance[exit_month]['wins'] += 1
            elif trade.get('pnl', 0) < 0:
                monthly_performance[exit_month]['losses'] += 1
                
        self.performance['by_month'] = monthly_performance
        
        # Save updated performance data
        self._save_data()
        
        # Update statistics
        self._update_stats()
    
    def _update_stats(self):
        """
        Update trading statistics for analysis.
        """
        closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']
        
        if not closed_trades:
            self.stats = {}
            self._save_data()
            return
        
        # Winning streak analysis
        trades_by_date = sorted(closed_trades, key=lambda x: x.get('exit_time', x.get('entry_time')))
        
        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        current_is_win = None
        
        for trade in trades_by_date:
            is_win = trade.get('pnl', 0) > 0
            
            if current_is_win is None:
                current_is_win = is_win
                current_streak = 1
            elif current_is_win == is_win:
                current_streak += 1
            else:
                if current_is_win:
                    max_win_streak = max(max_win_streak, current_streak)
                else:
                    max_loss_streak = max(max_loss_streak, current_streak)
                    
                current_is_win = is_win
                current_streak = 1
                
        # Check final streak
        if current_is_win is not None:
            if current_is_win:
                max_win_streak = max(max_win_streak, current_streak)
            else:
                max_loss_streak = max(max_loss_streak, current_streak)
        
        # Time of day analysis
        hour_performance = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        
        for trade in closed_trades:
            hour = int(trade.get('entry_time').split()[1].split(':')[0])
            
            hour_performance[hour]['trades'] += 1
            hour_performance[hour]['pnl'] += trade.get('pnl', 0)
            
            if trade.get('pnl', 0) > 0:
                hour_performance[hour]['wins'] += 1
                
        # Convert to regular dict with win rates
        hour_stats = {}
        for hour, data in hour_performance.items():
            hour_stats[str(hour)] = {
                'trades': data['trades'],
                'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0,
                'pnl': data['pnl']
            }
        
        # Average hold time
        hold_times = []
        
        for trade in closed_trades:
            if 'entry_time' in trade and 'exit_time' in trade:
                try:
                    entry = datetime.strptime(trade['entry_time'], '%Y-%m-%d %H:%M:%S')
                    exit = datetime.strptime(trade['exit_time'], '%Y-%m-%d %H:%M:%S')
                    hold_time = (exit - entry).total_seconds() / 60  # Minutes
                    hold_times.append(hold_time)
                except:
                    pass
        
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0
        
        # Psychology correlation if available
        psych_correlation = {}
        
        trades_with_psych = [t for t in closed_trades if 'psychology' in t]
        if trades_with_psych:
            fear_greed_win_rate = []
            sentiment_performance = defaultdict(lambda: {'trades': 0, 'wins': 0})
            
            for trade in trades_with_psych:
                # Fear & Greed correlation
                if 'fear_greed_score' in trade['psychology']:
                    score = trade['psychology']['fear_greed_score']
                    is_win = trade.get('pnl', 0) > 0
                    fear_greed_win_rate.append((score, 1 if is_win else 0))
                
                # Sentiment correlation
                if 'sentiment' in trade['psychology']:
                    sentiment = trade['psychology']['sentiment']
                    sentiment_performance[sentiment]['trades'] += 1
                    if trade.get('pnl', 0) > 0:
                        sentiment_performance[sentiment]['wins'] += 1
            
            # Calculate sentiment win rates
            for sentiment, data in sentiment_performance.items():
                psych_correlation[sentiment] = {
                    'trades': data['trades'],
                    'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0
                }
        
        # Compile stats
        self.stats = {
            'max_win_streak': max_win_streak,
            'max_loss_streak': max_loss_streak,
            'hour_performance': hour_stats,
            'avg_hold_time_minutes': avg_hold_time,
            'psychology_correlation': psych_correlation,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self._save_data()
    
    def get_performance(self):
        """
        Get the latest performance metrics.
        
        Returns:
            dict: Performance metrics
        """
        return self.performance
    
    def get_stats(self):
        """
        Get the latest statistics.
        
        Returns:
            dict: Trading statistics
        """
        return self.stats
    
    def generate_report(self, report_type='summary', start_date=None, end_date=None, index=None):
        """
        Generate a performance report.
        
        Args:
            report_type (str): Type of report ('summary', 'detailed', 'monthly', 'by_index')
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            index (str, optional): Filter by index
            
        Returns:
            dict: Report data
        """
        if report_type == 'summary':
            return {
                'type': 'summary',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'performance': self.performance,
                'stats': self.stats
            }
        
        elif report_type == 'detailed':
            # Filter trades by date range and index if provided
            filtered_trades = self.trades
            
            if start_date:
                if end_date is None:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    
                filtered_trades = self.get_trades_by_date_range(start_date, end_date)
            
            if index:
                filtered_trades = [t for t in filtered_trades if t['index'] == index]
            
            # Calculate performance for filtered trades
            if not filtered_trades:
                return {
                    'type': 'detailed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'index': index,
                    'trades': 0,
                    'message': 'No trades found matching the criteria'
                }
            
            closed_trades = [t for t in filtered_trades if t['status'] == 'CLOSED']
            
            if not closed_trades:
                return {
                    'type': 'detailed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'index': index,
                    'trades': len(filtered_trades),
                    'closed_trades': 0,
                    'message': 'No closed trades found matching the criteria'
                }
            
            total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
            winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
            
            return {
                'type': 'detailed',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'start_date': start_date,
                'end_date': end_date,
                'index': index,
                'trades': len(filtered_trades),
                'closed_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'win_rate': len(winning_trades) / len(closed_trades) if closed_trades else 0,
                'total_pnl': total_pnl,
                'avg_pnl': total_pnl / len(closed_trades) if closed_trades else 0,
                'trade_list': [
                    {
                        'trade_id': t['trade_id'],
                        'index': t['index'],
                        'signal': t['signal'],
                        'entry_time': t['entry_time'],
                        'exit_time': t.get('exit_time', 'Open'),
                        'pnl': t.get('pnl', 'Open'),
                        'status': t['status']
                    }
                    for t in filtered_trades
                ]
            }
            
        elif report_type == 'monthly':
            if not self.performance or 'by_month' not in self.performance:
                return {
                    'type': 'monthly',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': 'No monthly data available'
                }
                
            monthly_data = self.performance['by_month']
            
            # Add win rates
            monthly_report = {}
            for month, data in monthly_data.items():
                monthly_report[month] = {
                    **data,
                    'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0
                }
                
            return {
                'type': 'monthly',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'monthly_performance': monthly_report
            }
            
        elif report_type == 'by_index':
            if not self.performance or 'by_index' not in self.performance:
                return {
                    'type': 'by_index',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': 'No index data available'
                }
                
            return {
                'type': 'by_index',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'index_performance': self.performance['by_index']
            }
            
        else:
            return {
                'error': f"Unknown report type: {report_type}",
                'available_types': ['summary', 'detailed', 'monthly', 'by_index']
            }
    
    def plot_performance(self, plot_type='equity_curve', start_date=None, end_date=None, save_path=None):
        """
        Generate performance visualization.
        
        Args:
            plot_type (str): Type of plot ('equity_curve', 'win_loss', 'monthly', 'hourly')
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            save_path (str, optional): Path to save the plot
            
        Returns:
            matplotlib.figure.Figure: The generated plot
        """
        # Set up plot style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("deep")
        
        # Filter trades by date range if provided
        filtered_trades = self.trades
        
        if start_date:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            filtered_trades = self.get_trades_by_date_range(start_date, end_date)
        
        closed_trades = [t for t in filtered_trades if t['status'] == 'CLOSED']
        
        if not closed_trades:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No closed trades in the selected period", 
                   ha='center', va='center', fontsize=14)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
                
            return fig
        
        if plot_type == 'equity_curve':
            # Sort trades by exit time
            sorted_trades = sorted(closed_trades, 
                                  key=lambda x: datetime.strptime(x.get('exit_time', x.get('entry_time')), '%Y-%m-%d %H:%M:%S'))
            
            # Calculate cumulative PnL
            dates = []
            cumulative_pnl = []
            current_pnl = 0
            
            for trade in sorted_trades:
                exit_time = datetime.strptime(trade.get('exit_time', trade.get('entry_time')), '%Y-%m-%d %H:%M:%S')
                current_pnl += trade.get('pnl', 0)
                
                dates.append(exit_time)
                cumulative_pnl.append(current_pnl)
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 7))
            
            ax.plot(dates, cumulative_pnl, marker='o', linestyle='-', markersize=4, linewidth=2)
            
            # Add zero line
            ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
            
            # Format the plot
            ax.set_title('Equity Curve', fontsize=16)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Cumulative P&L', fontsize=12)
            
            # Highlight the starting and ending values
            if len(cumulative_pnl) > 1:
                # Start point
                ax.scatter(dates[0], cumulative_pnl[0], color='green', s=100, zorder=5)
                ax.text(dates[0], cumulative_pnl[0], f" Start", va='center')
                
                # End point
                ax.scatter(dates[-1], cumulative_pnl[-1], color='blue', s=100, zorder=5)
                ax.text(dates[-1], cumulative_pnl[-1], f" End: {cumulative_pnl[-1]:.2f}", va='center')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        elif plot_type == 'win_loss':
            # Count trades by result
            winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
            losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]
            breakeven_trades = [t for t in closed_trades if t.get('pnl', 0) == 0]
            
            # Count trades by signal type
            signal_counts = {}
            
            for trade in closed_trades:
                signal = trade['signal']
                result = 'win' if trade.get('pnl', 0) > 0 else 'loss' if trade.get('pnl', 0) < 0 else 'breakeven'
                
                if signal not in signal_counts:
                    signal_counts[signal] = {'win': 0, 'loss': 0, 'breakeven': 0}
                    
                signal_counts[signal][result] += 1
            
            # Create plots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
            
            # Overall win/loss pie chart
            labels = ['Winning', 'Losing', 'Breakeven']
            sizes = [len(winning_trades), len(losing_trades), len(breakeven_trades)]
            colors = ['#4CAF50', '#F44336', '#9E9E9E']
            
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=False)
            ax1.axis('equal')
            ax1.set_title('Trade Outcomes', fontsize=14)
            
            # Signal type performance
            signals = list(signal_counts.keys())
            win_counts = [signal_counts[s]['win'] for s in signals]
            loss_counts = [signal_counts[s]['loss'] for s in signals]
            
            x = np.arange(len(signals))
            width = 0.35
            
            ax2.bar(x - width/2, win_counts, width, label='Wins', color='#4CAF50')
            ax2.bar(x + width/2, loss_counts, width, label='Losses', color='#F44336')
            
            ax2.set_xticks(x)
            ax2.set_xticklabels(signals)
            ax2.set_title('Performance by Signal Type', fontsize=14)
            ax2.legend()
            
            plt.tight_layout()
            
        elif plot_type == 'monthly':
            if not self.performance or 'by_month' not in self.performance:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, "No monthly data available", 
                       ha='center', va='center', fontsize=14)
                
                if save_path:
                    plt.savefig(save_path, bbox_inches='tight')
                    
                return fig
            
            monthly_data = self.performance['by_month']
            months = sorted(list(monthly_data.keys()))
            pnl_values = [monthly_data[m]['pnl'] for m in months]
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Bar chart of monthly PnL
            bars = ax.bar(months, pnl_values, color=['green' if p > 0 else 'red' for p in pnl_values])
            
            # Add value labels on the bars
            for bar in bars:
                height = bar.get_height()
                label_pos = height + 10 if height > 0 else height - 10
                alignment = 'bottom' if height > 0 else 'top'
                ax.text(bar.get_x() + bar.get_width()/2., label_pos,
                        f'{height:.0f}',
                        ha='center', va=alignment)
            
            # Add trade count as text
            for i, month in enumerate(months):
                counts = monthly_data[month]['trades']
                ax.text(i, 0, f"{counts} trades", ha='center', va='center', rotation=90, alpha=0.7)
            
            ax.set_title('Monthly P&L Performance', fontsize=16)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('P&L', fontsize=12)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        elif plot_type == 'hourly':
            if not self.stats or 'hour_performance' not in self.stats:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, "No hourly data available", 
                       ha='center', va='center', fontsize=14)
                
                if save_path:
                    plt.savefig(save_path, bbox_inches='tight')
                    
                return fig
            
            hour_data = self.stats['hour_performance']
            hours = sorted([int(h) for h in hour_data.keys()])
            
            pnl_values = [hour_data[str(h)]['pnl'] for h in hours]
            win_rates = [hour_data[str(h)]['win_rate'] * 100 for h in hours]
            
            fig, ax1 = plt.subplots(figsize=(12, 7))
            
            # Bar chart for PnL
            bars = ax1.bar(hours, pnl_values, color=['green' if p > 0 else 'red' for p in pnl_values], alpha=0.7)
            
            # Add win rate as line on secondary y-axis
            ax2 = ax1.twinx()
            ax2.plot(hours, win_rates, marker='o', linestyle='-', color='blue', linewidth=2)
            
            ax1.set_title('Performance by Hour of Day', fontsize=16)
            ax1.set_xlabel('Hour', fontsize=12)
            ax1.set_ylabel('P&L', fontsize=12)
            ax2.set_ylabel('Win Rate %', fontsize=12)
            
            # Set x-ticks to show all hours
            ax1.set_xticks(hours)
            
            # Add legend
            ax1.legend(['P&L'], loc='upper left')
            ax2.legend(['Win Rate'], loc='upper right')
            
            plt.tight_layout()
        
        # Save the plot if requested
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            
        return fig