"""QRCodeWidget class module."""

from __future__ import annotations

import io

import qrcode
from kivy.core.image import Image as CoreImage
from kivy.properties import OptionProperty, StringProperty
from kivy.uix.image import Image


class QRCodeWidget(Image):
    """A widget to display a QR code."""

    content: str = StringProperty()
    fit_mode = OptionProperty(
        'contain',
        options=['scale-down', 'fill', 'contain', 'cover'],
    )

    def on_content(self: QRCodeWidget, _: QRCodeWidget, value: str) -> None:
        """Handle the `content` property change."""
        img = qrcode.make(value, version=1, border=1)

        data = io.BytesIO()
        img.save(data)
        data.seek(0)

        core_image = CoreImage(data, ext='png')
        texture = core_image.texture

        self.texture = texture
