# test_user_manager.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.QuizzingApp.userprofile import manage_user
from src.QuizzingApp.userprofile.user import RegularUser, PremiumUser


class TestUserManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp_dir = tempfile.TemporaryDirectory()
        cls.temp_json = Path(cls._tmp_dir.name) / "users_test.json"

    @classmethod
    def tearDownClass(cls):
        cls._tmp_dir.cleanup()
        cls._tmp_dir = None
        cls.temp_json = None

    def setUp(self):
        manage_user.deleteAllUsers()
        if self.temp_json.exists():
            self.temp_json.unlink()

    def tearDown(self):
        manage_user.deleteAllUsers()
        if self.temp_json.exists():
            self.temp_json.unlink()

    def test_create_user_regular_and_premium_and_invalid_type(self):
        reg = manage_user.createUser("regular", "u1", "Alice", 20, "alice@example.com", [90])
        prem = manage_user.createUser("premium", "u2", "Bob", 30, "bob@example.com", [100])

        self.assertIsInstance(reg, RegularUser)
        self.assertEqual(reg.profile_level, "regular")
        self.assertIsInstance(prem, PremiumUser)
        self.assertEqual(prem.profile_level, "premium")

        self.assertIs(manage_user.getUser("u1"), reg)
        self.assertIs(manage_user.getUser("u2"), prem)
        self.assertEqual(len(manage_user.getAllUsers()), 2)

        with self.assertRaises(ValueError):
            manage_user.createUser("vip", "u3", "Carol", 40, "carol@example.com", [70])


    def test_delete_user_and_get_user_behaviour(self):
        u1 = manage_user.createUser("regular", "u1", "Alice", 20, "alice@example.com")
        u2 = manage_user.createUser("premium", "u2", "Bob", 30, "bob@example.com")

        self.assertIsNotNone(manage_user.getUser("u1"))
        self.assertIsNotNone(manage_user.getUser("u2"))
        self.assertTrue(manage_user.deleteUser("u1"))
        self.assertIsNone(manage_user.getUser("u1"))
        self.assertFalse(manage_user.deleteUser("u1"))

        users = manage_user.getAllUsers()
        self.assertEqual(len(users), 1)
        self.assertIs(users[0], u2)

    def test_delete_all_users_clears_state(self):
        manage_user.createUser("regular", "u1", "Alice", 20, "alice@example.com")
        manage_user.createUser("premium", "u2", "Bob", 30, "bob@example.com")
        self.assertGreater(len(manage_user.getAllUsers()), 0)
        manage_user.deleteAllUsers()

        self.assertEqual(len(manage_user.getAllUsers()), 0)
        self.assertIsNone(manage_user.getUser("u1"))
        self.assertIsNone(manage_user.getUser("u999"))
        self.assertFalse(manage_user.deleteUser("u1"))

    def test_to_json_and_get_json_roundtrip(self):
        manage_user.createUser("regular", "u1", "Alice", 20, "alice@example.com")
        manage_user.createUser("premium", "u2", "Bob", 30, "bob@example.com", [100])
        manage_user.toJson(filepath=self.temp_json)
        self.assertTrue(self.temp_json.exists())
        manage_user.deleteAllUsers()
        self.assertEqual(len(manage_user.getAllUsers()), 0)
        manage_user.getJson(filepath=self.temp_json)
        users = manage_user.getAllUsers()

        self.assertEqual(len(users), 2)
        levels = sorted(u.profile_level for u in users)
        self.assertEqual(levels, ["premium", "regular"])

        premium_users = [u for u in users if u.profile_level == "premium"]
        self.assertEqual(len(premium_users), 1)
        self.assertEqual(premium_users[0].email, "bob@example.com")


    def test_register_user_premium_and_invalid_age(self):
        inputs = ["Carol", "abc", "carol@example.com", "yes"]

        with patch("builtins.input", side_effect=inputs), \
             patch("src.QuizzingApp.userprofile.manage_user.uuid.uuid4",
                   return_value="another-uuid-999999"), \
             patch("src.QuizzingApp.userprofile.manage_user.time.sleep"):
            user_id, name = manage_user.registerUser(filepath=self.temp_json)

        self.assertEqual(name, "Carol")
        self.assertEqual(len(user_id), 8)

        user = manage_user.getUser(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.age, 0)
        self.assertEqual(user.profile_level, "premium")
        self.assertEqual(user.email, "carol@example.com")

        manage_user.getJson(filepath=self.temp_json)
        levels = [u.profile_level for u in manage_user.getAllUsers()]
        self.assertIn("premium", levels)


if __name__ == "__main__":
    unittest.main()