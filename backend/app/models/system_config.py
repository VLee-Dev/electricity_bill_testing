from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemConfig(Base):
    """
    Bảng system_config - Cấu hình hệ thống (key-value)
    VD: vat_rate, smtp_host, smtp_port, issuer_name, invoice_due_days...
    """
    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
