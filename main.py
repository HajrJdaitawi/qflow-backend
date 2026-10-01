import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase environment variables are missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class QuestionRequest(BaseModel):
    question: str
    lecture_id: int
    student_name: str = "Anonymous"


@app.get("/")
def home():
    return {"message": "Q-Flow Backend is running"}


@app.get("/lectures/{lecture_id}/topics")
def get_topics(lecture_id: int):
    try:
        result = (
            supabase.table("Topics")
            .select("id, name, description")
            .eq("lecture_id", lecture_id)
            .execute()
        )
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions")
def receive_question(data: QuestionRequest):
    try:
        result = supabase.table("Questions").insert({
            "lecture_id": data.lecture_id,
            "student_name": data.student_name,
            "question_text": data.question,
            "topic_id": None
        }).execute()

        return {
            "message": "Question saved successfully",
            "question": result.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
