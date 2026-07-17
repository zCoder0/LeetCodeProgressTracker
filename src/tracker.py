import sys
from src.exception import ProjectException
from src.config import Settings
import json


def save_data(path,data):

    try:
        with open(path, "w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        raise ProjectException(e,sys)

  

def load_data(path):
    try:
        with open(path, "r",encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return []
        return json.loads(content)
    
    except Exception as e:
        raise ProjectException(e,sys)
  
class Tracker:
    
    def __init__(self):
        self.path = Settings.DATA_FILE_PATH
        self.problems=load_data(self.path) or []
        self.dificult ={
            "EASY",
            "MEDIUM",
            "HARD"
        }
    def duplication(self,id):

        self.problems = load_data(self.path) or []

        for problem in self.problems:
            if problem.get('id') == id:
                return True 
    
        return False
    
    def validate_key(self,**data):
        wrong_key=[]
        for key in data.keys():
            if key in ['id',"title","difficulty","topics"]:
                continue
            else:
                wrong_key.append(key)
        return wrong_key

    def validate_values(self,**data):
        
        if data.get("difficulty") not in self.dificult:
            return "Wrong difficulty level"
        if not isinstance(data.get("id"), int):
            return "Id must be an integer"
        if not isinstance(data.get("title"), str):
            return "Title must be a string"
        if not isinstance(data.get("topics"), list):
            return "Topics must be a list"
        return True

    def validation(self, **data):
        wrong_key = self.validate_key(**data)
        if wrong_key:
            return "Wrong keys in input data", wrong_key
        
        val = self.validate_values(**data)
        if val != True:
            return val
        
        return True
    
    def add_problems(self,**data):
        
        message =self.validation(**data)

        if message != True:
            return message
        
        self.problems = load_data(self.path)  or []
        self.problems.append(data)
        return save_data(self.path, self.problems)
    
    def delete_problem(self,id):
        self.problems = load_data(self.path) or []
        initial_len = len(self.problems)
        if not self.problems:
            return False
        
        self.problems = [p for p in self.problems if p.get('id') != id]

        if len(self.problems) < initial_len:
            return save_data(self.path, self.problems)

        return False
    
    def update_problem(self,**data):
        wrong_key = self.validate_key(**data)
        if wrong_key:
            return f"wrong keys {wrong_key} in input data"

        self.problems = load_data(self.path) or []

        for problem in self.problems:
            if problem.get('id') == data.get('id'):
                problem.update(data)
                return save_data(self.path, self.problems)
        
        return False