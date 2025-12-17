// Copy-code functionality for code blocks
// Detects code blocks in Rich HTML and adds copy buttons

class CopyCodeManager {
    constructor() {
        this.copyIconSVG = `
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5.5 3.5V2C5.5 1.44772 5.94772 1 6.5 1H13.5C14.0523 1 14.5 1.44772 14.5 2V11C14.5 11.5523 14.0523 12 13.5 12H12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <rect x="1.5" y="4.5" width="9" height="10" rx="1" stroke="currentColor" stroke-width="1.5"/>
            </svg>
        `;

        this.checkIconSVG = `
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 8L6.5 11.5L13 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }

    /**
     * Add copy buttons to all code blocks in the given element
     * @param {HTMLElement} element - Container element to search for code blocks
     */
    addCopyButtons(element) {
        // Find all <pre> tags
        const preElements = element.querySelectorAll('pre:not(.copy-buttons-processed)');

        preElements.forEach(pre => {
            pre.classList.add('copy-buttons-processed');

            // Get the HTML content
            const html = pre.innerHTML;

            // Rich code blocks have spans with background-color: #242933
            // Split by lines and identify code blocks
            const lines = html.split('\n');
            const codeBlockRanges = [];
            let inCodeBlock = false;
            let blockStart = -1;

            lines.forEach((line, index) => {
                const hasCodeBg = line.includes('background-color: #242933') ||
                                 line.includes('background-color:#242933');

                if (hasCodeBg && !inCodeBlock) {
                    // Start of code block
                    inCodeBlock = true;
                    blockStart = index;
                } else if (!hasCodeBg && inCodeBlock && line.trim() !== '') {
                    // End of code block (non-empty non-code line)
                    codeBlockRanges.push({start: blockStart, end: index - 1});
                    inCodeBlock = false;
                }
            });

            // Don't forget last block
            if (inCodeBlock) {
                codeBlockRanges.push({start: blockStart, end: lines.length - 1});
            }

            // No code blocks found
            if (codeBlockRanges.length === 0) {
                return;
            }

            // For each code block, insert a wrapper and button
            // We need to do this in reverse order to not mess up indices
            for (let i = codeBlockRanges.length - 1; i >= 0; i--) {
                const range = codeBlockRanges[i];

                // Extract the code block lines
                const codeHTMLLines = lines.slice(range.start, range.end + 1);
                const codeHTML = codeHTMLLines.join('\n');

                // Get the text content (without HTML tags) for copying
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = codeHTML;
                let codeText = tempDiv.textContent;

                // Clean up Rich formatting artifacts
                // Remove box-drawing characters and extra padding while preserving indentation
                codeText = this._cleanCodeText(codeText);

                // Create wrapper span for this code block
                const wrapperId = `code-block-${Date.now()}-${i}`;
                const wrapperStart = `<span class="code-block-wrapper" id="${wrapperId}" style="position: relative; display: inline-block;">`;
                const wrapperEnd = `</span>`;

                // Replace the lines with wrapped version
                lines.splice(range.start, range.end - range.start + 1, wrapperStart + codeHTML + wrapperEnd);

                // After DOM update, add button
                setTimeout(() => {
                    const wrapper = pre.querySelector(`#${wrapperId}`);
                    if (!wrapper) return;

                    // Detect if this is inside a tool panel (double wall)
                    const isInToolPanel = this._isInToolPanel(codeHTML);
                    const copyBtn = this._createCopyButton(codeText, isInToolPanel);
                    wrapper.appendChild(copyBtn);
                }, 0);
            }

            // Update pre with wrapped content
            pre.innerHTML = lines.join('\n');
        });
    }

    /**
     * Clean code text by removing Rich formatting artifacts
     * @private
     */
    _cleanCodeText(codeText) {
        let codeLines = codeText.split('\n');

        // First pass: remove box characters and identify content lines
        codeLines = codeLines.map(line => {
            // Remove box-drawing characters
            line = line.replace(/│/g, '');
            return line;
        }).filter(line => line.trim().length > 0); // Remove empty lines

        // Second pass: find minimum indentation (excluding empty lines)
        const minIndent = Math.min(...codeLines.map(line => {
            const match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        }));

        // Third pass: remove common indentation and trailing whitespace
        return codeLines
            .map(line => line.substring(minIndent).trimEnd())
            .join('\n')
            .trim();
    }

    /**
     * Detect if code block is inside a tool panel (has double walls)
     * @private
     */
    _isInToolPanel(codeHTML) {
        // Tool panels have "│ │" pattern (double wall with space)
        // Regular agent content has just "│" (single wall)
        const hasDoubleWall = codeHTML.includes('│ │');

        // Debug logging
        console.log('[CopyCode] Checking for tool panel:', {
            hasDoubleWall,
            sample: codeHTML.substring(0, 100)
        });

        return hasDoubleWall;
    }

    /**
     * Create a copy button element
     * @private
     */
    _createCopyButton(codeText, isInToolPanel = false) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        if (isInToolPanel) {
            copyBtn.classList.add('tool-panel-offset');
        }
        copyBtn.innerHTML = this.copyIconSVG;
        copyBtn.title = 'Copy code';

        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(codeText);

                // Visual feedback
                copyBtn.innerHTML = this.checkIconSVG;
                copyBtn.classList.add('copied');

                // Reset after 2 seconds
                setTimeout(() => {
                    copyBtn.innerHTML = this.copyIconSVG;
                    copyBtn.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
            }
        });

        return copyBtn;
    }
}

// Export for use in main app
window.CopyCodeManager = CopyCodeManager;
