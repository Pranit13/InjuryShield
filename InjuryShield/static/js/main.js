// Function to fetch real-time metrics and update the dashboard
async function fetchRealtimeMetrics() {
    try {
        const response = await fetch('/api/realtime_metrics');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const metrics = await response.json();
        
        const metricsContainer = document.getElementById('real-time-metrics');
        const lastUpdatedTime = document.getElementById('last-updated-time');

        if (metricsContainer) {
            metricsContainer.innerHTML = `
                <div class="metric-item">
                    <strong>Total Persons (24h):</strong> <span class="value">${metrics.total_persons_24h}</span>
                </div>
                <div class="metric-item">
                    <strong>Total Violations (24h):</strong> <span class="value">${metrics.total_violations_24h}</span>
                </div>
                <div class="metric-item">
                    <strong>Compliance Rate (24h):</strong> 
                    <span class="value compliance-rate ${getComplianceRateClass(metrics.compliance_rate_24h)}">
                        ${metrics.compliance_rate_24h}%
                    </span>
                </div>
                <div class="metric-item">
                    <strong>Total Logs (24h):</strong> <span class="value">${metrics.total_logs_24h}</span>
                </div>
            `;
        }

        if (lastUpdatedTime) {
            lastUpdatedTime.textContent = moment().format('YYYY-MM-DD HH:mm:ss');
        }

        console.log('Real-time metrics updated:', metrics);

    } catch (error) {
        console.error('Failed to fetch real-time metrics:', error);
        const metricsContainer = document.getElementById('real-time-metrics');
        if (metricsContainer) {
            metricsContainer.innerHTML = `<p style="color: red;">Error loading metrics: ${error.message}</p>`;
        }
    }
}

// Helper function to get a CSS class based on compliance rate
function getComplianceRateClass(rate) {
    if (rate >= 95) {
        return 'good';
    } else if (rate >= 80) {
        return 'medium';
    } else {
        return 'bad';
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Only fetch real-time metrics on the index (dashboard) page
    if (document.getElementById('real-time-metrics')) {
        fetchRealtimeMetrics(); // Fetch immediately on load
        setInterval(fetchRealtimeMetrics, 15000); // Fetch every 15 seconds
    }
    // Chart rendering logic is now in history.html directly, no need here for this batch
});