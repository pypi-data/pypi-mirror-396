"""Streaming API endpoints using Server-Sent Events (SSE)."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..db import get_db, get_result
from ..db.connection import get_vibelab_home
from ..models.result import ResultStatus

logger = logging.getLogger(__name__)

router = APIRouter()


async def stream_result_logs(result_id: int) -> AsyncGenerator[str, None]:
    """
    Generator that yields SSE events for a result's streaming logs.
    
    SSE format:
    - event: output|status|patch|error
    - data: JSON payload
    """
    home = get_vibelab_home()
    result_dir = home / "results" / str(result_id)

    combined_path = result_dir / "combined.stream"
    status_path = result_dir / "stream.status"
    patch_path = result_dir / "patch.diff"

    last_combined_size = 0
    last_patch_content = ""
    wait_count = 0
    max_wait = 120  # 60 seconds max wait for stream to start

    # Send initial connection event
    yield f"event: connected\ndata: {json.dumps({'result_id': result_id})}\n\n"

    # Check if result exists and get initial status
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            yield f"event: error\ndata: {json.dumps({'error': 'Result not found'})}\n\n"
            return
        
        # If result is already completed/failed, send final data and exit
        if result.status in (ResultStatus.COMPLETED, ResultStatus.FAILED, ResultStatus.TIMEOUT, ResultStatus.INFRA_FAILURE):
            yield f"event: status\ndata: {json.dumps({'status': result.status.value})}\n\n"
            
            # Send final logs if available
            stdout_file = result_dir / "stdout.log"
            stderr_file = result_dir / "stderr.log"
            if stdout_file.exists():
                yield f"event: output\ndata: {json.dumps({'data': stdout_file.read_text(), 'stream': 'stdout'})}\n\n"
            if stderr_file.exists():
                yield f"event: output\ndata: {json.dumps({'data': stderr_file.read_text(), 'stream': 'stderr'})}\n\n"
            
            # Send patch if available
            if patch_path.exists():
                yield f"event: patch\ndata: {json.dumps({'patch': patch_path.read_text()})}\n\n"
            
            yield f"event: done\ndata: {json.dumps({'status': result.status.value})}\n\n"
            return
        break

    # Wait for streaming to start (but check if status file already exists)
    if status_path.exists():
        # Status file already exists, send it immediately
        last_status = status_path.read_text().strip()
        yield f"event: status\ndata: {json.dumps({'status': last_status})}\n\n"
    else:
        # Wait for streaming to start
        while not status_path.exists() and wait_count < max_wait:
            await asyncio.sleep(0.5)
            wait_count += 1
            # Send keepalive
            yield f": keepalive\n\n"

        if not status_path.exists():
            yield f"event: error\ndata: {json.dumps({'error': 'Stream did not start'})}\n\n"
            return

        # Send initial status
        last_status = status_path.read_text().strip()
        yield f"event: status\ndata: {json.dumps({'status': last_status})}\n\n"

    # Stream loop
    while True:
        # Check status and emit if changed
        status = status_path.read_text().strip() if status_path.exists() else "unknown"
        if status != last_status:
            yield f"event: status\ndata: {json.dumps({'status': status})}\n\n"
            last_status = status

        # Read new combined output
        if combined_path.exists():
            try:
                current_size = combined_path.stat().st_size
                if current_size > last_combined_size:
                    with open(combined_path, "r") as f:
                        f.seek(last_combined_size)
                        new_content = f.read()
                        if new_content:
                            yield f"event: output\ndata: {json.dumps({'data': new_content, 'offset': last_combined_size})}\n\n"
                    last_combined_size = current_size
            except Exception as e:
                logger.warning(f"Error reading combined stream: {e}")

        # Check for patch updates
        if patch_path.exists():
            try:
                patch_content = patch_path.read_text()
                if patch_content != last_patch_content:
                    yield f"event: patch\ndata: {json.dumps({'patch': patch_content})}\n\n"
                    last_patch_content = patch_content
            except Exception:
                pass

        # If completed or failed, send final status and exit
        if status in ("completed", "failed", "infra_failure"):
            # Send any remaining output
            if combined_path.exists():
                try:
                    current_size = combined_path.stat().st_size
                    if current_size > last_combined_size:
                        with open(combined_path, "r") as f:
                            f.seek(last_combined_size)
                            new_content = f.read()
                            if new_content:
                                yield f"event: output\ndata: {json.dumps({'data': new_content})}\n\n"
                except Exception:
                    pass

            # Final patch
            if patch_path.exists():
                try:
                    yield f"event: patch\ndata: {json.dumps({'patch': patch_path.read_text()})}\n\n"
                except Exception:
                    pass

            yield f"event: done\ndata: {json.dumps({'status': status})}\n\n"
            break

        await asyncio.sleep(0.3)


@router.get("/{result_id}/stream")
async def stream_result(result_id: int):
    """
    Stream logs for a result in real-time using Server-Sent Events.
    
    Events:
    - connected: Initial connection established
    - status: Status update (running/completed/failed)
    - output: New log output
    - patch: Git diff update
    - done: Stream finished
    - error: Error occurred
    """
    return StreamingResponse(
        stream_result_logs(result_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/{result_id}/stream/status")
def get_stream_status(result_id: int):
    """Get current streaming status for a result."""
    home = get_vibelab_home()
    status_path = home / "results" / str(result_id) / "stream.status"
    
    if status_path.exists():
        return {"status": status_path.read_text().strip(), "streaming": True}
    
    # Check if result exists and is running
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return {
            "status": result.status.value,
            "streaming": result.status == ResultStatus.RUNNING,
        }

