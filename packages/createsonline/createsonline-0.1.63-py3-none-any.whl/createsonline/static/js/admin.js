// CREATESONLINE Admin Panel JavaScript v0.1.6

class CreatesonlineAdmin {
    constructor() {
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupForms();
        this.setupTables();
        this.setupModals();
        this.setupNotifications();
    }

    setupNavigation() {
        // Sidebar toggle for mobile
        const toggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.admin-sidebar');
        
        if (toggle && sidebar) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }

        // Active menu item
        const currentPath = window.location.pathname;
        document.querySelectorAll('.admin-sidebar li').forEach(item => {
            if (item.dataset.path === currentPath) {
                item.classList.add('active');
            }
        });
    }

    setupForms() {
        // Form validation
        document.querySelectorAll('.admin-form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });

        // Auto-save functionality
        document.querySelectorAll('[data-autosave]').forEach(input => {
            let timeout;
            input.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => this.autoSave(input), 1000);
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearError(input);
            }
        });

        return isValid;
    }

    showError(input, message) {
        const error = input.nextElementSibling;
        if (error && error.classList.contains('error-message')) {
            error.textContent = message;
        } else {
            const errorEl = document.createElement('span');
            errorEl.className = 'error-message';
            errorEl.textContent = message;
            errorEl.style.color = '#ef4444';
            errorEl.style.fontSize = '0.875rem';
            input.parentNode.insertBefore(errorEl, input.nextSibling);
        }
        input.style.borderColor = '#ef4444';
    }

    clearError(input) {
        const error = input.nextElementSibling;
        if (error && error.classList.contains('error-message')) {
            error.remove();
        }
        input.style.borderColor = '';
    }

    setupTables() {
        // Sortable tables
        document.querySelectorAll('.admin-table th[data-sort]').forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(header);
            });
        });

        // Row selection
        document.querySelectorAll('.admin-table input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const row = e.target.closest('tr');
                row.classList.toggle('selected', e.target.checked);
            });
        });

        // Bulk actions
        const bulkSelect = document.getElementById('bulk-select');
        if (bulkSelect) {
            bulkSelect.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.admin-table tbody input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    cb.checked = e.target.checked;
                    cb.closest('tr').classList.toggle('selected', e.target.checked);
                });
            });
        }
    }

    sortTable(header) {
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const column = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aValue = a.children[column].textContent.trim();
            const bValue = b.children[column].textContent.trim();
            
            if (!isNaN(aValue) && !isNaN(bValue)) {
                return isAscending ? aValue - bValue : bValue - aValue;
            }
            
            return isAscending 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });

        rows.forEach(row => tbody.appendChild(row));

        // Toggle sort direction
        header.classList.toggle('sort-asc', !isAscending);
        header.classList.toggle('sort-desc', isAscending);
    }

    setupModals() {
        // Open modal
        document.querySelectorAll('[data-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.add('active');
                }
            });
        });

        // Close modal
        document.querySelectorAll('.modal-close, .modal-backdrop').forEach(close => {
            close.addEventListener('click', () => {
                close.closest('.modal').classList.remove('active');
            });
        });
    }

    setupNotifications() {
        // Auto-dismiss notifications
        document.querySelectorAll('.admin-notification').forEach(notification => {
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
        });
    }

    autoSave(input) {
        const data = {
            field: input.name,
            value: input.value
        };

        fetch('/admin/autosave', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Auto-saved', 'success');
        })
        .catch(error => {
            console.error('Auto-save failed:', error);
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `admin-notification admin-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#10b981' : '#2563eb'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            transition: opacity 0.3s;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // API Methods
    async fetchData(endpoint) {
        try {
            const response = await fetch(endpoint);
            return await response.json();
        } catch (error) {
            this.showNotification('Failed to fetch data', 'error');
            throw error;
        }
    }

    async saveData(endpoint, data) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            this.showNotification('Failed to save data', 'error');
            throw error;
        }
    }

    async deleteData(endpoint) {
        try {
            const response = await fetch(endpoint, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            this.showNotification('Failed to delete data', 'error');
            throw error;
        }
    }
}

// Initialize admin panel when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new CreatesonlineAdmin();
    console.log('CREATESONLINE Admin Panel v0.1.6 initialized');
});
