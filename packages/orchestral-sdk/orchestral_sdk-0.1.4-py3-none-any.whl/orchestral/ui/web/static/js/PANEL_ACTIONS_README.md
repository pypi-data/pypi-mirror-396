# Panel Actions Framework

A modular, extensible system for adding action buttons (copy, edit, regenerate, etc.) to Rich panels in the web UI.

## Architecture

The framework consists of three main concepts:

1. **Actions** - What buttons do (copy text, edit, regenerate, etc.)
2. **Panel Detectors** - How to identify different panel types (system prompt, user message, code block, etc.)
3. **Rules** - Which actions to apply to which panel types

## Usage

### Basic Setup (in app.js)

```javascript
// Initialize the panel actions manager
this.panelActions = new PanelActionsManager(this);

// Define rules for which actions apply to which panels
this.panelActionRules = [
    { panelType: 'system-prompt', actions: ['copy-text', 'edit-system-prompt'] },
    { panelType: 'user-message', actions: ['copy-text'] },
    { panelType: 'agent-message', actions: ['copy-text'] },
    { panelType: 'code-block', actions: ['copy-code'] },
];

// Apply actions when rendering content
this.panelActions.applyActions(contentDiv, this.panelActionRules);
```

### Built-in Actions

The following actions are pre-registered:

- **`copy-text`** - Copy clean text from panel (strips box-drawing characters)
- **`copy-code`** - Copy code from code blocks
- **`edit-system-prompt`** - Edit system prompt (opens modal)
- **`regenerate`** - Regenerate response (placeholder for future feature)
- **`branch`** - Branch conversation from this point (placeholder for future feature)

### Built-in Panel Detectors

The following panel types are pre-detected:

- **`system-prompt`** - System prompt panels
- **`user-message`** - User message panels
- **`agent-message`** - Agent/assistant response panels
- **`code-block`** - Code blocks
- **`any-panel`** - Any Rich panel (fallback)

## Extending the Framework

### Adding a New Action

```javascript
panelActions.registerAction('my-action', {
    icon: '🔥',  // Can be emoji or SVG
    successIcon: '✓',  // Optional - shown after successful action
    title: 'My Cool Action',
    className: 'panel-action-btn my-action-btn',  // CSS classes
    onClick: (button, panelElement) => {
        // Your action logic here
        console.log('Action clicked!');

        // For async actions with visual feedback:
        const originalIcon = button.innerHTML;
        button.innerHTML = button.dataset.successIcon;
        button.classList.add('success');

        setTimeout(() => {
            button.innerHTML = originalIcon;
            button.classList.remove('success');
        }, 2000);
    }
});
```

### Adding a New Panel Detector

```javascript
panelActions.registerPanelDetector('my-panel-type', (preElement) => {
    const text = preElement.textContent || preElement.innerText;
    const html = preElement.innerHTML;

    // Return true if this is your panel type
    return text.includes('MyPanelMarker');
});
```

### Using Your New Action

```javascript
// Add to rules
this.panelActionRules.push({
    panelType: 'my-panel-type',
    actions: ['my-action', 'copy-text']  // Can combine multiple actions
});
```

## Future Enhancements

Potential additions to consider:

1. **Position Control** - Allow actions on left/right/top/bottom
2. **Action Groups** - Dropdown menus for related actions
3. **Keyboard Shortcuts** - Hotkeys for common actions
4. **Action Conditions** - Only show actions based on state (e.g., "regenerate" only for latest message)
5. **Custom Icons** - Better icon system with customizable SVGs
6. **Animations** - Smooth transitions and hover effects
7. **Mobile Support** - Touch-friendly buttons for mobile devices

## Example: Adding a "Regenerate" Feature

```javascript
// 1. Register the action with actual implementation
panelActions.registerAction('regenerate', {
    icon: '🔄',
    title: 'Regenerate response',
    className: 'panel-action-btn regenerate-btn',
    onClick: async (button, panelElement) => {
        // Get the message ID from the panel (you'd need to add this)
        const messageId = panelElement.dataset.messageId;

        // Send regenerate request to backend
        this.wsManager.send('regenerate', { message_id: messageId });

        // Visual feedback
        button.innerHTML = '⏳';
        button.disabled = true;

        // Re-enable after completion (listen for server response)
    }
});

// 2. Add to rules - only for agent messages
this.panelActionRules.push({
    panelType: 'agent-message',
    actions: ['copy-text', 'regenerate', 'branch']
});

// 3. Add backend support in handlers
// (implement the 'regenerate' message handler)
```

## Migration from Legacy Code

The framework currently runs alongside the legacy `CopyCodeManager` and `SystemPromptEditManager` for backwards compatibility. Once the new system is fully tested, the legacy code can be removed.

### Migration Checklist

- [x] Create `PanelActionsManager`
- [x] Register default actions (copy-text, copy-code, edit-system-prompt)
- [x] Register default detectors (system-prompt, user-message, agent-message, code-block)
- [x] Create unified CSS for panel action buttons
- [x] Integrate into app.js with rules
- [ ] Test all actions work correctly
- [ ] Remove legacy `CopyCodeManager`
- [ ] Remove legacy `SystemPromptEditManager`
- [ ] Update CSS to remove legacy classes

## Styling

All panel action buttons use the `.panel-action-btn` base class with unified styling:

- Hidden by default (opacity: 0)
- Appear on panel hover (opacity: 1)
- Gold highlight on hover (#d7af00)
- Positioned absolutely in top-right by default
- Multiple buttons stack horizontally (nth-of-type positioning)

See `style.css` under "Panel Actions Framework" section for details.
