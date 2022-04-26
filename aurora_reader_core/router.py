from fastapi_utils.inferring_router import InferringRouter
from starlette.responses import RedirectResponse
from aurora_reader_core.auroraswap import Auroraswap

"""
router with its .get and .post routes below.
include this router in a fastapi instance.
"""
router: InferringRouter = InferringRouter()


@router.get(
    "/",
    summary="Home Page"
)
async def home():
    response: RedirectResponse = RedirectResponse(url="/docs")  # redirect to interface
    return response


@router.get(
    "/apr",
    summary="Returns auroraswap's annual yield"
)
async def get_auroraswap_apr():
    return Auroraswap().calculate_rewards()
