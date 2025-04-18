"""
Performance Tracking and Metrics Calculation Module

This module calculates advanced trading metrics from trade logs.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict


class PerformanceTracker:
    """
    Advanced performance metrics and analysis for trading.
    """
    
    def __init__(self, trade_logger):
        """
        Initialize the performance tracker.
        
        Args:
            trade_logger (TradeLogger): Instance of the trade logger
        """
        self.trade_logger = trade_logger
        
    def calculate_metrics(self, start_date=None, end_date=None, index=None):
        """
        Calculate comprehensive trading metrics.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            index (str, optional): Filter by index
            
        Returns:
            dict: Comprehensive metrics
        """
        # Get filtered trades
        trades = self.trade_logger.trades
        
        if start_date:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            trades = self.trade_logger.get_trades_by_date_range(start_date, end_date)
        
        if index:
            trades = [t for t in trades if t['index'] == index]
            
        closed_trades = [t for t in trades if t['status'] == 'CLOSED']
        
        if not closed_trades:
            return {
                'error': 'No closed trades found for the specified filters',
                'start_date': start_date,
                'end_date': end_date,
                'index': index
            }
            
        # Extract PnL data
        pnl_values = [t.get('pnl', 0) for t in closed_trades]
        
        # Basic metrics
        total_pnl = sum(pnl_values)
        avg_pnl = total_pnl / len(pnl_values)
        
        # Winning metrics
        winning_trades = [p for p in pnl_values if p > 0]
        losing_trades = [p for p in pnl_values if p < 0]
        breakeven_trades = [p for p in pnl_values if p == 0]
        
        win_rate = len(winning_trades) / len(pnl_values) if pnl_values else 0
        profit_factor = sum(winning_trades) / abs(sum(losing_trades)) if sum(losing_trades) != 0 else float('inf')
        
        # Average win/loss and ratio
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0
        win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float('inf')
        
        # Advanced metrics
        if len(pnl_values) > 1:
            # Volatility and related metrics
            std_dev = np.std(pnl_values)
            
            # If we have dates, calculate annualized metrics
            has_dates = all('exit_time' in t for t in closed_trades)
            annualized_return = None
            sharpe_ratio = None
            sortino_ratio = None
            
            if has_dates:
                try:
                    # Sort trades by exit time
                    sorted_trades = sorted(closed_trades, 
                                         key=lambda x: datetime.strptime(x['exit_time'], '%Y-%m-%d %H:%M:%S'))
                    
                    first_date = datetime.strptime(sorted_trades[0]['exit_time'], '%Y-%m-%d %H:%M:%S')
                    last_date = datetime.strptime(sorted_trades[-1]['exit_time'], '%Y-%m-%d %H:%M:%S')
                    
                    # Calculate trading days
                    days = (last_date - first_date).days
                    trading_days = max(1, days * 5/7)  # Approximate trading days
                    
                    # Calculate annualized return
                    annualized_return = (total_pnl / trading_days) * 252  # Annualized assuming 252 trading days
                    
                    # Calculate daily returns for risk metrics
                    daily_returns = []
                    current_day = None
                    day_pnl = 0
                    
                    for trade in sorted_trades:
                        exit_day = datetime.strptime(trade['exit_time'], '%Y-%m-%d %H:%M:%S').date()
                        
                        if current_day is None:
                            current_day = exit_day
                            day_pnl = trade.get('pnl', 0)
                        elif exit_day == current_day:
                            day_pnl += trade.get('pnl', 0)
                        else:
                            daily_returns.append(day_pnl)
                            current_day = exit_day
                            day_pnl = trade.get('pnl', 0)
                    
                    # Add the last day
                    if day_pnl != 0:
                        daily_returns.append(day_pnl)
                    
                    # Calculate Sharpe and Sortino ratios
                    if len(daily_returns) > 1:
                        avg_daily_return = np.mean(daily_returns)
                        std_daily_return = np.std(daily_returns)
                        
                        # Sharpe Ratio (assuming 0% risk-free rate for simplicity)
                        sharpe_ratio = (avg_daily_return / std_daily_return) * np.sqrt(252) if std_daily_return > 0 else None
                        
                        # Sortino Ratio (downside deviation)
                        downside_returns = [r for r in daily_returns if r < 0]
                        downside_deviation = np.std(downside_returns) if downside_returns else 0
                        sortino_ratio = (avg_daily_return / downside_deviation) * np.sqrt(252) if downside_deviation > 0 else None
                            
                except Exception as e:
                    print(f"Error calculating time-based metrics: {str(e)}")
            
            # Maximum drawdown calculation
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
            underwater_periods = []
            current_underwater = False
            underwater_start = 0
            
            for i, pnl in enumerate(cumulative_pnl):
                if pnl > peak:
                    peak = pnl
                    
                    if current_underwater:
                        underwater_end = i - 1
                        underwater_periods.append((underwater_start, underwater_end))
                        current_underwater = False
                        
                drawdown = peak - pnl
                max_drawdown = max(max_drawdown, drawdown)
                
                if drawdown > 0 and not current_underwater:
                    current_underwater = True
                    underwater_start = i
            
            # Check if still underwater at the end
            if current_underwater:
                underwater_periods.append((underwater_start, len(cumulative_pnl) - 1))
                
            # Calculate longest underwater period
            longest_underwater = max([(end - start + 1) for start, end in underwater_periods]) if underwater_periods else 0
            
            # Calculate recovery factor
            recovery_factor = total_pnl / max_drawdown if max_drawdown > 0 else float('inf')
            
            # Compile advanced metrics
            advanced_metrics = {
                'std_deviation': std_dev,
                'max_drawdown': max_drawdown,
                'recovery_factor': recovery_factor,
                'longest_underwater_period': longest_underwater
            }
            
            # Add time-based metrics if available
            if annualized_return is not None:
                advanced_metrics['annualized_return'] = annualized_return
            
            if sharpe_ratio is not None:
                advanced_metrics['sharpe_ratio'] = sharpe_ratio
                
            if sortino_ratio is not None:
                advanced_metrics['sortino_ratio'] = sortino_ratio
                
        else:
            # Not enough trades for advanced metrics
            advanced_metrics = {
                'std_deviation': 0,
                'max_drawdown': 0,
                'recovery_factor': 0,
                'longest_underwater_period': 0
            }
        
        # Consistency metrics
        if len(closed_trades) > 5:
            # Analyze win/loss distribution by date
            trades_by_date = defaultdict(lambda: {'wins': 0, 'losses': 0})
            
            for trade in closed_trades:
                date = trade.get('exit_time', trade.get('entry_time')).split()[0]
                if trade.get('pnl', 0) > 0:
                    trades_by_date[date]['wins'] += 1
                elif trade.get('pnl', 0) < 0:
                    trades_by_date[date]['losses'] += 1
            
            # Calculate win rate by day
            daily_win_rates = []
            
            for date, counts in trades_by_date.items():
                if counts['wins'] + counts['losses'] > 0:
                    win_rate = counts['wins'] / (counts['wins'] + counts['losses'])
                    daily_win_rates.append(win_rate)
            
            # Consistency of win rates
            win_rate_consistency = 1 - np.std(daily_win_rates) if daily_win_rates else 0
            
            consistency_metrics = {
                'win_rate_consistency': win_rate_consistency,
                'daily_win_rates': {
                    'mean': np.mean(daily_win_rates) if daily_win_rates else 0,
                    'median': np.median(daily_win_rates) if daily_win_rates else 0,
                    'std': np.std(daily_win_rates) if daily_win_rates else 0
                }
            }
        else:
            consistency_metrics = {
                'win_rate_consistency': 0,
                'daily_win_rates': {
                    'mean': 0,
                    'median': 0,
                    'std': 0
                }
            }
        
        # Combine all metrics
        return {
            'basic_metrics': {
                'total_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'breakeven_trades': len(breakeven_trades),
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_pnl': total_pnl,
                'avg_pnl_per_trade': avg_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'win_loss_ratio': win_loss_ratio
            },
            'advanced_metrics': advanced_metrics,
            'consistency_metrics': consistency_metrics
        }
    
    def analyze_trade_psychology(self, trades=None):
        """
        Analyze how psychological factors affected trade outcomes.
        
        Args:
            trades (list, optional): List of trades to analyze or None to use all trades
            
        Returns:
            dict: Psychological analysis
        """
        if trades is None:
            trades = self.trade_logger.trades
            
        # Filter for closed trades with psychology data
        trades = [t for t in trades if t['status'] == 'CLOSED' and 'psychology' in t]
        
        if not trades:
            return {
                'error': 'No trades with psychological data found'
            }
            
        # Extract psychological factors
        fear_greed_analysis = []
        sentiment_analysis = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        contrarian_analysis = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        
        for trade in trades:
            psych = trade['psychology']
            pnl = trade.get('pnl', 0)
            is_win = pnl > 0
            
            # Fear & Greed analysis
            if 'fear_greed_score' in psych:
                fear_greed_analysis.append({
                    'score': psych['fear_greed_score'],
                    'result': 'win' if is_win else 'loss',
                    'pnl': pnl
                })
                
            # Sentiment analysis
            if 'sentiment' in psych:
                sentiment = psych['sentiment']
                sentiment_analysis[sentiment]['trades'] += 1
                sentiment_analysis[sentiment]['pnl'] += pnl
                if is_win:
                    sentiment_analysis[sentiment]['wins'] += 1
                    
            # Contrarian analysis
            if 'contrarian_bias' in psych:
                bias = psych['contrarian_bias']
                contrarian_analysis[bias]['trades'] += 1
                contrarian_analysis[bias]['pnl'] += pnl
                if is_win:
                    contrarian_analysis[bias]['wins'] += 1
        
        # Calculate win rates and average PnL for sentiment analysis
        sentiment_results = {}
        for sentiment, data in sentiment_analysis.items():
            sentiment_results[sentiment] = {
                'trades': data['trades'],
                'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0,
                'total_pnl': data['pnl'],
                'avg_pnl': data['pnl'] / data['trades'] if data['trades'] > 0 else 0
            }
            
        # Calculate win rates and average PnL for contrarian analysis
        contrarian_results = {}
        for bias, data in contrarian_analysis.items():
            contrarian_results[bias] = {
                'trades': data['trades'],
                'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0,
                'total_pnl': data['pnl'],
                'avg_pnl': data['pnl'] / data['trades'] if data['trades'] > 0 else 0
            }
            
        # Analyze fear & greed correlation with performance
        fear_greed_correlation = None
        
        if fear_greed_analysis:
            # Group by score range
            score_ranges = {
                'Extreme Fear (0-10)': [],
                'Fear (10-30)': [],
                'Neutral (30-70)': [],
                'Greed (70-90)': [],
                'Extreme Greed (90-100)': []
            }
            
            for entry in fear_greed_analysis:
                score = entry['score']
                
                if score < 10:
                    score_ranges['Extreme Fear (0-10)'].append(entry)
                elif score < 30:
                    score_ranges['Fear (10-30)'].append(entry)
                elif score < 70:
                    score_ranges['Neutral (30-70)'].append(entry)
                elif score < 90:
                    score_ranges['Greed (70-90)'].append(entry)
                else:
                    score_ranges['Extreme Greed (90-100)'].append(entry)
                    
            # Calculate performance by score range
            fear_greed_results = {}
            
            for range_name, entries in score_ranges.items():
                if not entries:
                    continue
                    
                wins = sum(1 for e in entries if e['result'] == 'win')
                total_pnl = sum(e['pnl'] for e in entries)
                
                fear_greed_results[range_name] = {
                    'trades': len(entries),
                    'win_rate': wins / len(entries) if entries else 0,
                    'total_pnl': total_pnl,
                    'avg_pnl': total_pnl / len(entries) if entries else 0
                }
                
            fear_greed_correlation = fear_greed_results
        
        return {
            'total_psychological_trades': len(trades),
            'sentiment_analysis': sentiment_results,
            'contrarian_analysis': contrarian_results,
            'fear_greed_analysis': fear_greed_correlation
        }
    
    def analyze_pattern_effectiveness(self, trades=None):
        """
        Analyze the effectiveness of different patterns in generating profitable trades.
        
        Args:
            trades (list, optional): List of trades to analyze or None to use all trades
            
        Returns:
            dict: Pattern effectiveness analysis
        """
        if trades is None:
            trades = self.trade_logger.trades
            
        # Filter for closed trades with pattern data
        trades = [t for t in trades if t['status'] == 'CLOSED' and 'patterns_detected' in t]
        
        if not trades:
            return {
                'error': 'No trades with pattern data found'
            }
            
        # Extract and analyze patterns
        pattern_performance = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})
        
        for trade in trades:
            patterns = trade['patterns_detected']
            pnl = trade.get('pnl', 0)
            is_win = pnl > 0
            
            # Add to overall pattern stats
            if not patterns:
                pattern_performance['No Pattern']['trades'] += 1
                pattern_performance['No Pattern']['pnl'] += pnl
                if is_win:
                    pattern_performance['No Pattern']['wins'] += 1
            else:
                for pattern in patterns:
                    pattern_performance[pattern]['trades'] += 1
                    pattern_performance[pattern]['pnl'] += pnl
                    if is_win:
                        pattern_performance[pattern]['wins'] += 1
        
        # Calculate win rates and average PnL
        pattern_results = {}
        
        for pattern, data in pattern_performance.items():
            pattern_results[pattern] = {
                'trades': data['trades'],
                'win_rate': data['wins'] / data['trades'] if data['trades'] > 0 else 0,
                'total_pnl': data['pnl'],
                'avg_pnl': data['pnl'] / data['trades'] if data['trades'] > 0 else 0
            }
            
        # Sort patterns by effectiveness (win rate * avg_pnl)
        effectiveness = {}
        
        for pattern, data in pattern_results.items():
            effectiveness[pattern] = data['win_rate'] * data['avg_pnl']
            
        top_patterns = {k: v for k, v in sorted(effectiveness.items(), key=lambda item: item[1], reverse=True)}
        
        return {
            'total_pattern_trades': len(trades),
            'pattern_performance': pattern_results,
            'pattern_effectiveness_ranking': top_patterns
        }
    
    def plot_metrics_dashboard(self, save_path=None):
        """
        Generate a comprehensive metrics dashboard.
        
        Args:
            save_path (str, optional): Path to save the dashboard
            
        Returns:
            matplotlib.figure.Figure: The generated dashboard
        """
        # Get closed trades
        closed_trades = [t for t in self.trade_logger.trades if t['status'] == 'CLOSED']
        
        if not closed_trades:
            fig, ax = plt.subplots(figsize=(15, 10))
            ax.text(0.5, 0.5, "No closed trades available for dashboard", 
                  ha='center', va='center', fontsize=14)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
                
            return fig
        
        # Set up plot style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("deep")
        
        # Create dashboard with multiple plots
        fig = plt.figure(figsize=(15, 12))
        
        # Define grid layout
        gs = fig.add_gridspec(3, 2)
        
        # 1. Equity Curve (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        
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
        
        # Plot equity curve
        ax1.plot(dates, cumulative_pnl, marker='o', linestyle='-', markersize=4, linewidth=2)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax1.set_title('Equity Curve', fontsize=12)
        ax1.set_ylabel('Cumulative P&L', fontsize=10)
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        
        # 2. Win/Loss Pie Chart (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]
        breakeven_trades = [t for t in closed_trades if t.get('pnl', 0) == 0]
        
        labels = ['Winning', 'Losing', 'Breakeven']
        sizes = [len(winning_trades), len(losing_trades), len(breakeven_trades)]
        colors = ['#4CAF50', '#F44336', '#9E9E9E']
        
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=False)
        ax2.axis('equal')
        ax2.set_title('Trade Outcomes', fontsize=12)
        
        # 3. Performance by Index (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        
        # Group trades by index
        trades_by_index = defaultdict(list)
        
        for trade in closed_trades:
            trades_by_index[trade['index']].append(trade)
            
        # Calculate performance by index
        indices = list(trades_by_index.keys())
        pnl_by_index = [sum(t.get('pnl', 0) for t in trades_by_index[i]) for i in indices]
        
        # Create horizontal bar chart
        bars = ax3.barh(indices, pnl_by_index, color=['green' if p > 0 else 'red' for p in pnl_by_index])
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            label_pos = width + 5 if width > 0 else width - 5
            alignment = 'left' if width > 0 else 'right'
            ax3.text(label_pos, bar.get_y() + bar.get_height()/2, f'{width:.0f}',
                   ha=alignment, va='center')
        
        ax3.set_title('P&L by Index', fontsize=12)
        ax3.set_xlabel('P&L', fontsize=10)
        ax3.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        # 4. Performance by Signal Type (middle right)
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Group trades by signal type
        trades_by_signal = defaultdict(list)
        
        for trade in closed_trades:
            trades_by_signal[trade['signal']].append(trade)
            
        # Calculate performance by signal
        signals = list(trades_by_signal.keys())
        pnl_by_signal = [sum(t.get('pnl', 0) for t in trades_by_signal[s]) for s in signals]
        win_rates = [len([t for t in trades_by_signal[s] if t.get('pnl', 0) > 0]) / len(trades_by_signal[s]) if trades_by_signal[s] else 0 for s in signals]
        
        # Create horizontal bar chart with win rate overlay
        bars = ax4.barh(signals, pnl_by_signal, color=['green' if p > 0 else 'red' for p in pnl_by_signal], alpha=0.7)
        
        # Add win rate as text
        for i, (signal, win_rate) in enumerate(zip(signals, win_rates)):
            ax4.text(5, i, f"{win_rate:.0%} Win", va='center', ha='left', 
                    color='white', fontweight='bold', fontsize=9)
        
        ax4.set_title('P&L by Signal Type', fontsize=12)
        ax4.set_xlabel('P&L', fontsize=10)
        ax4.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        # 5. Monthly Performance (bottom left)
        ax5 = fig.add_subplot(gs[2, 0])
        
        # Group trades by month
        trades_by_month = defaultdict(list)
        
        for trade in closed_trades:
            month = trade.get('exit_time', trade.get('entry_time')).split()[0][:7]  # YYYY-MM
            trades_by_month[month].append(trade)
            
        # Calculate monthly PnL
        months = sorted(list(trades_by_month.keys()))
        monthly_pnl = [sum(t.get('pnl', 0) for t in trades_by_month[m]) for m in months]
        
        # Create bar chart
        bars = ax5.bar(months, monthly_pnl, color=['green' if p > 0 else 'red' for p in monthly_pnl])
        
        # Format the x-axis to show only month names
        ax5.set_xticklabels([m.split('-')[1] + '/' + m.split('-')[0][2:] for m in months])
        
        ax5.set_title('Monthly P&L', fontsize=12)
        ax5.set_ylabel('P&L', fontsize=10)
        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. Drawdown Analysis (bottom right)
        ax6 = fig.add_subplot(gs[2, 1])
        
        # Calculate drawdowns
        equity_curve = np.array(cumulative_pnl)
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak * 100  # As percentage
        
        # Plot drawdown
        ax6.fill_between(dates, drawdown, alpha=0.7, color='red')
        ax6.set_ylim(bottom=0)  # Start from 0
        ax6.invert_yaxis()  # Invert y-axis to show drawdowns as going down
        
        ax6.set_title('Drawdown Analysis', fontsize=12)
        ax6.set_ylabel('Drawdown %', fontsize=10)
        ax6.tick_params(axis='x', rotation=45, labelsize=8)
        
        # Add overall metrics as text at the bottom
        metrics = self.calculate_metrics()
        
        if 'error' not in metrics:
            basic = metrics['basic_metrics']
            advanced = metrics['advanced_metrics']
            
            metrics_text = (
                f"Total Trades: {basic['total_trades']}  |  "
                f"Win Rate: {basic['win_rate']:.1%}  |  "
                f"Profit Factor: {basic['profit_factor']:.2f}  |  "
                f"Max Drawdown: {advanced['max_drawdown']:.0f}  |  "
                f"Sharpe Ratio: {advanced.get('sharpe_ratio', 'N/A')}"
            )
            
            fig.text(0.5, 0.01, metrics_text, ha='center', fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.5))
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Add title
        plt.suptitle('Trading Performance Dashboard', fontsize=16, y=0.98)
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            
        return fig