"""create agent phase0 tables

Revision ID: 20260211_01
Revises:
Create Date: 2026-02-11 13:10:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260211_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tbl_AgentTasks",
        sa.Column("TaskID", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("TaskType", sa.String(length=64), nullable=False),
        sa.Column(
            "Status", sa.String(length=32), nullable=False, server_default="pending"
        ),
        sa.Column("Payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("Result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ErrorMessage", sa.Text(), nullable=True),
        sa.Column(
            "CreatedAt",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("StartedAt", sa.DateTime(), nullable=True),
        sa.Column("FinishedAt", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("TaskID"),
        comment="Agent异步任务跟踪表",
    )
    op.create_index(
        op.f("ix_tbl_AgentTasks_Status"), "tbl_AgentTasks", ["Status"], unique=False
    )
    op.create_index(
        op.f("ix_tbl_AgentTasks_TaskType"), "tbl_AgentTasks", ["TaskType"], unique=False
    )

    op.create_table(
        "tbl_AgentIngestRecords",
        sa.Column("RecordID", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("TaskID_FK", sa.Integer(), nullable=True),
        sa.Column("SourceFilePath", sa.String(length=500), nullable=False),
        sa.Column("SourceFileName", sa.String(length=255), nullable=True),
        sa.Column(
            "ExtractedData", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "FieldConfidences", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("OverallConfidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column(
            "ReviewStatus",
            sa.String(length=32),
            nullable=False,
            server_default="pending_review",
        ),
        sa.Column("ReviewedByUserID_FK", sa.Integer(), nullable=True),
        sa.Column("ReviewedAt", sa.DateTime(), nullable=True),
        sa.Column("TraceMeta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "CreatedAt",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["ReviewedByUserID_FK"], ["tbl_Users.UserID"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["TaskID_FK"], ["tbl_AgentTasks.TaskID"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("RecordID"),
        comment="Agent文档摄取记录表",
    )
    op.create_index(
        op.f("ix_tbl_AgentIngestRecords_ReviewStatus"),
        "tbl_AgentIngestRecords",
        ["ReviewStatus"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tbl_AgentIngestRecords_TaskID_FK"),
        "tbl_AgentIngestRecords",
        ["TaskID_FK"],
        unique=False,
    )

    op.create_table(
        "tbl_AgentAuditLogs",
        sa.Column("AuditID", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("UserID_FK", sa.Integer(), nullable=True),
        sa.Column("TaskID_FK", sa.Integer(), nullable=True),
        sa.Column("ActionType", sa.String(length=64), nullable=False),
        sa.Column("UserInput", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ToolTrace", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("FinalResponse", sa.Text(), nullable=True),
        sa.Column("DurationMs", sa.Integer(), nullable=True),
        sa.Column(
            "CreatedAt",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["TaskID_FK"], ["tbl_AgentTasks.TaskID"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["UserID_FK"], ["tbl_Users.UserID"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("AuditID"),
        comment="Agent审计日志表",
    )
    op.create_index(
        op.f("ix_tbl_AgentAuditLogs_ActionType"),
        "tbl_AgentAuditLogs",
        ["ActionType"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tbl_AgentAuditLogs_TaskID_FK"),
        "tbl_AgentAuditLogs",
        ["TaskID_FK"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tbl_AgentAuditLogs_UserID_FK"),
        "tbl_AgentAuditLogs",
        ["UserID_FK"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_tbl_AgentAuditLogs_UserID_FK"), table_name="tbl_AgentAuditLogs"
    )
    op.drop_index(
        op.f("ix_tbl_AgentAuditLogs_TaskID_FK"), table_name="tbl_AgentAuditLogs"
    )
    op.drop_index(
        op.f("ix_tbl_AgentAuditLogs_ActionType"), table_name="tbl_AgentAuditLogs"
    )
    op.drop_table("tbl_AgentAuditLogs")

    op.drop_index(
        op.f("ix_tbl_AgentIngestRecords_TaskID_FK"), table_name="tbl_AgentIngestRecords"
    )
    op.drop_index(
        op.f("ix_tbl_AgentIngestRecords_ReviewStatus"),
        table_name="tbl_AgentIngestRecords",
    )
    op.drop_table("tbl_AgentIngestRecords")

    op.drop_index(op.f("ix_tbl_AgentTasks_TaskType"), table_name="tbl_AgentTasks")
    op.drop_index(op.f("ix_tbl_AgentTasks_Status"), table_name="tbl_AgentTasks")
    op.drop_table("tbl_AgentTasks")
