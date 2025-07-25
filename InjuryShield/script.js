/**
 * =============================================================================
 * InjuryShield Front-End Application Logic (Backend-Connected Version)
 * =============================================================================
 * This script manages all dynamic functionalities by fetching data from a
 * backend API. All hardcoded data has been removed.
 *
 * NOTE: Replace the placeholder API endpoints (e.g., '/api/notifications')
 * with your actual backend routes.
 */

// --- 1. DOM Ready Initializer ---

document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    console.log(`Initializing InjuryShield UI for: ${currentPage || 'index.html'}`);
    
    handleActiveNavigation(currentPage);

    switch (currentPage) {
        case '':
        case 'index.html':
            initializeIndexPage();
            break;
        case 'dashboard.html':
            initializeDashboardPage();
            break;
        case 'reports.html':
            initializeReportsPage();
            break;
        case 'history.html':
            initializeHistoryPage();
            break;
        case 'cameras.html':
            initializeCamerasPage();
            break;
        case 'settings.html':
            initializeSettingsPage();
            break;
    }
});


// --- 2. API Service Layer ---

const API_BASE_URL = 'http://127.0.0.1:5000/api'; // Replace with your actual backend URL

/**
 * A generic helper function to fetch data from the backend.
 * @param {string} endpoint - The API endpoint to fetch (e.g., '/notifications').
 * @returns {Promise<object>} - A promise that resolves with the JSON data.
 */
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch data from ${endpoint}:`, error);
        // Return a default error state or an empty object/array
        return { error: true, message: error.message, data: [] };
    }
}


// --- 3. Navigation Management ---

function handleActiveNavigation(currentPage) {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const pageIdentifier = (currentPage === '' || currentPage === 'index.html') ? 'index.html' : currentPage;
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === pageIdentifier) {
            link.classList.add('active');
        }
    });
}


// --- 4. Widget Rendering Functions ---

function renderNotifications(container, notificationsData) {
    if (!container) return;
    
    if (!notificationsData || notificationsData.length === 0) {
        container.innerHTML = '<p class="no-data-message">No new notifications.</p>';
        return;
    }

    const iconMap = { /* SVG icon strings */ }; // Keep icon map
    container.innerHTML = notificationsData.map(notif => `
        <div class="notification-item">...</div>
    `).join('');
}

function renderCalendar(calendarBody, monthYearDisplay) {
    // This function can remain as is, as it's based on client's current date
    // Or it could be modified to fetch events for the month from an API
    if (!calendarBody || !monthYearDisplay) return;
    // ... (calendar logic from previous file remains unchanged)
}

function renderChart(canvasId, chartConfig) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (ctx && chartConfig.data.labels.length > 0) {
        new Chart(ctx, chartConfig);
    }
}


// --- 5. Page-Specific Initializers (Now Asynchronous) ---

async function initializeIndexPage() {
    const notificationsContainer = document.getElementById('notifications-container');
    const result = await fetchData('/notifications');
    if (!result.error) {
        renderNotifications(notificationsContainer, result.data);
    }
}

async function initializeDashboardPage() {
    renderCalendar(document.getElementById('calendar-body'), document.getElementById('month-year'));

    const result = await fetchData('/dashboard/analytics');
    if (result.error) return; // Handle error state in UI if needed

    const dashboardData = result.data;

    // Populate KPI cards
    document.getElementById('kpi-compliance-rate').textContent = `${dashboardData.metrics.complianceRate}%`;
    document.getElementById('kpi-active-alerts').textContent = dashboardData.metrics.activeAlerts;
    document.getElementById('kpi-persons-monitored').textContent = dashboardData.metrics.personsMonitored;

    // Render chart
    const dailyComplianceConfig = {
        type: 'line',
        data: {
            labels: dashboardData.charts.dailyCompliance.labels,
            datasets: [{
                label: 'Compliance Rate %',
                data: dashboardData.charts.dailyCompliance.data,
                borderColor: 'hsl(221, 83%, 53%)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    };
    renderChart('dailyComplianceChart', dailyComplianceConfig);
}

async function initializeReportsPage() {
    const result = await fetchData('/reports/analytics');
    if (result.error) return;

    const analyticsData = result.data;

    const hourlyTrendsConfig = {
        type: 'bar',
        data: {
            labels: analyticsData.hourlyTrends.labels,
            datasets: [{ data: analyticsData.hourlyTrends.data, backgroundColor: 'hsla(3, 84%, 60%, 0.7)' }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    };

    const violationTypesConfig = {
        type: 'doughnut',
        data: {
            labels: analyticsData.violationTypes.labels,
            datasets: [{ data: analyticsData.violationTypes.data, backgroundColor: ['hsl(3, 84%, 60%)', 'hsl(28, 95%, 58%)', 'hsl(221, 83%, 53%)'] }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
    };
    
    renderChart('hourlyTrendsChart', hourlyTrendsConfig);
    renderChart('violationTypesChart', violationTypesConfig);
}

async function initializeHistoryPage() {
    const tableBody = document.getElementById('history-table-body');
    const result = await fetchData('/history/logs');
    
    if (tableBody) {
        if (result.error || result.data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="no-data-message">Could not load history or no events found.</td></tr>';
        } else {
            tableBody.innerHTML = result.data.map(item => `
                <tr>
                    <td><strong>${item.id}</strong></td>
                    <td>${new Date(item.timestamp).toLocaleString()}</td>
                    <td>${item.type}</td>
                    <td><span class="status-badge status-${item.priority.toLowerCase()}">${item.priority}</span></td>
                    <td>${item.location}</td>
                    <td>${item.details}</td>
                    <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                </tr>
            `).join('');
        }
    }
}

async function initializeCamerasPage() {
    const gridContainer = document.getElementById('camera-grid-container');
    const focusImage = document.getElementById('focus-camera-image');
    // ... (other DOM element references)

    const result = await fetchData('/cameras');
    if (result.error || result.data.length === 0) {
        if (gridContainer) gridContainer.innerHTML = '<p class="no-data-message">Could not load cameras.</p>';
        return;
    }
    
    const cameraData = result.data;

    function setFocusView(cameraId) {
        const cam = cameraData.find(c => c.id === cameraId);
        if (!cam) return;
        // ... (logic to update focus view with 'cam' data)
    }

    gridContainer.innerHTML = cameraData.map(cam => `
        <div class="camera-grid-card" data-camera-id="${cam.id}">...</div>
    `).join('');

    gridContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.camera-grid-card');
        if (card) {
            setFocusView(parseInt(card.dataset.cameraId, 10));
        }
    });

    setFocusView(cameraData[0].id); // Set initial focus
}

function initializeSettingsPage() {
    // Settings can often be a mix of static UI and fetched data.
    // For now, we'll keep the accordion logic static.
    const accordions = document.querySelectorAll('.accordion-header');
    accordions.forEach(accordion => {
        accordion.addEventListener('click', () => {
            const content = accordion.nextElementSibling;
            accordion.classList.toggle('active');
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
}