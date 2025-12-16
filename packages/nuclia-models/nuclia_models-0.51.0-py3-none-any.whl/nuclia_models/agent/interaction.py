import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from nuclia_models.agent.memory import Answer, Context, Step

# Models used between client and API for itneraction requests/responses/streams


class Operation(int, Enum):
    START = 0
    STOP = 1


class InteractionOperation(int, Enum):
    QUESTION = 0
    QUIT = 1
    USER_RESPONSE = 2


class AnswerOperation(int, Enum):
    ANSWER = 0
    START = 2
    DONE = 3
    ERROR = 4
    AGENT_REQUEST = 5


class InteractionRequest(BaseModel):
    question: str
    headers: dict[str, str] = {}
    operation: InteractionOperation = InteractionOperation.QUESTION


class UserToAgentInteraction(BaseModel):
    """Sends a user response to an agent request"""

    request_id: str
    response: str
    operation: InteractionOperation = InteractionOperation.USER_RESPONSE


class ARAGException(BaseModel):
    detail: str


class ValidationFeedbackSchema(BaseModel):
    call_tool: bool


class PromptFeedbackSchema(BaseModel):
    prompt_id: str
    data: Any


class Feedback(BaseModel):
    request_id: str
    feedback_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    question: str
    module: str
    agent_id: str
    data: Any
    timeout_ms: int = 10_000
    response_schema: Any


class AragAnswer(BaseModel):
    exception: Optional[ARAGException] = None
    answer: Optional[str] = None
    agent_request: Optional[str] = None
    generated_text: Optional[str] = None
    step: Optional[Step] = None
    possible_answer: Optional[Answer] = None
    context: Optional[Context] = None
    operation: AnswerOperation = AnswerOperation.ANSWER
    seqid: Optional[int] = None
    original_question_uuid: Optional[str] = None
    actual_question_uuid: Optional[str] = None
    feedback: Optional[Feedback] = None
