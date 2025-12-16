from pydantic import BaseModel


class DummyModel(BaseModel):
    """Placeholder model to satisfy linting until real models are added."""

    message: str = "Hello from core"


def hello() -> str:
    print('1O')
    return DummyModel().message
