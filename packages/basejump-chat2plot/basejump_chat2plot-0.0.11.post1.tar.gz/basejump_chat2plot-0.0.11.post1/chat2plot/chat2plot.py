import copy
import re
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Literal, Type, TypeVar


import commentjson
import jsonschema
import pandas as pd
import pydantic

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.chat_engine import SimpleChatEngine

from plotly.graph_objs import Figure

from chat2plot.dataset_description import description
from chat2plot.dictionary_helper import delete_null_field
from chat2plot.prompt import (
    JSON_TAG,
    error_correction_prompt,
    explanation_prompt,
    system_prompt,
)
from chat2plot.render import draw_plotly,draw_altair
from chat2plot.schema import PlotConfig, ResponseType, get_schema_of_chart_config

_logger = getLogger(__name__)

T = TypeVar("T", bound=pydantic.BaseModel)
ModelDeserializer = Callable[[dict[str, Any]], T]

# These errors are caught within the application.
# Other errors (e.g. openai.error.RateLimitError) are propagated to user code.
_APPLICATION_ERRORS = (
    pydantic.ValidationError,
    jsonschema.ValidationError,
    ValueError,
    KeyError,
    AssertionError,
)


@dataclass(frozen=True)
class Plot:
    figure: Figure | None
    config: PlotConfig | dict[str, Any] | pydantic.BaseModel | None
    response_type: ResponseType
    explanation: str
    conversation_history: list[ChatMessage] | None


class ChatSession:
    """chat with conversation history"""
    
    def __init__(
        self,
        llm: BaseChatEngine,
        df: pd.DataFrame,
        system_prompt_template: str,
        user_prompt_template: str,
        description_strategy: str = "head",
        functions: list[dict[str, Any]] | None = None,
    ):
        self._system_prompt_template = system_prompt_template
        self._user_prompt_template = user_prompt_template
        self.llm = llm
        #Replaced BaseMessage with ChatMessage
        self.agent = SimpleChatEngine.from_defaults(
                llm=self.llm,
                chat_history=[
                    ChatMessage(
                        role=MessageRole.SYSTEM,
                        content=system_prompt_template.format(
                            dataset=description(df, description_strategy)
                        )
                    )
                ]
            )
        self._functions = functions

    @property
    def history(self) -> list[ChatMessage]:
        return copy.deepcopy(self.agent._memory.get_all())

    def query(self, q: str, raw: bool = False) -> ChatMessage:
        prompt = q if raw else self._user_prompt_template.format(text=q)
        response = self._query(prompt)
        return response

    def _query(self, prompt: str) -> ChatMessage:
        response = self.agent.chat(message=prompt)  
        print(response.response)
        return response

    def last_response(self) -> str:
        return self.history[-1].content


class Chat2PlotBase:
    @property
    def session(self) -> ChatSession:
        raise NotImplementedError()

    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        raise NotImplementedError()

    def __call__(
        self, q: str, config_only: bool = False, show_plot: bool = False
    ) -> Plot:
        return self.query(q, config_only, show_plot)


class Chat2Plot(Chat2PlotBase):
    def __init__(
        self,
        df: pd.DataFrame,
        chart_schema: Literal["simple"] | Type[pydantic.BaseModel],
        *,
        chat: BaseChatEngine | None = None,
        language: str | None = 'English',
        description_strategy: str = "head",
        verbose: bool = False,
        custom_deserializer: ModelDeserializer | None = None,
    ):
        self._target_schema: Type[pydantic.BaseModel] = (
            PlotConfig if chart_schema == "simple" else chart_schema  # type: ignore
        )

        chat_model = _get_or_default_chat_model(chat)

        self._session = ChatSession(
            chat_model,
            df,
            system_prompt("simple", language, self._target_schema),
            "<{text}>",
            description_strategy,
            functions=[
                get_schema_of_chart_config(self._target_schema, as_function=True)
            ]

        )
        self._df = df
        self._verbose = verbose
        self._custom_deserializer = custom_deserializer
        self._language = language

    @property
    def session(self) -> ChatSession:
        return self._session

    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        raw_response = self._session.query(q)

        try:
            if self._verbose:
                _logger.info(f"request: {q}")
                _logger.info(f"first response: {raw_response}")
            return self._parse_response(q, raw_response, config_only, show_plot)
        except _APPLICATION_ERRORS as e:
            if self._verbose:
                _logger.warning(traceback.format_exc())
            msg = e.message if isinstance(e, jsonschema.ValidationError) else str(e)
            error_correction = error_correction_prompt().format(
                error_message=msg,
            )
            corrected_response = self._session.query(error_correction)
            if self._verbose:
                _logger.info(f"retry response: {corrected_response}")

            try:
                return self._parse_response(
                    q, corrected_response, config_only, show_plot
                )
            except _APPLICATION_ERRORS as e:
                if self._verbose:
                    _logger.warning(e)
                    _logger.warning(traceback.format_exc())
                return Plot(
                    None,
                    None,
                    ResponseType.FAILED_TO_RENDER,
                    "",
                    self._session.history,
                )

    def __call__(
        self, q: str, config_only: bool = False, show_plot: bool = False
    ) -> Plot:
        return self.query(q, config_only, show_plot)

    def _parse_response(
        self, q: str, response: ChatMessage, config_only: bool, show_plot: bool
    ) -> Plot:
        
        explanation, json_data = parse_json(response.response)

        try:
            if self._custom_deserializer:
                config = self._custom_deserializer(json_data)
            else:
                config = self._target_schema.parse_obj(json_data)
        except _APPLICATION_ERRORS:
            _logger.warning(traceback.format_exc())
            # To reduce the number of failure cases as much as possible,
            # only check against the json schema when instantiation fails.
            jsonschema.validate(json_data, self._target_schema.schema())
            raise

        if self._verbose:
            _logger.info(config)

        if config_only or not isinstance(config, PlotConfig):
            return Plot(
                None, config, ResponseType.SUCCESS, explanation, self._session.history
            )

        figure = draw_plotly(self._df, config, show_plot)
        return Plot(
            figure, config, ResponseType.SUCCESS, explanation, self._session.history
        )


