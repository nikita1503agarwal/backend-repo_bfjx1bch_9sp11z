import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import create_document, get_documents, db
from schemas import User as UserSchema, Post as PostSchema, Comment as CommentSchema, Offer as OfferSchema

app = FastAPI(title="CampusLink API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Helpers ----------

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    if "_id" in out:
        out["id"] = out.pop("_id")
    return out


def serialize_list(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [serialize_doc(d) for d in docs]


# ---------- Root & Health ----------

@app.get("/")
def read_root():
    return {"message": "CampusLink backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# ---------- Users ----------

@app.post("/api/users")
def create_user(user: UserSchema):
    inserted_id = create_document("user", user)
    return {"id": inserted_id}


@app.get("/api/users")
def list_users(role: Optional[str] = Query(None, description="Filter by role: student|professor|company")):
    filt: Dict[str, Any] = {}
    if role:
        filt["role"] = role
    docs = get_documents("user", filt, limit=200)
    return serialize_list(docs)


# ---------- Posts ----------

@app.post("/api/posts")
def create_post(post: PostSchema):
    inserted_id = create_document("post", post)
    return {"id": inserted_id}


@app.get("/api/posts")
def list_posts(
    type: Optional[str] = Query(None, description="question|internship_request|discussion"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    created_by: Optional[str] = Query(None, description="Filter by author id"),
    limit: int = Query(50, ge=1, le=200)
):
    filt: Dict[str, Any] = {}
    if type:
        filt["type"] = type
    if created_by:
        filt["created_by"] = created_by
    if tag:
        filt["tags"] = {"$in": [tag]}
    docs = get_documents("post", filt, limit=limit)
    # newest first if possible (by created_at)
    docs.sort(key=lambda d: d.get("created_at"), reverse=True)
    return serialize_list(docs)


# ---------- Comments ----------

@app.post("/api/comments")
def create_comment(comment: CommentSchema):
    inserted_id = create_document("comment", comment)
    return {"id": inserted_id}


@app.get("/api/comments")
def list_comments(post_id: str, limit: int = Query(100, ge=1, le=500)):
    docs = get_documents("comment", {"post_id": post_id}, limit=limit)
    docs.sort(key=lambda d: d.get("created_at"))
    return serialize_list(docs)


# ---------- Offers ----------

@app.post("/api/offers")
def create_offer(offer: OfferSchema):
    inserted_id = create_document("offer", offer)
    return {"id": inserted_id}


@app.get("/api/offers")
def list_offers(post_id: Optional[str] = None, created_by: Optional[str] = None, limit: int = Query(100, ge=1, le=300)):
    filt: Dict[str, Any] = {}
    if post_id:
        filt["post_id"] = post_id
    if created_by:
        filt["created_by"] = created_by
    docs = get_documents("offer", filt, limit=limit)
    docs.sort(key=lambda d: d.get("created_at"), reverse=True)
    return serialize_list(docs)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
