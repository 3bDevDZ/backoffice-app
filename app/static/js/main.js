/**
 * Main JavaScript file for CommerceFlow application
 * Handles common frontend functionality
 */

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize i18n if available
    if (window.i18n) {
        window.i18n.initI18n();
    }
    
    // Initialize tooltips if using a tooltip library
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
});

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Add tooltip functionality if needed
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            // Tooltip implementation
        });
    });
}

/**
 * Initialize modals
 */
function initializeModals() {
    // Open modal
    document.querySelectorAll('[data-modal-open]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal-open');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
            }
        });
    });
    
    // Close modal
    document.querySelectorAll('[data-modal-close]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Validate form
 * @param {HTMLFormElement} form - Form element to validate
 * @returns {boolean} True if valid
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

/**
 * Initialize real-time updates (for dashboard, stock levels, etc.)
 */
function initializeRealTimeUpdates() {
    // Check if we're on a page that needs real-time updates
    const dashboard = document.querySelector('[data-realtime="dashboard"]');
    const stock = document.querySelector('[data-realtime="stock"]');
    
    if (dashboard) {
        // Set up dashboard refresh interval
        setInterval(() => {
            refreshDashboard();
        }, 30000); // Refresh every 30 seconds
    }
    
    if (stock) {
        // Set up stock level refresh interval
        setInterval(() => {
            refreshStockLevels();
        }, 5000); // Refresh every 5 seconds
    }
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    if (window.api && window.api.get) {
        window.api.get('/api/dashboard/kpi')
            .then(data => {
                updateDashboardUI(data);
            })
            .catch(error => {
                console.error('Failed to refresh dashboard:', error);
            });
    }
}

/**
 * Refresh stock levels
 */
function refreshStockLevels() {
    // Get current filter parameters from URL or form
    const urlParams = new URLSearchParams(window.location.search);
    const params = new URLSearchParams({
        page: urlParams.get('page') || '1',
        page_size: urlParams.get('per_page') || '50',
        search: urlParams.get('search') || '',
        location_id: urlParams.get('location_id') || '',
        min_quantity: urlParams.get('min_quantity') || '',
        include_zero: urlParams.get('include_zero') || 'false'
    });
    
    // Use frontend route instead of API
    fetch(`/stock/data/levels?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                updateStockUI(data.data);
            }
        })
        .catch(error => {
            console.error('Failed to refresh stock levels:', error);
        });
    
    // Also refresh alerts count
    fetch('/stock/data/alerts?page=1&page_size=10')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                updateStockAlertsCount(data.data);
            }
        })
        .catch(error => {
            console.error('Failed to refresh stock alerts:', error);
        });
}

/**
 * Update dashboard UI with new data
 * @param {Object} data - Dashboard KPI data
 */
function updateDashboardUI(data) {
    // Update dashboard metrics
    const revenueEl = document.querySelector('[data-metric="revenue"]');
    if (revenueEl && data.revenue) {
        revenueEl.textContent = formatCurrency(data.revenue);
    }
    
    const stockAlertsEl = document.querySelector('[data-metric="stock-alerts"]');
    if (stockAlertsEl && data.stock_alerts !== undefined) {
        stockAlertsEl.textContent = data.stock_alerts;
    }
    
    const activeOrdersEl = document.querySelector('[data-metric="active-orders"]');
    if (activeOrdersEl && data.active_orders !== undefined) {
        activeOrdersEl.textContent = data.active_orders;
    }
}

/**
 * Update stock UI with new data
 * @param {Object} data - Stock levels response data with items and pagination
 */
function updateStockUI(data) {
    if (!data || !data.items) return;
    
    const items = data.items;
    
    // Update stats cards
    const totalItemsEl = document.getElementById('total-items');
    if (totalItemsEl) {
        totalItemsEl.textContent = data.pagination?.total || items.length;
    }
    
    const outOfStockEl = document.getElementById('out-of-stock');
    if (outOfStockEl) {
        const outOfStockCount = items.filter(item => item.is_out_of_stock).length;
        outOfStockEl.textContent = outOfStockCount;
    }
    
    const lowStockEl = document.getElementById('low-stock');
    if (lowStockEl) {
        const lowStockCount = items.filter(item => item.is_below_minimum && !item.is_out_of_stock).length;
        lowStockEl.textContent = lowStockCount;
    }
    
    // Update stock table rows
    const tbody = document.querySelector('table tbody');
    if (tbody && items.length > 0) {
        // Update existing rows or create new ones
        items.forEach((item, index) => {
            const row = tbody.children[index];
            if (row) {
                // Update existing row
                updateStockRow(row, item);
            } else {
                // Create new row
                const newRow = createStockRow(item);
                tbody.appendChild(newRow);
            }
        });
        
        // Remove extra rows if items decreased
        while (tbody.children.length > items.length) {
            tbody.removeChild(tbody.lastChild);
        }
    }
}

/**
 * Update a stock table row with new data
 * @param {HTMLElement} row - Table row element
 * @param {Object} item - Stock item data
 */
function updateStockRow(row, item) {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 7) {
        // Update quantity cells with animation if changed
        const physicalCell = cells[2];
        const reservedCell = cells[3];
        const availableCell = cells[4];
        
        if (physicalCell && physicalCell.textContent.trim() !== item.physical_quantity.toFixed(2)) {
            animateValueChange(physicalCell, item.physical_quantity.toFixed(2));
        }
        if (reservedCell && reservedCell.textContent.trim() !== item.reserved_quantity.toFixed(2)) {
            animateValueChange(reservedCell, item.reserved_quantity.toFixed(2));
        }
        if (availableCell) {
            const newValue = item.available_quantity.toFixed(2);
            if (availableCell.textContent.trim() !== newValue) {
                animateValueChange(availableCell, newValue);
                // Update color based on availability
                availableCell.className = availableCell.className.replace(/text-(red|orange|green)-600/g, '');
                if (item.available_quantity <= 0) {
                    availableCell.classList.add('text-red-600');
                } else if (item.is_below_minimum) {
                    availableCell.classList.add('text-orange-600');
                } else {
                    availableCell.classList.add('text-green-600');
                }
            }
        }
        
        // Update status badge
        const statusCell = cells[6];
        if (statusCell) {
            updateStatusBadge(statusCell, item);
        }
    }
}

/**
 * Create a new stock table row
 * @param {Object} item - Stock item data
 * @returns {HTMLElement} Table row element
 */
function createStockRow(item) {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50';
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm font-medium text-gray-900">${item.product_name || 'N/A'}</div>
            <div class="text-sm text-gray-500">${item.product_code}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">${item.location_name || 'N/A'}</div>
            <div class="text-sm text-gray-500">${item.location_code}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.physical_quantity.toFixed(2)}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.reserved_quantity.toFixed(2)}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium ${getAvailabilityColorClass(item)}">${item.available_quantity.toFixed(2)}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item.min_stock ? item.min_stock.toFixed(2) : '-'}</td>
        <td class="px-6 py-4 whitespace-nowrap">${getStatusBadgeHTML(item)}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
            <a href="/stock/movements?product_id=${item.product_id}&location_id=${item.location_id}" class="text-indigo-600 hover:text-indigo-900">View Movements</a>
        </td>
    `;
    return row;
}

/**
 * Get availability color class based on stock status
 */
function getAvailabilityColorClass(item) {
    if (item.available_quantity <= 0) return 'text-red-600';
    if (item.is_below_minimum) return 'text-orange-600';
    return 'text-green-600';
}

/**
 * Get status badge HTML
 */
function getStatusBadgeHTML(item) {
    if (item.is_out_of_stock) {
        return '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Out of Stock</span>';
    } else if (item.is_below_minimum) {
        return '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">Low Stock</span>';
    } else if (item.is_overstock) {
        return '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Overstock</span>';
    } else {
        return '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">OK</span>';
    }
}

/**
 * Update status badge in a cell
 */
function updateStatusBadge(cell, item) {
    cell.innerHTML = getStatusBadgeHTML(item);
}

/**
 * Animate value change in a cell
 */
function animateValueChange(cell, newValue) {
    cell.classList.add('transition-all', 'duration-300');
    cell.style.backgroundColor = '#fef3c7'; // yellow-100
    cell.textContent = newValue;
    setTimeout(() => {
        cell.style.backgroundColor = '';
        setTimeout(() => {
            cell.classList.remove('transition-all', 'duration-300');
        }, 300);
    }, 300);
}

/**
 * Update stock alerts count
 */
function updateStockAlertsCount(data) {
    const alertsCountEl = document.getElementById('active-alerts');
    if (alertsCountEl && data.pagination) {
        alertsCountEl.textContent = data.pagination.total || data.items?.length || 0;
    }
}

/**
 * Format currency value
 * @param {number} value - Currency value
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

