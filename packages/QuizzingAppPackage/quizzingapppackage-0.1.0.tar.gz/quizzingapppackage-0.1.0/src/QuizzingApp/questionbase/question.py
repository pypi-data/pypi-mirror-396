class Question:
    def __init__(self, qid, qtype, qtitle, qtext, qanswer):
        self.qid = qid
        self.qtype = qtype
        self.qtitle = qtitle
        self.qtext = qtext
        self.qanswer = qanswer

    def setText(self,new_text):
        self.qtext=new_text

    def setAnswer(self,new_answer):
        self.qanswer=new_answer
    
    def setTitle(self,new_title):
        self.qtitle=new_title
    
    def setType(self, new_type):
        self.qtype=new_type

    def getText(self):
        return self.qtext
    
    def getAnswer(self):
        return self.qanswer
    
    def getTitle(self):
        return self.qtitle
    
    def getType(self):
        return self.qtype
    
    def display(self):
        return (
            f"QID: {self.qid}\n"
            f"Title: {self.qtitle}\n"
            f"Question: {self.qtext}\n"
            f"Type: {self.qtype}"
        )
    
    def checkAnswer(self,user_input):
        user=str(user_input).strip().lower()
        correct_answer=str(self.qanswer).strip().lower()
        return user==correct_answer
    
    def toDict(self):
        return{
            "qid":self.qid,
            "qtype":self.qtype,
            "qtitle":self.qtitle,
            "qtext":self.qtext,
            "qanswer":self.qanswer
        }
    
class MCQuestion(Question):
    def __init__(self, qid, qtitle, qtext, qoptions, qanswer):
        super().__init__(qid, "MC", qtitle, qtext, qanswer)
        self.qoptions=qoptions
    def display(self):
        base_display=super().display()
        opts="\n".join([f"{i+1}. {opt}" for i,opt in enumerate(self.qoptions)])
        return f"{base_display}\nOptions:\n{opts}"
    def shuffle(self):
        import random
        random.shuffle(self.qoptions)
    def toDict(self):
        data=super().toDict()
        data["qoptions"]=self.qoptions
        return data

class TFQuestion(Question):
    def __init__(self, qid, qtitle, qtext, qanswer):
        super().__init__(qid, "TF", qtitle, qtext, qanswer)

class SAQuestion(Question):
    def __init__(self, qid, qtitle, qtext, qanswer):
        super().__init__(qid, "SA", qtitle, qtext, qanswer)