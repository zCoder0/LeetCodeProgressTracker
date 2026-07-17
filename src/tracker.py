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
    
    except FileNotFoundError:
        return []
    except Exception as e:
        raise ProjectException(e,sys)
  
class Tracker:
    
    def __init__(self):
        self.path = Settings.DATA_FILE_PATH
        self.index_map_path=Settings.DATA_INDEX_MAP_PATH
        self.problems=load_data(self.path) or []
        self.problems_index_map = load_data(self.index_map_path) or {}
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
        
        is_duplicate = self.duplication(data.get("id"))
        if is_duplicate:
            return "Duplicate value"
        
        self.problems = load_data(self.path)  or []
        self.problems.append(data)
        self.problems_index_map.update({data.get("id"):len(self.problems)-1})
        if save_data(self.path, self.problems) and save_data(self.index_map_path,self.problems_index_map):
            return True
        return False
    
    def delete_problem(self,id):
        id=str(id)
        self.problems = load_data(self.path) or []
        self.problems_index_map = load_data(self.index_map_path) or {}
        
        if not self.problems and not self.problems_index_map:
            return False
        
        #0
        idx = self.problems_index_map.get(id) or None 
        if idx is None:
            return False 
        
        del self.problems_index_map[id]

        if idx == len(self.problems)-1:
            if len(self.problems)<=1:
                self.problems=[]
            else:
                self.problems = self.problems[:-1] or []

            if save_data(self.path ,self.problems) and save_data(self.index_map_path , self.problems_index_map):
                return True
        
        self.problems[idx] = self.problems[-1]
        self.problems.pop(-1)
        self.problems_index_map[str(self.problems[idx].get("id"))] = idx

        if save_data(self.path ,self.problems) and save_data(self.index_map_path , self.problems_index_map):
            return True
        
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