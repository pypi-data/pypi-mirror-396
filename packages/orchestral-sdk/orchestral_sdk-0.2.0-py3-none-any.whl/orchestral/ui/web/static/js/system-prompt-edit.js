// System Prompt Edit Button
// Adds edit button to system prompt panels in Rich HTML

class SystemPromptEditManager {
    constructor(orchestralUI) {
        this.orchestralUI = orchestralUI;

        this.gearIconHTML = `⚙`;
    }

    /**
     * Add edit buttons to all system prompt panels in the given element
     * @param {HTMLElement} element - Container element to search for system prompts
     */
    addEditButtons(element) {
        // Find all <pre> tags that haven't been processed
        const preElements = element.querySelectorAll('pre:not(.system-prompt-processed)');

        preElements.forEach(pre => {
            const html = pre.innerHTML;
            const text = pre.textContent || pre.innerText;

            // Check if this is a system prompt panel
            // System prompts have title "System" in the panel header
            // Try multiple detection methods
            const isSystemPrompt =
                html.includes('>System<') ||
                html.includes('>system<') ||
                text.includes('System') ||
                text.includes('┌') && (text.includes('System') || text.includes('system'));

            console.log('[SystemPromptEdit] Checking pre element:', {
                isSystemPrompt,
                textSample: text.substring(0, 100),
                htmlSample: html.substring(0, 200)
            });

            if (!isSystemPrompt) {
                return;
            }

            console.log('[SystemPromptEdit] Found system prompt! Adding edit button');

            // Mark as processed
            pre.classList.add('system-prompt-processed');

            // Add a wrapper with position relative for absolute positioning of button
            const wrapper = document.createElement('div');
            wrapper.className = 'system-prompt-wrapper';
            wrapper.style.position = 'relative';
            wrapper.style.display = 'inline-block';
            wrapper.style.width = '100%';

            // Move the pre into the wrapper
            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(pre);

            // Create edit button
            const editBtn = this._createEditButton();
            wrapper.appendChild(editBtn);
        });
    }

    /**
     * Create an edit button element
     * @private
     */
    _createEditButton() {
        const editBtn = document.createElement('button');
        editBtn.className = 'edit-system-prompt-btn';
        editBtn.innerHTML = this.gearIconHTML;
        editBtn.title = 'Edit system prompt';

        editBtn.addEventListener('click', () => {
            // Call the orchestralUI method to show the modal
            if (this.orchestralUI && this.orchestralUI.showSystemPromptModal) {
                this.orchestralUI.showSystemPromptModal();
            }
        });

        return editBtn;
    }
}

// Export for use in main app
window.SystemPromptEditManager = SystemPromptEditManager;
