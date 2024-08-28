import os
from flask import Flask, render_template, request, url_for, send_file
from PIL import Image, ImageDraw
import re

app = Flask(__name__)

# Directory to save the processed headshots
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Avenir', sans-serif; color: #5c5a5b; }}
        a {{ color: #DB499A; text-decoration: none; }}
    </style>
</head>
<body>
<div style="width: 600px;">
  <table cellpadding="0" cellspacing="0" style="width: 100%; border-spacing: 0;">
    <tr>
      <td style="width: 120px; vertical-align: top; padding: 0;">
        <img src="{headshot_url}" alt="{name} Headshot" style="width: 120px; height: 120px; display: block; border-radius: 0 0 45px 0;">
      </td>
      <td style="vertical-align: top; padding-left: 10px; text-align: left;">
        <p style="margin: 1px 0;"><strong>{name}</strong></p>
        <p style="margin: 4px 0;"><em>{title}</em></p>
        <p style="margin: 4px 0;"><strong>C </strong>{cell_number}</p>
        <p style="margin: 4px 0;"><strong>E </strong><a href="mailto:{email}">{email}</a></p>
      </td>
    </tr>
     <!-- Spacer Row for Separation -->
    <tr><td colspan="2" style="height: 10px;"></td></tr>
    <!-- Second Row for Banners -->
    <tr>
      <td colspan="2" style="padding: 0; text-align: left;">
        <a href="https://hedyandhopp.com/" style="display: inline;"><img src="https://i.imgur.com/iLpJv2j.png" alt="Hedy & Hopp" style="vertical-align: top; width: 320px; height: 82px;"></a>
        <a href="https://podcasters.spotify.com/pod/show/wearemarketinghappy" style="display: inline; margin-left: 1%;"><img src="https://i.imgur.com/tpTA5J3.png" alt="We Are, Marketing Happy Podcast" style="vertical-align: top; width: 120px; height: 80px;"></a>
      </td>
    </tr>
  </table>

</div>
</body>
</html>
"""

def process_image(image_path):
    with Image.open(image_path).convert("RGB") as img:
        img = img.resize((120, 120), Image.ANTIALIAS)
        rounded_img = Image.new("RGB", (120, 120), (255, 255, 255))
        rounded_img.paste(img, (0, 0))

        mask = Image.new('L', (120, 120), 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([0, 0, 120, 120], fill=255)
        draw.pieslice([120 - 90, 120 - 90, 120 + 90, 120 + 90], start=0, end=90, fill=0)

        rounded_img.putalpha(mask)
        processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + os.path.basename(image_path))
        rounded_img.save(processed_image_path, "PNG")

    return processed_image_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name'].upper()
        title = request.form['title'].title()
        cell_number = re.sub(r'\D', '', request.form['cell_number'])
        cell_number = f"({cell_number[:3]}) {cell_number[3:6]}-{cell_number[6:]}"
        email = request.form['email']

        headshot = request.files['headshot']
        headshot_filename = headshot.filename
        headshot_path = os.path.join(app.config['UPLOAD_FOLDER'], headshot_filename)
        headshot.save(headshot_path)
        
        processed_headshot_path = process_image(headshot_path)
        
        # Generate the URL for the processed image
        headshot_url = url_for('static', filename='uploads/' + os.path.basename(processed_headshot_path))

        signature_html = template.format(
            name=name,
            title=title,
            cell_number=cell_number,
            email=email,
            headshot_url=headshot_url
        )

        # Save the HTML file
        signature_filename = f"signature_{name.lower().replace(' ', '_')}.html"
        signature_filepath = os.path.join(app.config['UPLOAD_FOLDER'], signature_filename)
        with open(signature_filepath, 'w') as f:
            f.write(signature_html)

        return render_template('index.html', signature=signature_html, download_link=url_for('download_file', filename=signature_filename))

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
