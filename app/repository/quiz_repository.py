class QuizRepository:
    """Repository for quiz-related database operations using raw psycopg2 SQL"""
    
    @staticmethod
    def get_quiz_by_id(connection, quiz_id: str) -> dict:
        """Get quiz by ID"""
        cursor = connection.cursor()
        query = """
            SELECT id, title, description, difficulty_level, time_limit, level, created_at
            FROM quizzes
            WHERE id = %s
        """
        cursor.execute(query, (quiz_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "difficulty_level": result[3],
                "time_limit": result[4],
                "level": result[5],
                "created_at": result[6],
            }
        return None
    
    @staticmethod
    def get_all_quizzes(connection, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all quizzes with pagination"""
        cursor = connection.cursor()
        query = """
            SELECT id, title, description, difficulty_level, time_limit, level, created_at
            FROM quizzes
            ORDER BY level ASC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, skip))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty_level": row[3],
                "time_limit": row[4],
                "level": row[5],
                "created_at": row[6],
            }
            for row in results
        ]
    
    @staticmethod
    def get_quiz_by_level(connection, level: int) -> dict:
        """Get quiz by level"""
        cursor = connection.cursor()
        query = """
            SELECT id, title, description, difficulty_level, time_limit, level, created_at
            FROM quizzes
            WHERE level = %s
        """
        cursor.execute(query, (level,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "difficulty_level": result[3],
                "time_limit": result[4],
                "level": result[5],
                "created_at": result[6],
            }
        return None
    
    @staticmethod
    def get_questions_by_quiz(connection, quiz_id: str) -> list[dict]:
        """Get all questions for a specific quiz"""
        cursor = connection.cursor()
        query = """
            SELECT id, quiz_id, question_text, question_category, explanation, created_at
            FROM quiz_questions
            WHERE quiz_id = %s
            ORDER BY created_at ASC
        """
        cursor.execute(query, (quiz_id,))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": row[0],
                "quiz_id": row[1],
                "question_text": row[2],
                "question_category": row[3],
                "explanation": row[4],
                "created_at": row[5],
            }
            for row in results
        ]
    
    @staticmethod
    def get_question_by_id(connection, question_id: str) -> dict:
        """Get question by ID"""
        cursor = connection.cursor()
        query = """
            SELECT id, quiz_id, question_text, question_category, explanation, created_at
            FROM quiz_questions
            WHERE id = %s
        """
        cursor.execute(query, (question_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "quiz_id": result[1],
                "question_text": result[2],
                "question_category": result[3],
                "explanation": result[4],
                "created_at": result[5],
            }
        return None
    
    @staticmethod
    def get_options_by_question(connection, question_id: str) -> list[dict]:
        """Get all options for a specific question"""
        cursor = connection.cursor()
        query = """
            SELECT id, question_id, content, category, is_correct, created_at
            FROM quiz_options
            WHERE question_id = %s
            ORDER BY created_at ASC
        """
        cursor.execute(query, (question_id,))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": row[0],
                "question_id": row[1],
                "content": row[2],
                "category": row[3],
                "is_correct": row[4],
                "created_at": row[5],
            }
            for row in results
        ]
    
    @staticmethod
    def get_option_by_id(connection, option_id: str) -> dict:
        """Get option by ID"""
        cursor = connection.cursor()
        query = """
            SELECT id, question_id, content, category, is_correct, created_at
            FROM quiz_options
            WHERE id = %s
        """
        cursor.execute(query, (option_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "question_id": result[1],
                "content": result[2],
                "category": result[3],
                "is_correct": result[4],
                "created_at": result[5],
            }
        return None
    
    @staticmethod
    def create_attempt(connection, attempt_id: str, quiz_id: str, user_id: str, total_questions: int) -> dict:
        """Create a new quiz attempt"""
        cursor = connection.cursor()
        query = """
            INSERT INTO attempts_quiz (id, quiz_id, user_id, score, total_questions, submitted_at, is_completed)
            VALUES (%s, %s, %s, 0, %s, NOW(), false)
            RETURNING id, quiz_id, user_id, score, total_questions, is_completed
        """
        cursor.execute(query, (attempt_id, quiz_id, user_id, total_questions))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "quiz_id": result[1],
                "user_id": result[2],
                "score": result[3],
                "total_questions": result[4],
                "is_completed": result[5],
            }
        return None
    
    @staticmethod
    def get_attempt_by_id(connection, attempt_id: str) -> dict:
        """Get attempt by ID"""
        cursor = connection.cursor()
        query = """
            SELECT id, quiz_id, user_id, score, total_questions, submitted_at, is_completed
            FROM attempts_quiz
            WHERE id = %s
        """
        cursor.execute(query, (attempt_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "quiz_id": result[1],
                "user_id": result[2],
                "score": result[3],
                "total_questions": result[4],
                "submitted_at": result[5],
                "is_completed": result[6],
            }
        return None
    
    @staticmethod
    def create_attempt_answer(connection, answer_id: str, attempt_id: str, question_id: str, selected_option_id: str) -> dict:
        """Create an attempt answer"""
        cursor = connection.cursor()
        query = """
            INSERT INTO attempts_quiz_answer (id, attempt_id, question_id, selected_option_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id, attempt_id, question_id, selected_option_id
        """
        cursor.execute(query, (answer_id, attempt_id, question_id, selected_option_id))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "attempt_id": result[1],
                "question_id": result[2],
                "selected_option_id": result[3],
            }
        return None
    
    @staticmethod
    def get_user_attempts(connection, quiz_id: str, user_id: str) -> list[dict]:
        """Get all attempts for a user on a specific quiz"""
        cursor = connection.cursor()
        query = """
            SELECT id, quiz_id, user_id, score, total_questions, submitted_at, is_completed
            FROM attempts_quiz
            WHERE quiz_id = %s AND user_id = %s
            ORDER BY submitted_at DESC
        """
        cursor.execute(query, (quiz_id, user_id))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": row[0],
                "quiz_id": row[1],
                "user_id": row[2],
                "score": row[3],
                "total_questions": row[4],
                "submitted_at": row[5],
                "is_completed": row[6],
            }
            for row in results
        ]
    
    @staticmethod
    def get_attempt_answers(connection, attempt_id: str) -> list[dict]:
        """Get all answers for a specific attempt"""
        cursor = connection.cursor()
        query = """
            SELECT id, attempt_id, question_id, selected_option_id, created_at
            FROM attempts_quiz_answer
            WHERE attempt_id = %s
            ORDER BY created_at ASC
        """
        cursor.execute(query, (attempt_id,))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": row[0],
                "attempt_id": row[1],
                "question_id": row[2],
                "selected_option_id": row[3],
                "created_at": row[4],
            }
            for row in results
        ]
    
    @staticmethod
    def update_attempt_score(connection, attempt_id: str, score: int) -> dict:
        """Update attempt score and completion status"""
        cursor = connection.cursor()
        query = """
            UPDATE attempts_quiz
            SET score = %s, is_completed = true, submitted_at = NOW()
            WHERE id = %s
            RETURNING id, quiz_id, user_id, score, total_questions, submitted_at, is_completed
        """
        cursor.execute(query, (score, attempt_id))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "quiz_id": result[1],
                "user_id": result[2],
                "score": result[3],
                "total_questions": result[4],
                "submitted_at": result[5],
                "is_completed": result[6],
            }
        return None
    
    @staticmethod
    def get_ongoing_attempt(connection, quiz_id: str, user_id: str) -> dict:
        """Get ongoing (not completed) attempt for user on a quiz"""
        cursor = connection.cursor()
        query = """
            SELECT id, quiz_id, user_id, score, total_questions, submitted_at, is_completed
            FROM attempts_quiz
            WHERE quiz_id = %s AND user_id = %s AND is_completed = false
            ORDER BY submitted_at DESC
            LIMIT 1
        """
        cursor.execute(query, (quiz_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                "id": result[0],
                "quiz_id": result[1],
                "user_id": result[2],
                "score": result[3],
                "total_questions": result[4],
                "submitted_at": result[5],
                "is_completed": result[6],
            }
        return None
    
    @staticmethod
    def get_attempt_progress(connection, attempt_id: str) -> dict:
        """Get attempt progress - count of answered questions"""
        cursor = connection.cursor()
        
        # Get attempt details
        query = """
            SELECT id, quiz_id, user_id, score, total_questions, submitted_at, is_completed
            FROM attempts_quiz
            WHERE id = %s
        """
        cursor.execute(query, (attempt_id,))
        attempt = cursor.fetchone()
        
        if not attempt:
            cursor.close()
            return None
        
        # Count answered questions
        count_query = """
            SELECT COUNT(*) FROM attempts_quiz_answer
            WHERE attempt_id = %s
        """
        cursor.execute(count_query, (attempt_id,))
        answered_count = cursor.fetchone()[0]
        cursor.close()
        
        return {
            "id": attempt[0],
            "quiz_id": attempt[1],
            "user_id": attempt[2],
            "score": attempt[3],
            "total_questions": attempt[4],
            "answered_questions": answered_count,
            "remaining_questions": attempt[4] - answered_count,
            "submitted_at": attempt[5],
            "is_completed": attempt[6],
        }
    
    @staticmethod
    def get_answered_questions_details(connection, attempt_id: str) -> list[dict]:
        """Get detailed information about answered questions"""
        cursor = connection.cursor()
        query = """
            SELECT 
                aqa.id,
                aqa.attempt_id,
                aqa.question_id,
                aqa.selected_option_id,
                qq.question_text,
                qq.question_category,
                qo.content as selected_option_content,
                qo.is_correct,
                aqa.created_at
            FROM attempts_quiz_answer aqa
            JOIN quiz_questions qq ON aqa.question_id = qq.id
            JOIN quiz_options qo ON aqa.selected_option_id = qo.id
            WHERE aqa.attempt_id = %s
            ORDER BY aqa.created_at ASC
        """
        cursor.execute(query, (attempt_id,))
        results = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "answer_id": row[0],
                "attempt_id": row[1],
                "question_id": row[2],
                "selected_option_id": row[3],
                "question_text": row[4],
                "question_category": row[5],
                "selected_option_content": row[6],
                "is_correct": row[7],
                "answered_at": row[8],
            }
            for row in results
        ]
