import json
from typing import List, Optional, Any, Dict, TypedDict, Union
import gradio as gr

# --- Types ---

class SelectItem(TypedDict):
    label: str
    value: str
    icon: Optional[str]
    size: Optional[str]  # e.g. "32px", "2rem"

class SelectCategory(TypedDict):
    label: str
    icon: Optional[str]
    children: List[SelectItem]

# --- Styles (Converted from Tailwind to CSS) ---

CSS = """
/* Scoped styles for CategorizedSelect */
.gs-wrapper {
    position: relative;
    font-family: 'Inter', -apple-system, sans-serif;
    width: 100%;
    color: #1f2937;
}

/* Input Area */
.gs-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.gs-input {
    width: 100%;
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    padding: 0.5rem 0.75rem;
    padding-right: 2.5rem; /* space for icon */
    font-size: 0.875rem;
    line-height: 1.25rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.15s ease-in-out;
    outline: none;
}

.gs-input:hover {
    border-color: #93c5fd;
}

.gs-input:focus {
    border-color: #60a5fa;
    box-shadow: 0 0 0 2px #dbeafe;
}

.gs-icon-container {
    position: absolute;
    right: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9ca3af;
    pointer-events: none;
}

.gs-clear-btn {
    cursor: pointer;
    pointer-events: auto;
    color: #9ca3af;
    display: none; /* hidden by default */
}
.gs-clear-btn:hover { color: #4b5563; }

.gs-arrow-icon {
    transition: transform 0.2s;
}

.gs-arrow-icon.rotate-180 {
    transform: rotate(180deg);
}

/* Dropdown Panel */
.gs-dropdown-panel {
    position: absolute;
    z-index: 50;
    left: 0;
    right: 0;
    margin-top: 0.25rem;
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    display: none; /* hidden by default */
    height: 24rem; /* h-96 */
    overflow: hidden;
    flex-direction: row;
}

.gs-dropdown-panel.open {
    display: flex;
    animation: fadeIn 0.15s ease-out forwards;
}

@media (max-width: 768px) {
    .gs-dropdown-panel {
        flex-direction: column;
    }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Category List (Left) */
.gs-category-col {
    width: 30%;
    border-right: 1px solid #f3f4f6;
    background-color: rgba(249, 250, 251, 0.5); /* bg-gray-50/50 */
    overflow-y: auto;
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.gs-cat-item {
    display: flex;
    align-items: center;
    padding: 0.625rem 0.75rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
    user-select: none;
    color: #4b5563;
    transition: all 0.15s;
}

.gs-cat-item:hover {
    background-color: #f3f4f6;
    color: #111827;
}

.gs-cat-item.active {
    background-color: #ffedd5; /* orange-100 */
    color: #c2410c; /* orange-700 */
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    font-weight: 600;
}

.gs-cat-icon {
    margin-right: 0.75rem;
    display: flex;
    align-items: center;
    color: #9ca3af;
}

.gs-cat-item.active .gs-cat-icon {
    color: #f97316; /* orange-500 */
}

.gs-cat-indicator {
    width: 0.375rem;
    height: 0.375rem;
    border-radius: 9999px;
    background-color: #fb923c; /* orange-400 */
    margin-left: 0.5rem;
}

/* Items Grid (Right) */
.gs-items-col {
    width: 70%;
    background-color: white;
    overflow-y: auto;
    padding: 1rem;
}

.gs-items-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
}

.gs-item-card {
    border: 1px solid #f3f4f6;
    background-color: white;
    border-radius: 0.5rem;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    height: 100%;
}

.gs-item-card:hover {
    background-color: #fff7ed; /* orange-50 */
    border-color: #fed7aa; /* orange-200 */
    transform: translateY(-1px);
}

.gs-item-icon {
    margin-bottom: 0.5rem;
    color: #9ca3af;
    transition: color 0.2s, transform 0.2s;
}

.gs-item-card:hover .gs-item-icon {
    color: #f97316; /* orange-500 */
    transform: scale(1.05);
}

.gs-item-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #4b5563;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.gs-item-card:hover .gs-item-label {
    color: #111827;
}

/* Empty State */
.gs-empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #9ca3af;
    font-size: 0.875rem;
}
.gs-empty-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 9999px;
    background-color: #f9fafb;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.75rem;
}

/* Scrollbar */
.gs-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
.gs-scroll::-webkit-scrollbar-track { background: transparent; }
.gs-scroll::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 20px; }
.gs-scroll::-webkit-scrollbar-thumb:hover { background-color: #d1d5db; }

.hidden { display: none !important; }

/* Dark Mode Support */
body.dark .gs-wrapper { color: #e5e7eb; }

body.dark .gs-input {
    background-color: #1f2937;
    color: #e5e7eb;
    border-color: #374151;
}
body.dark .gs-input:hover { border-color: #60a5fa; }
body.dark .gs-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px #1e40af; }

body.dark .gs-clear-btn:hover { color: #d1d5db; }

body.dark .gs-dropdown-panel {
    background-color: #1f2937;
    border-color: #374151;
}

body.dark .gs-category-col {
    border-right-color: #374151;
    background-color: rgba(17, 24, 39, 0.5);
}

body.dark .gs-cat-item { color: #d1d5db; }
body.dark .gs-cat-item:hover {
    background-color: #374151;
    color: #f9fafb;
}
body.dark .gs-cat-item.active {
    background-color: #7c2d12;
    color: #ffedd5;
}
body.dark .gs-cat-item.active .gs-cat-icon { color: #fb923c; }

body.dark .gs-items-col { background-color: #1f2937; }

body.dark .gs-item-card {
    border-color: #374151;
    background-color: #1f2937;
}
body.dark .gs-item-card:hover {
    background-color: #431407;
    border-color: #c2410c;
}
body.dark .gs-item-card:hover .gs-item-icon { color: #fb923c; }
body.dark .gs-item-label { color: #d1d5db; }
body.dark .gs-item-card:hover .gs-item-label { color: #f9fafb; }

body.dark .gs-empty-icon { background-color: #374151; }

body.dark .gs-scroll::-webkit-scrollbar-thumb { background-color: #4b5563; }
body.dark .gs-scroll::-webkit-scrollbar-thumb:hover { background-color: #6b7280; }
"""

