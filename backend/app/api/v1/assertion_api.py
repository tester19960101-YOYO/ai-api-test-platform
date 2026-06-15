from fastapi import APIRouter, HTTPException

from app.core.assertion_dsl import assertion_to_dsl, assertions_to_dsl_list, parse_assertion_dsl
from app.core.response import success_response
from app.schemas.assertion import AssertionParseRequest, AssertionToDslRequest

router = APIRouter()


@router.post("/assertion/parse")
def parse_assertion(payload: AssertionParseRequest) -> dict:
    try:
        assertion = parse_assertion_dsl(payload.dsl, source="user", enabled=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return success_response({"dsl": payload.dsl, "assertion": assertion})


@router.post("/assertion/to-dsl")
def to_dsl(payload: AssertionToDslRequest) -> dict:
    try:
        if isinstance(payload.assertion, list):
            dsl = assertions_to_dsl_list(payload.assertion)
        else:
            dsl = assertion_to_dsl(payload.assertion)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return success_response({"dsl": dsl})
