import os
import re
import json
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import litert_lm

# Default path (can be overridden via environment variable)
DEFAULT_MODEL_PATH = os.path.expanduser(
    os.getenv(
        "LITERT_MODEL_PATH",
        "~/litert-models/models/gemma-4-E2B-it.litertlm"
    )
)
MODEL_ID = os.getenv("LITERT_MODEL_ID", "gemma-4-E2B-it")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "4000"))

# Global model engine instance to prevent re-instantiating heavy flatbuffers per request
engine_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine_instance
    if os.path.exists(DEFAULT_MODEL_PATH):
        print(f"📦 Pre-loading LiteRT Engine from: {DEFAULT_MODEL_PATH}")
        try:
            engine_instance = litert_lm.Engine(DEFAULT_MODEL_PATH)
            print("✅ LiteRT Engine loaded successfully.")
        except Exception as e:
            print(f"⚠️ Warning: Could not pre-load LiteRT engine: {e}")
    else:
        print(f"⚠️ Model path does not exist yet: {DEFAULT_MODEL_PATH}")
        print("   The engine will initialize dynamically once the model file is present.")
    yield
    if engine_instance:
        try:
            engine_instance.close()
        except Exception:
            pass

app = FastAPI(
    title="LiteRT-LM OpenAI Bridge for OpenClaw",
    version="1.0.0",
    lifespan=lifespan
)

def get_engine():
    global engine_instance
    if engine_instance is None:
        if not os.path.exists(DEFAULT_MODEL_PATH):
            raise HTTPException(
                status_code=500,
                detail=f"LiteRT model flatbuffer not found at '{DEFAULT_MODEL_PATH}'. Check LITERT_MODEL_PATH."
            )
        engine_instance = litert_lm.Engine(DEFAULT_MODEL_PATH)
    return engine_instance

@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models catalog endpoint."""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "litert-local",
                "permission": [],
                "root": MODEL_ID,
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", True)
    last_user_message = messages[-1]["content"] if messages else ""

    def response_generator():
        engine = get_engine()
        with engine.create_conversation() as conversation:
            for chunk in conversation.send_message_async(last_user_message):
                try:
                    if isinstance(chunk, dict):
                        content = chunk.get("content", {})
                        if isinstance(content, dict):
                            text_delta = content.get("text", "")
                        elif isinstance(content, list) and len(content) > 0:
                            text_delta = content.get("text", "") if isinstance(content, dict) else str(content)
                        else:
                            text_delta = str(content)
                    else:
                        content = getattr(chunk, "content", "")
                        if hasattr(content, "text"):
                            text_delta = content.text
                        elif isinstance(content, list) and len(content) > 0:
                            text_delta = getattr(content, "text", str(content))
                        else:
                            text_delta = str(content)
                except Exception:
                    text_delta = str(chunk)

                # Strip stringified Python list-dict wrappers: "[{'type': 'text', 'text': 'Hello'}]"
                if text_delta.startswith("[{'") or "'text':" in text_delta:
                    match = re.search(r"'text':\s*'([^']*)'", text_delta)
                    if match:
                        text_delta = match.group(1)
                    else:
                        try:
                            start_idx = text_delta.find("'text': '") + 9
                            end_idx = text_delta.rfind("'}")
                            if start_idx > 8 and end_idx > start_idx:
                                text_delta = text_delta[start_idx:end_idx]
                        except Exception:
                            pass

                payload = {
                    "choices": [
                        {
                            "delta": {"content": text_delta},
                            "index": 0,
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(payload)}\n\n"
            
            yield "data: [DONE]\n\n"

    if stream:
        return StreamingResponse(response_generator(), media_type="text/event-stream")
    
    # Non-streaming fallback for agent compaction and summary checks
    engine = get_engine()
    full_text = ""
    with engine.create_conversation() as conversation:
        for chunk in conversation.send_message_async(last_user_message):
            try:
                if isinstance(chunk, dict):
                    content = chunk.get("content", {})
                    t = content.get("text", "") if isinstance(content, dict) else str(content)
                else:
                    content = getattr(chunk, "content", "")
                    t = getattr(content, "text", str(content))
            except Exception:
                t = str(chunk)
            full_text += t

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": full_text},
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }


@app.post("/v1/embeddings")
async def embeddings(request: Request):
    """Mock embeddings endpoint to satisfy OpenClaw memory sync watchers."""
    body = await request.json()
    inputs = body.get("input", "")
    if isinstance(inputs, str):
        inputs = [inputs]
        
    data_payload = [
        {"object": "embedding", "index": idx, "embedding": [0.0] * 768}
        for idx, _ in enumerate(inputs)
    ]
        
    return {
        "object": "list",
        "data": data_payload,
        "model": MODEL_ID,
        "usage": {"prompt_tokens": 0, "total_tokens": 0}
    }

def main():
    import uvicorn
    print(f"⚡ Starting LiteRT OpenAI Bridge on http://{HOST}:{PORT}")
    print(f"📦 Configured Model Path: {DEFAULT_MODEL_PATH}")
    uvicorn.run(app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()
