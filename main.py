import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: List[dict] | None = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatResponse(BaseModel):
    reply: str
    messages: List[ChatMessage]


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Dummy chat endpoint that simulates an assistant reply.
    It reflects the user's message with a friendly, helpful tone and a short tip.
    """
    user_msg = (req.message or "").strip()

    if not user_msg:
        assistant_reply = (
            "Hi! I'm a lightweight demo assistant. Ask me anything, or say hello to get started."
        )
    else:
        # Simple playful transformation to feel interactive without external deps
        reversed_hint = user_msg[::-1][:40]
        assistant_reply = (
            f"You said: '{user_msg}'. Here's a quick thought: focus on one clear step next. "
            f"(fun hint: '{reversed_hint}' backwards)."
        )

    history: List[ChatMessage] = []
    if req.history:
        # Keep only last few messages for brevity, validate roles if present
        for m in req.history[-8:]:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role in ("user", "assistant", "system"):
                history.append(ChatMessage(role=role, content=content))

    history.append(ChatMessage(role="user", content=user_msg))
    history.append(ChatMessage(role="assistant", content=assistant_reply))

    return ChatResponse(reply=assistant_reply, messages=history)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
