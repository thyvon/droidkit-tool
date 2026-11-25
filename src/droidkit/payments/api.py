"""Qt facade for payments — context property `PaymentsApi`."""

from __future__ import annotations

import os

from PySide6.QtCore import Property, QObject, Signal, Slot

from droidkit.payments.khqr import KhqrError, KhqrService
from droidkit.payments.models import CheckoutSession, PaymentStatus


class PaymentsApi(QObject):
    qrChanged = Signal()
    statusChanged = Signal()
    errorChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._session: CheckoutSession | None = None
        self._qr_base64 = ""
        self._status = PaymentStatus.UNPAID.value
        self._error = ""
        token = os.environ.get("DROIDKIT_BAKONG_TOKEN", "")
        base = os.environ.get("DROIDKIT_BAKONG_BASE_URL", "")
        self._svc = KhqrService(token=token or None, base_url=base or None)

    @Property(str, notify=qrChanged)
    def qrBase64(self) -> str:
        return self._qr_base64

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(str, notify=errorChanged)
    def errorMessage(self) -> str:
        return self._error

    @Property(float, notify=qrChanged)
    def amount(self) -> float:
        return self._session.amount if self._session else 0.0

    @Property(str, notify=qrChanged)
    def billNumber(self) -> str:
        return self._session.bill_number if self._session else ""

    @Slot(float, str, str, result=bool)
    def createOfflineQr(self, amount: float, account_id: str, merchant_name: str) -> bool:
        self._error = ""
        try:
            session = self._svc.create_offline_qr(
                account_id=account_id.strip(),
                merchant_name=merchant_name.strip() or "DroidKit",
                amount=float(amount),
            )
        except (KhqrError, ValueError, TypeError) as exc:
            self._error = str(exc)
            self.errorChanged.emit()
            return False
        self._session = session
        self._qr_base64 = KhqrService.to_png_base64(session.qr_payload)
        self._status = session.status.value
        self.qrChanged.emit()
        self.statusChanged.emit()
        self.errorChanged.emit()
        return True

    @Slot(float, result=bool)
    def createWebCheckout(self, amount: float) -> bool:
        self._error = ""
        try:
            session = self._svc.create_web_checkout(amount=float(amount))
        except (KhqrError, ValueError, TypeError) as exc:
            self._error = str(exc)
            self.errorChanged.emit()
            return False
        self._session = session
        self._qr_base64 = KhqrService.to_png_base64(session.qr_payload)
        self._status = session.status.value
        self.qrChanged.emit()
        self.statusChanged.emit()
        self.errorChanged.emit()
        return True

    @Slot(result=str)
    def pollPayment(self) -> str:
        if not self._session:
            return self._status
        try:
            status = self._svc.check_payment(self._session.md5)
        except KhqrError as exc:
            self._error = str(exc)
            self.errorChanged.emit()
            return self._status
        self._status = status.value
        self.statusChanged.emit()
        return self._status

    @Slot()
    def reset(self) -> None:
        self._session = None
        self._qr_base64 = ""
        self._status = PaymentStatus.UNPAID.value
        self._error = ""
        self.qrChanged.emit()
        self.statusChanged.emit()
        self.errorChanged.emit()


__all__ = ["PaymentsApi"]
