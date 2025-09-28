import tkinter as tk
from tkinterweb import HtmlFrame

# Website to load
DEFAULT_URL = "https://en.wikipedia.org/wiki/Main_Page"

# Glow highlight JS
HIGHLIGHT_JS = """
(() => {
  const style = document.createElement("style");
  style.textContent = `
    .glow-highlight {
      outline: 3px solid dodgerblue !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 8px dodgerblue !important;
      border-radius: 6px !important;
    }
  `;
  document.head.appendChild(style);

  document.addEventListener("click", e => {
    e.target.classList.add("glow-highlight");
    console.log("✨ Highlighted:", e.target);
  }, true);
})();
"""

root = tk.Tk()
root.title("Python.com Viewer")
root.geometry("1000x600")

# Sidebar on the right
sidebar = tk.Frame(root, width=200, bg="lightgray")
sidebar.pack(side="right", fill="y")

# Browser view
browser = HtmlFrame(root)
browser.pack(side="left", expand=True, fill="both")

def load_default():
    browser.load_website(DEFAULT_URL)
    # Inject script after a short delay (let the page load)
    root.after(3000, lambda: browser.run_javascript(HIGHLIGHT_JS))

# Load page & inject script at startup
load_default()

root.mainloop()
