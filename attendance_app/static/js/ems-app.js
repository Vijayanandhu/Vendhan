// EMS 2.0 JavaScript Application

// Global variables
let currentUser = null;
let unreadMessageCount = 0;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize real-time clock
    initializeClock();
    
    // Initialize message system
    initializeMessages();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize data tables
    initializeDataTables();
    
    // Initialize auto-save functionality
    initializeAutoSave();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Real-time clock functionality
function initializeClock() {
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        updateClock();
        setInterval(updateClock, 1000);
    }
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const dateString = now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        clockElement.innerHTML = `
            <div class="clock-time">${timeString}</div>
            <div class="clock-date">${dateString}</div>
        `;
    }
}

// Message system initialization
function initializeMessages() {
    // Check for unread messages
    checkUnreadMessages();
    
    // Set up periodic check for new messages
    setInterval(checkUnreadMessages, 30000); // Check every 30 seconds
}

function checkUnreadMessages() {
    fetch('/api/messages/unread-count')
        .then(response => response.json())
        .then(data => {
            updateUnreadMessageBadge(data.count);
        })
        .catch(error => {
            console.log('Could not check unread messages:', error);
        });
}

function updateUnreadMessageBadge(count) {
    const badge = document.getElementById('unread-count');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
    unreadMessageCount = count;
}

// Form validation initialization
function initializeFormValidations() {
    // Add custom validation styles
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for specific fields
    initializeFieldValidations();
}

function initializeFieldValidations() {
    // Email validation
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        field.addEventListener('blur', validateEmail);
    });
    
    // Password strength validation
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        field.addEventListener('input', validatePasswordStrength);
    });
    
    // Date validation
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        field.addEventListener('change', validateDate);
    });
}

function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(email);
    
    updateFieldValidation(event.target, isValid, 'Please enter a valid email address');
}

function validatePasswordStrength(event) {
    const password = event.target.value;
    const strength = calculatePasswordStrength(password);
    
    // Update password strength indicator if it exists
    const strengthIndicator = document.getElementById('password-strength');
    if (strengthIndicator) {
        updatePasswordStrengthIndicator(strengthIndicator, strength);
    }
}

function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
}

function updatePasswordStrengthIndicator(indicator, strength) {
    const strengthTexts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    indicator.textContent = strengthTexts[strength] || 'Very Weak';
    indicator.className = `badge bg-${strengthColors[strength] || 'danger'}`;
}

function validateDate(event) {
    const date = new Date(event.target.value);
    const today = new Date();
    const isValid = date >= today;
    
    updateFieldValidation(event.target, isValid, 'Date cannot be in the past');
}

function updateFieldValidation(field, isValid, errorMessage) {
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        if (feedback) {
            feedback.textContent = errorMessage;
        }
    }
}

// Data tables initialization
function initializeDataTables() {
    // Add search functionality to tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            if (table) {
                filterTable(table, this.value);
            }
        });
    });
    
    // Add sorting functionality
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            sortTable(table, columnIndex);
        });
    });
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers first
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }
        
        // Try to parse as dates
        const aDate = new Date(aText);
        const bDate = new Date(bText);
        
        if (!isNaN(aDate.getTime()) && !isNaN(bDate.getTime())) {
            return aDate - bDate;
        }
        
        // Default to string comparison
        return aText.localeCompare(bText);
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Auto-save functionality
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                autoSaveForm(form);
            }, 2000));
        });
    });
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Save to localStorage as backup
    const formId = form.id || 'auto-save-form';
    localStorage.setItem(`auto-save-${formId}`, JSON.stringify(data));
    
    // Show auto-save indicator
    showAutoSaveIndicator();
}

function showAutoSaveIndicator() {
    const indicator = document.getElementById('auto-save-indicator');
    if (indicator) {
        indicator.style.display = 'block';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 2000);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="spinner-green mx-auto"></div>';
    }
}

function hideLoading(element, originalContent) {
    if (element) {
        element.innerHTML = originalContent;
    }
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Clock in/out functionality
function clockIn(projectId = null) {
    const data = projectId ? { project_id: projectId } : {};
    
    apiRequest('/api/attendance/clock-in', {
        method: 'POST',
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.success) {
            showNotification('Clocked in successfully!', 'success');
            updateAttendanceStatus();
        } else {
            showNotification(response.message || 'Failed to clock in', 'error');
        }
    })
    .catch(error => {
        showNotification('Error clocking in', 'error');
        console.error('Clock in error:', error);
    });
}

function clockOut(breakDuration = 0, notes = '') {
    const data = {
        break_duration: breakDuration,
        notes: notes
    };
    
    apiRequest('/api/attendance/clock-out', {
        method: 'POST',
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.success) {
            showNotification('Clocked out successfully!', 'success');
            updateAttendanceStatus();
        } else {
            showNotification(response.message || 'Failed to clock out', 'error');
        }
    })
    .catch(error => {
        showNotification('Error clocking out', 'error');
        console.error('Clock out error:', error);
    });
}

function updateAttendanceStatus() {
    apiRequest('/api/attendance/today')
        .then(data => {
            const statusElement = document.getElementById('attendance-status');
            if (statusElement) {
                updateAttendanceDisplay(statusElement, data);
            }
        })
        .catch(error => {
            console.error('Error updating attendance status:', error);
        });
}

function updateAttendanceDisplay(element, data) {
    let statusHtml = '';
    
    if (data.clocked_in && !data.clocked_out) {
        statusHtml = `
            <div class="alert alert-success">
                <i class="fas fa-clock me-2"></i>
                Clocked in at ${formatTime(data.clock_in_time)}
                <button class="btn btn-sm btn-outline-success ms-2" onclick="showClockOutModal()">
                    Clock Out
                </button>
            </div>
        `;
    } else if (data.clocked_out) {
        statusHtml = `
            <div class="alert alert-info">
                <i class="fas fa-check-circle me-2"></i>
                Work completed for today (${data.total_hours} hours)
            </div>
        `;
    } else {
        statusHtml = `
            <div class="alert alert-warning">
                <i class="fas fa-play-circle me-2"></i>
                Ready to start work
                <button class="btn btn-sm btn-outline-primary ms-2" onclick="showClockInModal()">
                    Clock In
                </button>
            </div>
        `;
    }
    
    element.innerHTML = statusHtml;
}

function formatTime(timeString) {
    if (!timeString) return '';
    const date = new Date(timeString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to notification container or body
    const container = document.getElementById('notification-container') || document.body;
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Modal helpers
function showClockInModal() {
    const modal = new bootstrap.Modal(document.getElementById('clockInModal'));
    modal.show();
}

function showClockOutModal() {
    const modal = new bootstrap.Modal(document.getElementById('clockOutModal'));
    modal.show();
}

// Export functions for global access
window.EMS = {
    clockIn,
    clockOut,
    showNotification,
    apiRequest,
    updateAttendanceStatus,
    showClockInModal,
    showClockOutModal
};