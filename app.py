from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import qrcode
import io
from PIL import Image
import cv2
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def decode_qr_code(image):
    """Decode QR codes using OpenCV"""
    # Convert PIL Image to numpy array
    img_np = np.array(image)
    
    # Convert to grayscale if it's a color image
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np
    
    # Initialize QRCode detector
    detector = cv2.QRCodeDetector()
    
    # Detect and decode
    data, vertices, _ = detector.detectAndDecode(gray)
    return data if data else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'url' in request.form:
        input_URL = request.form.get('url', 'https://www.google.com/')
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=4,
        )
        qr.add_data(input_URL)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="red", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes)
        img_bytes.seek(0)
        
        return send_file(
            img_bytes,
            mimetype='image/png',
            as_attachment=True,
            download_name='url_qrcode.png'
        )
    
    return render_template('index.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode_qr():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                image = Image.open(file.stream)
                decoded_text = decode_qr_code(image)
                
                if not decoded_text:
                    flash('No QR code found in the image', 'error')
                    return redirect(request.url)
                
                return render_template('decode_result.html', decoded_text=decoded_text)
            
            except Exception as e:
                flash(f'Error decoding QR code: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload an image file (PNG, JPG, JPEG)', 'error')
            return redirect(request.url)
    
    return render_template('decode.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)