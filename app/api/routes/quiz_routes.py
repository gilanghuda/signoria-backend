from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.db_connection import get_db
from app.core.middleware.jwt import get_current_user
from app.services.quiz_services import QuizService
from pydantic import BaseModel

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


# Request/Response Models
class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_option_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "selected_option_id": "660e8400-e29b-41d4-a716-446655440000"
            }
        }


class SubmitCameraAnswerRequest(BaseModel):
    question_id: str
    is_correct: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_correct": True
            }
        }


# Routes
@router.get("", summary="List all quizzes")
def list_quizzes(skip: int = 0, limit: int = 10, db = Depends(get_db)):
    """
    Get all available quizzes with pagination.
    
    **Parameters:**
    - `skip`: Number of quizzes to skip (default: 0)
    - `limit`: Number of quizzes to return per page (default: 10)
    
    **Returns:** List of quiz summaries with metadata
    
    **Example Request:**
    ```
    GET /api/quizzes?skip=0&limit=10
    ```
    """
    quizzes = QuizService.get_all_quizzes(db, skip, limit)
    
    return {
        "status": "success",
        "data": quizzes,
        "count": len(quizzes)
    }


@router.get("/{quiz_id}", summary="Get quiz details")
def get_quiz(quiz_id: str, db = Depends(get_db)):
    """
    Get complete quiz with all questions and options.
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz
    
    **Returns:**
    Complete quiz object with:
    - Quiz metadata (title, description, level, time_limit)
    - All questions with their options
    - For `image_alphabet`: text options (A, B, C, D)
    - For `image_options`: image path options
    - For `camera_based`: empty options array
    
    **⚠️ Important:** The `is_correct` field is NOT included in responses to prevent cheating!
    
    **Example Request:**
    ```
    GET /api/quizzes/550e8400-e29b-41d4-a716-446655440000
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Quiz Level 1 - Huruf/Angka: A dan B",
        "level": 1,
        "total_questions": 10,
        "questions": [
          {
            "id": "660e8400-...",
            "question_text": "https://signoria.gilanghuda.my.id/dict/dictionary/A.jpg",
            "question_category": "image_alphabet",
            "explanation": "Karakter: A",
            "options": [
              {"id": "770e8400-...", "content": "A", "category": "text"},
              {"id": "770e8400-...", "content": "F", "category": "text"}
            ]
          }
        ]
      }
    }
    ```
    """
    quiz_details = QuizService.get_quiz_details(db, quiz_id)
    
    if not quiz_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return {
        "status": "success",
        "data": quiz_details
    }


