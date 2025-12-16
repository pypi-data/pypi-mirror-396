import json
import uuid
import time
from pathlib import Path
from .user import RegularUser, PremiumUser
from ..errors import InvalidAgeError, InvalidEmailError, DataFileNotFoundError, InvalidNameError

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
USERS_JSON = DATA_DIR / "users.json"

_users = {}
def createUser(user_type, user_id, name, age, email, grades=None):
    if grades is None:
        grades = []
    if user_type == "regular":
        user = RegularUser(user_id, name, age, email, grades)
    elif user_type == "premium":
        user = PremiumUser(user_id, name, age, email, grades)
    else:
        raise ValueError("user_type must be 'regular' or 'premium'")
    _users[user_id] = user
    return user

def deleteUser(user_id):
    if user_id in _users:
        del _users[user_id]
        return True
    return False

def getUser(user_id):
    return _users.get(user_id)

def getAllUsers():
    return list(_users.values())

def deleteAllUsers():
    global _users
    _users.clear()

def toJson(filepath=USERS_JSON):
    filepath = Path(filepath)
    try: 
        filepath.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise DataFileNotFoundError('No permission')
    data = [user.toDict() for user in _users.values()]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def getJson(filepath=USERS_JSON):
    global _users
    if not Path(filepath).exists():
        _users = {}
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_users = json.load(f)
    except PermissionError:
        raise DataFileNotFoundError('no permission')
    
    _users = {}
    for item in raw_users:
        user_type = item.get("profile_level", "regular")
        if user_type == "premium":
            user = PremiumUser(
                item["user_id"],
                item["name"],
                item["age"],
                item["email"],
                item.get("grades", []),
            )
        else:
            user = RegularUser(
                item["user_id"],
                item["name"],
                item["age"],
                item["email"],
                item.get("grades", []),
            )
        _users[user.user_id] = user

def registerUser(filepath=USERS_JSON):
    getJson(filepath)
    print("\n=== User Registration ===")
    user_id = str(uuid.uuid4())[:8]
    name = input("Enter your name: ").strip()
    age = input("Enter your age: ").strip()
    email = input("Enter your email: ").strip()
    profile_type = input("Do you want premium? (yes/no): ").strip().lower()

        
    invalids = ['@', '#', '$', '%']
    if any(char in name for char in invalids):
            raise InvalidNameError("name invaild")
    
    try:
        age = int(age)
        if age < 0 or age > 150:
            raise InvalidAgeError(f"Age {age} is out of valid range (0-150)")
    except ValueError:
        print("Invalid age. Setting to 0.")
        age = 0
    
    try:
        if '@' not in email:
            raise InvalidEmailError('not a vaild email')
    except Exception as e:
        raise InvalidEmailError("email not vaild")

    
    profile_level = "regular"
    if profile_type in ["yes", "y"]:
        print("Upgrading to premium...")
        time.sleep(3)
        profile_level = "premium"
        
    if profile_level == "premium":
        user = PremiumUser(user_id, name, age, email, [])
    else:
        user = RegularUser(user_id, name, age, email, [])
    
    _users[user_id] = user
    toJson(filepath)
    print(f"\nRegister successful!")
    return user_id, name