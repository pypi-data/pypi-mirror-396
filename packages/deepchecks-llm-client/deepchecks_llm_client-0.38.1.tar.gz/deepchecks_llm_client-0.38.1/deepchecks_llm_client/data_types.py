import enum
import logging
import typing as t
from dataclasses import dataclass
from datetime import datetime

from deepchecks_llm_client.utils import check_topic
from pytz import UTC

__all__ = ["EnvType", "AnnotationType", "Interaction", "Step", "Application",
           "ApplicationType", "ApplicationVersion", "ApplicationVersionSchema",
           "LogInteraction", "InteractionType", "BuiltInInteractionType", "UserValueProperty",
           "PropertyColumnType", "UserValuePropertyType", "InteractionCompleteEvents",
           "InteractionTypeVersionData", "CreateInteractionTypeVersionData", "UpdateInteractionTypeVersionData",
           "Span", "SpanKind"]


logging.basicConfig()
logger = logging.getLogger(__name__)


class EnvType(str, enum.Enum):
    PROD = "PROD"
    EVAL = "EVAL"
    PENTEST = "PENTEST"


class AnnotationType(str, enum.Enum):
    GOOD = "good"
    BAD = "bad"
    UNKNOWN = "unknown"


class PropertyColumnType(str, enum.Enum):
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"


@dataclass
class Step:
    name: str
    value: str

    def to_json(self):
        return {
            self.name: self.value
        }

    @classmethod
    def as_jsonl(cls, steps):
        if steps is None:
            return None
        return [step.to_json() for step in steps]


@dataclass
class UserValueProperty:
    """Data class representing user provided property"""
    name: str
    value: t.Any
    reason: t.Optional[str] = None


@dataclass
class Interaction:
    user_interaction_id: t.Union[str, int]
    input: str
    output: str
    information_retrieval: t.Union[str, t.List[str]]
    history: t.Union[str, t.List[str]]
    full_prompt: str
    expected_output: str
    action: str
    tool_response: str
    is_completed: bool
    metadata: t.Dict[str, str]
    tokens: int
    builtin_properties: t.Dict[str, t.Any]
    user_value_properties: t.Dict[str, t.Any]
    custom_prompt_properties: t.Dict[str, t.Any]
    properties_reasons: t.Dict[str, t.Any]
    created_at: datetime
    interaction_datetime: datetime
    interaction_type: str
    topic: str
    session_id: t.Union[str, int]
    annotation: t.Optional[AnnotationType]
    annotation_reason: t.Optional[str]


@dataclass
class InteractionUpdate:
    """A dataclass representing an update interaction object.

        Attributes
        ----------
        input : str
            Input data
        output : str
            Output data
        expected_output : str, optional
            Full expected output data, defaults to None
        full_prompt : str, optional
            Full prompt data, defaults to None
        action : str, optional
            Action taken during the interaction, defaults to None
        tool_response : str, optional
            Tool response data, defaults to None
        information_retrieval : str, optional
            Information retrieval, defaults to None
        history : str, optional
            History (for instance "chat history"), defaults to None
        annotation : AnnotationType, optional
            Annotation type of the interaction, defaults to None
        steps : list of Step, optional
            List of steps taken during the interaction, defaults to None
        user_value_properties : list of UserValueProperty, optional
            Additional user value properties, defaults to None
        annotation_reason : str, optional
            Reason for the annotation, defaults to None
        started_at : datetime or float, optional
            Timestamp the interaction started at. Datetime format is deprecated, use timestamp instead
        finished_at : datetime or float, optional
            Timestamp the interaction finished at. Datetime format is deprecated, use timestamp instead
        is_completed : bool, optional
            Indicates if the interaction is completed, defaults to True
        metadata : dict, optional
            Metadata for the interaction, defaults to None
        tokens : int, optional
            Token count for the interaction, defaults to None
        """
    input: t.Optional[str] = None
    output: t.Optional[str] = None
    information_retrieval: t.Optional[t.Union[str, t.List[str]]] = None
    history: t.Optional[t.Union[str, t.List[str]]] = None
    full_prompt: t.Optional[str] = None
    expected_output: t.Optional[str] = None
    action: t.Optional[str] = None
    tool_response: t.Optional[str] = None
    is_completed: bool = True
    metadata: t.Optional[t.Dict[str, str]] = None
    tokens: t.Optional[int] = None
    annotation: t.Optional[t.Union[AnnotationType, str]] = None
    annotation_reason: t.Optional[str] = None
    steps: t.Optional[t.List[Step]] = None
    user_value_properties: t.Optional[t.List[UserValueProperty]] = None
    started_at: t.Optional[t.Union[datetime, float]] = None
    finished_at: t.Optional[t.Union[datetime, float]] = None

    def to_json(self):
        if isinstance(self.started_at, datetime) or isinstance(self.finished_at, datetime):
            logger.warning(
                "Deprecation Warning: Usage of datetime for started_at/finished_at is deprecated, use timestamp instead."
            )
            self.started_at = (self.started_at.timestamp() if isinstance(self.started_at, datetime) else self.started_at) \
                if self.started_at else datetime.now(tz=UTC).timestamp()
            self.finished_at = (self.finished_at.timestamp() if isinstance(self.finished_at, datetime) else self.finished_at) \
                if self.finished_at else None

        data = {
            "input": self.input,
            "output": self.output,
            "expected_output": self.expected_output,
            "action": self.action,
            "tool_response": self.tool_response,
            "full_prompt": self.full_prompt,
            "information_retrieval": self.information_retrieval
            if self.information_retrieval is None or isinstance(self.information_retrieval, list)
            else [self.information_retrieval],
            "history": self.history
            if self.history is None or isinstance(self.history, list)
            else [self.history],
            "annotation": (
                None if self.annotation is None else
                self.annotation.value if isinstance(self.annotation, AnnotationType)
                else str(self.annotation).lower().strip()
            ),
            "steps": [step.to_json() for step in self.steps] if self.steps else None,
            "custom_properties": {prop.name: prop.value for prop in self.user_value_properties} if self.user_value_properties else None,
            "custom_properties_reasons": {
                prop.name: prop.reason for prop in self.user_value_properties if prop.reason
            } if self.user_value_properties else None,
            "annotation_reason": self.annotation_reason,
            "is_completed": self.is_completed,
            "metadata": self.metadata,
            "tokens": self.tokens,
        }
        if self.started_at:
            data["started_at"] = self.started_at
        if self.finished_at:
            data["finished_at"] = self.finished_at

        return data


