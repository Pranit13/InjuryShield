/**
 * =============================================================================
 * InjuryShield Front-End Application Logic
 * =============================================================================
 * This script manages all dynamic and interactive functionalities for the
 * InjuryShield dashboard, including navigation, data visualization, and UI updates.
 *
 * Table of Contents:
 * 1. Global State & DOM Ready Initializer
 * 2. Navigation Management
 * 3. Data Simulation & Models
 * 4. Widget Rendering Functions
 *    - Notifications
 *    - Calendar
 *    - Charts (Analytics)
 *    - Tables (History & Logs)
 *    - Camera Feeds
 * 5. Page-Specific Initializers
 *    - Dashboard Page
 *    - Reports Page
 *    - History Page
 *    - Cameras Page
 *    - Settings Page
 */

document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Global State & DOM Ready Initializer ---

    // Simulates a router by getting the current page filename
    const currentPage = window.location.pathname.split('/').pop();

    console.log(`Initializing InjuryShield UI for: ${currentPage || 'index.html'}`);

    // Core initialization functions to run on every page
    handleActiveNavigation(currentPage);

    // Page-specific initialization
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


// --- 2. Navigation Management ---

/**
 * Sets the 'active' class on the correct sidebar navigation link
 * based on the current HTML file being viewed.
 * @param {string} currentPage - The filename of the current page (e.g., "dashboard.html").
 */
function handleActiveNavigation(currentPage) {
    const navLinks = document.querySelectorAll('.sidebar-nav a');

    // Normalize page name for comparison
    const pageIdentifier = (currentPage === '' || currentPage === 'index.html') ? 'index.html' : currentPage;

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === pageIdentifier) {
            link.classList.add('active');
        }
    });
}


// --- 3. Data Simulation & Models ---

const FAKE_DATA = {
    notifications: [
        { type: 'danger', message: 'CRITICAL: No Helmet detected at Stamping Press #3.', time: 'Yesterday, 4:15 PM' },
        { type: 'danger', message: 'CRITICAL: No Safety Vest detected in high-traffic forklift zone.', time: 'Yesterday, 2:30 PM' },
        { type: 'warning', message: 'Multiple workers detected without safety gloves at Assembly Line B.', time: 'Yesterday, 11:05 AM' },
        { type: 'success', message: 'System Scan Complete: 100% compliance detected during morning shift.', time: 'Yesterday, 8:00 AM' },
        { type: 'danger', message: 'CRITICAL: Fall detected near conveyor belt. Immediate check required.', time: 'Yesterday, 7:45 AM' },
        { type: 'info', message: 'Camera CAM-04 (Warehouse Entrance) appears offline.', time: 'Yesterday, 6:00 AM' }
    ],
    cameras: [
        { id: 1, name: 'Main Production Line', section: 'Production', status: 'compliant', image: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?q=80&w=800&auto=format&fit=crop', alerts: 0 },
        { id: 2, name: 'Warehouse Entrance', section: 'Logistics', status: 'compliant', image: 'https://images.unsplash.com/photo-1586528116311-08dd4c7f12da?q=80&w=800&auto=format&fit=crop', alerts: 0 },
        { id: 3, name: 'Stamping Press Area', section: 'Production', status: 'violation', image: 'https://images.unsplash.com/photo-1560264280-88b68371db39?q=80&w=800&auto=format&fit=crop', alerts: 1 },
        { id: 4, name: 'Loading Bay #2', section: 'Logistics', status: 'offline', image: 'https://images.unsplash.com/photo-1587293852726-70cdb121d176?q=80&w=800&auto=format&fit=crop', alerts: 0 },
        { id: 5, name: 'Assembly Line B', section: 'Production', status: 'compliant', image: 'https://images.unsplash.com/photo-1558992299-73b28b6b3671?q=80&w=800&auto=format&fit=crop', alerts: 0 },
        { id: 6, name: 'Quality Control Lab', section: 'Labs', status: 'compliant', image: 'https://images.unsplash.com/photo-1518152006812-edab29b069ac?q=80&w=800&auto=format&fit=crop', alerts: 0 }
    ],
    // Add more fake data for other pages as needed...
};


// --- 4. Widget Rendering Functions ---

/**
 * Populates the notifications widget with simulated data.
 * @param {HTMLElement} container - The DOM element to insert notifications into.
 */
function renderNotifications(container) {
    if (!container) return;

    const iconMap = {
        danger: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
        warning: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
        success: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
        info: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`
    };

    container.innerHTML = FAKE_DATA.notifications.map(notif => `
        <div class="notification-item">
            <div class="notification-icon icon-${notif.type}">
                ${iconMap[notif.type]}
            </div>
            <div class="notification-content">
                <p>${notif.message}</p>
                <span>${notif.time}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Populates a calendar widget for a given month and year.
 * @param {HTMLElement} calendarBody - The container for the calendar days.
 * @param {HTMLElement} monthYearDisplay - The element to display "Month Year".
 */
function renderCalendar(calendarBody, monthYearDisplay) {
    if (!calendarBody || !monthYearDisplay) return;

    const now = new Date();
    const month = now.getMonth();
    const year = now.getFullYear();

    monthYearDisplay.textContent = now.toLocaleString('default', { month: 'long', year: 'numeric' });

    const firstDayOfMonth = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    calendarBody.innerHTML = ''; // Clear previous content

    // Create day name headers
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(name => {
        const dayNameCell = document.createElement('div');
        dayNameCell.className = 'calendar-day-name';
        dayNameCell.textContent = name;
        calendarBody.appendChild(dayNameCell);
    });

    // Add empty cells for days before the 1st
    for (let i = 0; i < firstDayOfMonth; i++) {
        calendarBody.innerHTML += `<div class="calendar-day empty"></div>`;
    }

    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
        const dayCell = document.createElement('div');
        dayCell.className = 'calendar-day';
        dayCell.textContent = i;
        if (i === now.getDate()) {
            dayCell.classList.add('today');
        }
        // Add dummy event indicators
        if (i === 15 || i === 22) {
            dayCell.classList.add('has-event');
        }
        calendarBody.appendChild(dayCell);
    }
}


/**
 * Renders a chart using Chart.js.
 * @param {string} canvasId - The ID of the canvas element.
 * @param {object} chartConfig - The configuration object for Chart.js.
 */
function renderChart(canvasId, chartConfig) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (ctx) {
        new Chart(ctx, chartConfig);
    }
}


// --- 5. Page-Specific Initializers ---

function initializeIndexPage() {
    const notificationsContainer = document.getElementById('notifications-container');
    renderNotifications(notificationsContainer);
}

function initializeDashboardPage() {
    const calendarBody = document.getElementById('calendar-body');
    const monthYearDisplay = document.getElementById('month-year');
    renderCalendar(calendarBody, monthYearDisplay);

    // Dashboard-specific chart
    const dailyComplianceConfig = {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Compliance Rate %',
                data: [96.5, 97.2, 98.1, 95.5, 93.8, 94.1, 97.9],
                borderColor: 'hsl(221, 83%, 53%)',
                backgroundColor: 'hsla(221, 83%, 53%, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#fff',
                pointBorderColor: 'hsl(221, 83%, 53%)',
                pointHoverRadius: 7,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: false, min: 90, grid: { drawBorder: false } }, x: { grid: { display: false } } },
            plugins: { legend: { display: false } }
        }
    };
    renderChart('dailyComplianceChart', dailyComplianceConfig);
}

