from PIL import Image
import qrcode

from PIL import Image
import qrcode

# Your website URL
url = "https://dataskillacademy.com"

# Create QR code with high error correction
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Generate QR code image
qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# Optional: add a logo inside the QR code
logo = Image.open("Kenneh_Introduction_to_Data_Science_certificates.jpg")  # your small logo
logo_size = 50
logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
pos_logo = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
qr_img.paste(logo, pos_logo, mask=logo if logo.mode == 'RGBA' else None)

# Open your certificate image
certificate = Image.open("Kenneh_Introduction_to_Data_Science_certificates.jpg")  # your certificate file

# Calculate bottom-left position
x = 20  # 20 px from the left edge
y = certificate.height - qr_img.height - 20  # 20 px from the bottom edge
certificate.paste(qr_img, (x, y))

# Save final image
certificate.save("certificate_with_qr.png")
print("Certificate saved with QR code in bottom-left corner.")
