from fastapi import FastAPI

app = FastAPI()


def process_question(question: str):
    return {
        "question": question,
        "status": "ready for AI"
    }


@app.post("/questions")
def receive_question(question: str):
    result = process_question(question)

    return result