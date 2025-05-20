from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str
    input: str = ""
    language: str = "python3" 

@app.post("/execute")
async def execute_code(data: CodeInput):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://emkc.org/api/v2/piston/execute",
            json={
                "language": data.language,
                "version": "3.10.0",
                "files": [{"name": "main.py", "content": data.code}],
                "stdin": data.input,
            },
        )
        result = response.json()
        run_result = result.get("run", {})
        return {
            "output": run_result.get('output', ''),
            "error": run_result.get("stderr", "")
        }
