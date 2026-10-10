"""Bounded minimal NVIDIA interpreter, reusing the existing provider client."""

from openai import OpenAIError

from nasa_fire_ai.llm.interfaces import NvidiaStructuredClient, ProviderFailure
from nasa_fire_ai.query.native_interpreter import SYSTEM_PROMPT, MinimalInterpretationV2


class NvidiaMinimalInterpreter(NvidiaStructuredClient):
    def interpret_minimal(self, query):
        try:
            response = self.client.with_options(timeout=40, max_retries=0).chat.completions.create(
                model=self.model_identity,
                temperature=0,
                stream=False,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                response_format={"type": "json_object"},
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
            return MinimalInterpretationV2.model_validate_json(response.choices[0].message.content)
        except (OpenAIError, ValueError, TypeError, IndexError) as error:
            raise ProviderFailure(type(error).__name__) from error
