import uuid
from datetime import datetime
import json
import random
import os
from ..errors import DataFileNotFoundError, UserNotFoundError, EmptyQuestionDataError
def loadAllQuestions(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise DataFileNotFoundError("question file not found")
    if isinstance(data, dict) and "questions" in data:
        return data["questions"]
    return data

def loadUsers(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise DataFileNotFoundError("user file not found")
    if isinstance(data, dict) and "users" in data:
        return data["users"]
    return data

def selectUser(users):
    if not users or len(users) == 0:
        raise UserNotFoundError("Currently no users")
    print("\n=== User Login ===")
    print("Available users:")
    for user in users:
        print(f"  - {user['name']}")
    
    user_name_input = input("\nEnter your name: ").strip()

    for user in users:
        if user['name'].lower() == user_name_input.lower():
            print(f"Welcome, {user['name']}!")
            return user['user_id'], user['name'], user['profile_level']
    
    print(f"User '{user_name_input}' not found.")
    return None, None, None

def showQuestions(questions):
    if not questions:
        raise EmptyQuestionDataError("No questions to display")
    for q in questions:
        qid = q.get('qid', 'N/A')
        qtitle = q.get('qtitle', q.get('topic', 'N/A'))
        print(f"[{qid}] {qtitle}")
        
def pickQuestions(all_questions, num_questions):
    if not all_questions:
        raise EmptyQuestionDataError("Question bank is empty")
    
    mc_questions = [q for q in all_questions if q.get('qtype', q.get('type', '')) in ['MC', 'MCQ']]
    tf_questions = [q for q in all_questions if q.get('qtype', q.get('type', '')) == 'TF']
    sr_questions = [q for q in all_questions if q.get('qtype', q.get('type', '')) in ['SR', 'SA']]
    
    selected = []
    
    if num_questions[0] > 0:
        selected.extend(random.sample(mc_questions, min(num_questions[0], len(mc_questions))))
    
    if num_questions[1] > 0:
        selected.extend(random.sample(tf_questions, min(num_questions[1], len(tf_questions))))
    
    if num_questions[2] > 0:
        selected.extend(random.sample(sr_questions, min(num_questions[2], len(sr_questions))))
    random.shuffle(selected)
    
    return selected

def createSession(user_id, user_name, num_questions, question_ids):
    if not user_id or not user_name:
        raise ValueError("User ID and name cannot be empty")
    if not question_ids or len(question_ids) == 0:
        raise EmptyQuestionDataError("Cannot create session without questions")
    return QuizSession(
        user_id=user_id,
        user_name=user_name,
        num_questions=num_questions,
        question_ids=question_ids
    )

class QuizSession:
    def __init__(self, user_id, user_name, num_questions, question_ids):
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.user_name = user_name
        
        self.num_questions = num_questions
        self.sum_questions = sum(num_questions)
        self.question_ids = question_ids
        
        self.start_time = None
        self.end_time = None
        self.current_index = 0
        self.isFinished = False
        
        self.answer = []
        
    def startSession(self):
        self.start_time = datetime.now()
        self.current_index = 0
        print(f"Quiz started for {self.user_name} at {self.start_time}. Good luck!")
    
    def askQuestions(self, all_questions):
        if not all_questions:
            raise EmptyQuestionDataError("No questions available to ask")
        
        for i, qid in enumerate(self.question_ids):
            question = next((q for q in all_questions if q['qid'] == qid), None)
            if not question:
                continue
                
            print(f"\n{'='*50}")
            print(f"Question {i+1} of {self.sum_questions}")
            print(f"Title: {question.get('qtitle', question.get('topic', 'N/A'))}")
            print(f"\n{question.get('qtext', question.get('text', ''))}")

            if question.get('qtype', question.get('type', '')) in ['MC', 'MCQ']:
                print("\nOptions:")
                for option in question.get('qoptions', question.get('options', [])):
                    print(f"  {option}")

            user_answer = input("\nYour answer: ").strip()
            self.answer.append((qid, user_answer))
            self.current_index += 1
            
        print(f"\n{'='*50}")
        print("All questions completed!")
        
    def getCurrentQuestion(self):
        if self.current_index < self.sum_questions:
            return self.questions[self.current_index]
        else:
            return None
    
    def nextQuestion(self):
        if self.current_index < self.sum_questions:
            return self.questions[self.current_index]
        return None
    
    def submitAnswer(self, answer):
        if self.current_index < self.sum_questions:
            q = self.questions[self.current_index]
            self.answer.append((q["id"], answer))
            self.current_index += 1
        else:
            print("No more questions left to answer.")
        
    def endSession(self):
        self.end_time = datetime.now()
        self.isFinished = True
        print(f"This is the end of the quiz. Well done {self.user_name}!")
        
    def culculateTime(self):
        if self.start_time and self.end_time:
            total_time = (self.end_time - self.start_time).total_seconds()
            return total_time
        return None 
    
    def toDict(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "num_questions": self.num_questions,
            "sum_questions": self.sum_questions,
            "question_ids": self.question_ids,
            "total_time": self.culculateTime(),
            "answer": self.answer
        }   