import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from supabase import create_client

app = FastAPI(title="Q-Flow Backend")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase environment variables are missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class LectureRequest(BaseModel):
    title: str
    professor_name: str
    topics: list[str] = []


class QuestionRequest(BaseModel):
    question: str
    lecture_id: int
    student_name: str = "Anonymous"
    student_id: str = ""


@app.get("/")
def home():
    return {"message": "Q-Flow Backend is running"}


@app.post("/lectures")
def create_lecture(data: LectureRequest):
    try:
        # Save lecture
        lecture_result = (
            supabase.table("lectures")
            .insert({
                "title": data.title,
                "professor_name": data.professor_name,
            })
            .execute()
        )

        if not lecture_result.data:
            raise HTTPException(
                status_code=500,
                detail="Lecture was not created"
            )

        lecture = lecture_result.data[0]
        lecture_id = lecture["id"]

        # Save lecture topics
        topics_data = [
            {
                "lecture_id": lecture_id,
                "name": topic.strip(),
                "order": index + 1,
            }
            for index, topic in enumerate(data.topics)
            if topic.strip()
        ]

        saved_topics = []

        if topics_data:
            topics_result = (
                supabase.table("topics")
                .insert(topics_data)
                .execute()
            )
            saved_topics = topics_result.data or []

        return {
            "message": "Lecture created successfully",
            "lecture": lecture,
            "topics": saved_topics,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lectures/{lecture_id}/topics")
def get_topics(lecture_id: int):
    try:
        result = (
            supabase.table("topics")
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
            "student_id": data.student_id,
            "question_text": data.question,
            "topic_id": None,
        }).execute()

        return {
            "message": "Question saved successfully",
            "question": result.data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lectures/{lecture_id}/questions")
def get_student_questions(
    lecture_id: int,
    student_id: str = Query(..., min_length=1),
):
    try:
        result = (
            supabase.table("Questions")
            .select(
                "id, lecture_id, student_name, student_id, "
                "question_text, topic_id, created_at"
            )
            .eq("lecture_id", lecture_id)
            .eq("student_id", student_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lectures/{lecture_id}/questions/count")
def get_question_count(lecture_id: int):
    try:
        result = (
            supabase.table("Questions")
            .select("id", count="exact")
            .eq("lecture_id", lecture_id)
            .execute()
        )

        return {
            "lecture_id": lecture_id,
            "count": result.count or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
