import os
from flask import Flask, render_template, request, send_from_directory
import qrcode
from PIL import Image, ImageDraw

app = Flask(__name__)

# Static folder for generated files
GENERATED_FOLDER = 'static/generated'
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# Function to add rounded corners to an image
def add_rounded_corners(image, radius):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius, fill=255)
    rounded = Image.new('RGBA', image.size)
    rounded.paste(image, mask=mask)
    return rounded

# Function to generate a QR code with a logo and white space
def generate_qr_with_logo(data, logo_path, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Add the logo if provided
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        qr_width, qr_height = qr_img.size
        logo_size = int(qr_width / 5)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        logo = add_rounded_corners(logo, radius=20)

        # Add white box for the logo
        white_box_size = int(logo_size * 1.4)
        white_box_position = (
            (qr_width - white_box_size) // 2,
            (qr_height - white_box_size) // 2,
            (qr_width + white_box_size) // 2,
            (qr_height + white_box_size) // 2,
        )
        draw = ImageDraw.Draw(qr_img)
        draw.rectangle(white_box_position, fill="white")

        # Paste the logo onto the white space
        logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        qr_img.paste(logo, logo_position, mask=logo)

    qr_img.save(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        work_phone = request.form['work_phone']
        email = request.form['email']
        designation = request.form['designation']
        organization = request.form['organization']
        website = request.form['website']
        address = request.form['address']

        # Handle custom logo upload
        logo = request.files.get('logo')
        logo_path = None
        if logo:
            logo_path = os.path.join(GENERATED_FOLDER, logo.filename)
            logo.save(logo_path)

        # Generate vCard format
        vcard_data = f"""
BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name}
FN:{first_name} {last_name}
TEL;TYPE=cell:{mobile}
TEL;TYPE=work:{work_phone}
EMAIL:{email}
TITLE:{designation}
ORG:{organization}
URL:{website}
ADR;TYPE=WORK,PREF:;;{address}
END:VCARD
"""

        # Path to save the QR code
        qr_img_filename = 'contact_qr_code_with_logo.png'
        qr_img_path = os.path.join(GENERATED_FOLDER, qr_img_filename)

        # Generate QR code with logo
        generate_qr_with_logo(vcard_data, logo_path, qr_img_path)

        # Return image preview
        return render_template('index.html', qr_code_path=f"/static/generated/{qr_img_filename}")

if __name__ == '__main__':
    app.run(debug=True)
