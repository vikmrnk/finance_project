// Make all form controls have the proper appearance
document.addEventListener('DOMContentLoaded', function() {
    // Disable browser-native validation popups for consistent UI messages.
    document.querySelectorAll('form').forEach(function(form) {
        form.setAttribute('novalidate', 'novalidate');
    });

    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarToggle = document.getElementById('sidebarCollapse');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    const mobileBreakpoint = 991;

    function isMobileView() {
        return window.innerWidth <= mobileBreakpoint;
    }

    function closeMobileSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('mobile-open');
        document.body.classList.remove('sidebar-open');
        if (sidebarBackdrop) {
            sidebarBackdrop.classList.remove('show');
        }
    }

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (isMobileView()) {
                sidebar.classList.toggle('mobile-open');
                document.body.classList.toggle('sidebar-open');
                if (sidebarBackdrop) {
                    sidebarBackdrop.classList.toggle('show');
                }
            } else {
                sidebar.classList.toggle('active');
                if (content) {
                    content.classList.toggle('active');
                }
            }
        });

        window.addEventListener('resize', function() {
            if (!isMobileView()) {
                closeMobileSidebar();
            } else {
                if (content) {
                    content.classList.remove('active');
                }
            }
        });

        if (sidebarBackdrop) {
            sidebarBackdrop.addEventListener('click', closeMobileSidebar);
        }

        sidebar.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                if (isMobileView()) {
                    closeMobileSidebar();
                }
            });
        });
    }

    // Find all select elements and make sure they have the proper classes
    const selectElements = document.querySelectorAll('select');
    selectElements.forEach(function(select) {
        select.classList.add('form-select');
        
        // Make sure the element has at least one option
        if (select.options.length === 0) {
            const defaultOption = document.createElement('option');
            defaultOption.text = 'No options available';
            defaultOption.value = '';
            defaultOption.disabled = true;
            defaultOption.selected = true;
            select.appendChild(defaultOption);
        }
    });

    // Make text-like inputs and textareas use consistent Bootstrap styling.
    const styledInputs = document.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]), textarea');
    styledInputs.forEach(function(element) {
        element.classList.add('form-control');
    });
    
    // Fix all number inputs to have step="any" for decimal values
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        if (!input.hasAttribute('step')) {
            input.setAttribute('step', 'any');
        }
    });
    
    // Fix all date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            const today = new Date();
            const year = today.getFullYear();
            let month = today.getMonth() + 1;
            let day = today.getDate();
            
            // Ensure the month and day are formatted with leading zeros if needed
            month = month < 10 ? '0' + month : month;
            day = day < 10 ? '0' + day : day;
            
            input.value = `${year}-${month}-${day}`;
        }
    });
}); 