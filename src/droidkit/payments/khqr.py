"""Bakong KHQR helper — wraps the MIT `bakong-khqr` package.

Two modes:
  1. Offline static/dynamic QR (account_id + merchant fields) — no token needed
  2. Relay / official API (token + optional base_url) — for web checkout + status
"""

from __future__ import annotations

import uuid
from typing import Any

from droidkit.payments.models import CheckoutSession, PaymentStatus


class KhqrError(RuntimeError):
    pass


class KhqrService:
    def __init__(self, *, token: str | None = None, base_url: str | None = None) -> None:
        self._token = token
        self._base_url = base_url
        self._client: Any = None

    def _khqr(self) -> Any:
        if self._client is None:
            try:
                from bakong_khqr import KHQR
            except ImportError as exc:
                raise KhqrError(
                    "bakong-khqr is not installed. Run: pip install bakong-khqr"
                ) from exc
            if self._base_url and self._token:
                self._client = KHQR(token=self._token, base_url=self._base_url)
            elif self._token:
                self._client = KHQR(self._token)
            else:
                self._client = KHQR()
        return self._client

    def create_offline_qr(
        self,
        *,
        account_id: str,
        merchant_name: str,
        amount: float,
        currency: str = "KHR",
        merchant_city: str = "Phnom Penh",
        bill_number: str | None = None,
    ) -> CheckoutSession:
        bill = bill_number or uuid.uuid4().hex[:12].upper()
        qr = self._khqr().create_qr(
            account_id=account_id,
            merchant_name=merchant_name,
            merchant_city=merchant_city,
            amount=amount,
            currency=currency,
            bill_number=bill,
        )
        payload = str(qr)
        md5 = self._khqr().generate_md5(payload)
        return CheckoutSession(
            bill_number=bill,
            qr_payload=payload,
            md5=md5,
            amount=amount,
            currency=currency,
            merchant_name=merchant_name,
        )

    def create_web_checkout(
        self,
        *,
        amount: float,
        bill_number: str | None = None,
        return_url: str | None = None,
        currency: str = "KHR",
    ) -> CheckoutSession:
        if not self._token:
            raise KhqrError("Web checkout requires a Bakong / relay token.")
        bill = bill_number or uuid.uuid4().hex[:12].upper()
        resp = self._khqr().create_qr(
            amount=amount,
            bill_number=bill,
            return_url=return_url,
            currency=currency,
        )
        payload = str(resp)
        md5 = getattr(resp, "md5", "") or self._khqr().generate_md5(payload)
        return CheckoutSession(
            bill_number=bill,
            qr_payload=payload,
            md5=md5,
            amount=amount,
            currency=currency,
        )

    def check_payment(self, md5: str) -> PaymentStatus:
        try:
            status = self._khqr().check_payment(md5)
        except Exception as exc:
            raise KhqrError(str(exc)) from exc
        try:
            return PaymentStatus(str(status).upper())
        except ValueError:
            return PaymentStatus.ERROR

    @staticmethod
    def to_png_base64(qr_payload: str, box_size: int = 8, border: int = 2) -> str:
        import base64
        import io

        import qrcode

        qr = qrcode.QRCode(box_size=box_size, border=border)
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")
