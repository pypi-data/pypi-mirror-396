import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import os
import json
from src.QuizzingApp.questionbase.question_manager import QuestionManager
from src.QuizzingApp.questionbase.question import Question, MCQuestion, TFQuestion, SAQuestion


class TestQuestionManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_file = "test_questions.json"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_file):
            os.remove(cls.temp_file)

    def setUp(self):
        self.manager = QuestionManager()

        self.q1 = Question("Q1", "SA", "Title1", "Text1", "Ans1")
        self.q2 = TFQuestion("Q2", "Title2", "Text2", "True")
        self.q3 = MCQuestion("Q3", "Math", "2+2=?", ["1", "2", "4"], "4")

        self.manager.addQuestion(self.q1)
        self.manager.addQuestion(self.q2)
        self.manager.addQuestion(self.q3)

    def tearDown(self):
        self.manager = None

    def test_add_delete_filter_get(self):
        self.assertEqual(len(self.manager.questions), 3)
        self.assertIsInstance(self.manager.questions[0], Question)

        tf_list = self.manager.filterQuestions("TF")
        self.assertEqual(len(tf_list), 1)
        self.assertIsInstance(tf_list[0], TFQuestion)

        self.manager.deleteQuestion("Q2")
        self.assertEqual(len(self.manager.questions), 2)
        ids = [q.qid for q in self.manager.questions]
        self.assertNotIn("Q2", ids)

        all_q = self.manager.getAllQuestions()
        self.assertEqual(len(all_q), 2)
        self.assertIsInstance(all_q[0], Question)

    def test_toJson_and_getJson(self):
        self.manager.toJson(self.temp_file)
        self.assertTrue(os.path.exists(self.temp_file))

        with open(self.temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 3)
        self.assertIn("qid", data[0])
        self.assertIn("qtitle", data[1])

        new_manager = QuestionManager()
        new_manager.getJson(self.temp_file)

        self.assertEqual(len(new_manager.questions), 3)

        q = new_manager.questions[0]
        self.assertIsInstance(q, Question)
        self.assertEqual(q.qid, "Q1")

        mc = new_manager.questions[2]
        self.assertIsInstance(mc, MCQuestion)
        self.assertEqual(mc.qoptions, ["1", "2", "4"])
        self.assertEqual(mc.qanswer, "4")

    def test_filter_multiple_types(self):
        sa_questions = self.manager.filterQuestions("SA")
        self.assertEqual(len(sa_questions), 1)
        self.assertEqual(sa_questions[0].qid, "Q1")
        
        mc_questions = self.manager.filterQuestions("MC")
        self.assertEqual(len(mc_questions), 1)
        self.assertEqual(mc_questions[0].qid, "Q3")
        empty_list = self.manager.filterQuestions("NONEXISTENT")
        self.assertEqual(len(empty_list), 0)

    def test_delete_nonexistent_question(self):
        initial_count = len(self.manager.questions)
        self.manager.deleteQuestion("NONEXISTENT_ID")
        self.assertEqual(len(self.manager.questions), initial_count)

    def test_empty_question_manager(self):
        empty_manager = QuestionManager()
        all_questions = empty_manager.getAllQuestions()
        self.assertEqual(len(all_questions), 0)
        filtered = empty_manager.filterQuestions("MC")
        self.assertEqual(len(filtered), 0)
        
        empty_manager.deleteQuestion("Q1")
        self.assertEqual(len(empty_manager.questions), 0)


if __name__ == "__main__":
    unittest.main()

