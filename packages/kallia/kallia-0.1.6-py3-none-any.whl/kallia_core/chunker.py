import kallia_core.models as Models
import kallia_core.prompts as Prompts
from typing import List
from kallia_core.utils import Utils
from kallia_core.messages import Messages


class Chunker:
    @staticmethod
    def create(
        text: str, temperature: float = 0.0, max_tokens: int = 8192
    ) -> List[Models.Chunk]:
        messages = [
            {"role": "system", "content": Prompts.SEMANTIC_CHUNKING_PROMPT},
            {"role": "user", "content": text},
        ]
        response = Messages.send(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = Utils.unwrap_tag("information", response)
        if content is None:
            content = Utils.unwrap_json_tag(response)
        parsed_content = Utils.parse_json(content)
        return parsed_content if parsed_content else []
