import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import User, Book, Transaction, Document, Subscription, ForumPost, Club, Report, SecuritySettings

app = FastAPI(title="LibVault API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "LibVault API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# --- Minimal CRUD endpoints to support UI scaffolding ---
@app.post("/users", response_model=dict)
def create_user(user: User):
    inserted_id = create_document("user", user)
    return {"id": inserted_id}

@app.get("/users", response_model=List[dict])
def list_users():
    return get_documents("user")

@app.post("/books", response_model=dict)
def create_book(book: Book):
    inserted_id = create_document("book", book)
    return {"id": inserted_id}

@app.get("/books", response_model=List[dict])
def list_books():
    return get_documents("book")

@app.post("/transactions", response_model=dict)
def create_tx(tx: Transaction):
    inserted_id = create_document("transaction", tx)
    return {"id": inserted_id}

@app.get("/transactions", response_model=List[dict])
def list_txs():
    return get_documents("transaction")

@app.post("/documents", response_model=dict)
def create_document_meta(doc: Document):
    inserted_id = create_document("document", doc)
    return {"id": inserted_id}

@app.get("/documents", response_model=List[dict])
def list_documents():
    return get_documents("document")

# Simple AI endpoints (stubs to be replaced with real providers)
class AISummaryRequest(BaseModel):
    text: str

@app.post("/ai/summarize")
def ai_summarize(req: AISummaryRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    # naive summary stub
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    summary = '. '.join(sentences[:2]) + ('.' if sentences else '')
    return {"summary": summary or text[:140]}

class AISearchRequest(BaseModel):
    query: str

@app.post("/ai/search")
def ai_search(req: AISearchRequest):
    q = req.query.lower()
    # Return top few matching books by title/author as a demo
    results = db["book"].find({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"author": {"$regex": q, "$options": "i"}}]}).limit(10) if db else []
    return {"results": list(results)}

class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    seed_tags: Optional[List[str]] = None

@app.post("/ai/recommend")
def ai_recommend(req: RecommendationRequest):
    # naive content-based: return books sharing tags
    query = {"tags": {"$in": req.seed_tags or []}} if (req.seed_tags) else {}
    results = db["book"].find(query).limit(10) if db else []
    return {"results": list(results)}

# Upload endpoint placeholder for documents; in production use object storage
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # save to tmp folder as demo
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"url": f"/files/{file.filename}"}

@app.get("/files/{filename}")
def get_file(filename: str):
    path = os.path.join("uploads", filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return StreamingResponse(open(path, "rb"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