@dataclass
class LogInteraction(InteractionUpdate):
    """A dataclass representing a new interaction object.

    Attributes
    ----------
    input : str
        Input data
    output : str
        Output data
    expected_output : str, optional
        Full expected output data, defaults to None
    full_prompt : str, optional
        Full prompt data, defaults to None
    annotation : AnnotationType, optional
        Annotation type of the interaction, defaults to None
    user_interaction_id : str, optional
        Unique identifier of the interaction, defaults to None
    steps : list of Step, optional
        List of steps taken during the interaction, defaults to None
    user_value_properties : list of UserValueProperty, optional
        Additional user value properties, defaults to None
    information_retrieval : str, optional
        Information retrieval, defaults to None
    history : str, optional
        History (for instance "chat history"), defaults to None
    annotation_reason : str, optional
        Reason for the annotation, defaults to None
    started_at : datetime or float, optional
        Timestamp the interaction started at. Datetime format is deprecated, use timestamp instead
    finished_at : datetime or float, optional
        Timestamp the interaction finished at. Datetime format is deprecated, use timestamp instead
    vuln_type : str, optional
        Type of vulnerability (Only used in case of EnvType.PENTEST and must be sent there), defaults to None
    vuln_trigger_str : str, optional
        Vulnerability trigger string (Only used in case of EnvType.PENTEST and is optional there), defaults to None
    session_id: str, optional
        The identifier for the session associated with this interaction.
        If not provided, a session ID will be automatically generated.
    interaction_type: str, optional
        The type of interaction.
        None is deprecated. If not provided, the interaction type will default to the application's default type.
    metadata: t.Dict[str, str], optional
        Metdata for the interaction.
    tokens: int, optional
        Token count for the interaction.
    """
    user_interaction_id: t.Optional[t.Union[str, int]] = None
    vuln_type: t.Optional[str] = None
    vuln_trigger_str: t.Optional[str] = None
    topic: t.Optional[str] = None
    interaction_type: t.Optional[str] = None
    session_id: t.Optional[t.Union[str, int]] = None

    def to_json(self):
        data = super().to_json()
        if self.interaction_type is None:
            logger.warning(
                "Deprecation Warning: The value 'None' for 'interaction_type' is deprecated. "
                "Please specify an explicit interaction type."
            )

        # rename custom_properties to custom_props:
        data["custom_props"] = data.pop("custom_properties", None)
        data["custom_props_reasons"] = data.pop("custom_properties_reasons", None)

        data.update({
            "user_interaction_id": str(self.user_interaction_id) if self.user_interaction_id is not None else None,
            "vuln_type": self.vuln_type,
            "vuln_trigger_str": self.vuln_trigger_str,
            "session_id": str(self.session_id) if self.session_id is not None else None,
            "interaction_type": self.interaction_type,
        })
        check_topic(self.topic)
        if self.topic is not None:
            data["topic"] = self.topic

        return data


class SpanKind(str, enum.Enum):
    LLM = "LLM"
    TOOL = "TOOL"
    CHAIN = "CHAIN"
    AGENT = "AGENT"
    RETRIEVAL = "RETRIEVER"


