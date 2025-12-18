import pandera as pa
from pandera.typing import Series, String, Float
from typing import Optional
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# =============================================================================
# TimeOffSchema - For /timeoff/requests/changes endpoint (change events)
# =============================================================================

class TimeOffSchema(BrynQPanderaDataFrameModel):
    """Schema for time off change events from /timeoff/requests/changes endpoint."""
    change_type: Series[String] = pa.Field(coerce=True, description="Change Type", alias="changeType")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    employee_display_name: Series[String] = pa.Field(coerce=True, description="Employee Display Name", alias="employeeDisplayName")
    employee_email: Series[String] = pa.Field(coerce=True, description="Employee Email", alias="employeeEmail")
    request_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Request ID", alias="requestId")
    policy_type_display_name: Series[String] = pa.Field(coerce=True, description="Policy Type Display Name", alias="policyTypeDisplayName")
    type: Series[String] = pa.Field(coerce=True, description="Request type", alias="type")
    start_date: Series[String] = pa.Field(coerce=True, nullable=True, description="Start Date", alias="startDate")
    start_portion: Series[String] = pa.Field(coerce=True, nullable=True, description="Start Portion", alias="startPortion")
    end_date: Series[String] = pa.Field(coerce=True, nullable=True, description="End Date", alias="endDate")
    end_portion: Series[String] = pa.Field(coerce=True, nullable=True, description="End Portion", alias="endPortion")
    day_portion: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Day Portion", alias="dayPortion")
    date: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Date", alias="date")
    hours_on_date: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Hours on Date", alias="hoursOnDate")
    daily_hours: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Daily Hours", alias="dailyHours")
    duration_unit: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Duration Unit", alias="durationUnit")
    total_duration: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Total Duration", alias="totalDuration")
    total_cost: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Total Cost", alias="totalCost")
    change_reason: Optional[Series[String]] = pa.Field(nullable=True, coerce=True, description="Change Reason", alias="changeReason")
    visibility: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Visibility", alias="visibility")

    class Config:
        coerce = True


# =============================================================================
# TimeOffRequest - For /timeoff/employees/{id}/requests/{requestId} endpoint
# =============================================================================

