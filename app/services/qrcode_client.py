import httpx

from app.settings import SETTINGS


class QRCodeClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def generate_png(self, data: str) -> bytes:
        """
        Request to the qrcode-generator service to generate a PNG.
        """
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            resp = await client.post(
                "/generate",
                json={"data": data},
            )
            resp.raise_for_status()
            return resp.content


qr_client = QRCodeClient(SETTINGS.QRCODE_SERVICE_URL)
