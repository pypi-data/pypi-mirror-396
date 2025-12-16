class MlFlowConfig:

    def __init__(self, **kwargs):
        self.tracking_host = kwargs.get('tracking_host', "http://localhost:5050")
        self.mlflow_system_prompt_id = kwargs.get('mlflow_system_prompt_id', None)
        self.mlflow_user_prompt_id = kwargs.get('mlflow_user_prompt_id', None)

    tracking_host: str
    mlflow_system_prompt_id: str | None
    mlflow_user_prompt_id: str | None