function initializeReportsPage() {
    const hourlyTrendsConfig = {
        type: 'bar',
        data: {
            labels: ['8am', '10am', '12pm', '2pm', '4pm', '6pm'],
            datasets: [{
                label: 'Violations',
                data: [5, 9, 4, 12, 10, 3],
                backgroundColor: 'hsla(3, 84%, 60%, 0.8)',
                borderRadius: 8,
                barThickness: 20,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { grid: { drawBorder: false } }, x: { grid: { display: false } } },
            plugins: { legend: { display: false } }
        }
    };

    const violationTypesConfig = {
        type: 'doughnut',
        data: {
            labels: ['No Helmet', 'No Vest', 'Zone Breach', 'No Gloves'],
            datasets: [{
                data: [45, 30, 15, 10],
                backgroundColor: ['hsl(3, 84%, 60%)', 'hsl(28, 95%, 58%)', 'hsl(262, 83%, 64%)', 'hsl(221, 83%, 53%)'],
                borderWidth: 5,
                borderColor: 'var(--card-bg)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: { legend: { position: 'bottom', labels: { padding: 20 } } }
        }
    };

    renderChart('hourlyTrendsChart', hourlyTrendsConfig);
    renderChart('violationTypesChart', violationTypesConfig);
}

function initializeHistoryPage() {
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = document.getElementById(tab.dataset.tab);

            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            tabContents.forEach(content => content.classList.remove('active'));
            target.classList.add('active');
        });
    });
}

function initializeCamerasPage() {
    const gridContainer = document.getElementById('camera-grid-container');
    const focusViewContainer = document.getElementById('focus-view-container');
    const focusImage = document.getElementById('focus-camera-image');
    const focusName = document.getElementById('focus-camera-name');
    const focusStatusText = document.getElementById('focus-camera-status-text');
    const focusStatusIndicator = document.getElementById('focus-camera-status-indicator');

    if (!gridContainer || !focusViewContainer) return;

    // Render grid
    gridContainer.innerHTML = FAKE_DATA.cameras.map(cam => `
        <div class="camera-grid-card" data-camera-id="${cam.id}">
            <img src="${cam.image}" class="video-thumbnail" alt="${cam.name}">
            <div class="grid-overlay">
                <div class="status-dot dot-${cam.status}"></div>
                <div>
                    <h5>${cam.name}</h5>
                    <span>${cam.section}</span>
                </div>
            </div>
        </div>
    `).join('');

    // Function to update the focus view
    function setFocusView(cameraId) {
        const cam = FAKE_DATA.cameras.find(c => c.id === cameraId);
        if (!cam) return;

        focusImage.src = cam.image;
        focusName.textContent = cam.name;
        focusStatusText.textContent = `Status: ${cam.status.charAt(0).toUpperCase() + cam.status.slice(1)}`;
        focusStatusIndicator.textContent = cam.status.toUpperCase();
        
        focusStatusIndicator.className = 'status-indicator'; // Reset classes
        focusStatusIndicator.classList.add(cam.status);
    }

    // Add click listeners to grid cards
    gridContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.camera-grid-card');
        if (card) {
            const camId = parseInt(card.dataset.cameraId, 10);
            setFocusView(camId);
        }
    });

    // Set initial focus view
    setFocusView(1);
}

function initializeSettingsPage() {
    const accordions = document.querySelectorAll('.accordion-header');

    accordions.forEach(accordion => {
        accordion.addEventListener('click', () => {
            const content = accordion.nextElementSibling;
            const icon = accordion.querySelector('.accordion-icon');
            
            accordion.classList.toggle('active');
            
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                icon.style.transform = 'rotate(0deg)';
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });
}