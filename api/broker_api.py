from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="Mock Broker API")

DECISION_API_URL = "http://127.0.0.1:8000/evaluate-trade"

# ----------------- MODELS -----------------
class OrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    status: str
    reason: str

# ----------------- ENDPOINT -----------------
@app.post("/place-order", response_model=OrderResponse)
def place_order(order: OrderRequest):

    try:
        resp = requests.post(
            DECISION_API_URL,
            json=order.dict(),
            timeout=1
        )
    except Exception:
        # Decision API not reachable at all
        return OrderResponse(
            status="ERROR",
            reason="Decision engine unreachable"
        )

    if resp.status_code != 200:
        # Decision API crashed or returned error
        return OrderResponse(
            status="ERROR",
            reason="Decision engine error"
        )

    try:
        decision_resp = resp.json()
    except ValueError:
        # Response was not JSON
        return OrderResponse(
            status="ERROR",
            reason="Invalid response from decision engine"
        )

    decision = decision_resp.get("decision")

    if decision == "ALLOW":
        return OrderResponse(
            status="EXECUTED",
            reason="Order passed risk checks"
        )

    if decision == "SOFT_DELAY":
        return OrderResponse(
            status="DELAYED",
            reason="Order delayed due to risk conditions"
        )

    if decision == "HARD_BLOCK":
        return OrderResponse(
            status="BLOCKED",
            reason="Order blocked by TradeGuard AI"
        )

    # Fallback safety
    return OrderResponse(
        status="ERROR",
        reason="Unknown decision state"
    )
