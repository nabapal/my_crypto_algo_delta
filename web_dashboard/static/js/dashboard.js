/**
 * Dashboard JavaScript - Real-time Trading Bot Interface
 * Handles WebSocket connections, real-time updates, and user interactions
 */

class TradingDashboard {
    constructor() {
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 5000;
        this.isConnected = false;
        
        // Initialize dashboard
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Trading Dashboard...');
        
        // Start WebSocket connection
        this.connectWebSocket();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start periodic updates
        this.startPeriodicUpdates();
        
        // Update time display
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        
        // Load initial data
        this.loadInitialData();
    }
    
    // WebSocket Management
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/trading-updates`;
        
        console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.websocket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('❌ Failed to create WebSocket:', error);
            this.updateConnectionStatus('error');
            this.attemptReconnect();
        }
    }
    
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message:', data);
            
            switch (data.type) {
                case 'trade_opened':
                    this.handleTradeOpened(data.data);
                    break;
                case 'trade_closed':
                    this.handleTradeClosed(data.data);
                    break;
                case 'pnl_update':
                    this.handlePnLUpdate(data.data);
                    break;
                case 'status_update':
                    this.handleStatusUpdate(data.data);
                    break;
                case 'heartbeat':
                    // Keep connection alive
                    break;
                default:
                    console.log('📦 Received initial status:', data);
                    this.updateDashboardWithStatus(data);
            }
        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.updateConnectionStatus('failed');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        
        setTimeout(() => {
            this.connectWebSocket();
        }, this.reconnectDelay);
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const statusIcon = statusElement.querySelector('i');
        
        switch (status) {
            case 'connected':
                statusIcon.className = 'fas fa-circle text-success';
                statusElement.innerHTML = `<i class="fas fa-circle text-success"></i> Connected`;
                break;
            case 'disconnected':
                statusIcon.className = 'fas fa-circle text-warning';
                statusElement.innerHTML = `<i class="fas fa-circle text-warning"></i> Reconnecting...`;
                break;
            case 'error':
            case 'failed':
                statusIcon.className = 'fas fa-circle text-danger';
                statusElement.innerHTML = `<i class="fas fa-circle text-danger"></i> Connection Failed`;
                break;
        }
    }
    
    // Event Handlers
    setupEventListeners() {
        // Log type selection
        document.querySelectorAll('#log-types .list-group-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchLogType(e.target.dataset.logType);
                
                // Update active state
                document.querySelectorAll('#log-types .list-group-item').forEach(i => i.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
        
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetPane = e.target.getAttribute('data-bs-target');
                if (targetPane === '#logs-pane') {
                    this.loadLogs('console');
                } else if (targetPane === '#trades-pane') {
                    this.loadTrades();
                } else if (targetPane === '#performance-pane') {
                    this.loadPerformance();
                }
            });
        });
    }
    
    // Real-time Event Handlers
    handleTradeOpened(data) {
        console.log('🎯 Trade opened:', data);
        
        // Show notification
        this.showNotification(
            `New ${data.position_type} position opened at $${Number(data.entry_price).toLocaleString()}`,
            'success'
        );
        
        // Update position display
        this.updatePositionStatus(`${data.position_type} Position Active`);
        
        // Refresh data
        this.refreshFinancialData();
        this.loadTrades();
    }
    
    handleTradeClosed(data) {
        console.log('💰 Trade closed:', data);
        
        const pnl = Number(data.pnl);
        const pnlText = pnl >= 0 ? `+$${pnl.toFixed(2)}` : `-$${Math.abs(pnl).toFixed(2)}`;
        const alertType = pnl >= 0 ? 'success' : 'danger';
        
        // Show notification
        this.showNotification(
            `Trade closed with P&L: ${pnlText}`,
            alertType
        );
        
        // Update position display
        this.updatePositionStatus('No Active Position');
        
        // Refresh data
        this.refreshFinancialData();
        this.loadTrades();
    }
    
    handlePnLUpdate(data) {
        // Update unrealized P&L
        const unrealizedPnl = Number(data.unrealized_pnl);
        const element = document.getElementById('unrealized-pnl');
        
        if (element) {
            const formatted = unrealizedPnl >= 0 ? `+$${unrealizedPnl.toFixed(2)}` : `-$${Math.abs(unrealizedPnl).toFixed(2)}`;
            element.textContent = formatted;
            element.className = `metric-value ${unrealizedPnl >= 0 ? 'positive' : 'negative'}`;
        }
    }
    
    handleStatusUpdate(data) {
        console.log('📊 Status update:', data);
        
        // Update bot status
        const statusIndicator = document.getElementById('bot-status-indicator');
        const statusText = document.getElementById('bot-status-text');
        const pidText = document.getElementById('bot-pid');
        
        if (data.running) {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-success"></i>';
            statusText.textContent = 'RUNNING';
            pidText.textContent = `PID: ${data.pid}`;
        } else {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i>';
            statusText.textContent = 'STOPPED';
            pidText.textContent = 'PID: --';
        }
    }
    
    // Data Loading Methods
    async loadInitialData() {
        console.log('📊 Loading initial data...');
        
        try {
            await Promise.all([
                this.refreshFinancialData(),
                this.loadTrades(),
                this.loadLogs('console')
            ]);
            
            console.log('✅ Initial data loaded');
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }
    
    async refreshFinancialData() {
        try {
            const response = await fetch('/api/bot-integrated');
            const data = await response.json();
            
            // Handle bot status
            this.handleStatusUpdate({
                running: data.bot_status === 'RUNNING',
                status: data.bot_status
            });

            // Handle portfolio data using bot integration structure
            if (data.portfolio) {
                this.updateMetric('initial-capital', data.portfolio.initial_capital, 'currency');
                this.updateMetric('current-balance', data.portfolio.total_balance, 'currency');
                this.updateMetric('unrealized-pnl', data.portfolio.unrealized_pnl, 'currency', true);
                this.updateMetric('realized-pnl', data.portfolio.realized_pnl, 'currency', true);
                
                // Update total return percentage
                this.updateMetric('total-return', data.portfolio.total_return_percent, 'percentage', true);
                
                // Update trading stats
                if (data.trading_stats) {
                    this.updateMetric('completed-trades', data.trading_stats.total_trades);
                    this.updateMetric('win-rate', data.trading_stats.win_rate, 'percentage');
                    this.updateMetric('avg-win', data.trading_stats.avg_win, 'currency');
                    this.updateMetric('avg-loss', data.trading_stats.avg_loss, 'currency');
                }
                
                // Update position status
                const positionElement = document.querySelector('.position-status');
                if (positionElement) {
                    if (data.portfolio.has_active_position) {
                        positionElement.textContent = 'Active Position';
                        positionElement.className = 'position-status active';
                    } else {
                        positionElement.textContent = 'No Position';
                        positionElement.className = 'position-status inactive';
                    }
                }
                
                // Update detailed position content
                this.updatePositionContent(data);
            }

        } catch (error) {
            console.error('❌ Error refreshing financial data:', error);
        }
    }
    
    async loadTrades() {
        try {
            const response = await fetch('/api/trades');
            const data = await response.json();
            
            if (data.trades) {
                this.updateTradesTable(data.trades);
            }
            
            if (data.summary) {
                // Update realized P&L from completed trades
                const completedTrades = data.trades.filter(trade => trade.Action === 'EXIT');
                const realizedPnl = completedTrades.reduce((sum, trade) => sum + (trade['P&L'] || 0), 0);
                this.updateMetric('realized-pnl', realizedPnl, 'currency', true);
            }
            
        } catch (error) {
            console.error('❌ Error loading trades:', error);
        }
    }
    
    async loadLogs(logType = 'console') {
        try {
            const response = await fetch(`/api/logs/${logType}`);
            const data = await response.json();
            
            const logContent = document.getElementById('log-content');
            if (data.logs) {
                logContent.textContent = data.logs;
                // Scroll to bottom
                logContent.scrollTop = logContent.scrollHeight;
            } else {
                logContent.textContent = data.error || 'No log data available';
            }
            
        } catch (error) {
            console.error(`❌ Error loading ${logType} logs:`, error);
            document.getElementById('log-content').textContent = 'Error loading logs';
        }
    }
    
    async loadPerformance() {
        try {
            const response = await fetch('/api/performance');
            const data = await response.json();
            
            const performanceContent = document.getElementById('performance-content');
            
            if (data.performance && Object.keys(data.performance).length > 0) {
                performanceContent.innerHTML = this.formatPerformanceData(data.performance);
            } else {
                performanceContent.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-bar fa-2x"></i>
                        <p class="mt-2">No performance data available yet</p>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('❌ Error loading performance:', error);
            document.getElementById('performance-content').innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                    <p class="mt-2">Error loading performance data</p>
                </div>
            `;
        }
    }
    
    // UI Update Methods
    updateMetric(elementId, value, type = 'number', signed = false) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        let formatted;
        let className = 'metric-value';
        
        switch (type) {
            case 'currency':
                if (signed && value !== 0) {
                    formatted = value >= 0 ? `+$${Math.abs(value).toFixed(2)}` : `-$${Math.abs(value).toFixed(2)}`;
                    className += value >= 0 ? ' positive' : ' negative';
                } else {
                    formatted = `$${Math.abs(value).toFixed(2)}`;
                }
                break;
            case 'percentage':
                if (signed && value !== 0) {
                    formatted = value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
                    className += value >= 0 ? ' positive' : ' negative';
                } else {
                    formatted = `${value.toFixed(1)}%`;
                }
                break;
            case 'number':
            default:
                formatted = Number(value).toLocaleString();
                break;
        }
        
        element.textContent = formatted;
        element.className = className;
    }
    
    updateMetricChange(elementId, value) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const formatted = value >= 0 ? `+$${value.toFixed(2)}` : `-$${Math.abs(value).toFixed(2)}`;
        const className = `metric-change ${value >= 0 ? 'positive' : 'negative'}`;
        
        element.textContent = formatted;
        element.className = className;
    }
    
    updatePositionStatus(status) {
        const element = document.getElementById('position-status');
        if (element) {
            element.querySelector('h6').textContent = status;
        }
    }
    
    updatePositionContent(data) {
        const positionContentElement = document.getElementById('position-content');
        if (!positionContentElement) return;
        
        if (data.portfolio.has_active_position && data.active_position) {
            const position = data.active_position;
            const pnlClass = position.unrealized_pnl >= 0 ? 'text-success' : 'text-danger';
            const pnlSign = position.unrealized_pnl >= 0 ? '+' : '';
            
            positionContentElement.innerHTML = `
                <div class="card bg-dark border-secondary">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="card-title text-primary">
                                    <i class="fas fa-crosshairs me-2"></i>
                                    ${position.side} Position - ${position.symbol}
                                </h6>
                                <div class="row g-3">
                                    <div class="col-6">
                                        <small class="text-muted">Entry Price</small>
                                        <div class="fw-bold">$${position.entry_price.toLocaleString()}</div>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">Current Price</small>
                                        <div class="fw-bold">$${position.current_price.toLocaleString()}</div>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">Quantity</small>
                                        <div class="fw-bold">${position.quantity.toFixed(8)}</div>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">Duration</small>
                                        <div class="fw-bold">${position.duration}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="row g-3">
                                    <div class="col-12">
                                        <small class="text-muted">Unrealized P&L</small>
                                        <div class="fw-bold fs-5 ${pnlClass}">
                                            ${pnlSign}$${Math.abs(position.unrealized_pnl).toFixed(2)}
                                            <small class="ms-2">(${pnlSign}${position.pnl_percentage.toFixed(2)}%)</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">Stop Loss</small>
                                        <div class="fw-bold text-danger">$${position.stop_loss.toLocaleString()}</div>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted">Take Profit</small>
                                        <div class="fw-bold text-success">$${position.take_profit.toLocaleString()}</div>
                                    </div>
                                    <div class="col-12">
                                        <small class="text-muted">Entry Time</small>
                                        <div class="fw-bold">${position.entry_time}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            positionContentElement.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-chart-line fa-3x mb-3"></i>
                    <h5>No Active Position</h5>
                    <p>The bot is currently monitoring the market for trading opportunities.</p>
                </div>
            `;
        }
    }
    
    updateTradesTable(trades) {
        const tbody = document.getElementById('trades-tbody');
        
        if (!trades || trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No trades available</td></tr>';
            return;
        }
        
        // Show most recent trades first
        const recentTrades = trades.slice(-20).reverse();
        
        tbody.innerHTML = recentTrades.map(trade => {
            const pnl = trade['P&L'] || 0;
            const pnlClass = pnl > 0 ? 'pnl-positive' : pnl < 0 ? 'pnl-negative' : '';
            const pnlFormatted = pnl !== 0 ? `$${pnl.toFixed(2)}` : '--';
            
            return `
                <tr>
                    <td>${trade['Trade_ID']}</td>
                    <td>
                        <span class="badge bg-${trade.Action === 'ENTRY' ? 'primary' : 'success'}">
                            ${trade.Action}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-${trade.Position_Type === 'SHORT' ? 'danger' : 'info'}">
                            ${trade.Position_Type}
                        </span>
                    </td>
                    <td>$${Number(trade.Entry_Price || trade.Exit_Price || 0).toLocaleString()}</td>
                    <td>${Number(trade.Quantity).toFixed(6)} BTC</td>
                    <td class="${pnlClass}">${pnlFormatted}</td>
                    <td>${new Date(trade.Timestamp_UTC).toLocaleTimeString()}</td>
                </tr>
            `;
        }).join('');
    }
    
    formatPerformanceData(performance) {
        // Format performance data for display
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="performance-metric">
                        <h6>Total Return</h6>
                        <div class="value">${performance.total_return || '0.00'}%</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="performance-metric">
                        <h6>Sharpe Ratio</h6>
                        <div class="value">${performance.sharpe_ratio || '0.00'}</div>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <h6>Performance Details:</h6>
                <pre class="bg-dark text-light p-3 rounded">${JSON.stringify(performance, null, 2)}</pre>
            </div>
        `;
    }
    
    // Utility Methods
    switchLogType(logType) {
        console.log(`📋 Switching to ${logType} logs`);
        this.loadLogs(logType);
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = document.getElementById('toast-message');
        const toastTime = document.getElementById('toast-time');
        
        // Set message and time
        toastBody.textContent = message;
        toastTime.textContent = new Date().toLocaleTimeString();
        
        // Set toast type
        toast.className = `toast border-${type}`;
        toastBody.className = `toast-body text-${type}`;
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        console.log(`🔔 Notification: ${message}`);
    }
    
    updateTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }
    
    startPeriodicUpdates() {
        // Refresh financial data every 30 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.refreshFinancialData();
            }
        }, 30000);
        
        // Refresh logs every 10 seconds if logs tab is active
        setInterval(() => {
            const logsPane = document.getElementById('logs-pane');
            if (logsPane && logsPane.classList.contains('show')) {
                const activeLogType = document.querySelector('#log-types .list-group-item.active')?.dataset.logType || 'console';
                this.loadLogs(activeLogType);
            }
        }, 10000);
    }
}

// Global functions
function refreshDashboard() {
    console.log('🔄 Manual refresh triggered');
    if (window.dashboard) {
        window.dashboard.loadInitialData();
        window.dashboard.showNotification('Dashboard refreshed', 'success');
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM loaded, initializing dashboard...');
    window.dashboard = new TradingDashboard();
});
