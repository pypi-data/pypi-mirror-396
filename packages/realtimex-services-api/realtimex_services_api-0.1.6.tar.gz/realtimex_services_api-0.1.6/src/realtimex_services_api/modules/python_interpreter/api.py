"""A2A Agents API Router."""

import traceback
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse

# Initialize router with tags for OpenAPI documentation
python_interpreter_router = APIRouter(tags=["python-interpreter"])


def _create_error_response(
    status_code: int, error_code: str, message: str, details: dict = None
) -> JSONResponse:
    """Create standardized error response."""
    content = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


@python_interpreter_router.post("/run")
async def run_script(request: Request, body: Any = Body(None)) -> JSONResponse:
    """
    Run python script
    """
    import tempfile
    import subprocess
    import os
    import re
    import json
    import hashlib

    from ...utils import (
        get_uv_executable,
        load_env_configs,
        get_cache_dir
    )

    try:
        script_content = body["script"]
        flow_variables = {}
        if "variables" in body:
            flow_variables = body["variables"]

        run_id = ""
        if "run_id" in body:
            run_id = body["run_id"]

        session_id = None
        if "session_id" in body:
            session_id = body["session_id"]
            flow_variables["session_id"] = session_id

        thread_id = None
        if "thread_id" in body:
            thread_id = body["thread_id"]
            flow_variables["thread_id"] = thread_id

        workspace_slug = None
        if "workspace_slug" in body:
            workspace_slug = body["workspace_slug"]
            flow_variables["workspace_slug"] = workspace_slug

        env_configs = load_env_configs()
        my_env = os.environ.copy()
        
        stdout = ""
        stderr = ""
        result = ""

        script_hash = hashlib.sha256(script_content.encode('utf-8')).hexdigest()
        
        cache_dir = os.path.join(get_cache_dir(),".realtimex.ai","python_interpreter")
        os.makedirs(os.path.join(get_cache_dir(),".realtimex.ai","python_interpreter"),exist_ok=True)
        tmp_name = f"{os.path.join(cache_dir,script_hash)}.py"
        payload_tmp_name = ""

        if run_id and flow_variables:
            tmp_name = f"{os.path.join(cache_dir,run_id)}.py"
            payload_tmp_name = f"{os.path.join(cache_dir,run_id)}.json"
            with open(payload_tmp_name, 'w') as f:
                json.dump(flow_variables,f)

        with open(tmp_name, 'w') as f:
            f.write(script_content)
        
        process = subprocess.Popen(
            [
                get_uv_executable(),
                "run",
                tmp_name,
                run_id,
                payload_tmp_name
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=my_env,
            text=True,
            shell=False  # Don't use shell=True unless you really need it
        )

        stdout, stderr = process.communicate()
        # print("process",[
        #         get_uv_executable(),
        #         "run",
        #         tmp_name,
        #         run_id,
        #         payload_tmp_name
        #     ])
        # print("stdout",stdout)
        # print("stderr",stderr)

        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        if os.path.exists(payload_tmp_name):
            os.remove(payload_tmp_name)
        

        match = re.search(r"<output>(.*?)</output>", stdout, re.DOTALL)
        if match:
            result = match.group(1)
            try:
                result = json.loads(result)
            except ValueError as e:
                pass
        

        return {"success": True,"error": {},"stdout":stdout,"stderr":stderr,"result":result}

    except HTTPException as e:
        if e.status_code == 400:
            return _create_error_response(400, "INVALID_INPUT", e.detail)
        elif e.status_code == 404:
            return _create_error_response(404, "USER_NOT_FOUND", e.detail)
        else:
            return _create_error_response(e.status_code, "REQUEST_ERROR", e.detail)
    except Exception as e:
        print(traceback.format_exc())
        return _create_error_response(500, "INTERNAL_ERROR", str(e))

