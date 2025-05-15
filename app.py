from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import qrcode
import io
from PIL import Image
import pyzbar.pyzbar as pyzbar
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flashing messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if it's a URL submission (QR generation)
        if 'url' in request.form:
            input_URL = request.form.get('url', 'https://www.google.com/')
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=15,
                border=4,
            )
            
            qr.add_data(input_URL)
            qr.make(fit=True)
            
            # Create image in memory
            img = qr.make_image(fill_color="red", back_color="white")
            
            # Save image to bytes buffer
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
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Check if file is an image
        if file and allowed_file(file.filename):
            try:
                # Read the image file
                image = Image.open(file.stream)
                
                # Decode the QR code
                decoded_objects = pyzbar.decode(image)
                
                if not decoded_objects:
                    flash('No QR code found in the image')
                    return redirect(request.url)
                
                # Get the decoded data
                decoded_text = decoded_objects[0].data.decode('utf-8')
                
                return render_template('decode_result.html', decoded_text=decoded_text)
            
            except Exception as e:
                flash(f'Error decoding QR code: {str(e)}')
                return redirect(request.url)
        
        else:
            flash('Invalid file type. Please upload an image file (PNG, JPG, JPEG)')
            return redirect(request.url)
    
    return render_template('decode.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)