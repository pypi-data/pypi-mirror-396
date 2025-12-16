from pydantic import BaseModel, Field
from typing import Annotated, Generic
from nexo.types.string import OptStrT


class Recommendation(BaseModel, Generic[OptStrT]):
    recommendation: Annotated[
        OptStrT, Field(..., description="Checkup ASCVD Risk's recommendation")
    ]