@dataclass
class Span:
    """A dataclass representing a span within a trace for tracking nested operations.

    A Span represents a unit of work within a distributed trace, allowing you to track
    hierarchical relationships between operations. This is designed to work with the
    OtelParser system for converting spans into interactions.

    Attributes
    ----------
    span_id : str
        The unique identifier for this span
    span_name : str
        The name of this span, describing the operation being tracked
    span_kind : SpanKind
        The type of span (Root is CHAIN without parent_id)
    trace_id : str
        The unique identifier for the trace this span belongs to. All spans
        in the same trace share this ID
    parent_id : str or None
        The ID of the parent span for tree structure. None if this is the root span
    started_at : float
        Timestamp when the span started (numeric value for ordering)
    finished_at : float
        Timestamp when the span finished (numeric value for ordering)
    status_code : {'OK', 'ERROR'}, optional
        The status code indicating whether the span completed successfully.
        'OK' indicates success, 'ERROR' indicates failure. Defaults to 'OK'
    status_description : str or None, optional
        Human-readable description providing additional context about the status,
        particularly useful for explaining error conditions. Defaults to None
    input : str, optional
        Input data for this span's operation, defaults to None
    output : str, optional
        Output data from this span's operation, defaults to None
    full_prompt : str, optional
        Full prompt data, defaults to None
    expected_output : str, optional
        Expected output data, defaults to None
    information_retrieval : str, optional
        Information retrieval data, defaults to None
    tokens : int, optional
        Token count for aggregation purposes, defaults to None
    graph_parent_name : str, optional
        Graph metadata indicating "who triggered me" (the span_name of another span), defaults to None
    session_id : str, optional
        The identifier for the session associated with this span, defaults to None
    metadata : t.Dict[str, str], optional
        Additional metadata for the span, defaults to None
    """

    span_id: str
    span_name: str
    trace_id: str
    span_kind: SpanKind
    parent_id: t.Optional[str]
    started_at: float
    finished_at: float
    status_code: t.Literal['OK', 'ERROR'] = 'OK'
    status_description: t.Optional[str] = None
    input: t.Optional[str] = None
    output: t.Optional[str] = None
    full_prompt: t.Optional[str] = None
    expected_output: t.Optional[str] = None
    information_retrieval: t.Optional[t.List[str]] = None
    tokens: t.Optional[int] = None
    graph_parent_name: t.Optional[str] = None
    session_id: t.Optional[str] = None
    metadata: t.Optional[t.Dict[str, str]] = None

    def to_span_data(self):
        attributes = {
            "deepchecks.agent.framework": "deepchecks_sdk",
            "openinference.span.kind": self.span_kind
        }

        # Text fields with .value suffix in attributes
        if self.input is not None:
            attributes["input.value"] = self.input
        if self.output is not None:
            attributes["output.value"] = self.output
        if self.full_prompt is not None:
            attributes["full_prompt.value"] = self.full_prompt
        if self.expected_output is not None:
            attributes["expected_output.value"] = self.expected_output
        if self.information_retrieval is not None:
            attributes["information_retrieval.value"] = self.information_retrieval

        # Token count (optional, for aggregation)
        if self.tokens is not None:
            attributes["llm.token_count.total"] = self.tokens

        # Graph parent name (who triggered me)
        if self.graph_parent_name is not None:
            attributes["graph.node.id"] = self.span_name
            attributes["graph.node.parent_id"] = self.graph_parent_name

        # Session ID (optional)
        if self.session_id is not None:
            attributes["session.id"] = self.session_id

        # Metadata (optional)
        if self.metadata is not None:
            attributes["metadata"] = self.metadata

        # Convert timestamps to ISO 8601 format with Z suffix (CrewAI format)
        start_time_iso = datetime.fromtimestamp(self.started_at, tz=UTC).isoformat().replace('+00:00', 'Z')
        end_time_iso = datetime.fromtimestamp(self.finished_at, tz=UTC).isoformat().replace('+00:00', 'Z')

        # Build the span structure matching OTEL format
        span_data = {
            "name": self.span_name,
            "kind": "SpanKind.INTERNAL",
            "status": {"status_code": self.status_code, "description": self.status_description},
            "events": [],
            "context": {
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "trace_state": "[]",
            },
            "parent_id": self.parent_id,
            "start_time": start_time_iso,
            "end_time": end_time_iso,
            "attributes": attributes,
        }

        return span_data


@dataclass
class UserValuePropertyType:
    display_name: str
    type: t.Union[PropertyColumnType, str]
    description: t.Union[str, None] = None


