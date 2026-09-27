"""Gộp các bản ghi price_tiers trùng tier_no về 1 bản ghi duy nhất (lấy bản ghi mới nhất).

Revision ID: 005_cleanup_price_tiers_dupes
Revises: 004_add_email_log_columns
Create Date: 2026-09-26 17:10:00.000000

"""
from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '005_cleanup_price_tiers_dupes'
down_revision = '004_add_email_log_columns'
branch_labels = None
depends_on = None


def upgrade():
    """
    Nếu có nhiều bản ghi cùng tier_no (do lịch sử update trước đó tạo bản ghi mới),
    chỉ giữ lại 1 bản ghi duy nhất có effective_from mới nhất cho mỗi tier_no.
    Các bản ghi cũ hơn sẽ bị xóa.
    """
    conn = op.get_bind()

    # Xóa các bản ghi cũ (giữ lại bản ghi có effective_from mới nhất cho mỗi tier_no)
    conn.execute(text("""
        DELETE FROM price_tiers
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT DISTINCT ON (tier_no) id
                FROM price_tiers
                ORDER BY tier_no, effective_from DESC
            ) AS latest
        )
    """))


def downgrade():
    # Không có rollback vì đã xóa dữ liệu
    pass
