import os
import time
import threading
from typing import Any, Dict, List, Optional

from google.genai import Client
from google.api_core.exceptions import ResourceExhausted

from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from config import settings
from accl.utils.config_loader import load_model_config
from accl.generator.llm_parser import parse_json_from_llm
from accl.llm.base import BaseLLM
from accl.utils.token_logger import TokenLogger

# Use a named logger that should be configured in logging_config.yaml
logger = logging.getLogger("llm")


class TokenRateLimiter:
    """
    Simple thread-safe RPM + TPM limiter.
    """

    def __init__(self, max_rpm: int, max_tpm: int):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm

        self.lock = threading.Lock()
        self.request_timestamps: List[float] = []
        self.token_timestamps: List[tuple[float, int]] = []  # (timestamp, tokens)

    def _prune(self) -> None:
        """Remove entries older than 60 seconds."""
        cutoff = time.time() - 60
        self.request_timestamps = [t for t in self.request_timestamps if t > cutoff]
        self.token_timestamps = [
            (t, tok) for (t, tok) in self.token_timestamps if t > cutoff
        ]

    def check(self, incoming_tokens: int) -> None:
        """
        Block with sleep() if limit would be exceeded.

        Parameters
        ----------
        incoming_tokens : int
            Estimated number of tokens for the next request.
        """
        while True:
            with self.lock:
                self._prune()

                req_count = len(self.request_timestamps)
                token_count = sum(tok for _, tok in self.token_timestamps)

                if req_count < self.max_rpm and (token_count + incoming_tokens) < self.max_tpm:
                    # safe to proceed
                    now = time.time()
                    self.request_timestamps.append(now)
                    self.token_timestamps.append((now, incoming_tokens))

                    logger.debug(
                        "RateLimiter allowed request: req_count=%d, token_count=%d, incoming=%d, max_rpm=%d, max_tpm=%d",
                        req_count,
                        token_count,
                        incoming_tokens,
                        self.max_rpm,
                        self.max_tpm,
                    )
                    return

                # need to wait
                sleep_time = 0.1
                logger.debug(
                    "RateLimiter sleeping %.1fs (req_count=%d, token_count=%d, incoming=%d, max_rpm=%d, max_tpm=%d)",
                    sleep_time,
                    req_count,
                    token_count,
                    incoming_tokens,
                    self.max_rpm,
                    self.max_tpm,
                )

            time.sleep(sleep_time)


class GeminiLLM(BaseLLM):
    """
    Gemini LLM with:
      - explicit google-genai client support
      - rate limiter for RPM + TPM
      - token usage logging
    """

    model_cfg = load_model_config()

    DEFAULT_MAX_RPM = model_cfg["model"].get("DEFAULT_MAX_RPM", 30)
    DEFAULT_MAX_TPM = model_cfg["model"].get("DEFAULT_MAX_TPM", 150_000)

    def __init__(
        self,
        model_name: Optional[str] = None,
        client: Optional[Client] = None,
        max_rpm: Optional[int] = None,
        max_tpm: Optional[int] = None,
        token_logger: Optional[TokenLogger] = None,
    ) -> None:
        if model_name is None:
            model_cfg = load_model_config()
            model_name = model_cfg["name"]

        os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

        self._client = client or Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name

        self._model = ChatGoogleGenerativeAI(
            model=model_name,
            client=self._client,
        )

        self.token_logger = token_logger

        self.limiter = TokenRateLimiter(
            max_rpm=max_rpm or self.DEFAULT_MAX_RPM,
            max_tpm=max_tpm or self.DEFAULT_MAX_TPM,
        )

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.current_template: Optional[str] = None
        self.current_batch: Optional[int] = None

        logger.info(
            "Initialised GeminiLLM(model_name=%s, max_rpm=%d, max_tpm=%d)",
            self.model_name,
            self.limiter.max_rpm,
            self.limiter.max_tpm,
        )

    def invoke(self, prompt: str, **kwargs: Any) -> Any:
        """
        Execute a request with rate limiting and token logging.

        Parameters
        ----------
        prompt : str
            Full prompt text to send to the model.

        Returns
        -------
        Any
            Raw response object from `ChatGoogleGenerativeAI`.
        """
        # rough estimate for limiter, not used for billing
        estimated_tokens = int(len(prompt.split()) * 1.3)

        logger.debug(
            "Invoking Gemini model='%s' with estimated_tokens=%d template=%s batch=%s",
            self.model_name,
            estimated_tokens,
            self.current_template,
            self.current_batch,
        )

        # Check local rate limits before hitting the API
        self.limiter.check(estimated_tokens)

        try:
            resp = self._model.invoke(prompt, **kwargs)
        except ResourceExhausted as e:
            # Remote API-level rate limit, back off and retry
            sleep_seconds = 5
            logger.warning(
                "Gemini API rate limit exceeded (ResourceExhausted: %s). "
                "Sleeping for %d seconds and retrying...",
                e,
                sleep_seconds,
            )
            time.sleep(sleep_seconds)
            return self.invoke(prompt, **kwargs)

        # Extract token usage if available
        meta = getattr(resp, "usage_metadata", None)
        in_t = out_t = 0

        if meta:
            # meta may behave like a mapping or an object; getattr + get covers both
            in_t = getattr(meta, "input_tokens", None) or meta.get("input_tokens", 0)
            out_t = getattr(meta, "output_tokens", None) or meta.get("output_tokens", 0)

            self.total_input_tokens += in_t
            self.total_output_tokens += out_t
            total = self.total_input_tokens + self.total_output_tokens

            logger.info(
                "Gemini tokens template=%s batch=%s in=%d out=%d total=%d",
                self.current_template,
                self.current_batch,
                in_t,
                out_t,
                total,
            )
        else:
            logger.debug(
                "No usage_metadata found on Gemini response for template=%s batch=%s",
                self.current_template,
                self.current_batch,
            )

        if self.token_logger and meta:
            try:
                self.token_logger.log_call(
                    template_name=self.current_template or "unknown",
                    batch_id=self.current_batch if self.current_batch is not None else -1,
                    input_tokens=in_t,
                    output_tokens=out_t,
                    metadata=meta,
                )
            except Exception as e:
                logger.exception("Failed to log token usage via TokenLogger: %s", e)

        return resp

    def set_context(self, template_name: str, batch_id: int) -> None:
        """
        Attach context information for logging (template + batch).

        Parameters
        ----------
        template_name : str
            Name / key of the current template being processed.
        batch_id : int
            Identifier for the current batch within that template.
        """
        self.current_template = template_name
        self.current_batch = batch_id
        logger.debug(
            "GeminiLLM context set: template=%s batch=%s",
            template_name,
            batch_id,
        )

    def invoke_json(self, prompt: str, **kwargs: Any) -> List[Dict]:
        """
        Invoke the model and parse the response as JSON.

        Parameters
        ----------
        prompt : str
            Full prompt text to send to the model.

        Returns
        -------
        list of dict
            Parsed JSON content from the model response.
        """
        resp = self.invoke(prompt, **kwargs)
        raw = getattr(resp, "content", str(resp))
        return parse_json_from_llm(raw)
