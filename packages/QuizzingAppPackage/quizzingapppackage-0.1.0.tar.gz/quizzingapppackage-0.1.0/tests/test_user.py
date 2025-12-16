# test_user.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# test case
import unittest
from src.QuizzingApp.userprofile.user import User, RegularUser, PremiumUser

class TestUserClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_user_id = "u123"

    @classmethod
    def tearDownClass(cls):
        cls.base_user_id = None

    def setUp(self):
        self.user = User(
            user_id=self.base_user_id,
            name="Alice",
            age=20,
            email="alice@example.com",
        )

    def tearDown(self):
        self.user = None

    def test_get_user_info_and_to_dict_initial_state(self):
        info = self.user.getUserInfo()
        self.assertEqual(info["user_id"], "u123")
        self.assertEqual(info["name"], "Alice")
        self.assertEqual(info["age"], 20)
        self.assertEqual(info["email"], "alice@example.com")
        self.assertEqual(info["grades"], [])
        self.assertEqual(info["profile_level"], "regular")
        info_dict = self.user.toDict()
        self.assertEqual(info_dict, info)

    def test_set_user_info_partial_update(self):
        self.user.setUserInfo(name="Bob", email="bob@example.com")
        info = self.user.getUserInfo()
        self.assertEqual(info["name"], "Bob")
        self.assertEqual(info["email"], "bob@example.com")
        self.assertEqual(info["age"], 20)         
        self.assertEqual(info["user_id"], "u123")  
        self.assertEqual(info["grades"], [])
        self.assertEqual(info["profile_level"], "regular")

    def test_add_score_and_get_avg_for_empty_and_non_empty(self):
        self.assertEqual(self.user.getAvg(), 0.0)
        self.user.addScore(80)
        self.user.addScore(90)
        self.user.addScore(100)
        self.assertEqual(len(self.user.grades), 3)
        self.assertListEqual(self.user.grades, [80, 90, 100])
        self.assertAlmostEqual(self.user.getAvg(), 90.0)
        info = self.user.getUserInfo()
        info["grades"].append(0)
        self.assertEqual(len(self.user.grades), 3)
        self.assertListEqual(self.user.grades, [80, 90, 100])


    def test_regular_and_premium_user_profile_levels(self):
        regular = RegularUser("r1", "Reg", 18, "reg@example.com")
        premium = PremiumUser("p1", "Pre", 25, "pre@example.com", grades=[100])
        self.assertIsInstance(regular, User)
        self.assertIsInstance(premium, User)
        self.assertEqual(regular.profile_level, "regular")
        self.assertEqual(premium.profile_level, "premium")
        self.assertEqual(premium.grades, [100])
        self.assertEqual(regular.getAvg(), 0.0)
        self.assertAlmostEqual(premium.getAvg(), 100.0)




    def test_init_with_grades_and_custom_profile_level(self):
        grades = [50, 60, 70]
        u = User(
            user_id="u9",
            name="Tom",
            age=30,
            email="tom@example.com",
            grades=grades,
            profile_level="vip",
        )

        self.assertEqual(u.user_id, "u9")
        self.assertEqual(u.name, "Tom")
        self.assertEqual(u.age, 30)
        self.assertEqual(u.email, "tom@example.com")
        self.assertListEqual(u.grades, [50, 60, 70])
        self.assertEqual(u.profile_level, "vip")
        self.assertAlmostEqual(u.getAvg(), (50 + 60 + 70) / 3)

    def test_set_user_info_update_age_and_no_change(self):
        self.user.setUserInfo(age=25)
        info = self.user.getUserInfo()
        self.assertEqual(info["age"], 25)
        self.assertEqual(info["name"], "Alice")
        self.assertEqual(info["email"], "alice@example.com")
        self.assertEqual(info["user_id"], "u123")
        self.assertEqual(info["grades"], [])
        self.assertEqual(info["profile_level"], "regular")
        self.user.setUserInfo()
        info2 = self.user.getUserInfo()
        self.assertEqual(info2["age"], 25)
        self.assertEqual(info2["name"], "Alice")
        self.assertEqual(info2["email"], "alice@example.com")
        self.assertEqual(info2["user_id"], "u123")
        self.assertEqual(info2["grades"], [])
        self.assertEqual(info2["profile_level"], "regular")

if __name__ == "__main__":
    unittest.main()