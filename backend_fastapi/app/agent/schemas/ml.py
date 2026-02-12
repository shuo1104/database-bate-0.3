"""Schemas for ML inference placeholders."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MLFeatureSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Feature name")
    value: Any = Field(..., description="Feature value")
    source: str | None = Field(default=None, description="Feature source")


class MLPredictionInputSchema(BaseModel):
    model_name: str = Field(
        default="default", min_length=1, description="Model identifier"
    )
    features: list[MLFeatureSchema] = Field(
        default_factory=list,
        description="Feature list",
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Extended context"
    )


class MLPredictionOutputSchema(BaseModel):
    model_name: str = Field(..., min_length=1, description="Model identifier")
    prediction: Any = Field(default=None, description="Prediction result")
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Prediction confidence",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Prediction metadata"
    )
    error: str | None = Field(default=None, description="Error message")
