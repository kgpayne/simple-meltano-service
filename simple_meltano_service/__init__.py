import logging
import os
import subprocess
import tempfile

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger(__name__)

# TODO: source this automagically from the current python environmen, or just use the host's meltano
PATH = "/Users/kp/Library/Caches/pypoetry/virtualenvs/simple-meltano-service-vRXJhctv-py3.11/bin"


@app.get("/")
async def root():
    return {"message": "Hello World"}


class EnvVar(BaseModel):
    name: str
    value: str


class Extractor(BaseModel):
    name: str
    variant: str | None


class Loader(BaseModel):
    name: str
    variant: str | None


class RunRequest(BaseModel):
    extractor: Extractor
    loader: Loader
    env_vars: list[EnvVar]


@app.post("/run/")
async def run(run_request: RunRequest):
    # create temporary project directory
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        base_env = {
            "PATH": os.environ.get("PATH") + f":{PATH}"
        }  # needed for host binaries such as git

        # create meltano project
        result = subprocess.run(
            ["meltano", "init", "."],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=base_env,
        )
        logger.info(result.stdout)

        # add extractor
        cmd = ["meltano", "add", "extractor", run_request.extractor.name]
        if run_request.extractor.variant:
            cmd.extend(["--variant", run_request.extractor.variant])

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=tmpdir, env=base_env
        )
        logger.info(result.stdout)
        if result.returncode != 0:
            return {
                "message": "Failed to add extractor!",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }, 500

        # add loader
        cmd = ["meltano", "add", "loader", run_request.loader.name]
        if run_request.loader.variant:
            cmd.extend(["--variant", run_request.loader.variant])

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=tmpdir, env=base_env
        )
        logger.info(result.stdout)
        if result.returncode != 0:
            return {
                "message": "Failed to add loader!",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }, 500

        # run pipeline
        cmd = [
            "meltano",
            "run",
            run_request.extractor.name,
            run_request.loader.name,
        ]
        run_env = {env_var.name: env_var.value for env_var in run_request.env_vars}
        run_env.update(base_env)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=run_env,
        )
        logger.info(result.stdout)

        if result.returncode != 0:
            return {
                "message": "Failed to run pipeline!",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }, 500

        return {
            "message": "Pipeline run successfully!",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }, 200
