"""Mock HR API"""
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="Mock HR API")

employees_db: dict = {}


class CreateEmployeeRequest(BaseModel):
    name: str
    department: str
    role: str
    start_date: str


@app.post("/v1/employees")
async def create_employee(request: CreateEmployeeRequest):
    employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"

    employees_db[employee_id] = {
        "employee_id": employee_id,
        "name": request.name,
        "department": request.department,
        "role": request.role,
        "start_date": request.start_date,
        "status": "active",
    }

    return {
        "employee_id": employee_id,
        "message": f"員工 {request.name} 已創建",
    }


@app.get("/v1/employees/{employee_id}")
async def get_employee(employee_id: str):
    if employee_id not in employees_db:
        return {"error": "Employee not found"}
    return employees_db[employee_id]


@app.get("/v1/employees")
async def list_employees():
    return {"employees": list(employees_db.values())}


@app.get("/healthz")
async def health():
    return {"status": "healthy"}
