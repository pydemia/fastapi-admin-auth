from tiktoken import encoding_for_model
from asgiref.sync import async_to_sync, sync_to_async


from corusapi.types.enums.model import ModelType


class TokenCalculator:
    """
    User Input의 Token 수를 계산하여 반환해주는 함수.
    """
    def __init__(self, model_type: str = "gpt-3.5-turbo") -> None:
        self.model_type = model_type
        self.encoding = encoding_for_model(model_type)

    def calculate(self, text: str) -> int:
        token_size = len(self.encoding.encode(text))
        return token_size

    def calculate_naver(self, text: str) -> int:
        return async_to_sync(self.acalculate_naver)(text)

    async def acalculate_naver(self, text: str) -> int:
        from corusadmin.llm.models import naver_token_compute_model
        tokenizer = await sync_to_async(naver_token_compute_model)()
        return await tokenizer.acalc_token(text)
