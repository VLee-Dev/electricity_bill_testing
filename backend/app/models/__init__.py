# Import all models để SQLAlchemy nhận biết relationships
from app.models.admin import Admin
from app.models.customer import Customer
from app.models.email_log import EmailLog
from app.models.household import Household
from app.models.invoice import Invoice, InvoiceTierDetail
from app.models.meter_reading import MeterReading
from app.models.payment import Payment
from app.models.price_tier import PriceTier
from app.models.system_config import SystemConfig

__all__ = [
    "Admin",
    "Customer",
    "Household",
    "MeterReading",
    "PriceTier",
    "Invoice",
    "InvoiceTierDetail",
    "Payment",
    "EmailLog",
    "SystemConfig",
]
