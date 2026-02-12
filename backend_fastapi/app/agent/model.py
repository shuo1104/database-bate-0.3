# -*- coding: utf-8 -*-
"""Agent data models (Phase 0)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgentTaskModel(Base):
    """Asynchronous task tracking table."""

    __tablename__ = "tbl_AgentTasks"
    __table_args__ = {"comment": "Agent asynchronous task tracking table"}

    TaskID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Task ID",
    )
    TaskType: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Task type (ingest/query/chat)",
    )
    Status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        index=True,
        comment="Task status (pending/running/success/failed)",
    )
    Payload: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Task input payload",
    )
    Result: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Task output result",
    )
    ErrorMessage: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message",
    )
    CreatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="Created at",
    )
    StartedAt: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Started at",
    )
    FinishedAt: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Finished at",
    )


class AgentIngestRecordModel(Base):
    """Document ingestion record table."""

    __tablename__ = "tbl_AgentIngestRecords"
    __table_args__ = {"comment": "Agent document ingestion record table"}

    RecordID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Record ID",
    )
    TaskID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tbl_AgentTasks.TaskID", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Task ID foreign key",
    )
    SourceFilePath: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original file path",
    )
    SourceFileName: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Original file name",
    )
    ExtractedData: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Structured extraction result",
    )
    FieldConfidences: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Field confidence",
    )
    OverallConfidence: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        nullable=True,
        comment="Overall confidence",
    )
    ReviewStatus: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending_review",
        index=True,
        comment="Review status (pending_review/approved/rejected/modified)",
    )
    ReviewedByUserID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tbl_Users.UserID", ondelete="SET NULL"),
        nullable=True,
        comment="Reviewer user ID",
    )
    ReviewedAt: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Reviewed at",
    )
    TraceMeta: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Trace metadata (extraction time, model version, etc.)",
    )
    CreatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="Created at",
    )


class AgentAuditLogModel(Base):
    """Agent audit log table."""

    __tablename__ = "tbl_AgentAuditLogs"
    __table_args__ = {"comment": "Agent audit log table"}

    AuditID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Audit ID",
    )
    UserID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tbl_Users.UserID", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID foreign key",
    )
    TaskID_FK: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tbl_AgentTasks.TaskID", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Task ID foreign key",
    )
    ActionType: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Action type",
    )
    UserInput: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="User input",
    )
    ToolTrace: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Tool trace",
    )
    FinalResponse: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Final response",
    )
    DurationMs: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Duration (ms)",
    )
    CreatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="Created at",
    )