class Chat2Vega(Chat2PlotBase):
    def __init__(
        self,
        df: pd.DataFrame,
        chat: BaseChatEngine | None = None,
        language: str | None = None,
        description_strategy: str = "head",
        verbose: bool = False,
    ):
        self._session = ChatSession(
            _get_or_default_chat_model(chat),
            df,
            system_prompt("vega", language, None),
            "<{text}>",
            description_strategy,
        )
        self._df = df
        self._verbose = verbose

    @property
    def session(self) -> ChatSession:
        return self._session

    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        res = ChatMessage(role=MessageRole.ASSISTANT, content=self._session.query(q).response)
        try:
            explanation, config = parse_json(res.content)
            if "data" in config:
                del config["data"]
            if self._verbose:
                _logger.info(config)
        except _APPLICATION_ERRORS:
            _logger.warning(f"failed to parse LLM response: {res}")
            _logger.warning(traceback.format_exc())
            return Plot(
                None, None, ResponseType.UNKNOWN, res.content, self._session.history
            )

        if config_only:
            return Plot(
                None, config, ResponseType.SUCCESS, explanation, self._session.history
            )

        try:
            plot = draw_altair(self._df, config, show_plot)
            return Plot(
                plot, config, ResponseType.SUCCESS, explanation, self._session.history
            )
        except _APPLICATION_ERRORS:
            _logger.warning(traceback.format_exc())
            return Plot(
                None,
                config,
                ResponseType.FAILED_TO_RENDER,
                explanation,
                self._session.history,
            )

    def __call__(
        self, q: str, config_only: bool = False, show_plot: bool = False
    ) -> Plot:
        return self.query(q, config_only, show_plot)

def chat2plot(
    df: pd.DataFrame,
    schema_definition: Literal["simple", "vega"] | Type[pydantic.BaseModel] = "simple",
    chat: BaseChatEngine | None = None,
    language: str | None = None,
    description_strategy: str = "head",
    custom_deserializer: ModelDeserializer | None = None,
    verbose: bool = False,
) -> Chat2PlotBase:
    """Create Chat2Plot instance.

    Args:
        df: Data source for visualization.
        schema_definition: Type of json format; "vega" for vega-lite compliant json, "simple" for chat2plot built-in
              data structure. If you want a custom schema definition, pass a type inheriting from pydantic.BaseModel
              as your own chart setting.
        chat: The chat instance for interaction with LLMs.
              If omitted, `AzureOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613")` will be used.
        language: Language of explanations. If not specified, it will be automatically inferred from user prompts.
        description_strategy: Type of how the information in the dataset is embedded in the prompt.
              Defaults to "head" which embeds the contents of df.head(5) in the prompt.
              "dtypes" sends only columns and types to LLMs and does not send the contents of the dataset,
              which allows for privacy but may reduce accuracy.
        custom_deserializer: A custom function to convert the json returned by the LLM into a object.
        verbose: If `True`, chat2plot will output logs.

    Returns:
        Chat instance.
    """

    if schema_definition == "simple":
        return Chat2Plot(
            df,
            "simple",
            chat=chat,
            language=language,
            description_strategy=description_strategy,
            verbose=verbose,
            custom_deserializer=custom_deserializer,
        )
    if schema_definition == "vega":
        return Chat2Vega(df, chat, language, description_strategy, verbose)
    elif issubclass(schema_definition, pydantic.BaseModel):
        return Chat2Plot(
            df,
            schema_definition,
            chat=chat,
            language=language,
            description_strategy=description_strategy,
            verbose=verbose,
            custom_deserializer=custom_deserializer,
        )
    else:
        raise ValueError(
            f"schema_definition should be one of [simple, vega] or pydantic.BaseClass (given: {schema_definition})"
        )


def _extract_tag_content(s: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*)</{tag}>", s, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1)
    else:
        m = re.search(rf"<{tag}>(.*)<{tag}>", s, re.MULTILINE | re.DOTALL)
        if m:
            return m.group(1)
    return ""


def parse_json(content: str) -> tuple[str, dict[str, Any]]:
    """parse json and split contents by pre-defined tags"""
    json_part = _extract_tag_content(content, "json")  # type: ignore
    if not json_part:
        raise ValueError(f"failed to find {JSON_TAG[0]} and {JSON_TAG[1]} tags")

    explanation_part = _extract_tag_content(content, "explain")
    if not explanation_part:
        explanation_part = _extract_tag_content(content, "explanation")

    # LLM rarely generates JSON with comments, so use the commentjson package instead of json
    return explanation_part.strip(), delete_null_field(commentjson.loads(json_part))


def _get_or_default_chat_model(chat: BaseChatEngine | None) -> BaseChatEngine:
    if chat is None:
        #Raise not implemented error 'model must be passed in etc.'
        return AzureOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613")  # type: ignore
    return chat



