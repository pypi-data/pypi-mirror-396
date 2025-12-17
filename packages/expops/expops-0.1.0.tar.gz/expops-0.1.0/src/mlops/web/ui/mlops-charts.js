/**
 * MLOps Dynamic Charts SDK
 * 
 * This library provides a user-friendly API for creating dynamic charts that
 * listen to metrics in real-time, similar to the Python @chart() decorator.
 * 
 * System logic is abstracted here, while users write chart definitions in their
 * project-specific chart files.
 */

// ==================== System Internal Classes ====================

class MetricsListener {
  constructor(projectId, runId, apiBase) {
    this.projectId = projectId;
    this.runId = runId;
    this.apiBase = apiBase;
    this.listeners = new Map(); // probe_path -> { callbacks, currentData, pollTimer }
    this.runStatusTimer = null;
    this.runFinished = false;
  }

  /**
   * Subscribe to metrics updates for a probe path
   * @param {string} probePath - The probe path (e.g., "nn_training_a/train_and_evaluate_nn")
   * @param {Function} callback - Called when metrics update: (metrics) => void
   * @returns {Function} Unsubscribe function
   */
  subscribe(probePath, callback) {
    if (!this.listeners.has(probePath)) {
      const listenerData = {
        callbacks: new Set(),
        currentData: null,
        pollTimer: null
      };
      this.listeners.set(probePath, listenerData);
      
      // Start polling for this probe
      this._startPolling(probePath);
    }
    
    const listenerData = this.listeners.get(probePath);
    listenerData.callbacks.add(callback);
    
    // Immediately invoke callback if we have data
    if (listenerData.currentData) {
      callback(listenerData.currentData);
    }
    
    // Return unsubscribe function
    return () => {
      listenerData.callbacks.delete(callback);
      if (listenerData.callbacks.size === 0) {
        this._stopPolling(probePath);
        this.listeners.delete(probePath);
      }
    };
  }

  /**
   * Subscribe to multiple probe paths
   * @param {Object} probePaths - Map of { key: probePath }
   * @param {Function} callback - Called with { key: metrics, ... }
   * @returns {Function} Unsubscribe function
   */
  subscribeAll(probePaths, callback) {
    const aggregatedData = {};
    const unsubscribers = [];
    
    for (const [key, probePath] of Object.entries(probePaths)) {
      const unsub = this.subscribe(probePath, (metrics) => {
        aggregatedData[key] = metrics;
        callback(aggregatedData);
      });
      unsubscribers.push(unsub);
    }
    
    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }

  async _fetchMetrics(probePath) {
    try {
      const encodedPath = encodeURIComponent(probePath);
      const url = `${this.apiBase}/projects/${encodeURIComponent(this.projectId)}/runs/${encodeURIComponent(this.runId)}/metrics/${encodedPath}`;
      const response = await fetch(url);
      if (!response.ok) return null;
      const data = await response.json();
      return data.metrics || null;
    } catch (error) {
      console.error(`Failed to fetch metrics for ${probePath}:`, error);
      return null;
    }
  }

  _startPolling(probePath) {
    const listenerData = this.listeners.get(probePath);
    if (!listenerData) return;
    
    const poll = async () => {
      if (this.runFinished) {
        this._stopPolling(probePath);
        return;
      }
      
      const metrics = await this._fetchMetrics(probePath);
      if (metrics !== null) {
        listenerData.currentData = metrics;
        listenerData.callbacks.forEach(callback => {
          try {
            callback(metrics);
          } catch (error) {
            console.error('Error in metrics callback:', error);
          }
        });
      }
    };
    
    // Initial fetch
    poll();
    
    // Poll every 2 seconds
    listenerData.pollTimer = setInterval(poll, 2000);
  }

  _stopPolling(probePath) {
    const listenerData = this.listeners.get(probePath);
    if (listenerData && listenerData.pollTimer) {
      clearInterval(listenerData.pollTimer);
      listenerData.pollTimer = null;
    }
  }

  /**
   * Start monitoring run status and stop all polling when run finishes
   */
  startRunStatusMonitoring() {
    if (this.runStatusTimer) return;
    
    const checkStatus = async () => {
      try {
        const url = `${this.apiBase}/projects/${encodeURIComponent(this.projectId)}/runs/${encodeURIComponent(this.runId)}/status`;
        const response = await fetch(url);
        if (!response.ok) return;
        const data = await response.json();
        const status = (data.status || '').toLowerCase();
        
        if (['completed', 'failed', 'cancelled'].includes(status)) {
          this.runFinished = true;
          this.stopAll();
        }
      } catch (error) {
        console.error('Error checking run status:', error);
      }
    };
    
    this.runStatusTimer = setInterval(checkStatus, 5000);
  }

  stopAll() {
    // Stop all polling
    for (const [probePath, _] of this.listeners) {
      this._stopPolling(probePath);
    }
    
    if (this.runStatusTimer) {
      clearInterval(this.runStatusTimer);
      this.runStatusTimer = null;
    }
    
    this.listeners.clear();
  }
}

