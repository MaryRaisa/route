import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

QR_DIR = os.path.join(os.path.dirname(__file__), 'static', 'qrcodes')

def generate_location_qr(location_id, location_name, base_url="http://127.0.0.1:5000"):
    """
    Generates an airport branded QR code for an airport location.
    The QR payload directs to the scan / navigation endpoint.
    """
    os.makedirs(QR_DIR, exist_ok=True)
    filename = f"qr_location_{location_id}.png"
    filepath = os.path.join(QR_DIR, filename)

    # Payload includes URL for direct smartphone camera open, and metadata
    target_url = f"{base_url}/scan?loc_id={location_id}"

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    # Primary colors for airport theme: Deep Navy (#0B192C) on White
    qr_img = qr.make_image(fill_color="#0B192C", back_color="white").convert('RGB')

    # Add header & footer banner with location name & airport branding
    qr_w, qr_h = qr_img.size
    banner_top_h = 45
    banner_bottom_h = 55
    total_w = qr_w
    total_h = qr_h + banner_top_h + banner_bottom_h

    canvas = Image.new('RGB', (total_w, total_h), color='#FFFFFF')
    draw = ImageDraw.Draw(canvas)

    # Draw Navy Header
    draw.rectangle([(0, 0), (total_w, banner_top_h)], fill='#0B192C')

    # Header text: "SMART QR AIRPORT GUIDE"
    # Fallback to default font if custom font not available
    try:
        font_header = ImageFont.truetype("arial.ttf", 15)
        font_footer = ImageFont.truetype("arialbd.ttf", 16)
        font_sub = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font_header = font_footer = font_sub = ImageFont.load_default()

    header_text = "✈ SMART QR AIRPORT GUIDE"
    # Calculate text position
    bbox_h = draw.textbbox((0, 0), header_text, font=font_header)
    w_h = bbox_h[2] - bbox_h[0]
    draw.text(((total_w - w_h) // 2, 13), header_text, fill='#00A8FF', font=font_header)

    # Paste QR Code in center
    canvas.paste(qr_img, (0, banner_top_h))

    # Draw Bottom Info Box
    draw.rectangle([(0, qr_h + banner_top_h), (total_w, total_h)], fill='#F0F4F8')

    loc_text = location_name[:26]
    bbox_f = draw.textbbox((0, 0), loc_text, font=font_footer)
    w_f = bbox_f[2] - bbox_f[0]
    draw.text(((total_w - w_f) // 2, qr_h + banner_top_h + 8), loc_text, fill='#0B192C', font=font_footer)

    sub_text = f"Checkpoint ID: #{location_id} • Scan to Navigate"
    bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
    w_s = bbox_s[2] - bbox_s[0]
    draw.text(((total_w - w_s) // 2, qr_h + banner_top_h + 30), sub_text, fill='#5A6A80', font=font_sub)

    # Draw border around whole card
    draw.rectangle([(0, 0), (total_w - 1, total_h - 1)], outline='#CBD5E1', width=1)

    canvas.save(filepath, format="PNG")
    rel_path = f"qrcodes/{filename}"
    return rel_path

def generate_all_qrcodes(base_url="http://127.0.0.1:5000"):
    """Generates QR codes for all locations in the database."""
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, location_name FROM locations")
    locations = cursor.fetchall()

    for loc in locations:
        rel_path = generate_location_qr(loc['id'], loc['location_name'], base_url=base_url)
        cursor.execute('''
            INSERT INTO qr_codes (location_id, qr_image_path)
            VALUES (?, ?)
            ON CONFLICT(location_id) DO UPDATE SET qr_image_path=excluded.qr_image_path
        ''', (loc['id'], rel_path))

    conn.commit()
    conn.close()
    print(f"Generated {len(locations)} QR codes successfully.")

if __name__ == '__main__':
    generate_all_qrcodes()
