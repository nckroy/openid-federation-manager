// Copyright (c) 2025 Internet2
// Licensed under the Apache License, Version 2.0 - see LICENSE file for details

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.minWidth = '300px';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Form validation
const registerForm = document.querySelector('.register-form');
if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        const entityId = document.getElementById('entity_id').value;
        const entityType = document.getElementById('entity_type').value;

        if (!entityId.startsWith('https://')) {
            e.preventDefault();
            showNotification('Entity ID must start with https://', 'error');
            return false;
        }

        if (!entityType) {
            e.preventDefault();
            showNotification('Please select an entity type', 'error');
            return false;
        }
    });
}

// Table sorting (if needed in future)
function sortTable(table, column, asc = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent;
        const bVal = b.cells[column].textContent;

        return asc
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
    });

    rows.forEach(row => tbody.appendChild(row));
}

// Confirm actions (can be extended for delete operations)
function confirmAction(message) {
    return confirm(message);
}

// Copy to clipboard helper
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy', 'error');
    }

    document.body.removeChild(textarea);
}

// Format JSON for display
function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

// Truncate long strings
function truncate(str, length = 50) {
    if (str.length <= length) return str;
    return str.substring(0, length) + '...';
}

// Console log for debugging (only in development)
if (window.location.hostname === 'localhost') {
    console.log('OpenID Federation Manager UI loaded');
}
