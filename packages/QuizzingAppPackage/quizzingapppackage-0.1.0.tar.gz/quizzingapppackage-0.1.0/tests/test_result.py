import unittest
from unittest.mock import mock_open, patch
import json
import os
import sys
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_PATH)
from src.QuizzingApp.quizsession.result import QuizResult

class TestQuizResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_questions = [
            {"qid": "q1", "qanswer": "2", "qtype": "MC"},
            {"qid": "q2", "qanswer": "T", "qtype": "TF"},
            {"qid": "q3", "qanswer": "hello", "qtype": "SA"},
        ]
        print("Set up Class")

    @classmethod
    def tearDownClass(cls):
        cls.mock_questions = None
        print("Tear down Class")

    def setUp(self):
        self.session_dict = {
            "session_id": "s1",
            "user_id": "u1",
            "user_name": "Tester",
            "num_questions": [1, 1, 1],
            "sum_questions": 3,
            "question_ids": ["q1", "q2", "q3"],
            "answer": [
                ("q1", "2"),
                ("q2", "T"),
                ("q3", "wrong")
            ],
            "total_time": 20
        }
        self.result = QuizResult(self.session_dict, TestQuizResult.mock_questions)
        print("Set up")

    def tearDown(self):
        self.result = None
        print("Tear down")

    def test_Initialization(self):
        self.assertEqual(self.result.user_id, "u1")
        self.assertEqual(self.result.user_name, "Tester")
        self.assertEqual(self.result.sum_questions, 3)
        self.assertEqual(len(self.result.questions), 3)
        self.assertEqual(len(self.result.results), 3)
        
    def test_CompareAnswer(self):
        question = {"qanswer": "Yes"}
        self.assertTrue(self.result.compareAnswer(question, "yes"))
        self.assertTrue(self.result.compareAnswer(question, "  YES  "))
        self.assertFalse(self.result.compareAnswer(question, "no"))

    def test_CountCorrect(self):
        self.assertEqual(self.result.countCorrect(), 2)
        self.assertEqual(self.result.countWrong(), 1)
        self.assertEqual(self.result.getScore(), 2)

    def test_Percentage(self):
        self.assertEqual(self.result.percentage(), round((2 / 3) * 100, 2))

    def test_ToDict(self):
        d = self.result.toDict()
        self.assertEqual(d["score"], 2)
        self.assertEqual(d["correct"], 2)
        self.assertEqual(d["wrong"], 1)
        self.assertEqual(d["total_questions"], 3)
        self.assertIn("results", d)
        self.assertIsInstance(d["results"], list)

    def test_ToJSON(self):
        json_str = self.result.toJSON()
        data = json.loads(json_str)
        self.assertEqual(data["score"], 2)
        self.assertIn("percentage", data)
        self.assertIn("user_id", data)

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.pie")
    def test_TypeChart(self, pie, show):
        self.result.typeChart()
        pie.assert_called_once()
        show.assert_called_once()
    
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_TypeCorrectBar(self, subplots, show):
        bar = unittest.mock.Mock()
        bar.get_height.return_value = 2
        bar.get_x.return_value = 0
        bar.get_width.return_value = 0.35
        ax = unittest.mock.Mock()
        ax.bar.return_value = [bar, bar]
        subplots.return_value = (None, ax)

        self.result.typeCorrectBar()
        self.assertEqual(ax.bar.call_count, 2)
        show.assert_called_once()


    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    @patch("os.path.getsize", return_value=10)
    @patch("os.path.exists", return_value=True)
    def test_SaveResult(self, mock_exists, mock_getsize, mock_file, mock_dump):
        filepath = "fake_path.json"
        
        self.result.saveResult(filepath)
        mock_file.assert_called_with(filepath, "w")
        self.assertTrue(mock_dump.called)

if __name__ == "__main__":
    unittest.main()
