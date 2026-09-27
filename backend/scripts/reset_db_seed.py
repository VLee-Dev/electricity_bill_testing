"""
Reset & seed lại database từ đầu.

Cách dùng (từ thư mục backend/):
    python scripts/reset_db_seed.py

Script sẽ:
1. Xóa toàn bộ bảng (drop_all) trong database hiện tại.
2. Tạo lại schema (create_all).
3. Seed dữ liệu mẫu:
   - 1 admin (admin / admin123)
   - 6 bậc giá điện EVN
   - 2 hộ dân mẫu (KH001, KH002)
   - 1 vài chỉ số điện mẫu (KH001, kỳ 2026-08)
   - system_config (vat_rate = 0.08, invoice_due_days = 15)
"""
import os
import sys
from pathlib import Path

# Thêm project root vào PYTHONPATH
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from sqlalchemy import delete
from datetime import date

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models.admin import Admin
from app.models.household import Household
from app.models.customer import Customer
from app.models.price_tier import PriceTier
from app.models.meter_reading import MeterReading
from app.models.system_config import SystemConfig
from app.security import hash_password


PRICE_TIERS = [
    # Bậc 1: 0-50 kWh
    {"tier_no": 1, "kwh_from": 0,   "kwh_to": 50,  "unit_price": 1984},
    # Bậc 2: 51-100 kWh
    {"tier_no": 2, "kwh_from": 51,  "kwh_to": 100, "unit_price": 2050},
    # Bậc 3: 101-200 kWh
    {"tier_no": 3, "kwh_from": 101, "kwh_to": 200, "unit_price": 2380},
    # Bậc 4: 201-300 kWh
    {"tier_no": 4, "kwh_from": 201, "kwh_to": 300, "unit_price": 2998},
    # Bậc 5: 301-400 kWh
    {"tier_no": 5, "kwh_from": 301, "kwh_to": 400, "unit_price": 3350},
    # Bậc 6: >= 401 kWh
    {"tier_no": 6, "kwh_from": 401, "kwh_to": None, "unit_price": 3460},
]


def main():
    print(f"[reset] Database: {settings.database_url}")
    print("[reset] Bước 1/3: Drop tất cả bảng ...")
    Base.metadata.drop_all(bind=engine)

    print("[reset] Bước 2/3: Tạo lại schema ...")
    Base.metadata.create_all(bind=engine)

    print("[reset] Bước 3/3: Seed dữ liệu mẫu ...")
    with SessionLocal.begin() as db:
        # Admin
        admin = Admin(
            username=settings.admin_email.split("@")[0],
            full_name="Quản trị viên",
            password_hash=hash_password(settings.admin_password),
        )
        db.add(admin)

        # Bảng giá 6 bậc
        for t in PRICE_TIERS:
            db.add(PriceTier(
                tier_no=t["tier_no"],
                kwh_from=t["kwh_from"],
                kwh_to=t["kwh_to"],
                unit_price=t["unit_price"],
                effective_from=date.today(),
                effective_to=None,
            ))

        # System config
        db.add(SystemConfig(key="vat_rate", value="0.08", description="VAT 8%"))
        db.add(SystemConfig(key="invoice_due_days", value="15", description="Hạn thanh toán 15 ngày"))

        # 2 hộ dân mẫu
        h1 = Household(
            customer_code="KH001",
            full_name="Nguyễn Văn A",
            address="123 Đường ABC, Quận 1, TP.HCM",
            phone="0901234567",
            email="kh001@example.com",
            meter_number="MT001",
        )
        h2 = Household(
            customer_code="KH002",
            full_name="Trần Thị B",
            address="456 Đường XYZ, Quận 2, TP.HCM",
            phone="0909876543",
            email="kh002@example.com",
            meter_number="MT002",
        )
        db.add_all([h1, h2])
        db.flush()  # lấy id

        # Customer accounts cho 2 hộ
        db.add(Customer(
            household_id=h1.id,
            password_hash=hash_password("123456"),
        ))
        db.add(Customer(
            household_id=h2.id,
            password_hash=hash_password("123456"),
        ))

        # Vài chỉ số điện mẫu cho KH001
        db.add(MeterReading(
            household_id=h1.id,
            period="2026-08",
            old_reading=0,
            new_reading=120,
            consumption=120,
        ))

    print("[reset] ✅ Reset & seed thành công.")
    print(f"  - Admin: {settings.admin_email} / {settings.admin_password}")
    print(f"  - Customer KH001 / 123456")
    print(f"  - Customer KH002 / 123456")


if __name__ == "__main__":
    main()
