"""Mock Active Directory API"""
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="Mock AD API")

accounts_db: dict = {}


class CreateAccountRequest(BaseModel):
    username: str
    display_name: str
    department: str
    role: str
    temp_password: str


@app.post("/v1/accounts")
async def create_account(request: CreateAccountRequest):
    account_id = str(uuid.uuid4())
    email = f"{request.username}@company.com"

    accounts_db[account_id] = {
        "account_id": account_id,
        "username": request.username,
        "display_name": request.display_name,
        "department": request.department,
        "role": request.role,
        "email": email,
        "temp_password": request.temp_password,
    }

    return {
        "account_id": account_id,
        "email": email,
        "message": f"賬戶 {request.username} 已創建",
    }


@app.get("/v1/check-username/{username}")
async def check_username(username: str):
    taken = any(a["username"] == username for a in accounts_db.values())
    return {"available": not taken}


@app.get("/v1/accounts/{account_id}")
async def get_account(account_id: str):
    if account_id not in accounts_db:
        return {"error": "Account not found"}
    return accounts_db[account_id]


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
