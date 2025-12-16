"""API request/response models for annotation endpoints."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from cat.cafe.annotation import Annotation, AnnotationSummary, ScoreType


class CreateAnnotationRequest(BaseModel):
    """Request model for creating an annotation."""

    trace_id: str = Field(..., description="ID of the trace being annotated")
    node_id: Optional[str] = Field(None, description="ID of specific span/event being annotated")
    metric_name: str = Field(..., description="Name of the annotation metric")
    score_type: ScoreType = Field(..., description="Type of score being provided")
    score_value: Any = Field(..., description="The annotation score (type depends on score_type)")
    comment: Optional[str] = Field(None, description="Optional comment or feedback")
    annotator_id: str = Field(..., description="ID of the person performing the annotation")


__all__ = ["Annotation", "AnnotationSummary", "CreateAnnotationRequest", "ScoreType"]
