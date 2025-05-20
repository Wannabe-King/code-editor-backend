from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import docker
import uuid
import os

app = FastAPI()
client = docker.from_env()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins like ["https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Or restrict to specific methods like ["POST"]
    allow_headers=["*"],  # Or restrict to specific headers
)

class CodeInput(BaseModel):
    code: str
    input: str
    language: str = "python"

@app.post("/execute")
def execute_code(data: CodeInput):
    # Create a temporary file
    filename = f"{uuid.uuid4().hex}.py"
    filepath = f"./temp_codes/{filename}"

    with open(filepath, "w") as f:
        f.write(data.code)

    try:
        # Run code inside Docker with input piped via bash
        command = f"bash -c 'echo \"{data.input}\" | python {filename}'"

        output = client.containers.run(
            image="python:3.10",
            command=command,
            volumes={
                os.path.abspath("temp_codes"): {
                    "bind": "/app",
                    "mode": "ro"
                }
            },
            working_dir="/app",
            remove=True,
            stdout=True,
            stderr=True
        )

        return {"output": output.decode(), "error": ""}
    
    except docker.errors.ContainerError as e:
        return {"output": "", "error": e.stderr.decode() if e.stderr else str(e)}
    
    finally:
        os.remove(filepath)
