/**
 * SkillFleet — Admin Dashboard Charts
 * Uses Chart.js to render analytics on the admin dashboard
 * Supports dynamic updating when toggling between light and dark modes.
 */

document.addEventListener('DOMContentLoaded', function () {
    let statusChart = null;
    let serviceChart = null;

    function getThemeColors() {
        const theme = document.documentElement.getAttribute('data-bs-theme');
        if (theme === 'dark') {
            return {
                text: '#94a3b8',       // slate-400
                grid: 'rgba(255, 255, 255, 0.08)'
            };
        } else {
            return {
                text: '#64748b',       // slate-500
                grid: 'rgba(0, 0, 0, 0.05)'
            };
        }
    }

    // Fetch stats from API
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            const colors = getThemeColors();
            statusChart = renderStatusChart(data.requests_by_status, colors);
            serviceChart = renderServiceChart(data.requests_per_service, colors);

            // Listen to theme changes to dynamically update charts color scheme
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                themeToggle.addEventListener('click', () => {
                    // Give a tiny timeout for data-bs-theme to change
                    setTimeout(() => {
                        const newColors = getThemeColors();
                        if (serviceChart) {
                            serviceChart.options.scales.x.ticks.color = newColors.text;
                            serviceChart.options.scales.y.ticks.color = newColors.text;
                            serviceChart.options.scales.y.grid.color = newColors.grid;
                            serviceChart.update();
                        }
                        if (statusChart) {
                            statusChart.options.plugins.legend.labels.color = newColors.text;
                            statusChart.update();
                        }
                    }, 50);
                });
            }
        })
        .catch(err => {
            console.error('Failed to load chart data:', err);
        });
});


/**
 * Doughnut chart — Requests by Status
 */
function renderStatusChart(data, colors) {
    const ctx = document.getElementById('requestsStatusChart');
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#d97706',  // Requested - amber
                    '#4f46e5',  // Assigned - indigo
                    '#059669',  // Closed - emerald
                ],
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.text,
                        padding: 20,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 13,
                            weight: '500'
                        },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                }
            }
        }
    });
}


/**
 * Bar chart — Requests per Service
 */
function renderServiceChart(data, colors) {
    const ctx = document.getElementById('requestsServiceChart');
    if (!ctx) return null;

    // Generate gradient colors
    const barColors = data.labels.map((_, i) => {
        const hue = (i * 45 + 230) % 360;
        return `hsl(${hue}, 65%, 55%)`;
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Requests',
                data: data.data,
                backgroundColor: barColors,
                borderRadius: 8,
                borderSkipped: false,
                barThickness: 40,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: colors.text,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    },
                    grid: {
                        color: colors.grid
                    }
                },
                x: {
                    ticks: {
                        color: colors.text,
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}
