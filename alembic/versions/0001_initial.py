"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "financial_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("record_type", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_financial_records_id", "financial_records", ["id"])
    op.create_index("ix_financial_records_user_id", "financial_records", ["user_id"])
    op.create_index("ix_financial_records_record_date", "financial_records", ["record_date"])
    op.create_index("ix_financial_records_record_type", "financial_records", ["record_type"])
    op.create_index("ix_financial_records_category", "financial_records", ["category"])
    op.create_index("ix_financial_records_is_deleted", "financial_records", ["is_deleted"])
    op.create_index("ix_financial_records_user_date", "financial_records", ["user_id", "record_date"])

    op.create_table(
        "token_blocklist",
        sa.Column("jti", sa.String(length=255), primary_key=True),
        sa.Column("token_type", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("token_blocklist")
    op.drop_index("ix_financial_records_user_date", table_name="financial_records")
    op.drop_index("ix_financial_records_is_deleted", table_name="financial_records")
    op.drop_index("ix_financial_records_category", table_name="financial_records")
    op.drop_index("ix_financial_records_record_type", table_name="financial_records")
    op.drop_index("ix_financial_records_record_date", table_name="financial_records")
    op.drop_index("ix_financial_records_user_id", table_name="financial_records")
    op.drop_index("ix_financial_records_id", table_name="financial_records")
    op.drop_table("financial_records")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
