class User:
    def __init__(self, user_id, name, age, email, grades=None, profile_level="regular"):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.email = email
        self.grades = grades if grades is not None else []
        self.profile_level = profile_level

    def setUserInfo(self, name=None, age=None, email=None):
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
        if email is not None:
            self.email = email

    def getUserInfo(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "grades": list(self.grades),
            "profile_level": self.profile_level,
        }

    def addScore(self, score):
        self.grades.append(score)

    def getAvg(self):
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)

    def toDict(self):
        return self.getUserInfo()

class RegularUser(User):
    def __init__(self, user_id, name, age, email, grades=None):
        super().__init__(
            user_id=user_id,
            name=name,
            age=age,
            email=email,
            grades=grades,
            profile_level="regular",
        )

class PremiumUser(User):
    def __init__(self, user_id, name, age, email, grades=None):
        super().__init__(
            user_id=user_id,
            name=name,
            age=age,
            email=email,
            grades=grades,
            profile_level="premium",
        )
