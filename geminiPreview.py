import webview
import tempfile

# This would be your Gemini output
modified_html = """
<html>
<head>
    <title>Gemini Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: darkblue; }
        p { font-size: 16px; }
    </style>
</head>
<body>
    <h1>Product Overview</h1>
    <p>Discover the key features of our latest product line.</p>
    <aside>
        <h2>Limited Offer!</h2>
        <p>50% off today only.</p>
    </aside>
</body>
</html>
"""

def open_html_in_browser(html_content, title="Modified Page"):
    # Save the HTML to a temporary file
    tmp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp_file.write(html_content)
    tmp_file.close()

    # Open the temp file in a pywebview window
    webview.create_window(title, f"file://{tmp_file.name}", width=1024, height=768, maximized=True)
    webview.start()


if __name__ == "__main__":
    open_html_in_browser(modified_html)