class ChartContext {
  constructor(projectId, runId, chartName, containerElement, apiBase) {
    this.projectId = projectId;
    this.runId = runId;
    this.chartName = chartName;
    this.containerElement = containerElement;
    this.apiBase = apiBase;
    this.chartInstance = null; // For Chart.js instances
  }

  /**
   * Helper to convert metrics data to time series array
   * Handles both dict {step: value} and array formats
   */
  toSeries(data) {
    if (typeof data === 'object' && !Array.isArray(data) && data !== null) {
      // Dict format: {0: val, 1: val, ...}
      const items = Object.entries(data).sort((a, b) => {
        const aNum = parseInt(a[0]);
        const bNum = parseInt(b[0]);
        return (isNaN(aNum) ? 0 : aNum) - (isNaN(bNum) ? 0 : bNum);
      });
      return items.map(([_, v]) => parseFloat(v));
    } else if (Array.isArray(data)) {
      return data.map(v => parseFloat(v));
    }
    return [];
  }

  /**
   * Get the latest scalar value from metrics data
   * Useful for static metrics or getting the final value
   */
  getValue(data) {
    if (typeof data === 'number') {
      return data;
    } else if (typeof data === 'object' && !Array.isArray(data) && data !== null) {
      const items = Object.entries(data).sort((a, b) => {
        const aNum = parseInt(a[0]);
        const bNum = parseInt(b[0]);
        return (isNaN(aNum) ? 0 : aNum) - (isNaN(bNum) ? 0 : bNum);
      });
      return items.length > 0 ? parseFloat(items[items.length - 1][1]) : null;
    } else if (Array.isArray(data) && data.length > 0) {
      return parseFloat(data[data.length - 1]);
    }
    return null;
  }

  /**
   * Clear the chart container
   */
  clear() {
    if (this.chartInstance && typeof this.chartInstance.destroy === 'function') {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
    this.containerElement.innerHTML = '';
  }

  /**
   * Set the chart instance (for Chart.js charts)
   */
  setChartInstance(chart) {
    if (this.chartInstance && typeof this.chartInstance.destroy === 'function') {
      this.chartInstance.destroy();
    }
    this.chartInstance = chart;
  }
}

// ==================== User-Facing Registry ====================

const CHART_REGISTRY = new Map();

/**
 * Decorator-style function to register a chart
 * 
 * Usage:
 *   chart('my_chart_name', (probePaths, ctx, listener) => {
 *     // Your chart logic here
 *   });
 * 
 * @param {string} name - Chart name (must match config)
 * @param {Function} renderFunction - Function with signature: (probePaths, ctx, listener) => void
 */
export function chart(name, renderFunction) {
  if (typeof name !== 'string' || !name.trim()) {
    throw new Error('Chart name must be a non-empty string');
  }
  if (typeof renderFunction !== 'function') {
    throw new Error('Chart render function must be a function');
  }
  
  CHART_REGISTRY.set(name, renderFunction);
}

/**
 * Get a registered chart by name
 * @param {string} name
 * @returns {Function|null}
 */
export function getChart(name) {
  return CHART_REGISTRY.get(name) || null;
}

/**
 * List all registered chart names
 * @returns {string[]}
 */
export function listCharts() {
  return Array.from(CHART_REGISTRY.keys());
}

// ==================== Chart Renderer ====================

/**
 * Render a dynamic chart in a container
 * 
 * @param {string} projectId
 * @param {string} runId
 * @param {string} chartName
 * @param {Object} chartConfig - Chart config from backend (includes probe_paths)
 * @param {HTMLElement} containerElement
 * @param {string} apiBase - API base URL
 * @returns {Function} Cleanup function
 */
export function renderDynamicChart(projectId, runId, chartName, chartConfig, containerElement, apiBase = '/api') {
  const renderFunction = CHART_REGISTRY.get(chartName);
  if (!renderFunction) {
    containerElement.innerHTML = `<div class="chart-error">Chart '${chartName}' not found. Did you register it?</div>`;
    return () => {};
  }

  const ctx = new ChartContext(projectId, runId, chartName, containerElement, apiBase);
  const listener = new MetricsListener(projectId, runId, apiBase);
  
  // Start run status monitoring for auto-shutdown
  listener.startRunStatusMonitoring();
  
  try {
    // Extract probe_paths from config
    const probePaths = chartConfig.probe_paths || {};
    
    // Call user's render function
    renderFunction(probePaths, ctx, listener);
  } catch (error) {
    console.error(`Error rendering chart '${chartName}':`, error);
    containerElement.innerHTML = `<div class="chart-error">Error: ${error.message}</div>`;
  }
  
  // Return cleanup function
  return () => {
    ctx.clear();
    listener.stopAll();
  };
}

/**
 * Render a static chart (just display the image)
 * 
 * @param {string} imageUrl - URL to the chart image
 * @param {HTMLElement} containerElement
 */
export function renderStaticChart(imageUrl, containerElement) {
  containerElement.innerHTML = '';
  const img = document.createElement('img');
  img.src = imageUrl;
  img.alt = 'Chart';
  img.style.maxWidth = '100%';
  img.style.height = 'auto';
  containerElement.appendChild(img);
}

// ==================== Exports ====================

export {
  MetricsListener,
  ChartContext,
  CHART_REGISTRY
};

