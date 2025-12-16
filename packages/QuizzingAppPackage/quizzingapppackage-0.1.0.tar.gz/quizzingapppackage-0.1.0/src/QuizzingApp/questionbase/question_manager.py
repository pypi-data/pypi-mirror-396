from .question import Question, MCQuestion, TFQuestion, SAQuestion
import json 
class QuestionManager:
    def __init__(self):
        self.questions=[]
    def addQuestion(self,question_obj):
        if question_obj is None:
            raise ValueError("Question object cannot be None")
        if not isinstance(question_obj, Question):
            raise ValueError("Must be a Question instance")
        self.questions.append(question_obj)
    def deleteQuestion(self,qid):
        if not qid:
            raise ValueError("no qid")
        self.questions=[q for q in self.questions if q.qid!=qid]
    def getAllQuestions(self):
        return self.questions
    def filterQuestions(self,qtype):
        if not qtype:
            raise ValueError("no question")
        return [q for q in self.questions if q.qtype==qtype]
    def toJson(self,filepath):
        if not filepath:
            raise ValueError("path not found")
        data=[q.toDict() for q in self.questions]
        with open(filepath, "w",encoding="utf-8") as f:
            json.dump(data,f,indent=4)
    def getJson(self,filepath):
        with open(filepath, "r",encoding="utf-8") as f:
            data=json.load(f)
        
        if isinstance(data, dict) and "questions" in data:
            data = data["questions"]
        
        self.questions=[]
        for q in data:
            qtype = q.get("qtype", q.get("type", ""))
            qid = q.get("qid")
            qtitle = q.get("qtitle", q.get("topic", ""))
            qtext = q.get("qtext", q.get("text", ""))
            qanswer = q.get("qanswer", q.get("answer", ""))

            if qtype == "MCQ":
                qtype = "MC"
            
            if qtype == "MC":
                qoptions = q.get("qoptions", q.get("options", []))
                obj = MCQuestion(qid, qtitle, qtext, qoptions, qanswer)
            elif qtype == "TF":
                obj = TFQuestion(qid, qtitle, qtext, qanswer)
            elif qtype == "SA":
                obj = SAQuestion(qid, qtitle, qtext, qanswer)
            else:
                obj = Question(qid, qtype, qtitle, qtext, qanswer)
                
            self.questions.append(obj)