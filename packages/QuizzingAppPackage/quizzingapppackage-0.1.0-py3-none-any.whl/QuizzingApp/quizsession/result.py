# This is where the result is processed and stored

from datetime import datetime
import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class QuizResult:
    def __init__(self, session_dict, all_questions):
        self.session_id = session_dict.get('session_id')
        self.user_id = session_dict.get('user_id')
        self.user_name = session_dict.get('user_name')
        self.num_questions = session_dict.get('num_questions', [0, 0, 0])
        self.sum_questions = session_dict.get('sum_questions', 0)
        self.question_ids = session_dict.get('question_ids', [])
        self.answers = session_dict.get('answer', [])
        self.total_time = session_dict.get('total_time')
        self.questions = [q for q in all_questions if q['qid'] in self.question_ids]
        self.results = []
        self._analyze_answers()
    
    def _analyze_answers(self):
        for qid, user_answer in self.answers:
            question = next((q for q in self.questions if q.get('qid') == qid), None)
            if question:
                is_correct = self.compareAnswer(question, user_answer)
                self.results.append({
                    'question': question,
                    'user_answer': user_answer,
                    'correct_answer': question.get('qanswer', question.get('answer', '')),
                    'is_correct': is_correct,
                    'qtype': question.get('qtype', question.get('type', ''))
                })
    
    def compareAnswer(self, question, answer):
        correct_answer = question.get('qanswer', question.get('answer', ''))

        if isinstance(answer, str) and isinstance(correct_answer, str):
            return answer.strip().lower() == correct_answer.strip().lower()
        return answer == correct_answer
    
    def countCorrect(self):
        return sum(1 for r in self.results if r['is_correct'])
    
    def countWrong(self):
        return sum(1 for r in self.results if not r['is_correct'])
    
    def getScore(self):
        return self.countCorrect()
    
    def percentage(self):
        if self.sum_questions == 0:
            return 0.0
        return round((self.countCorrect() / self.sum_questions) * 100, 2)
    
    def typeChart(self):
        type_counts = {}
        for result in self.results:
            qtype = result['qtype']
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        plt.figure(figsize=(6, 6))
        labels = list(type_counts.keys())
        sizes = list(type_counts.values())
        colors = ["#fff82b", "#5ea9f4", "#f77a8b"]
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)])
        plt.title(f'Question types distribution\n{self.user_name}')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    
    def typeCorrectBar(self):
        type_stats = {}
        for result in self.results:
            qtype = result['qtype']
            if qtype not in type_stats:
                type_stats[qtype] = {'correct': 0, 'incorrect': 0}
            
            if result['is_correct']:
                type_stats[qtype]['correct'] += 1
            else:
                type_stats[qtype]['incorrect'] += 1
        
        if not type_stats:
            print("No questions to visualize.")
            return

        types = list(type_stats.keys())
        correct_counts = [type_stats[t]['correct'] for t in types]
        incorrect_counts = [type_stats[t]['incorrect'] for t in types]
        
        x = np.arange(len(types))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bars1 = ax.bar(x - width/2, correct_counts, width, label='Correct', color="#92F090")
        bars2 = ax.bar(x + width/2, incorrect_counts, width, label='Incorrect', color="#e87269")
        
        ax.set_xlabel('Question type')
        ax.set_ylabel('Number of questions')
        ax.set_title(f'Correct vs incorrect answers for each type\n{self.user_name} - Score: {self.getScore()}/{self.sum_questions}')
        ax.set_xticks(x)
        ax.set_xticklabels(types)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def toDict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'score': self.getScore(),
            'total_questions': self.sum_questions,
            'percentage': self.percentage(),
            'correct': self.countCorrect(),
            'wrong': self.countWrong(),
            'total_time': self.total_time,
            'results': self.results
        }
    
    def toJSON(self):
        return json.dumps(self.toDict(), indent=4)
    
    def saveResult(self, filepath):
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, 'r') as f:
                try:
                    results_data = json.load(f)
                except json.JSONDecodeError:
                    results_data = []
        else:
            results_data = []
        
        result_dict = self.toDict()
        result_dict['results'] = [
            {
                'qid': r['question'].get('qid', ''),
                'user_answer': r['user_answer'],
                'correct_answer': r['correct_answer'],
                'is_correct': r['is_correct'],
                'qtype': r['qtype']
            }
            for r in self.results
        ]
        
        results_data.append(result_dict)
    
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=4)
        
        print(f"Result saved to {filepath}")
        
# too much for now
# def getDictFromSession(session):
#     return session.toDict()

# def trendPlot(results_list):  
#     if not results_list:
#         print("No past scores")
#         return
#     sessions = []
#     percentages = []
    
#     for i, result in enumerate(results_list):
#         if isinstance(result, QuizResult):
#             sessions.append(f"{i+1}")
#             percentages.append(result.percentage())
#         elif isinstance(result, dict):
#             sessions.append(f"{i+1}")
#             percentages.append(result.get('percentage', 0))
    
#     fig, p = plt.subplots(figsize=(12, 6))
#     x = np.arange(len(sessions))
#     p.plot(x, percentages, marker='s', linewidth=2, markersize=3, color="#60D369")
#     p.set_xlabel('Quiz Session')
#     p.set_ylabel('Percentage (%)')
#     p.set_title('Quiz Percentage Trend Over Time')
#     p.set_xticks(x)
#     p.set_xticklabels(sessions, ha='right')
#     p.set_ylim(0, 105)
#     p.grid(True, alpha=0.3)
#     p.legend()

#     for i, pct in enumerate(percentages):
#         p.text(i, pct, f'{pct:.1f}%', ha='center', va='bottom')
    
#     plt.tight_layout()
#     plt.show()