"""
Simple overlay injector for browser component analysis.

This module injects basic info buttons over website components.
"""


class OverlayInjector:
    """Simple overlay system for marking website components."""
    
    def __init__(self):
        """Initialize the overlay injector."""
        self.webview_window = None
        self.overlay_active = False
    
    def set_webview_window(self, window):
        """Set the webview window reference for JavaScript injection."""
        self.webview_window = window
    
    def inject_component_overlays(self):
        """Inject simple info buttons over website components."""
        if not self.webview_window:
            print("❌ No webview window available")
            return False
        
        try:
            print("🎯 Adding component markers...")
            
            # Use the simplified JavaScript
            js_code = self._create_simple_overlay_js()
            self.webview_window.evaluate_js(js_code)
            
            self.overlay_active = True
            print("✅ Component markers added!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _create_simple_overlay_js(self):
        """Create simple JavaScript for component markers."""
        return f"""
        {self._get_cleanup_js()}
        {self._get_component_finder_js()}
        {self._get_button_creator_js()}
        {self._get_styles_js()}
        """
    
    def _get_cleanup_js(self):
        """Remove any existing overlays."""
        return """
        // Clean up existing overlays
        document.querySelectorAll('.info-button, .info-popup').forEach(el => el.remove());
        console.log('🧹 Cleaned up old overlays');
        """
    
    def _get_component_finder_js(self):
        """Find components on the page."""
        return """
        // Find important page components
        const components = [];
        const selectors = ['nav', 'header', 'main', 'h1', 'h2', '.logo', '.menu', 'button'];
        
        selectors.forEach(selector => {{
            const elements = document.querySelectorAll(selector);
            elements.forEach((el, i) => {{
                if (components.length < 5) {{ // Max 5 components
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 30 && rect.height > 15) {{ // Skip tiny elements
                        components.push({{
                            element: el,
                            type: selector,
                            index: components.length + 1
                        }});
                    }}
                }}
            }});
        }});
        
        console.log(`📍 Found ${{components.length}} components`);
        """
    
    def _get_button_creator_js(self):
        """Create info buttons over components."""
        return """
        // Create info buttons
        components.forEach(comp => {{
            const rect = comp.element.getBoundingClientRect();
            const scrollX = window.pageXOffset;
            const scrollY = window.pageYOffset;
            
            // Create button
            const button = document.createElement('div');
            button.className = 'info-button';
            button.innerHTML = comp.index;
            button.style.cssText = `
                position: absolute;
                left: ${{rect.left + scrollX + rect.width - 20}}px;
                top: ${{rect.top + scrollY - 10}}px;
                width: 25px;
                height: 25px;
                background: #3498db;
                border: 2px solid white;
                border-radius: 50%;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                cursor: pointer;
                z-index: 9999;
            `;
            
            // Click handler
            button.addEventListener('click', () => {{
                alert(`Component: ${{comp.type}}\\nElement: ${{comp.element.tagName}}\\nPosition: ${{comp.index}}`);
            }});
            
            document.body.appendChild(button);
        }});
        """
    
    def _get_styles_js(self):
        """Add hover styles."""
        return """
        // Add hover styles
        const style = document.createElement('style');
        style.textContent = `
            .info-button:hover {
                background: #e74c3c !important;
                transform: scale(1.1);
            }
        `;
        document.head.appendChild(style);
        
        console.log('✅ Simple overlay complete');
        """
    
    def remove_overlays(self):
        """Remove all overlay buttons from the page."""
        if not self.webview_window:
            return
        
        try:
            js_remove = """
            document.querySelectorAll('.info-button').forEach(el => el.remove());
            console.log('🧹 Overlays removed');
            """
            
            self.webview_window.evaluate_js(js_remove)
            self.overlay_active = False
            print("✅ Overlays removed")
            
        except Exception as e:
            print(f"❌ Error removing overlays: {e}")
    
    def is_active(self):
        """Check if overlay is currently active."""
        return self.overlay_active