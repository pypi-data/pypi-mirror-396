class LlmConfig:

    def __init__(self, **kwargs):
        self.temperature = kwargs.get('temperature', 0.0)
        self.top_k = kwargs.get('top_k', 1)
        self.top_p = kwargs.get('top_p', None)
        self.max_tokens = kwargs.get('max_tokens', 40)
        self.repeat_penalty = kwargs.get('repeat_penalty', None)
        self.frequency_penalty = kwargs.get('frequency_penalty', None)
        self.presence_penalty = kwargs.get('presence_penalty', None)
        self.typical_p = kwargs.get('typical_p', None)
        self.num_thread = kwargs.get('num_thread', None)

    temperature: float
    top_k: int
    top_p: float | None
    max_tokens: int
    repeat_penalty: float | None
    frequency_penalty: float | None
    presence_penalty: float | None
    typical_p: float | None
    num_thread: int | None