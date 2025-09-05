// Main JavaScript for Kubwa Closet

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Form submission loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });

    // Image preview for file inputs
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                previewImage(file, input);
            }
        });
    });

    // Search functionality enhancements
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Add search icon animation
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', function() {
                const searchBtn = searchForm.querySelector('button[type="submit"]');
                if (searchBtn) {
                    const icon = searchBtn.querySelector('i');
                    if (icon) {
                        icon.classList.add('fa-spin');
                        setTimeout(() => icon.classList.remove('fa-spin'), 1000);
                    }
                }
            });
        }
    }

    // Modal enhancements
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                }
            });
        });

        const lazyImages = document.querySelectorAll('img.lazy[data-src]');
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Price input formatting
    const priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Utility Functions

function previewImage(file, inputElement) {
    if (!file.type.startsWith('image/')) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        // Remove existing preview
        const existingPreview = document.querySelector('#image-preview');
        if (existingPreview) {
            existingPreview.remove();
        }

        // Create new preview
        const preview = document.createElement('div');
        preview.id = 'image-preview';
        preview.className = 'mt-3';
        preview.innerHTML = `
            <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <div class="small text-muted mt-1">Preview: ${file.name}</div>
        `;

        // Insert after the input safely
        if (inputElement.parentNode) {
            inputElement.parentNode.insertBefore(preview, inputElement.nextSibling);
        }
    };
    reader.readAsDataURL(file);
}

function showToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to page
    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (toast.parentNode) {
            const bsAlert = new bootstrap.Alert(toast);
            bsAlert.close();
        }
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

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

// Export functions for use in other scripts
window.KubwaCloset = {
    previewImage,
    showToast,
    formatCurrency,
    debounce
};
