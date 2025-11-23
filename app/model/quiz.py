from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Quiz(Base):
    __tablename__ = 'quizzes'
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), default='medium', nullable=False)
    time_limit = Column(Integer, nullable=True)
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    
    id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_category = Column(String(50), nullable=False)
    explanation = Column(Text, default='', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class QuizOption(Base):
    __tablename__ = 'quiz_options'
    
    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default='option', nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AttemptQuiz(Base):
    __tablename__ = 'attempts_quiz'
    
    id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)


class AttemptQuizAnswer(Base):
    __tablename__ = 'attempts_quiz_answer'
    
    id = Column(String(36), primary_key=True)
    attempt_id = Column(String(36), ForeignKey('attempts_quiz.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(String(36), ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False)
    selected_option_id = Column(String(36), ForeignKey('quiz_options.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
