import os
import tempfile
import time
import webbrowser


def show_html(html: str, title: str):
    temp_path = os.path.join(tempfile.gettempdir(), f"{title}.html")
    with open(temp_path, "w") as f:
        f.write(html)
    try:
        if webbrowser.open("file://" + temp_path, new=0):
            time.sleep(1)
        else:
            return "Failed to open browser", 1
    except Exception as e:
        os.unlink(temp_path)
        return str(e), 1
