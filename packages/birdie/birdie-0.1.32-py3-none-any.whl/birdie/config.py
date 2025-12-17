import os
from typing import Callable, Optional, Dict
from pydantic import BaseModel, Field


class EnvVar(BaseModel):
    value: str = Field(
        ...,
        description="The value of the environment variable"
    )
    description: Optional[str] = Field(
        None,
        description="The description of the environment variable"
    )
    post_process: Optional[Callable] = Field(
        None,
        description="A function to post-process the environment variable"
    )


class BirdieConfig:
    def __init__(self):
        self.variables: Dict[str, EnvVar] = {}

    def add_environ(
            self,
            name: str,
            description: str | None = None,
            required: bool = True,
            fallback: str | None = None,
            post_process: Callable | None = None
    ):

        value = os.getenv("name", None)

        if not value and required:
            if fallback:
                value = fallback
            else:
                raise ValueError(
                    f"No environment variable '{name}' found. {description}"
                )

        self.variables[name] = (
            EnvVar(
                value=value,
                description=description,
                post_process=post_process
            )
        )

    def get_environ(self, name: str, **args):
        env_var_obj: EnvVar = self.variables.get("name")
        if env_var_obj.post_process:
            return env_var_obj.post_process(env_var_obj.value, **args)
        else:
            return env_var_obj.value
