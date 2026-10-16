from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime, timedelta
from io import BytesIO
import qrcode
from PIL import Image
from .models import CustomUser

CR80 = (85.6 * mm, 53.98 * mm)

def generate_user_id_pdf(user: CustomUser):
    buffer = BytesIO()
    width, height = CR80
    c = canvas.Canvas(buffer, pagesize=(width, height))

    # Background
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(0, 0, width, height, fill=1)
    text_x = 41.5*mm

    # Header
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(text_x, height - 8*mm, "LIMAFE")

    # Profile picture
    # Profile picture
    if user.profile_image:
        try:
            img = Image.open(user.profile_image.path)
            img = img.convert("RGB")  # Ensure RGB mode
            img = img.resize((int(28*mm), int(28*mm)), Image.LANCZOS)  # Resize to ID card size

            c.drawInlineImage(img, 5*mm, height - 32*mm)  # width & height inferred from image
        except Exception as e:
            print(f"Error adding profile image: {e}")

    # User info
    c.setFont("Helvetica-Bold", 7.5)
    text_x = 35*mm
    text_y = height - 12*mm
    line_height = 6*mm

    c.drawString(text_x, text_y, f"Name: {user.first_name} {user.last_name}")
    text_y -= line_height
    c.drawString(text_x, text_y, f"Role: {user.role.capitalize()}")
    text_y -= line_height-4
    c.drawString(text_x, text_y, f"Chapter: {user.chapter.name if user.chapter else 'N/A'}")
    text_y -= line_height
    positions = ', '.join([p.name for p in user.positions.all()])
    c.drawString(text_x, text_y, f"Positions: {positions if positions else 'N/A'}")

    # Validity
    issue_date = datetime.today()
    expiry_date = issue_date + timedelta(days=365*2)
    c.setFont("Helvetica", 6)
    c.drawString(5*mm, 10*mm, f"Issue: {issue_date.strftime('%Y-%m-%d')}")
    c.drawString(5*mm, 5*mm, f"Valid Until: {expiry_date.strftime('%Y-%m-%d')}")

    # UUID
    c.drawRightString(width - 5*mm, 5*mm, f"ID: {user.uuid}")

    # QR code
    qr_url = f"https://limafe.pythonanywhere.com/accounts/profile/{user.uuid}/"
    qr_img = qrcode.make(qr_url)
    qr_img = qr_img.convert("RGB")  # ensure PIL Image in RGB mode
    qr_size = 20 * mm
    right_margin = 2 * mm  # smaller margin = more to the right

    c.drawInlineImage(
        qr_img,
        width - qr_size - right_margin,
        10 * mm,
        width=qr_size,
        height=qr_size
    )

    # Finish
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer






from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime, timedelta
from io import BytesIO
import qrcode
from PIL import Image
from .models import CustomUser

CR80 = (85.6 * mm, 53.98 * mm)


def generate_admin_user_id_pdf(user: CustomUser):
    buffer = BytesIO()
    width, height = CR80
    c = canvas.Canvas(buffer, pagesize=(width, height))

    # -------------------
    # Gradient Background
    # -------------------
    stripe_height = height / 6
    gradient_colors = [
        colors.HexColor('#FFD700'),  # Gold
        colors.HexColor('#FFB347'),  # Orange-Gold
        colors.HexColor('#FFDD44'),  # Yellow-Gold
        colors.HexColor('#FFAA00'),  # Deep Gold
        colors.HexColor('#FFE066'),  # Light Gold
        colors.HexColor('#FFD700'),  # Gold again
    ]

    for i, col in enumerate(gradient_colors):
        y = i * stripe_height
        c.setFillColor(col)
        c.rect(0, y, width, stripe_height, fill=1, stroke=0)

    # -------------------
    # Header - LIMAFE
    # -------------------
    text_x = 41.5 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(text_x, height - 8 * mm, "LIMAFE")

    # -------------------
    # Profile picture
    # -------------------
    if user.profile_image:
        try:
            img = Image.open(user.profile_image.path).convert("RGB")
            img = img.resize((int(28 * mm), int(28 * mm)), Image.LANCZOS)
            c.drawInlineImage(img, 5 * mm, height - 32 * mm)
        except Exception as e:
            print(f"Error adding profile image: {e}")

    # -------------------
    # User info
    # -------------------
    text_x = 35 * mm
    c.setFont("Helvetica-Bold", 7.5)
    text_y = height - 12 * mm
    line_height = 6 * mm

    c.drawString(text_x, text_y, f"Name: {user.first_name} {user.last_name}")
    text_y -= line_height
    c.drawString(text_x, text_y, f"Role: {user.role.capitalize()}")
    text_y -= line_height
    c.drawString(text_x, text_y, f"Chapter: {user.chapter.name if user.chapter else 'N/A'}")
    text_y -= line_height
    positions = ", ".join([p.name for p in user.positions.all()])
    c.drawString(text_x, text_y, f"Positions: {positions if positions else 'N/A'}")

    # -------------------
    # Validity
    # -------------------
    issue_date = datetime.today()
    expiry_date = issue_date + timedelta(days=365 * 2)
    c.setFont("Helvetica", 6)
    c.drawString(5 * mm, 10 * mm, f"Issue: {issue_date:%Y-%m-%d}")
    c.drawString(5 * mm, 5 * mm, f"Valid Until: {expiry_date:%Y-%m-%d}")

    # -------------------
    # UUID
    # -------------------
    c.drawRightString(width - 5 * mm, 5 * mm, f"ID: {user.uuid}")

    # -------------------
    # QR code (NO BORDER, smaller)
    # -------------------
    qr_url = f"https://limafe.pythonanywhere.com/accounts/profile/{user.uuid}/"

    qr_size_mm = 16  # size in mm
    qr_size_px = int(qr_size_mm / mm * 72)  # convert mm to pixels at 72dpi

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,   # each box is 1px, will scale with size later
        border=0
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    # create the QR as PIL Image
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # scale to final size using NEAREST to keep edges sharp
    qr_img = qr_img.resize((qr_size_px, qr_size_px), Image.NEAREST)

    # draw on PDF
    c.drawInlineImage(qr_img, width - (qr_size_mm*mm + 5*mm), 10*mm, qr_size_mm*mm, qr_size_mm*mm)

    # -------------------
    # Finish PDF
    # -------------------
    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
