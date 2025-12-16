import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src.QuizzingApp.questionbase.question import Question, MCQuestion, TFQuestion, SAQuestion


class TestQuestion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_q = Question("Q0", "SA", "Base Title", "Base Text", "Answer")

    @classmethod
    def tearDownClass(cls):
        cls.base_q = None

    def setUp(self):
        self.q = Question("Q1", "TF", "Test Title", "Is sky blue?", "True")

    def tearDown(self):
        self.q = None

    def test_setters_and_getters(self):
        self.q.setText("Updated text")
        self.q.setAnswer("False")
        self.q.setTitle("Updated Title")
        self.q.setType("MC")

        self.assertEqual(self.q.getText(), "Updated text")
        self.assertEqual(self.q.getAnswer(), "False")
        self.assertEqual(self.q.getTitle(), "Updated Title")
        self.assertEqual(self.q.getType(), "MC")
        self.assertEqual(self.base_q.getTitle(), "Base Title")

    def test_display_checkanswer_toDict(self):
        disp = self.q.display()
        self.assertIn("QID: Q1", disp)
        self.assertIn("Test Title", disp)
        self.assertIn("Is sky blue?", disp)
        self.assertIn("TF", disp)

        self.assertTrue(self.q.checkAnswer("true"))
        self.assertTrue(self.q.checkAnswer(" True "))
        self.assertFalse(self.q.checkAnswer("false"))

        d = self.q.toDict()
        self.assertEqual(d["qid"], "Q1")
        self.assertEqual(d["qtype"], "TF")
        self.assertEqual(d["qtitle"], "Test Title")
        self.assertEqual(d["qanswer"], "True")

    def test_mc_tf_sa_questions(self):
        mc = MCQuestion("Q2", "Math", "2+2=?", ["1", "2", "4"], "4")
        tf = TFQuestion("Q3", "Logic", "Earth is round", "True")
        sa = SAQuestion("Q4", "Short", "Name a color", "red")

        self.assertEqual(mc.qtype, "MC")
        self.assertEqual(len(mc.qoptions), 3)
        self.assertIn("Options:", mc.display())
        self.assertEqual(mc.toDict()["qoptions"], ["1", "2", "4"])

        self.assertEqual(tf.qtype, "TF")
        self.assertTrue(tf.checkAnswer("true"))

        self.assertEqual(sa.qtype, "SA")
        self.assertTrue(sa.checkAnswer("RED"))


if __name__ == "__main__":
    unittest.main()
