from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message text")
    interaction_mode: Literal["chat", "voice"] = Field("chat", description="Interaction mode: 'chat' or 'voice'")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="LLM generated bot response")


class AnalyticsResponse(BaseModel):
    customer_name: Optional[str] = Field(None, description="Name of the customer if mentioned, else null")
    budget_mentioned: Optional[str] = Field(None, description="Budget mentioned by customer, else null")
    configuration_interest: Optional[str] = Field(None, description="Configuration interested in (2BHK, 3BHK), else null")
    interest_level: Literal["hot", "warm", "cold"] = Field(..., description="Assessed interest level")
    site_visit_status: Literal["booked", "failed", "not_requested"] = Field(..., description="Status of site visit request")
    follow_up_required: bool = Field(..., description="Whether human sales team follow up is needed")
    objections_raised: List[str] = Field(default_factory=list, description="List of objections raised by customer")
    language_used: str = Field(..., description="Primary language used (English, Hindi, Hinglish, etc.)")
    conversation_summary: str = Field(..., description="Concise summary of the interaction")
    do_not_contact: bool = Field(False, description="True if customer explicitly asked to stop contact / opt-out")
    escalated_to_human: bool = Field(False, description="True if conversation escalated to a human team member")
    follow_up_preferred_time: Optional[str] = Field(None, description="Preferred follow-up day/time if specified by customer, else null")
