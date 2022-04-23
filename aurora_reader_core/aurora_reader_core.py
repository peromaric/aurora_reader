from fastapi import FastAPI
import aurora_reader_core.router
from aurora_reader_core.router import router as aurora_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


class AuroraReader:
    def __init__(self):
        self.api: FastAPI = FastAPI(
            title="Get the apr that's it",
            description="Get the auroraswap apr"
        )
        self.api.include_router(aurora_router)
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"], #allow frontend to connect
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"], )

        self._run_uvicorn()


    def _run_uvicorn(self) -> None:
        uvicorn.run(self.api, host="0.0.0.0", port=8888)

    def get_api(self) -> FastAPI:
        return self.api
