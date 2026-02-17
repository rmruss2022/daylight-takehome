/**
 * Admin Actions Customization
 * Removes the empty "None" option from the actions dropdown
 * and sets "Delete selected" as the default
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initActionDropdown);
    } else {
        initActionDropdown();
    }
    
    function initActionDropdown() {
        // Find the action dropdown
        const actionSelect = document.querySelector('select[name="action"]');
        
        if (!actionSelect) {
            return;
        }
        
        // Remove the "-----" (empty) option
        const emptyOption = actionSelect.querySelector('option[value=""]');
        if (emptyOption) {
            emptyOption.remove();
        }
        
        // Find and select the delete option
        const deleteOption = actionSelect.querySelector('option[value="delete_selected"]');
        if (deleteOption) {
            deleteOption.selected = true;
            actionSelect.value = 'delete_selected';
        }
        
        // Trigger change event to update any listeners
        actionSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
})();
