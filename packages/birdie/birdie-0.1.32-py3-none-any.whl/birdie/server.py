from typing import Callable
from fastapi import FastAPI
import httpx

from birdie.output import ResultModel
from birdie.input import InteractModel


class BirdieAPI(FastAPI):
    def __init__(self,
                 init_func: Callable,
                 interact_func: Callable,
                 input_func: Callable,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        async def init_wrapper(input: dict):
            async def update_progress(
                title: str,
                description: str
            ):
                url = f"{input['birdie_host']}/api/v1/chat/webhook/progress"
                headers = {
                    "Authorization": f"Bearer {input['birdie_token']}",
                    "Content-Type": "application/json"
                }
                data = {
                    "title": title,
                    "description": description
                }
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            url,
                            json=data,
                            headers=headers
                        )
                        return response.json()
                except Exception as e:
                    print(f"Failed to send update: {e}")

            return await init_func(
                input,
                update_progress
            )

        self.add_api_route(
            "/initialize",
            init_wrapper,
            methods=["POST"],
            response_model=ResultModel
        )

        async def interact_wrapper(input: InteractModel):
            async def update_progress(
                title: str,
                description: str
            ):
                url = f"{input.birdie_host}/api/v1/chat/webhook/progress"
                headers = {
                    "Authorization": f"Bearer {input.birdie_token}",
                    "Content-Type": "application/json"
                }
                data = {
                    "title": title,
                    "description": description
                }
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            url,
                            json=data,
                            headers=headers
                        )
                        return response.json()
                except Exception as e:
                    print(f"Failed to send update: {e}")

            return await interact_func(
                input.message,
                input.state,
                input.result,
                update_progress
            )

        self.add_api_route(
            "/interact",
            interact_wrapper,
            methods=["POST"],
            response_model=ResultModel
        )
        self.add_api_route(
            "/input",
            input_func,
            methods=["GET"]
        )



