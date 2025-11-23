import uuid
from datetime import datetime
from app.repository.quiz_repository import QuizRepository


class QuizService:
    """Service layer for quiz operations"""
    
    @staticmethod
    def get_quiz_details(connection, quiz_id: str):
        """Get complete quiz details with all questions and options"""
        quiz = QuizRepository.get_quiz_by_id(connection, quiz_id)
        
        if not quiz:
            return None
        
        questions = QuizRepository.get_questions_by_quiz(connection, quiz_id)
        
        questions_data = []
        for question in questions:
            options = QuizRepository.get_options_by_question(connection, question["id"])
            
            options_data = [
                {
                    "id": option["id"],
                    "content": option["content"],
                    "category": option["category"],
                }
                for option in options
            ]
            
            question_data = {
                "id": question["id"],
                "question_text": question["question_text"],
                "question_category": question["question_category"],
                "explanation": question["explanation"],
                "options": options_data,
            }
            questions_data.append(question_data)
        
        return {
            "id": quiz["id"],
            "title": quiz["title"],
            "description": quiz["description"],
            "difficulty_level": quiz["difficulty_level"],
            "time_limit": quiz["time_limit"],
            "level": quiz["level"],
            "created_at": quiz["created_at"].isoformat() if quiz["created_at"] else None,
            "total_questions": len(questions_data),
            "questions": questions_data,
        }
    
    @staticmethod
    def get_all_quizzes(connection, skip: int = 0, limit: int = 100):
        """Get all quizzes with pagination"""
        quizzes = QuizRepository.get_all_quizzes(connection, skip, limit)
        
        return [
            {
                "id": quiz["id"],
                "title": quiz["title"],
                "description": quiz["description"],
                "difficulty_level": quiz["difficulty_level"],
                "time_limit": quiz["time_limit"],
                "level": quiz["level"],
                "created_at": quiz["created_at"].isoformat() if quiz["created_at"] else None,
            }
            for quiz in quizzes
        ]
    
    @staticmethod
    def start_quiz_attempt(connection, quiz_id: str, user_id: str):
        """Start a new quiz attempt"""
        quiz = QuizRepository.get_quiz_by_id(connection, quiz_id)
        
        if not quiz:
            return None
        
        questions = QuizRepository.get_questions_by_quiz(connection, quiz_id)
        attempt_id = str(uuid.uuid4())
        
        attempt = QuizRepository.create_attempt(connection, attempt_id, quiz_id, user_id, len(questions))
        
        return {
            "attempt_id": attempt["id"],
            "quiz_id": attempt["quiz_id"],
            "user_id": attempt["user_id"],
            "total_questions": attempt["total_questions"],
            "is_completed": attempt["is_completed"],
        }
    
    @staticmethod
    def submit_answer(connection, attempt_id: str, question_id: str, selected_option_id: str):
        """Submit an answer for a question"""
        attempt = QuizRepository.get_attempt_by_id(connection, attempt_id)
        
        if not attempt:
            return None
        
        question = QuizRepository.get_question_by_id(connection, question_id)
        option = QuizRepository.get_option_by_id(connection, selected_option_id)
        
        if not question or not option:
            return None
        
        answer_id = str(uuid.uuid4())
        answer = QuizRepository.create_attempt_answer(connection, answer_id, attempt_id, question_id, selected_option_id)
        
        return {
            "answer_id": answer["id"],
            "attempt_id": answer["attempt_id"],
            "question_id": answer["question_id"],
            "selected_option_id": answer["selected_option_id"],
            "is_correct": option["is_correct"],
        }
    
    @staticmethod
    def submit_camera_answer(connection, attempt_id: str, question_id: str, is_correct: bool):
        """Submit a camera-based answer"""
        attempt = QuizRepository.get_attempt_by_id(connection, attempt_id)
        
        if not attempt:
            return None
        
        question = QuizRepository.get_question_by_id(connection, question_id)
        
        if not question:
            return None
        
        options = QuizRepository.get_options_by_question(connection, question_id)
        camera_option = options[0] if options else None
        
        if not camera_option:
            return None
        
        answer_id = str(uuid.uuid4())
        answer = QuizRepository.create_attempt_answer(connection, answer_id, attempt_id, question_id, camera_option["id"])
        
        return {
            "answer_id": answer["id"],
            "attempt_id": answer["attempt_id"],
            "question_id": answer["question_id"],
            "is_correct": is_correct,
        }
    
    @staticmethod
    def submit_quiz(connection, attempt_id: str):
        """Submit/complete a quiz attempt and calculate final score"""
        attempt = QuizRepository.get_attempt_by_id(connection, attempt_id)
        
        if not attempt:
            return None
        
        answers = QuizRepository.get_attempt_answers(connection, attempt_id)
        
        # Calculate score
        correct_count = 0
        for answer in answers:
            option = QuizRepository.get_option_by_id(connection, answer["selected_option_id"])
            if option and option["is_correct"]:
                correct_count += 1
        
        # Update attempt
        attempt = QuizRepository.update_attempt_score(connection, attempt_id, correct_count)
        
        return {
            "attempt_id": attempt["id"],
            "quiz_id": attempt["quiz_id"],
            "user_id": attempt["user_id"],
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": round((attempt["score"] / attempt["total_questions"] * 100), 2),
            "is_completed": attempt["is_completed"],
            "submitted_at": attempt["submitted_at"].isoformat() if attempt["submitted_at"] else None,
        }
    
    @staticmethod
    def get_attempt_result(connection, attempt_id: str):
        """Get detailed attempt result"""
        attempt = QuizRepository.get_attempt_by_id(connection, attempt_id)
        
        if not attempt:
            return None
        
        answers = QuizRepository.get_attempt_answers(connection, attempt_id)
        
        answers_detail = []
        for answer in answers:
            question = QuizRepository.get_question_by_id(connection, answer["question_id"])
            option = QuizRepository.get_option_by_id(connection, answer["selected_option_id"])
            
            answers_detail.append({
                "question_id": answer["question_id"],
                "question_text": question["question_text"] if question else None,
                "question_category": question["question_category"] if question else None,
                "selected_option_id": answer["selected_option_id"],
                "selected_option_content": option["content"] if option else None,
                "is_correct": option["is_correct"] if option else False,
                "explanation": question["explanation"] if question else None,
            })
        
        return {
            "attempt_id": attempt["id"],
            "quiz_id": attempt["quiz_id"],
            "user_id": attempt["user_id"],
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": round((attempt["score"] / attempt["total_questions"] * 100), 2),
            "is_completed": attempt["is_completed"],
            "submitted_at": attempt["submitted_at"].isoformat() if attempt["submitted_at"] else None,
            "answers": answers_detail,
        }
