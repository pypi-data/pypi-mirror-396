import sys
import os
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_PATH)
from src.QuizzingApp.quizsession.session import QuizSession, pickQuestions, loadAllQuestions, loadUsers, selectUser
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta

class TestQuizSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_questions = [
            {"qid": "q1", "qtext": "this is q1", "qtitle": "mcq", "qtype": "MC", "qoptions": ["2"], "qanswer": "2"}, 
            {"qid": "q2", "qtext": "this is q2?", "qtitle": "tfq", "qtype": "TF", "qanswer": "T"}, 
            {"qid": "q3", "qtext": "this is q3", "qtitle": "saq", "qtype": "SA", "qanswer": "answer"}
        ]
        print("Set up Class")

    @classmethod
    def tearDownClass(cls):
        cls.mock_questions = None
        print("Tear down Class")

    def setUp(self):
        self.session = QuizSession(
            user_id="u1",
            user_name="name1",
            num_questions=[1, 1, 1],
            question_ids=["q1", "q2", "q3"]
        )
        self.all_questions = TestQuizSession.mock_questions
        print("Set up")

    def tearDown(self):
        self.session = None
        self.all_questions = None
        print("Tear down")
        
    def test_Initialization(self):
        self.assertEqual(self.session.user_id, "u1")
        self.assertEqual(self.session.user_name, "name1")
        self.assertEqual(self.session.num_questions, [1, 1, 1])
        self.assertEqual(self.session.sum_questions, 3)
        self.assertEqual(self.session.question_ids, ["q1", "q2", "q3"])
        self.assertEqual(self.session.current_index, 0)
        self.assertFalse(self.session.isFinished)

    def test_StartAndEnd(self):
        self.session.startSession()
        self.assertIsNotNone(self.session.start_time)
        self.assertIsInstance(self.session.start_time, datetime)
        self.assertEqual(self.session.current_index, 0)
        self.assertFalse(self.session.isFinished)

        self.session.endSession()
        self.assertTrue(self.session.isFinished)
        self.assertIsNotNone(self.session.end_time)
        self.assertIsInstance(self.session.end_time, datetime)

    def test_CalculateTime(self):
        self.session.startSession()
        self.session.end_time = self.session.start_time + timedelta(seconds=10)

        duration = self.session.culculateTime()
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 0)
        self.assertAlmostEqual(duration, 10, delta=0.01)
        self.assertNotEqual(duration, 5)

    def test_ToDict(self):
        self.session.startSession()
        self.session.endSession()

        d = self.session.toDict()
        self.assertIn("session_id", d)
        self.assertEqual(d["user_id"], "u1")
        self.assertEqual(d["user_name"], "name1")
        self.assertEqual(d["sum_questions"], 3)
        self.assertIsInstance(d["answer"], list)

    def test_SubmitAnswer(self):
        self.session.questions = [
            {"id": "q1"}, {"id": "q2"}, {"id": "q3"}
        ]

        self.session.submitAnswer("hello")
        self.assertEqual(len(self.session.answer), 1)
        self.assertEqual(self.session.current_index, 1)
        self.assertEqual(self.session.answer[0][1], "hello")
        self.assertIsInstance(self.session.answer, list)
    
    def test_GetAndNextQuestion(self):
        self.session.questions = ["Q1", "Q2", "Q3"]

        q1 = self.session.getCurrentQuestion()
        self.assertEqual(q1, "Q1")

        next_q = self.session.nextQuestion()
        self.assertEqual(next_q, "Q1")

        self.session.current_index = 2
        q3 = self.session.getCurrentQuestion()
        self.assertEqual(q3, "Q3")
    
    def test_PickQuestions(self):
        selected = pickQuestions(self.all_questions, [1, 1, 1])
        self.assertEqual(len(selected), 3)
        self.assertTrue(any(q["qtype"] == "MC" for q in selected))
        self.assertTrue(any(q["qtype"] == "TF" for q in selected))
        self.assertTrue(any(q["qtype"] == "SA" for q in selected))

    def test_LoadHelpers(self):
        with patch("builtins.open"), patch("json.load", return_value={"users": [{"name": "Alice"}]}):
            users = loadUsers("fake.json")
            self.assertIsInstance(users, list)
            self.assertEqual(users[0]["name"], "Alice")

        with patch("builtins.open"), patch("json.load", return_value={"questions": [{"qid": "q1"}]}):
            qs = loadAllQuestions("fake.json")
            self.assertEqual(qs[0]["qid"], "q1")
            
    @patch("builtins.input", side_effect=["2", "T", "answer"])      
    def test_AskQuestions(self, mock_input):
        self.session.askQuestions(self.all_questions)
        self.assertEqual(len(self.session.answer), 3)
        self.assertEqual(self.session.current_index, 3)
        self.assertEqual(self.session.answer[0][0], "q1")
        self.assertEqual(self.session.answer[1][1], "T")

    @patch("builtins.input", return_value="name1")
    def test_SelectUser(self, mock_input):
        users = [{"name": "name1", "user_id": "u1", "profile_level": "premium"}]
        uid, name, lvl = selectUser(users)
        self.assertEqual(uid, "u1")
        self.assertEqual(name, "name1")
        self.assertEqual(lvl, "premium")
        self.assertIsNotNone(uid)

    def test_SubmitAnswerOOR(self):
        self.session.questions = [{"id": "q1"}]
        self.session.current_index = 3
        initial_len = len(self.session.answer)
        self.session.submitAnswer("a")
        self.assertEqual(len(self.session.answer), 0)
        self.assertEqual(initial_len, 0)
        self.assertEqual(self.session.current_index, 3)
        self.assertGreater(self.session.current_index, self.session.sum_questions - 1)

if __name__ == "__main__":
    unittest.main()
