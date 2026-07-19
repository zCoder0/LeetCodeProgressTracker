import sys
from src.exception import ProjectException
from src.config import Settings
import json


def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def save_data(path,data):

    try:
        with open(path, "w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=serialize)
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
        self.difficult_grouping_path=Settings.DATA_DIFFICULT_GROUP_PATH
        self.topic_grouping_path=Settings.DATA_TOPIC_GROUP_PATH
        self.problems=load_data(self.path) or []
        self.problems_index_map = load_data(self.index_map_path) or {}
        self.difficult_grouping = load_data(self.difficult_grouping_path) or {}
        self.topic_grouping = load_data(self.topic_grouping_path) or {}
        for d in self.difficult_grouping:
            self.difficult_grouping[d] = set(self.difficult_grouping[d])
        for t in self.topic_grouping:
            self.topic_grouping[t] = set(self.topic_grouping[t])
        self.valid_difficulties ={
            "EASY",
            "MEDIUM",
            "HARD"
        }
    
    def duplication(self,id):
        return str(id) in self.problems_index_map
    
    def validate_key(self,**data):
        wrong_key=[]
        for key in data.keys():
            if key in ['id',"title","difficulty","topics"]:
                continue
            else:
                wrong_key.append(key)
        return wrong_key

    def validate_values(self,**data):
        
        if data.get("difficulty") not in self.valid_difficulties:
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
        
        self.problems.append(data)
        self.problems_index_map.update({str(data.get("id")): len(self.problems)-1})
        
        difficaulty = data.get("difficulty")
        topics = data.get("topics")

        if difficaulty:
            self._add_to_group(self.difficult_grouping, difficaulty, str(data.get("id")))

        if topics:
            for t in topics:
                t = self._clean_text(t)
                self._add_to_group(self.topic_grouping, t, str(data.get("id")))
    
        if self._save_all():
            return True
        return False
    
    def delete_problem(self,id):
        id=str(id)

        if not self.problems and not self.problems_index_map:
            return False
        
        idx = self.problems_index_map.get(id)
        if idx is None:
            return False 

        del self.problems_index_map[id]

        if self.problems[idx].get("difficulty"):
            self._remove_from_group(self.difficult_grouping, self.problems[idx].get("difficulty"), id)

        if self.problems[idx].get('topics'):
            for t in self.problems[idx].get('topics'):
                print(t)
                t = self._clean_text(t)
                self._remove_from_group(self.topic_grouping, t, id)
            
        if idx == len(self.problems)-1:
            if len(self.problems)<=1:
                self.problems=[]
            else:
                self.problems.pop()

            if self._save_all():
                return True
            return False
        
        self.problems[idx] = self.problems[-1]
        self.problems.pop(-1)
        self.problems_index_map[str(self.problems[idx].get("id"))] = idx
        
        if self._save_all():
            return True
        
        return False
    
    def update_problem(self,**data):
        message = self.validation(**data)
        if message != True:
            return message

        idx = self.problems_index_map.get(str(data.get('id')))
        if idx is None:
            return False
        
        old_difficulty = self.problems[idx].get('difficulty')
        new_difficulty = data.get("difficulty")
        if old_difficulty != new_difficulty:
            self._remove_from_group(self.difficult_grouping, old_difficulty, str(data.get('id')))
            self._add_to_group(self.difficult_grouping, new_difficulty, str(data.get('id')))

        old_topic = set(self._clean_text(i) for i in self.problems[idx].get('topics') )
        new_topic = set(self._clean_text(i) for i  in data.get('topics'))

        for key in (new_topic - old_topic):
            self._add_to_group(self.topic_grouping, key, str(data.get('id')))

        for key in (old_topic - new_topic):
            self._remove_from_group(self.topic_grouping, key, str(data.get('id')))
            

        self.problems[idx].update(data)
        return save_data(self.path, self.problems) and save_data(self.difficult_grouping_path, self.difficult_grouping) and save_data(self.topic_grouping_path, self.topic_grouping)

    def _add_to_group(self,group,key,id):

        if key not in group:
            group[key]=set()
        group[key].add(id)
    
    def _remove_from_group(self, group, key, id):

        if key not in group:
            return
        group[key].discard(id)
        if not group[key]:
            del group[key]

    def _clean_text(self,text:str):
        text = text.lower().strip()
        text = text.replace(" ", "_")
        text = text.replace("-", "_")
        return text

    def _save_all(self):
        return(
            save_data(self.path, self.problems) and
            save_data(self.index_map_path, self.problems_index_map) and
            save_data(self.difficult_grouping_path, self.difficult_grouping) and
            save_data(self.topic_grouping_path, self.topic_grouping)
        )



class TrackerSearh:

    def __init__(self):
        self.difficulty_group = load_data(Settings.DATA_DIFFICULT_GROUP_PATH) or {}
        self.topic_group = load_data(Settings.DATA_TOPIC_GROUP_PATH) or {}
        self.problems = load_data(Settings.DATA_FILE_PATH) or []
        self.problems_map = load_data(Settings.DATA_INDEX_MAP_PATH) or {}
        for d in self.difficulty_group:
            self.difficulty_group[d] = set(self.difficulty_group[d])
        for t in self.topic_group:
            self.topic_group[t] = set(self.topic_group[t])

    def _clean_text(self,text:str):
        text = text.lower().strip()
        text = text.replace(" ", "_")
        text = text.replace("-", "_")
        return text

    def search_by_id(self,id):
        idx=self.problems_map.get(str(id)) 
        return self.problems[idx] if idx is not None else None

    def search_by_topic(self,topic:str):
        topic = self._clean_text(topic)
        return self.topic_group.get(topic)

    def search_by_difficulty(self, difficulty:str):
        difficulty = difficulty.upper()
        return self.difficulty_group.get(difficulty)

    def search(self,query):
        result = set()

        topic_ids = self.search_by_topic(query)
        if topic_ids:
            result |= topic_ids

        difficulty_ids = self.search_by_difficulty(query)
        if difficulty_ids:
            result |= difficulty_ids

        problem = self.search_by_id(query)
        if problem:
            return [problem]

        return [self.search_by_id(i) for i in result]