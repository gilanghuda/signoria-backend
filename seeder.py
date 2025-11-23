import uuid
import os
import random
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model.quiz import Quiz, QuizQuestion, QuizOption, Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def generate_uuid():
    return str(uuid.uuid4())


def seed_quizzes():
    """Seed 30 quiz levels with 10 questions each"""
    session = SessionLocal()
    
    try:
        creator_id = generate_uuid()
        
        # Available characters
        alphabets = [c for c in 'ABCDEFGHIKLMNOPQRSTUVWXY']  # 24 letters
        numbers = [str(i) for i in range(10)]  # 0-9
        all_characters = alphabets + numbers  # 34 total
        
        # Define focus pairs for levels 1-29
        # Each level focuses on 2 characters
        level_pairs = [
            ('A', 'B'),  # Level 1
            ('C', 'D'),  # Level 2
            ('E', 'F'),  # Level 3
            ('G', 'H'),  # Level 4
            ('I', 'K'),  # Level 5
            ('L', 'M'),  # Level 6
            ('N', 'O'),  # Level 7
            ('P', 'Q'),  # Level 8
            ('R', 'S'),  # Level 9
            ('T', 'U'),  # Level 10
            ('V', 'W'),  # Level 11
            ('X', 'Y'),  # Level 12
            ('0', '1'),  # Level 13
            ('2', '3'),  # Level 14
            ('4', '5'),  # Level 15
            ('6', '7'),  # Level 16
            ('8', '9'),  # Level 17
            ('A', '0'),  # Level 18
            ('M', '5'),  # Level 19
            ('Y', '9'),  # Level 20
            ('B', '2'),  # Level 21
            ('F', '7'),  # Level 22
            ('K', '4'),  # Level 23
            ('S', '6'),  # Level 24
            ('H', '1'),  # Level 25
            ('Q', '3'),  # Level 26
            ('W', '8'),  # Level 27
            ('D', '0'),  # Level 28
            ('U', '9'),  # Level 29
        ]
        
        # Create 30 quizzes (levels 1-30)
        for level in range(1, 31):
            quiz_id = generate_uuid()
            
            if level < 30:
                pair = level_pairs[level - 1]
                quiz_title = f"Quiz Level {level} - Huruf/Angka: {pair[0]} dan {pair[1]}"
                quiz_description = f"Tebak huruf dan angka SIBI fokus pada: {pair[0]} dan {pair[1]}"
            else:
                quiz_title = f"Quiz Level 30 - Random Challenge"
                quiz_description = "Tebak huruf dan angka SIBI secara acak dari semua karakter"
            
            quiz = Quiz(
                id=quiz_id,
                title=quiz_title,
                description=quiz_description,
                difficulty_level="hard" if level > 20 else "medium" if level > 10 else "easy",
                time_limit=600,
                level=level,
                created_at=datetime.utcnow()
            )
            session.add(quiz)
            session.flush()
            
            # Create 10 questions per level with 3 different types
            # Type 1 (image_alphabet): 4 questions - image question with text options
            # Type 2 (image_options): 4 questions - text question with image options
            # Type 3 (camera_based): 2 questions - camera practice with no options
            
            question_types = ['image_alphabet'] * 4 + ['image_options'] * 4 + ['camera_based'] * 2
            random.shuffle(question_types)
            
            for q_idx, question_type in enumerate(question_types):
                q_id = generate_uuid()
                
                # Determine target character for this question
                if level < 30:
                    target_char = level_pairs[level - 1][q_idx % 2]
                else:
                    # Level 30: completely random
                    target_char = random.choice(all_characters)
                
                # === TYPE 1: Image question with text options ===
                if question_type == 'image_alphabet':
                    q = QuizQuestion(
                        id=q_id,
                        quiz_id=quiz_id,
                        question_text=f"https://signoria.gilanghuda.my.id/dict/dictionary/{target_char}.jpg",
                        question_category="image_alphabet",
                        explanation=f"Karakter: {target_char}",
                        created_at=datetime.utcnow()
                    )
                    session.add(q)
                    session.flush()
                    
                    # Generate 4 text options
                    wrong_choices = [c for c in all_characters if c != target_char]
                    options = [target_char] + random.sample(wrong_choices, 3)
                    random.shuffle(options)
                    
                    for opt in options:
                        session.add(QuizOption(
                            id=generate_uuid(),
                            question_id=q_id,
                            content=opt,
                            category="text",
                            is_correct=(opt == target_char)
                        ))
                
                # === TYPE 2: Text question with image options ===
                elif question_type == 'image_options':
                    q = QuizQuestion(
                        id=q_id,
                        quiz_id=quiz_id,
                        question_text=f"Yang mana dibawah ini bahasa isyarat untuk huruf/angka: {target_char}?",
                        question_category="image_options",
                        explanation=f"Jawaban yang benar adalah: {target_char}",
                        created_at=datetime.utcnow()
                    )
                    session.add(q)
                    session.flush()
                    
                    # Generate 4 image options
                    wrong_choices = [c for c in all_characters if c != target_char]
                    image_options = [target_char] + random.sample(wrong_choices, 3)
                    random.shuffle(image_options)
                    
                    for img_opt in image_options:
                        session.add(QuizOption(
                            id=generate_uuid(),
                            question_id=q_id,
                            content=f"https://signoria.gilanghuda.my.id/dict/dictionary/{img_opt}.jpg",
                            category="image",
                            is_correct=(img_opt == target_char)
                        ))
                
                # === TYPE 3: Camera-based practice ===
                elif question_type == 'camera_based':
                    q = QuizQuestion(
                        id=q_id,
                        quiz_id=quiz_id,
                        question_text=f"Praktikkan bahasa isyarat untuk huruf/angka: {target_char}",
                        question_category="camera_based",
                        explanation=f"Gunakan kamera untuk mengenali gerakan tangan Anda untuk karakter: {target_char}",
                        created_at=datetime.utcnow()
                    )
                    session.add(q)
                    session.flush()
                    
                    # Camera-based questions have no options
                    # Just add one implicit option that is the target character
                    session.add(QuizOption(
                        id=generate_uuid(),
                        question_id=q_id,
                        content=target_char,
                        category="camera",
                        is_correct=True
                    ))
        
        session.commit()
        print("✓ Quiz seeding completed successfully!")
        print(f"  - Created 30 quiz levels")
        print(f"  - Each level has 10 questions (4 image_alphabet + 4 image_options + 2 camera_based)")
        print(f"  - Levels 1-29: Focused on character pairs")
        print(f"  - Level 30: Completely random characters")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error during seeding: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_dotenv()
    Base.metadata.create_all(engine)
    seed_quizzes()
