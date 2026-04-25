from fastapi import APIRouter

router = APIRouter(prefix="/api",tags = ["chat"])

@router.post("/chat")
def chat() -> dict[str,str]:
    return {"message":"Chat emdpoint is ready."}