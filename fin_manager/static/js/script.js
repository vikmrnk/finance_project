// Make all form controls have the proper appearance
document.addEventListener('DOMContentLoaded', function() {
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