class BuiltInInteractionType(str, enum.Enum):
    QA = "Q&A"
    OTHER = "Other"
    SUMMARIZATION = "Summarization"
    CLASSIFICATION = "Classification"
    GENERATION = "Generation"
    FEATURE_EXTRACTION = "Feature Extraction"
    TOOL_USE = "Tool Use"
    RETRIEVAL = "Retrieval"
    CHAT = "Chat"
    CHAIN = "Chain"
    ROOT = "Root"
    LLM = "LLM"
    AGENT = "Agent"
    TOOL = "Tool"


class ApplicationType(str, enum.Enum):
    QA = "Q&A"
    OTHER = "OTHER"
    SUMMARIZATION = "SUMMARIZATION"
    GENERATION = "GENERATION"
    CLASSIFICATION = "CLASSIFICATION"
    FEATURE_EXTRACTION = "FEATURE EXTRACTION"
    TOOL_USE = "Tool Use"
    RETRIEVAL = "Retrieval"
    CHAT = "Chat"
    CHAIN = "Chain"
    ROOT = "Root"
    LLM = "LLM"
    AGENT = "Agent"
    TOOL = "Tool"


class InteractionCompleteEvents(str, enum.Enum):
    TOPICS_COMPLETED = "topics_completed"
    PROPERTIES_COMPLETED = "properties_completed"
    SIMILARITY_COMPLETED = "similarity_completed"
    LLM_PROPERTIES_COMPLETED = "llm_properties_completed"
    ANNOTATION_COMPLETED = "annotation_completed"
    DC_EVALUATION_COMPLETED = "dc_evaluation_completed"
    BUILTIN_LLM_PROPERTIES_COMPLETED = "builtin_llm_properties_completed"


@dataclass
class ApplicationVersionSchema:
    name: str
    description: t.Optional[str] = None
    additional_fields: t.Optional[t.Dict[str, t.Any]] = None

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "additional_fields": self.additional_fields if self.additional_fields else {}
        }


@dataclass
class ApplicationVersion:
    """A dataclass representing an Application Version.

    Attributes
    ----------
    id : int
        Version id
    name : str
        Version name
    ai_model : str
        AI model used within this version
    created_at : datetime
        Version created at timestamp
    updated_at : datetime
        Version updated at timestamp
    custom : list of dict
        Additional details about the version as key-value pairs
        This member is deprecated. It will be removed in future versions. Use additional_fields instead.
    additional_fields : dict
        Additional details about the version as dict
    """

    id: int
    name: str
    ai_model: str
    created_at: datetime
    updated_at: datetime
    description: t.Optional[str] = None
    additional_fields: t.Optional[t.Dict[str, t.Any]] = None


@dataclass
class Application:
    id: int
    name: str
    kind: ApplicationType
    created_at: datetime
    updated_at: datetime
    in_progress: bool
    versions: t.List[ApplicationVersion]
    interaction_types: t.List[str]
    description: t.Optional[str] = None
    log_latest_insert_time_epoch: t.Optional[int] = None
    n_of_llm_properties: t.Optional[int] = None
    n_of_interactions: t.Optional[int] = None
    notifications_enabled: t.Optional[bool] = None


@dataclass
class InteractionTypeVersionData:
    """A dataclass representing interaction type version data.

    Attributes
    ----------
    id : int
        Interaction type version data id
    interaction_type_id : int
        Interaction type id
    application_version_id : int
        Application version id
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict
        Additional metadata parameters
    created_at : datetime
        Created at timestamp
    updated_at : datetime
        Updated at timestamp
    """
    id: int
    interaction_type_id: int
    application_version_id: int
    model: t.Optional[str] = None
    prompt: t.Optional[str] = None
    metadata_params: t.Dict[str, t.Any] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class CreateInteractionTypeVersionData:
    """A dataclass for creating interaction type version data.

    Attributes
    ----------
    interaction_type_id : int
        Interaction type id
    application_version_id : int
        Application version id
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict
        Additional metadata parameters
    """
    interaction_type_id: int
    application_version_id: int
    model: t.Optional[str] = None
    prompt: t.Optional[str] = None
    metadata_params: t.Dict[str, t.Any] = None

    def to_json(self):
        return {
            "interaction_type_id": self.interaction_type_id,
            "application_version_id": self.application_version_id,
            "model": self.model,
            "prompt": self.prompt,
            "metadata_params": self.metadata_params or {},
        }


@dataclass
class UpdateInteractionTypeVersionData:
    """A dataclass for updating interaction type version data.

    Attributes
    ----------
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict or None
        Additional metadata parameters
    """
    model: t.Optional[str] = None
    prompt: t.Optional[str] = None
    metadata_params: t.Optional[t.Dict[str, t.Any]] = None

    def to_json(self):
        return {
            "model": self.model,
            "prompt": self.prompt,
            "metadata_params": self.metadata_params,
        }


@dataclass
class InteractionType:
    id: int
    name: str