class TimeOffRequest(BrynQPanderaDataFrameModel):
    """
    Schema for time off request details from Bob API.

    Based on: https://apidocs.hibob.com/reference/get_timeoff-employees-id-requests-requestid

    Supports all request types (discriminated by 'type' field):
    - days: Request for X days
    - hours: Request for X hours during the day (policy types measured in hours)
    - portionOnRange: Every morning or afternoon during days requested
    - hoursOnRange: X hours every day during days requested
    - differentDayDurations: Different hours on each day requested
    - specificHoursDayDurations: Specific hours per day
    - differentSpecificHoursDayDurations: Different specific hours on each day
    - percentageOnRange: X percent of every day during days requested
    - openEnded: Request without an end date yet

    All type-specific fields are optional since they vary by request type.

    Note: Complex nested fields (attachmentLinks, durations arrays) are not included
    """

    # -------------------------------------------------------------------------
    # IDENTIFIERS
    # -------------------------------------------------------------------------
    employee_id: Series[String] = pa.Field(
        coerce=True, description="Employee ID", alias="employeeId"
    )
    request_id: Series[pd.Int64Dtype] = pa.Field(
        coerce=True, description="Time Off Request ID", alias="requestId"
    )

    # -------------------------------------------------------------------------
    # REQUEST METADATA
    # -------------------------------------------------------------------------
    policy_type_display_name: Series[String] = pa.Field(
        coerce=True, description="Display name of the policy type", alias="policyTypeDisplayName"
    )
    created_on: Series[String] = pa.Field(
        coerce=True, description="Date and time the request was created", alias="createdOn"
    )
    description: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Request description", alias="description"
    )

    # -------------------------------------------------------------------------
    # TYPE DISCRIMINATOR
    # Valid values: days, hours, portionOnRange, hoursOnRange, differentDayDurations,
    #               specificHoursDayDurations, differentSpecificHoursDayDurations,
    #               percentageOnRange, openEnded
    # -------------------------------------------------------------------------
    type: Series[String] = pa.Field(
        coerce=True, description="Request type discriminator", alias="type"
    )

    # GENERAL INFO
    duration_unit: Series[String] = pa.Field(
        coerce=True, description="Unit for totalDuration/totalCost: 'days' or 'hours'", alias="durationUnit"
    )
    total_duration: Series[Float] = pa.Field(
        coerce=True, description="Total time including regular days off", alias="totalDuration"
    )
    total_cost: Series[Float] = pa.Field(
        coerce=True, description="Amount deducted from balance", alias="totalCost"
    )
    status: Series[String] = pa.Field(
        coerce=True, description="Request status: approved, pending, canceled, etc.", alias="status"
    )
    approved: Series[pd.BooleanDtype] = pa.Field(
        coerce=True, description="Whether request is approved", alias="approved"
    )

    has_attachment: Series[pd.BooleanDtype] = pa.Field(
        coerce=True, description="Whether request has attachments", alias="hasAttachment"
    )
    # Note: attachmentLinks array is not included (complex nested structure)

    reason_code: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Reason code from policy type's list", alias="reasonCode"
    )

    previous_request_id: Optional[Series[pd.Int64Dtype]] = pa.Field(
        nullable=True, coerce=True,
        description="ID of replaced request when date/time updated", alias="previousRequestId"
    )
    original_request_id: Optional[Series[pd.Int64Dtype]] = pa.Field(
        nullable=True, coerce=True,
        description="ID of the very first request in history chain", alias="originalRequestId"
    )

    approved_by: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Who approved the request", alias="approvedBy"
    )
    approved_at: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="When request was approved", alias="approvedAt"
    )

    declined_by: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Who declined the request", alias="declinedBy"
    )
    declined_at: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="When request was declined", alias="declinedAt"
    )
    decline_reason: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Why request was declined", alias="declineReason"
    )

    visibility: Series[String] = pa.Field(
        coerce=True, description="Visibility: 'Public', 'Private' or 'Custom name'", alias="visibility"
    )
    time_zone_offset: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True,
        description="GMT offset (e.g., 'GMT -5:00') for requests with specific times", alias="timeZoneOffset"
    )

    # -------------------------------------------------------------------------
    # TYPE-SPECIFIC FIELDS (optional, presence depends on 'type' value)
    # -------------------------------------------------------------------------

    # For types: days, portionOnRange, hoursOnRange, differentDayDurations,
    #            specificHoursDayDurations, differentSpecificHoursDayDurations,
    #            percentageOnRange, openEnded
    start_date: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="First day of time off", alias="startDate"
    )
    end_date: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Last day of time off (null for openEnded)", alias="endDate"
    )

    # For types: days, openEnded
    start_portion: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True,
        description="First day portion: all_day, morning, afternoon", alias="startPortion"
    )
    end_portion: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True,
        description="Last day portion: all_day, morning, afternoon (null for openEnded)", alias="endPortion"
    )

    # For type: hours
    date: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True, description="Date for single-day hours request", alias="date"
    )
    hours_on_date: Optional[Series[Float]] = pa.Field(
        nullable=True, coerce=True, description="Hours for single-day request", alias="hoursOnDate"
    )

    # For type: portionOnRange
    day_portion: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True,
        description="Portion for range: morning or afternoon", alias="dayPortion"
    )

    # For type: hoursOnRange
    daily_hours: Optional[Series[Float]] = pa.Field(
        nullable=True, coerce=True, description="Hours per day for range", alias="dailyHours"
    )

    # For type: percentageOnRange
    percentage_of_day: Optional[Series[pd.Int64Dtype]] = pa.Field(
        nullable=True, coerce=True, description="Percent of each day requested", alias="percentageOfDay"
    )

    # For types: specificHoursDayDurations, differentSpecificHoursDayDurations, openEnded
    time_zone: Optional[Series[String]] = pa.Field(
        nullable=True, coerce=True,
        description="Time zone name (e.g., 'Europe/London')", alias="timeZone"
    )

    # Note: 'durations' array is not included (complex nested structure with per-day details)

    class Config:
        coerce = True


# =============================================================================
# TimeOffBalanceSchema - For /timeoff/employees/{id}/balance endpoint
# =============================================================================

class TimeOffBalanceSchema(BrynQPanderaDataFrameModel):
    """Schema for time off balance from /timeoff/employees/{id}/balance endpoint."""
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    policy_type_name: Series[String] = pa.Field(coerce=True, description="Policy Type Name", alias="policyTypeName")
    policy_type_display_name: Series[String] = pa.Field(coerce=True, description="Policy Type Display Name", alias="policyTypeDisplayName")
    balance: Series[Float] = pa.Field(coerce=True, description="Current Balance", alias="balance")
    used: Series[Float] = pa.Field(coerce=True, description="Used Balance", alias="used")
    available: Series[Float] = pa.Field(coerce=True, description="Available Balance", alias="available")
    approved_requests: Series[Float] = pa.Field(coerce=True, description="Approved Requests", alias="approvedRequests")
    pending_requests: Series[Float] = pa.Field(coerce=True, description="Pending Requests", alias="pendingRequests")
    as_of_date: Series[String] = pa.Field(coerce=True, description="As of Date", alias="asOfDate")
    accrual_start_date: Series[String] = pa.Field(nullable=True, coerce=True, description="Accrual Start Date", alias="accrualStartDate")
    expiry_date: Series[String] = pa.Field(nullable=True, coerce=True, description="Expiry Date", alias="expiryDate")
    duration_unit: Series[String] = pa.Field(coerce=True, description="Duration Unit", alias="durationUnit")

    class Config:
        coerce = True
