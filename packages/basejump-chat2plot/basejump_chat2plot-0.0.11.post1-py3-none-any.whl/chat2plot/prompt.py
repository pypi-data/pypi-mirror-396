import json
from textwrap import dedent
from typing import Type

import pydantic

from chat2plot.schema import get_schema_of_chart_config

JSON_TAG = ["<json>", "</json>"]
EXPLANATION_TAG = ["<explain>", "</explain>"]


def system_prompt(
    model_type: str,
    language: str | None,
    target_schema: Type[pydantic.BaseModel] | None,
) -> str:
    return (
        _task_definition_part(model_type, target_schema)
        + "\n"
        + _data_and_detailed_instruction_part(language)
    )


def error_correction_prompt() -> str:

    return dedent(
        """
        Your response fails with the following error:
        {error_message}

        Correct the json and return a new explanation and json that fixes the above mentioned error.
        Do not generate the same json again.
    """
    )


def explanation_prompt(language: str | None, user_original_query: str) -> str:
    language_spec = (
        language
        or f'the same language as the user\'s original question (question: "{user_original_query}")'
    )
    prompt = dedent(
        f"""
    For the graph setting you have just output,
    please explain why you have output this graph setting in response to the user's question.
    The response MUST be in {language_spec}.
    """
    )
    return prompt


def _task_definition_part(
    model_type: str, target_schema: Type[pydantic.BaseModel] | None
) -> str:
    if model_type == "simple":

        assert target_schema is not None

        schema_json = json.dumps(
            get_schema_of_chart_config(
                target_schema, inlining_refs=True, remove_title=True
            ),
            indent=2,
        )

        return (
            dedent(
                """
                Your task is to generate chart configuration for the given dataset and user question delimited by <>.
                Every chart created should have all axis labeled with informative names to avoid having function definitions shown by default.
                Make sure to be careful with dates - if they are not truncated and have information by day, then all 365 days per year will be shown on the axis.
                Truncate the dates when appropriate to be careful not to show too many datapoints on the x axis. For example, bars in bar charts are difficult to
                see with that many data points.
                Responses should be in JSON format compliant to the following JSON Schema.

                """
            )
            + schema_json.replace("{", "{{").replace("}", "}}")
        )

    else:
        return dedent(
            """
            Your task is to generate chart configuration for the given dataset and user question delimited by <>.
            Every chart created should have all axis labeled with informative names to avoid having function definitions shown by default.
            Make sure to be careful with dates - if they are not truncated and have information by day, then all 365 days per year will be shown on the axis.
            Truncate the dates when appropriate to be careful not to show too many datapoints on the x axis. For example, bars in bar charts are difficult to
            see with that many data points.
            Responses should be in JSON format compliant with the vega-lite specification,
            but `data` field must be excluded.
            """
        )


def _data_and_detailed_instruction_part(language: str | None) -> str:
    language_spec = language or "English"

    dataset_description_part = dedent(
        """
        Note that the user may want to refine the chart by asking a follow-up question to a previous request,
        or may want to create a new chart in a completely new context.
        In the latter case, be careful not to use the context used for the previous chart.

        {dataset}
        """
    )

    instruction_part = dedent(
        f"""
        You should do the following step by step, and your response should include both 1 and 2:
        1. Explain whether filters should be applied to the data, which chart_type and columns should be used,
            and what transformations are necessary to fulfill the user's request.
            The explanation MUST be in {language_spec},
            and be understandable to someone who does not know the JSON schema definition.
            This text should be enclosed with {EXPLANATION_TAG[0]} and {EXPLANATION_TAG[1]} tag.
        2. Generate schema-compliant JSON that represents 1.
            This text should be enclosed with {JSON_TAG[0]} and {JSON_TAG[1]} tag.
        """
    )

    return dataset_description_part + instruction_part
