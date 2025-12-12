from __future__ import annotations

from typing import Any, Dict, List, Protocol, TypeVar

from accl.llm.base import BaseLLM
from accl.utils.prompt_loader import load_prompt
from accl.generator.llm_parser import parse_json_from_llm
from accl.generator.base import LLMGeneratedQuestion


class HasMetaAndPayload(Protocol):
    """
    Protocol for context objects with ``meta`` and ``payload`` attributes.

    Any context type used with :func:`generate_questions` must conform to
    this protocol. Typical examples include:

    * :class:`ChartQuestionContext`
    * :class:`DataTableQuestionContext`

    Attributes
    ----------
    meta : Any
        Metadata object describing the question (for example, year,
        subject, category, ID prefix).
    payload : Any
        Pydantic model instance representing the template payload
        (for example, chart config or data-table definition).
    """

    meta: Any
    payload: Any


ContextT = TypeVar("ContextT", bound=HasMetaAndPayload)


def generate_questions(
    context: Dict[str, List[ContextT]],
    context_key: str,
    model: BaseLLM,
    *,
    count: int = 1,
    prompt_key: str = "default_prompt",
    template_type: str = "",
    meta_cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate LLM questions for any template type using a shared pattern.

    This helper encapsulates the common LLM call flow used by different
    template types (charts, data tables, angles, etc.):

    1. Load a prompt template by key via :func:`load_prompt`.
    2. For each context object under ``context[context_key]``:
       - Serialise the payload to JSON via ``payload.model_dump_json()``.
       - Fill the prompt template placeholders.
       - Call the LLM and parse JSON from the response.
       - Validate each question via :class:`LLMGeneratedQuestion`.
       - Attach the original ``meta`` and ``payload`` to the result.

    Parameters
    ----------
    context : dict
        Mapping from a context key (for example, ``"charts"``,
        ``"data_tables"``) to a list of context objects that conform
        to :class:`HasMetaAndPayload`.
    context_key : str
        Key in ``context`` whose list of context objects should be
        processed (for example, ``"charts"`` or ``"data_tables"``).
    model : BaseLLM
        LLM wrapper used to invoke the underlying model. Must provide
        an ``invoke(prompt: str)`` method and return an object with a
        ``content`` attribute or a raw string.
    count : int, optional
        Number of questions the LLM should generate per context
        (used to fill the ``{{COUNT}}`` placeholder), by default 1.
    prompt_key : str, optional
        Key used by :func:`load_prompt` to fetch the YAML prompt
        template, by default ``"default_prompt"``.
    template_type : str, optional
        Logical template type label (for example, ``"chart"``,
        ``"datatable"``, ``"angle"``). Injected into the prompt via
        the ``{{TEMPLATE_TYPE}}`` placeholder, by default an empty
        string.
    meta_cfg : dict, optional
        Additional metadata context used by the prompt template.
        Common keys include:

        * ``"year"`` : str or int
        * ``"subject"`` : str
        * ``"category"`` : str

        These are injected into the prompt placeholders
        ``{{YEAR}}``, ``{{SUBJECT}}`` and ``{{TOPIC}}``.

    Returns
    -------
    list of dict
        Flattened list of results. Each item has the shape::

            {
                "meta": <QuestionMeta as dict>,
                "template": <payload as dict>,
                "llm_question": <LLMGeneratedQuestion as dict>,
            }
    """
    prompt_template = load_prompt(prompt_key)

    items = context[context_key]
    meta_cfg = meta_cfg or {}

    year = meta_cfg.get("year", "")
    subject = meta_cfg.get("subject", "")
    topic = meta_cfg.get("category", "")

    results: List[Dict[str, Any]] = []

    for ctx in items:
        payload_json = ctx.payload.model_dump_json()

        prompt = (
            prompt_template
            .replace("{{PAYLOAD_JSON}}", payload_json)
            .replace("{{COUNT}}", str(count))
            .replace("{{YEAR}}", str(year))
            .replace("{{SUBJECT}}", str(subject))
            .replace("{{TOPIC}}", str(topic))
            .replace("{{TEMPLATE_TYPE}}", template_type)
        )

        response = model.invoke(prompt)
        raw = getattr(response, "content", str(response))
        questions_json = parse_json_from_llm(raw)

        validated_questions = [
            LLMGeneratedQuestion.model_validate(q).model_dump()
            for q in questions_json
        ]

        for q in validated_questions:
            results.append(
                {
                    "meta": ctx.meta.model_dump(),
                    "template": ctx.payload.model_dump(),
                    "llm_question": q,
                }
            )

    return results