# --- Javascript (Web Component Definition) ---

JS_CLASS_DEF = """
if (!customElements.get('gradio-search-select')) {
    class GradioSearchSelect extends HTMLElement {
        constructor() {
            super();
            this._data = [];
            this._value = null; 
            this._selectedItem = null;
            this._activeCategoryIndex = 0;
            this._isOpen = false;
            this._searchTerm = '';
        }

        static get observedAttributes() {
            return ['initial-data', 'placeholder', 'value'];
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return;
            if (name === 'initial-data') {
                try {
                    this.data = JSON.parse(newValue);
                } catch (e) {
                    console.error('Invalid JSON in initial-data', e);
                }
            } else if (name === 'placeholder') {
                const input = this.querySelector('.gs-input');
                if (input) input.placeholder = newValue;
            } else if (name === 'value') {
                // External update to value
                this.value = newValue;
            }
        }

        connectedCallback() {
            this.render();
            
            this._handleDocumentClick = (e) => {
                if (!e.composedPath().includes(this)) {
                    this.close();
                }
            };
            document.addEventListener('click', this._handleDocumentClick);
        }

        disconnectedCallback() {
            document.removeEventListener('click', this._handleDocumentClick);
        }

        get data() { return this._data; }
        set data(val) {
            this._data = Array.isArray(val) ? val : [];
            this._activeCategoryIndex = 0;
            this.updateDropdown();
        }

        get value() { return this._value; }
        set value(val) {
            if (!val) {
                this.clearSelection(false);
                return;
            }

            let found = false;
            // Search in data to find item metadata
            if (this._data) {
                for (const cat of this._data) {
                    const item = cat.children?.find(c => c.value === val);
                    if (item) {
                        this.selectItem(item, false); // Do not emit event if setting programmatically
                        found = true;
                        break;
                    }
                }
            }
            
            if (!found) {
                // If value set but item not found (or data not loaded yet), just set raw value
                this._value = val;
                const input = this.querySelector('.gs-input');
                if (input) {
                    input.value = val;
                    this._updateInputState();
                }
            }
        }

        render() {
            const placeholder = this.getAttribute('placeholder') || 'Select...';
            
            this.innerHTML = `
            <div class="gs-wrapper">
                <div class="gs-input-wrapper">
                    <input 
                        type="text" 
                        class="gs-input"
                        placeholder="${placeholder}"
                        autocomplete="off"
                    >
                    <div class="gs-icon-container">
                        <div class="gs-arrow-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="gs-clear-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="gs-dropdown-panel">
                    <div class="gs-category-col gs-scroll"></div>
                    <div class="gs-items-col gs-scroll">
                        <div class="gs-items-grid"></div>
                        <div class="gs-empty-state hidden">
                            <div class="gs-empty-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="opacity: 0.4;">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>
                            <p>��ƥ����</p>
                        </div>
                    </div>
                </div>
            </div>
            `;

            this._bindEvents();
            this.updateDropdown();
        }

        _bindEvents() {
            const input = this.querySelector('.gs-input');
            const clearBtn = this.querySelector('.gs-clear-btn');
            
            input.addEventListener('focus', () => this.open());
            
            input.addEventListener('input', (e) => {
                this._searchTerm = e.target.value.toLowerCase();
                this._updateInputState();
                this.open();
                this.updateDropdown();
            });

            clearBtn.addEventListener('click', (e) => {
                e.stopPropagation(); 
                this.clearSelection(true);
                this.close();
            });
        }

        _updateInputState() {
            const input = this.querySelector('.gs-input');
            const arrowBtn = this.querySelector('.gs-arrow-icon');
            const clearBtn = this.querySelector('.gs-clear-btn');
            
            if (input.value && input.value.length > 0) {
                arrowBtn.classList.add('hidden');
                clearBtn.style.display = 'block';
            } else {
                arrowBtn.classList.remove('hidden');
                clearBtn.style.display = 'none';
            }
        }

        clearSelection(emitEvent = true) {
            this._value = null;
            this._selectedItem = null;
            this._searchTerm = '';
            
            const input = this.querySelector('.gs-input');
            if (input) {
                input.value = '';
                this._updateInputState();
            }

            this.updateDropdown();

            if (emitEvent) {
                this.dispatchEvent(new CustomEvent('change', {
                    detail: { value: null, item: null },
                    bubbles: true
                }));
            }
        }

        open() {
            if (this._isOpen) return;
            this._isOpen = true;
            const panel = this.querySelector('.gs-dropdown-panel');
            const arrow = this.querySelector('.gs-arrow-icon');
            panel.classList.add('open');
            arrow.classList.add('rotate-180');
        }

        close() {
            if (!this._isOpen) return;
            this._isOpen = false;
            const panel = this.querySelector('.gs-dropdown-panel');
            const arrow = this.querySelector('.gs-arrow-icon');
            panel.classList.remove('open');
            arrow.classList.remove('rotate-180');
        }

        selectItem(item, emitEvent = true) {
            this._value = item.value;
            this._selectedItem = item;
            
            const input = this.querySelector('.gs-input');
            input.value = item.label;
            this._updateInputState();
            
            if (emitEvent) {
                this.dispatchEvent(new CustomEvent('change', {
                    detail: { value: this._value, item: item },
                    bubbles: true
                }));
            }

            this.close();
        }

        setCategory(index) {
            this._activeCategoryIndex = index;
            this.updateDropdown(true);
        }

        _renderIcon(iconStr, size = '1.25rem') {
            if (!iconStr) return '';
            if (iconStr.trim().startsWith('<')) {
                return `<div style="width: ${size}; height: ${size}; display: flex; align-items: center; justify-content: center;">${iconStr}</div>`;
            }
            return `<img src="${iconStr}" style="width: ${size}; height: ${size}; object-fit: contain;" alt="icon">`;
        }

        updateDropdown() {
            const catList = this.querySelector('.gs-category-col');
            const itemsGrid = this.querySelector('.gs-items-grid');
            const emptyState = this.querySelector('.gs-empty-state');

            if (!this._data || this._data.length === 0) return;

            // Render Categories
            catList.innerHTML = this._data.map((cat, index) => {
                const isActive = index === this._activeCategoryIndex;
                const icon = this._renderIcon(cat.icon, '1.1rem');
                const activeClass = isActive ? 'active' : '';
                const indicator = isActive ? '<span class="gs-cat-indicator"></span>' : '';

                return `
                    <div class="gs-cat-item ${activeClass}" data-index="${index}">
                        <span class="gs-cat-icon">${icon}</span>
                        <span style="flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${cat.label}</span>
                        ${indicator}
                    </div>
                `;
            }).join('');

            catList.querySelectorAll('.gs-cat-item').forEach(el => {
                el.addEventListener('click', () => {
                    this.setCategory(parseInt(el.dataset.index));
                });
            });

            // Render Items
            const currentCategory = this._data[this._activeCategoryIndex];
            let items = currentCategory ? currentCategory.children : [];

            if (this._searchTerm) {
                items = items.filter(item => 
                    item.label.toLowerCase().includes(this._searchTerm) || 
                    (item.value && item.value.toLowerCase().includes(this._searchTerm))
                );
            }

            if (items.length === 0) {
                itemsGrid.innerHTML = '';
                itemsGrid.classList.add('hidden');
                emptyState.classList.remove('hidden');
            } else {
                itemsGrid.classList.remove('hidden');
                emptyState.classList.add('hidden');
                
                itemsGrid.innerHTML = items.map((item, idx) => {
                    const iconSize = item.size || '2rem'; 
                    const icon = this._renderIcon(item.icon, iconSize);
                    
                    return `
                        <div class="gs-item-card" data-idx="${idx}">
                            <div class="gs-item-icon">
                                ${icon}
                            </div>
                            <span class="gs-item-label">${item.label}</span>
                        </div>
                    `;
                }).join('');

                itemsGrid.querySelectorAll('.gs-item-card').forEach((el, idx) => {
                    el.addEventListener('click', () => {
                        this.selectItem(items[idx]);
                    });
                });
            }
        }
    }
    customElements.define('gradio-search-select', GradioSearchSelect);
}
"""
from gradio.events import Dependency

