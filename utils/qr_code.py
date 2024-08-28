from io import BytesIO

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import HorizontalGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer


def create_qr_code_from_peer_data(peer_data: str) -> BytesIO:
    """creates qr code from peer data

    Args:
        peer_data (str): peer data (config file), which will be encoded in qr code

    Returns:
        BytesIO: qr code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )

    qr.add_data(peer_data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=HorizontalGradiantColorMask(),
    )

    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return img_io


if __name__ == "__main__":
    with open("peer_data.txt", "r") as f:
        peer_data = f.read()
    img_io = create_qr_code_from_peer_data(peer_data)
    with open("qr_code.png", "wb") as f:
        f.write(img_io.read())
