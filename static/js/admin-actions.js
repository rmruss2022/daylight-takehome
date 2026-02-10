/**
 * Admin Actions Customization
 * STRIPPED: All JavaScript manipulation disabled to reset to base HTML behavior
 */

/*
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
            console.log('Action dropdown not found on this page');
            return;
        }
        
        console.log('Customizing action dropdown...');
        
        // Remove the "-----" (empty) option
        const emptyOption = actionSelect.querySelector('option[value=""]');
        if (emptyOption) {
            emptyOption.remove();
            console.log('✓ Removed empty option');
        }
        
        // Find and select the delete option
        const deleteOption = actionSelect.querySelector('option[value="delete_selected"]');
        if (deleteOption) {
            deleteOption.selected = true;
            actionSelect.value = 'delete_selected';
            console.log('✓ Set "delete_selected" as default');
        }
        
        // Trigger change event to update any listeners
        actionSelect.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Log the final state for debugging
        console.log('Action dropdown state:');
        console.log('  Options count:', actionSelect.options.length);
        console.log('  Selected value:', actionSelect.value);
        console.log('  Selected text:', actionSelect.options[actionSelect.selectedIndex]?.text);
        
        // Log computed styles for debugging
        const computed = window.getComputedStyle(actionSelect);
        console.log('  Text color:', computed.color);
        console.log('  -webkit-text-fill-color:', computed.webkitTextFillColor);
        console.log('  Background:', computed.backgroundColor);
    }
    
    console.log('admin-actions.js loaded');
})();
*/

console.log('admin-actions.js loaded (all customization disabled)');