@router.post("/{quiz_id}/attempts", summary="Start quiz attempt")
def start_quiz_attempt(
    quiz_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Start a new quiz attempt OR resume an ongoing attempt.
    
    **Behavior:**
    - If user has NO ongoing attempt: Creates new attempt
    - If user has ongoing attempt: Returns existing attempt (resume)
    
    **Authentication:** 
    - Automatically extracted from HTTP-only cookies or Authorization header
    - No need to pass user_id in request body
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    
    **Returns:**
    - `attempt_id`: Unique ID for this attempt (use for answer submissions)
    - `quiz_id`: The quiz being attempted
    - `user_id`: Your user ID (auto from JWT)
    - `total_questions`: Number of questions in this quiz
    - `is_completed`: false (until you submit)
    - `is_resumed`: Boolean - true if resuming, false if new
    
    **Example Request:**
    ```
    POST /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts
    
    Headers:
    - Cookie: access_token=<your-jwt-token>
    OR
    - Authorization: Bearer <your-jwt-token>
    ```
    
    **Example Response (New Attempt):**
    ```json
    {
      "status": "success",
      "data": {
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "total_questions": 10,
        "is_completed": false,
        "is_resumed": false
      }
    }
    ```
    
    **Example Response (Resumed Attempt):**
    ```json
    {
      "status": "success",
      "data": {
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "total_questions": 10,
        "is_completed": false,
        "is_resumed": true
      }
    }
    ```
    
    **⚠️ Important:**
    - Check `is_resumed` to determine if this is new or continuation
    - If resuming, frontend should fetch progress to show where user left off
    - Same attempt_id is used for answer submissions
    """
    attempt = QuizService.start_quiz_attempt(db, quiz_id, user_id)
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return {
        "status": "success",
        "data": attempt
    }


@router.get("/{quiz_id}/attempts/{attempt_id}/progress", summary="Get attempt progress")
def get_attempt_progress(
    quiz_id: str,
    attempt_id: str,
    db = Depends(get_db)
):
    """
    Get detailed progress of an ongoing attempt.
    
    **Use Cases:**
    - When resuming: Show how many questions answered vs remaining
    - Show which questions user already answered
    - Show the user's previous answers
    - Track progress percentage
    - Before submit: Verify all questions answered
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    - `attempt_id`: UUID of the attempt (path parameter)
    
    **Returns:**
    - `attempt_id`: The attempt ID
    - `quiz_id`: The quiz ID
    - `user_id`: The user ID
    - `total_questions`: Total questions in quiz
    - `answered_questions`: Number of questions already answered
    - `remaining_questions`: Number of questions still to answer
    - `progress_percentage`: Progress as percentage (0-100)
    - `is_completed`: Boolean - false if ongoing, true if submitted
    - `answered_details`: Array of detailed answered questions (NEW!)
      - `answer_id`: The answer submission ID
      - `question_id`: The question ID
      - `question_text`: The question content
      - `question_category`: image_alphabet, image_options, or camera_based
      - `selected_option_id`: The option user selected
      - `selected_option_content`: The content of selected option
      - `is_correct`: Whether the answer was correct
      - `answered_at`: ISO timestamp when answered
    
    **Example Request:**
    ```
    GET /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts/770e8400-e29b-41d4-a716-446655440000/progress
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "total_questions": 10,
        "answered_questions": 3,
        "remaining_questions": 7,
        "progress_percentage": 30.0,
        "is_completed": false,
        "answered_details": [
          {
            "answer_id": "990e8400-e29b-41d4-a716-446655440000",
            "question_id": "660e8400-e29b-41d4-a716-446655440001",
            "question_text": "https://signoria.gilanghuda.my.id/dict/dictionary/A.jpg",
            "question_category": "image_alphabet",
            "selected_option_id": "770e8400-e29b-41d4-a716-446655440001",
            "selected_option_content": "A",
            "is_correct": true,
            "answered_at": "2025-11-24T10:15:30"
          },
          {
            "answer_id": "991e8400-e29b-41d4-a716-446655440000",
            "question_id": "660e8400-e29b-41d4-a716-446655440002",
            "question_text": "Yang mana dibawah ini bahasa isyarat untuk huruf B?",
            "question_category": "image_options",
            "selected_option_id": "770e8400-e29b-41d4-a716-446655440002",
            "selected_option_content": "https://signoria.gilanghuda.my.id/dict/dictionary/B.jpg",
            "is_correct": false,
            "answered_at": "2025-11-24T10:16:15"
          },
          {
            "answer_id": "992e8400-e29b-41d4-a716-446655440000",
            "question_id": "660e8400-e29b-41d4-a716-446655440003",
            "question_text": "Praktikkan bahasa isyarat untuk huruf C",
            "question_category": "camera_based",
            "selected_option_id": "770e8400-e29b-41d4-a716-446655440003",
            "selected_option_content": "C",
            "is_correct": true,
            "answered_at": "2025-11-24T10:17:00"
          }
        ]
      }
    }
    ```
    
    **Usage in Frontend:**
    ```javascript
    // When user resumes quiz
    const progress = await fetch(
      \`/api/quizzes/\${quizId}/attempts/\${attemptId}/progress\`
    ).then(r => r.json());
    
    const { data } = progress;
    
    // Show summary
    console.log(\`Progress: \${data.progress_percentage}%\`);
    console.log(\`Answered: \${data.answered_questions}/\${data.total_questions}\`);
    console.log(\`Remaining: \${data.remaining_questions}\`);
    
    // Show previously answered questions
    data.answered_details.forEach((answer, idx) => {
      console.log(\`\nQuestion \${idx + 1}: \${answer.question_category}\`);
      console.log(\`Your answer: \${answer.selected_option_content}\`);
      console.log(\`Correct: \${answer.is_correct ? '✓' : '✗'}\`);
      console.log(\`Answered at: \${answer.answered_at}\`);
    });
    
    // Highlight which questions to answer next
    const answered_ids = data.answered_details.map(a => a.question_id);
    const remaining = allQuestions.filter(q => !answered_ids.includes(q.id));
    console.log(\`Next question to answer: \${remaining[0]?.question_text}\`);
    ```
    """
    progress = QuizService.get_attempt_progress(db, attempt_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    return {
        "status": "success",
        "data": progress
    }


@router.post("/{quiz_id}/attempts/{attempt_id}/answers", summary="Submit answer")
def submit_answer(
    quiz_id: str,
    attempt_id: str,
    request: SubmitAnswerRequest,
    db = Depends(get_db)
):
    """
    Submit an answer to a question during quiz attempt.
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    - `attempt_id`: UUID from start attempt (path parameter)
    - Request body: question_id and selected_option_id
    
    **Request Body:**
    ```json
    {
      "question_id": "660e8400-e29b-41d4-a716-446655440001",
      "selected_option_id": "770e8400-e29b-41d4-a716-446655440001"
    }
    ```
    
    **Returns:**
    - `answer_id`: ID of this submitted answer
    - `is_correct`: Boolean (true/false) - Use for immediate feedback ONLY
    
    **⚠️ IMPORTANT NOTES:**
    1. Server stores the answer (you don't need to track it)
    2. Do NOT use `is_correct` to update final score
    3. Final score is calculated on `/submit` endpoint
    4. Call this for each question as user progresses through quiz
    
    **Example Request:**
    ```
    POST /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts/770e8400-e29b-41d4-a716-446655440000/answers
    Content-Type: application/json
    
    {
      "question_id": "660e8400-e29b-41d4-a716-446655440001",
      "selected_option_id": "770e8400-e29b-41d4-a716-446655440001"
    }
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "answer_id": "990e8400-e29b-41d4-a716-446655440000",
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "question_id": "660e8400-e29b-41d4-a716-446655440001",
        "selected_option_id": "770e8400-e29b-41d4-a716-446655440001",
        "is_correct": true
      }
    }
    ```
    """
    result = QuizService.submit_answer(
        db,
        attempt_id,
        request.question_id,
        request.selected_option_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt, question, or option not found"
        )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{quiz_id}/attempts/{attempt_id}/camera-answers", summary="Submit camera answer")
def submit_camera_answer(
    quiz_id: str,
    attempt_id: str,
    request: SubmitCameraAnswerRequest,
    db = Depends(get_db)
):
    """
    Submit a camera-based answer (hand gesture recognition result).
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    - `attempt_id`: UUID from start attempt (path parameter)
    - Request body: question_id and is_correct
    
    **Request Body:**
    ```json
    {
      "question_id": "660e8400-e29b-41d4-a716-446655440001",
      "is_correct": true
    }
    ```
    
    **Returns:**
    - `answer_id`: ID of this submitted answer
    - `is_correct`: Result from your ML model
    
    **⚠️ IMPORTANT:**
    - Use this endpoint for `question_category: "camera_based"` ONLY
    - `is_correct` must come from YOUR gesture recognition ML model
    - Server stores this result and scores it on submission
    
    **Example Request:**
    ```
    POST /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts/770e8400-e29b-41d4-a716-446655440000/camera-answers
    Content-Type: application/json
    
    {
      "question_id": "660e8400-e29b-41d4-a716-446655440001",
      "is_correct": true
    }
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "answer_id": "990e8400-e29b-41d4-a716-446655440000",
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "question_id": "660e8400-e29b-41d4-a716-446655440001",
        "is_correct": true
      }
    }
    ```
    """
    result = QuizService.submit_camera_answer(
        db,
        attempt_id,
        request.question_id,
        request.is_correct
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt or question not found"
        )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{quiz_id}/attempts/{attempt_id}/submit", summary="Submit quiz")
def submit_quiz(
    quiz_id: str,
    attempt_id: str,
    db = Depends(get_db)
):
    """
    Submit and complete the quiz. Server calculates final score.
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    - `attempt_id`: UUID from start attempt (path parameter)
    
    **⚠️ IMPORTANT:**
    1. Call this AFTER submitting all answers
    2. Server checks each answer you submitted
    3. Final score is calculated server-side (NOT from client)
    4. No further answer submissions allowed after this
    5. Use returned score as source of truth
    
    **Returns:**
    - `score`: Number of correct answers (calculated by server)
    - `total_questions`: Total questions in quiz
    - `percentage`: Score as percentage (0-100)
    - `is_completed`: true (quiz is now locked)
    - `submitted_at`: ISO timestamp of submission
    
    **Example Request:**
    ```
    POST /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts/770e8400-e29b-41d4-a716-446655440000/submit
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "score": 8,
        "total_questions": 10,
        "percentage": 80.0,
        "is_completed": true,
        "submitted_at": "2025-11-24T10:30:45"
      }
    }
    ```
    """
    result = QuizService.submit_quiz(db, attempt_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/{quiz_id}/attempts/{attempt_id}/result", summary="Get attempt result")
def get_attempt_result(
    quiz_id: str,
    attempt_id: str,
    db = Depends(get_db)
):
    """
    Get detailed results of a completed quiz attempt.
    
    **Parameters:**
    - `quiz_id`: UUID of the quiz (path parameter)
    - `attempt_id`: UUID of the attempt (path parameter)
    
    **Returns:**
    Complete attempt with all answers showing:
    - Each question you answered
    - Your selected option/answer
    - Whether it was correct
    - Explanation for each question
    - Final score and percentage
    
    **Example Request:**
    ```
    GET /api/quizzes/550e8400-e29b-41d4-a716-446655440000/attempts/770e8400-e29b-41d4-a716-446655440000/result
    ```
    
    **Example Response:**
    ```json
    {
      "status": "success",
      "data": {
        "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "score": 8,
        "total_questions": 10,
        "percentage": 80.0,
        "is_completed": true,
        "submitted_at": "2025-11-24T10:30:45",
        "answers": [
          {
            "question_id": "660e8400-e29b-41d4-a716-446655440001",
            "question_text": "https://signoria.gilanghuda.my.id/dict/dictionary/A.jpg",
            "question_category": "image_alphabet",
            "selected_option_id": "770e8400-e29b-41d4-a716-446655440001",
            "selected_option_content": "A",
            "is_correct": true,
            "explanation": "Huruf A dalam SIBI"
          },
          {
            "question_id": "660e8400-e29b-41d4-a716-446655440002",
            "question_text": "Yang mana dibawah ini bahasa isyarat untuk huruf B?",
            "question_category": "image_options",
            "selected_option_id": "770e8400-e29b-41d4-a716-446655440002",
            "selected_option_content": "https://signoria.gilanghuda.my.id/dict/dictionary/B.jpg",
            "is_correct": false,
            "explanation": "Jawaban yang benar adalah: B"
          }
        ]
      }
    }
    ```
    """
    result = QuizService.get_attempt_result(db, attempt_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    return {
        "status": "success",
        "data": result
    }
