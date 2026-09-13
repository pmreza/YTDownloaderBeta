import webview
import base64
from PIL import Image
import io
import os

html = """
<!DOCTYPE html>
<html>
<body>
<svg id="mysvg" width="256" height="256" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-rocket">
<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
<path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
<path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
</svg>
<script>
window.onload = function() {
    var svg = document.getElementById('mysvg');
    var svgData = new XMLSerializer().serializeToString(svg);
    var canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    var ctx = canvas.getContext('2d');
    var img = new Image();
    img.onload = function() {
        ctx.drawImage(img, 0, 0, 256, 256);
        window.pywebview.api.send_img(canvas.toDataURL('image/png'));
    };
    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
}
</script>
</body>
</html>
"""

class Api:
    def send_img(self, data_url):
        try:
            header, encoded = data_url.split(",", 1)
            data = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(data))
            
            # Make sure it's RGBA
            img = img.convert("RGBA")
            
            img.save("logo.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print("Icon saved.")
        except Exception as e:
            print("Error:", e)
        finally:
            os._exit(0)

if __name__ == '__main__':
    api = Api()
    webview.create_window('Convert', html=html, js_api=api, hidden=True)
    webview.start()
