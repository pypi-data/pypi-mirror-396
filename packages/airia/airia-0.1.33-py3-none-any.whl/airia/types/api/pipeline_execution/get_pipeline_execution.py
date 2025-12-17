"""
Pydantic models for get_pipeline_execution API response.

This module defines the response models returned by the get_pipeline_execution endpoint,
including pipeline execution details and step execution logs.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineExecutionLogDetails(BaseModel):
    """
    Pipeline execution log details.

    Attributes:
        duration: Duration of the execution (e.g., "00:00:00.0000000").
        started_at: Start date for the pipeline execution.
        finished_at: End date for the pipeline execution.
        success: Success indicator for the pipeline execution.
        exception: First exception for the pipeline execution if any.
    """

    duration: Optional[str] = None
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    finished_at: Optional[datetime] = Field(None, alias="finishedAt")
    success: Optional[bool] = None
    exception: Optional[str] = None


class StepExecutionLogRecord(BaseModel):
    """
    Step execution log record.

    Attributes:
        pipeline_id: Pipeline ID.
        step_id: Step ID.
        step_type: Step type (e.g., "AIOperation", "dataSearch", etc.).
        step_title: Step title.
        duration: Duration of the execution (e.g., "00:00:00.0000000").
        started_at: Start date for the step execution.
        finished_at: End date for the step execution.
        success: Success indicator for the step execution.
        exception: First exception for the step execution if any.
    """

    pipeline_id: UUID = Field(alias="pipelineId")
    step_id: UUID = Field(alias="stepId")
    step_type: Optional[str] = Field(None, alias="stepType")
    step_title: Optional[str] = Field(None, alias="stepTitle")
    duration: Optional[str] = None
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    finished_at: Optional[datetime] = Field(None, alias="finishedAt")
    success: Optional[bool] = None
    exception: Optional[str] = None


class GetPipelineExecutionResponse(BaseModel):
    """
    Response model for get_pipeline_execution requests.

    Attributes:
        execution_id: Execution result ID.
        pipeline_id: Pipeline ID.
        tenant_id: Tenant ID.
        project_id: Project ID.
        log_record_details: Pipeline execution log details.
        step_execution_log_records: Step execution logs associated to the pipeline.
    """

    execution_id: UUID = Field(alias="executionId")
    pipeline_id: UUID = Field(alias="pipelineId")
    tenant_id: UUID = Field(alias="tenantId")
    project_id: UUID = Field(alias="projectId")
    log_record_details: Optional[PipelineExecutionLogDetails] = Field(
        None, alias="logRecordDetails"
    )
    step_execution_log_records: Optional[list[StepExecutionLogRecord]] = Field(
        None, alias="stepExecutionLogRecords"
    )
