import sys
import os
import uuid
from .quizsession.session import loadUsers, loadAllQuestions, selectUser, pickQuestions, createSession, showQuestions
from .quizsession.result import QuizResult
from .userprofile.manage_user import registerUser, getAllUsers, deleteAllUsers, getJson as getUserJson, toJson as saveUserJson
from .questionbase.question_manager import QuestionManager
from .questionbase.question import Question, MCQuestion, TFQuestion, SAQuestion

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    while True:
        print("\n====== Welcome to our Quizzing App ======")
        print("\nAre you a User or Admin?")
        user_input = input("[1] User\n[2] Admin\n[q] Quit\nEnter: ").strip().lower()
        
        if user_input in ['q', 'quit']:
            print("Thank you! Bye!")
            break
        
        try:
            role_choice = int(user_input)
        except ValueError:
            print("Invalid input. Try Again.")
            continue
        
        if role_choice == 1:
            print("\nWhich task would you like to perform?")
            user_task = input("[1] Register as an User\n[2] Start a Quiz\n[Q] Back to Main Menu\nEnter: ").strip().lower()
            
            if user_task in ['q', 'quit']:
                continue
            
            try:
                task_choice = int(user_task)
            except ValueError:
                print("Invalid input. Returning to main menu.")
                continue
            
            users_path = os.path.join(script_dir, "data/users.json")
            
            if task_choice == 1:
                user_id, user_name = registerUser(users_path)
            elif task_choice == 2:
                users = loadUsers(users_path)
                user_id, user_name, profile_level = selectUser(users)
                
                premium_for_use = profile_level
                
                if user_id is None:
                    print("User not found. Maybe register first?")
                    continue

                questions_path = os.path.join(script_dir, "data/questions.json")
                all_questions = loadAllQuestions(questions_path)
                
                print("\n=== Quiz Setup ===")
                print("\nHow many questions would you like?")
                try:
                    num_mc = int(input("Number of Multiple Choice questions: "))
                    num_tf = int(input("Number of True or False questions: "))
                    num_sr = int(input("Number of Short Answer questions: "))
                    num_questions = [num_mc, num_tf, num_sr]
                except ValueError:
                    print("Invalid input. Using default: 1 of each type.")
                    num_questions = [1, 1, 1]
                
                selected_questions = pickQuestions(all_questions, num_questions)
                
                print(f"\nSelected {len(selected_questions)} questions for quiz:")
                showQuestions(selected_questions)

                session = createSession(
                    user_id=user_id,
                    user_name=user_name,
                    num_questions=num_questions,
                    question_ids=[q['qid'] for q in selected_questions]
                )
                
                print(f"\n=== Quiz Session Created ===")
                print(f"Session ID: {session.session_id}")
                print(f"User: {session.user_name}")
                print(f"Total Questions: {session.sum_questions}")

                session.startSession()
                session.askQuestions(all_questions)
                session.endSession()
                
                result = QuizResult(session.toDict(), all_questions)
                print(f"Correct: {result.countCorrect()}/{result.sum_questions}")
                print(f"Wrong: {result.countWrong()}/{result.sum_questions}")
                print(f"Score: {result.getScore()}/{result.sum_questions}")
                print(f"Total Time: {result.total_time:.2f} seconds")
                sessions_path = os.path.join(script_dir, "data/sessions.json")
                result.saveResult(sessions_path)
                if premium_for_use == "premium":
                    print("Displaying charts...")
                    result.typeChart()
                    result.typeCorrectBar()
                else:
                    print("Too bad, no charts.")
            else:
                print("Invalid option.")
                
        elif role_choice == 2:
            print("\n=== Admin Panel ===")
            print("What would you like to do?")
            admin_input = input("[1] Add a Question\n[2] View All Questions\n[3] Delete All Questions\n[4] View All Users\n[5] Delete All Users\n[Q] Back to Main Menu\nEnter: ").strip().lower()
            
            if admin_input in ['q', 'quit']:
                continue
            
            try:
                admin_choice = int(admin_input)
            except ValueError:
                print("Invalid input. Returning to main menu.")
                continue
            
            questions_path = os.path.join(script_dir, "data/questions.json")
            users_path = os.path.join(script_dir, "data/users.json")

            if admin_choice == 1:
                print("\n=== Add a Question ===")
                qm = QuestionManager()
                qm.getJson(questions_path)
               
                qid = str(uuid.uuid4())[:8]
               
                qtype_input = input("Question type [1] MC [2] TF [3] SA: ").strip()
               
                if qtype_input == "1":
                    question = MCQuestion(qid, "", "", [], "")
                    question.setType("MC")
                    question.setTitle(input("Enter question title: ").strip())
                    question.setText(input("Enter question text: ").strip())
                   
                    qoptions = []
                    for i in range(4):
                        opt = input(f"Enter option {chr(65+i)}: ").strip()
                        qoptions.append(f"{chr(65+i)}: {opt}")
                    question.qoptions = qoptions
                   
                    question.setAnswer(input("Enter correct answer (A/B/C/D): ").strip().upper())
                    if question.getAnswer() not in ['A', 'B', 'C', 'D']:
                        print("Invalid. Set to A by default.")
                        question.setAnswer('A')
                elif qtype_input == "2":
                    question = TFQuestion(qid, "", "", "")
                    question.setType("TF")
                    question.setTitle(input("Enter question title: ").strip())
                    question.setText(input("Enter question text: ").strip())
                    question.setAnswer(input("Enter answer (T/F): ").strip())
                    if question.getAnswer() not in ['T', 'F']:
                        print("Invalid. Set to T by default.")
                        question.setAnswer('T')
                   
                elif qtype_input == "3":
                    question = SAQuestion(qid, "", "", "")
                    question.setType("SA")
                    question.setTitle(input("Enter question title: ").strip())
                    question.setText(input("Enter question text: ").strip())
                    question.setAnswer(input("Enter answer: ").strip())
                   
                else:
                    print("Invalid question type.")
                    continue
               
                qm.addQuestion(question)
                qm.toJson(questions_path)
                print(f"\nQuestion added!")

            elif admin_choice == 2:
                print("\n=== All Questions ===")
                qm = QuestionManager()
                qm.getJson(questions_path)
                questions = qm.getAllQuestions()
               
                if not questions:
                    print("No questions found.")
                else:
                    for q in questions:
                        print(f"\n{q.display()}")
                        print("-" * 50)
                       
            elif admin_choice == 3:
                confirm = input("\nAre you sure???").strip().lower()
                if confirm in ['yes', 'y']:
                    qm = QuestionManager()
                    qm.toJson(questions_path)
                    print("All questions deleted!")
                else:
                    print("Maybe not!")
                   
            elif admin_choice == 4:
                print("\n=== All Users ===")
                getUserJson(users_path)
                users = getAllUsers()
               
                if not users:
                    print("No user for now.")
                else:
                    for user in users:
                        info = user.getUserInfo()
                        print(f"\nUser ID: {info['user_id']}")
                        print(f"Name: {info['name']}")
                        print(f"Age: {info['age']}")
                        print(f"Email: {info['email']}")
                        print(f"Profile Level: {info['profile_level']}")
                        print(f"Grades: {info['grades']}")
                        print(f"Average: {user.getAvg():.2f}")
                        print("-" * 50)
                        
            elif admin_choice == 5:
                getUserJson(users_path)
                confirm = input("\nAre you sure???").strip().lower()
                if confirm in ['yes', 'y']:
                    deleteAllUsers()
                    saveUserJson(users_path) 
                    print("All users deleted!")
                else:
                    print("Maybe not!")
            else:
                print("Invalid option")
        else:
            print("Invalid choice. Try Again.")
    
if __name__ == "__main__":
    main()