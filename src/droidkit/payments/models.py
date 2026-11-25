"""Payment domain models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaymentStatus(StrEnum):
    UNPAID = "UNPAID"
    SCANNED = "SCANNED"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class CheckoutSession:
    bill_number: str
    qr_payload: str
    md5: str
    amount: float
    currency: str
    merchant_name: str = ""
    status: PaymentStatus = PaymentStatus.UNPAID

    @property
    def is_paid(self) -> bool:
        return self.status is PaymentStatus.PAID