class CategorizedSelect(gr.HTML):
    """
    A categorised select component with search capability, similar to Gradio-Style Search Component.
    Accepts hierarchical data (Categories -> Items).
    """
    
    def __init__(
        self,
        options: List[SelectCategory],
        value: Optional[str] = None,
        placeholder: str = "Search or select...",
        label: Optional[str] = None,
        elem_id: Optional[str] = None,
        visible: bool = True,
        **kwargs: Any
    ):
        """
        Args:
            options: List of categories with children items.
            value: Initial selected value (matches item 'value').
            placeholder: Input placeholder text.
            label: Optional label (not strictly used in HTML but good for parity).
            elem_id: HTML element ID.
            visible: Initial visibility.
        """
        self.options = options
        json_data = json.dumps(options)
        
        # HTML template instantiates the Web Component
        # We pass initial data as attributes
        html_template = f"""
        <gradio-search-select 
            id="{elem_id or 'cat-select'}"
            initial-data='{escape_json_string(json_data)}'
            value='{value or ""}'
            placeholder='{placeholder}'
        ></gradio-search-select>
        """

        # JS to run on load:
        # 1. Defines the Web Component class (once).
        # 2. Attaches event listener to bridge component events to Gradio's `trigger`.
        js_on_load = f"""
        {JS_CLASS_DEF}
        
        const selectEl = element.querySelector('gradio-search-select');
        
        // Forward 'change' events from the web component to Gradio
        if (selectEl) {{
            selectEl.addEventListener('change', (e) => {{
                console.log(e);
                // trigger is injected by Gradio's JS wrapper
                trigger('click', e.detail); 
            }});
        }}
        """

        super().__init__(
            value=value, # Pass value to base though mostly for init
            label=label,
            elem_id=elem_id,
            visible=visible,
            html_template=html_template,
            css_template=CSS,
            js_on_load=js_on_load,
            **kwargs
        )

        # def _wrap(evt: gr.EventData):
        #     return gr.update(value=evt._data['value'])
        # self.click(_wrap, outputs=self)

    def change(self, fn, inputs, outputs):
        def _wrap(evt: gr.EventData):
            return gr.update(value=evt._data['value'])
        self.click(_wrap, outputs=self)
        super().change(fn, inputs, outputs)
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component


if __name__ == "__main__":
    # Example usage
    demo = gr.Blocks()

    with demo:
        cat_select = CategorizedSelect(
            options=[
                {
                    "label": "Fruits",
                    "icon": "<svg>...</svg>",
                    "children": [
                        {"label": "Apple", "value": "apple", "icon": "<svg>...</svg>", "size": "2rem"},
                        {"label": "Banana", "value": "banana", "icon": "<svg>...</svg>", "size": "2rem"},
                    ],
                },
                {
                    "label": "Vegetables",
                    "icon": "<svg>...</svg>",
                    "children": [
                        {"label": "Carrot", "value": "carrot", "icon": "<svg>...</svg>", "size": "2rem"},
                        {"label": "Lettuce", "value": "lettuce", "icon": "<svg>...</svg>", "size": "2rem"},
                    ],
                },
            ],
            placeholder="Select a food item...",
        )

        def on_change(detail):
            return f"Selected: {detail['value']}"

        output = gr.Textbox(label="Selection Output")

        cat_select.change(on_change, inputs=[], outputs=output)

    demo.launch()