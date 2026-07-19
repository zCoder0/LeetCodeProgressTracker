import json
import pytest
from src.tracker import Tracker, TrackerSearh, save_data, load_data


@pytest.fixture
def tracker(tmp_path):
    data_file = tmp_path / "problems.json"
    index_file = tmp_path / "problems_map.json"
    data_file.write_text("[]")
    index_file.write_text("{}")

    import src.config
    original_path = src.config.Settings.DATA_FILE_PATH
    original_map = src.config.Settings.DATA_INDEX_MAP_PATH
    src.config.Settings.DATA_FILE_PATH = str(data_file)
    src.config.Settings.DATA_INDEX_MAP_PATH = str(index_file)

    t = Tracker()
    yield t

    src.config.Settings.DATA_FILE_PATH = original_path
    src.config.Settings.DATA_INDEX_MAP_PATH = original_map


class TestAddProblems:
    def test_add_valid(self, tracker):
        assert tracker.add_problems(id=1, title="Two Sum", difficulty="EASY", topics=["array"]) is True
        assert len(tracker.problems) == 1

    def test_duplicate(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        assert tracker.add_problems(id=1, title="B", difficulty="MEDIUM", topics=[]) == "Duplicate value"
        assert len(tracker.problems) == 1

    def test_wrong_key(self, tracker):
        result = tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[], invalid="x")
        assert result[0] == "Wrong keys in input data"
        assert "invalid" in result[1]

    def test_wrong_difficulty(self, tracker):
        result = tracker.add_problems(id=1, title="A", difficulty="IMPOSSIBLE", topics=[])
        assert result == "Wrong difficulty level"

    def test_wrong_id_type(self, tracker):
        result = tracker.add_problems(id="one", title="A", difficulty="EASY", topics=[])
        assert result == "Id must be an integer"

    def test_wrong_title_type(self, tracker):
        result = tracker.add_problems(id=1, title=123, difficulty="EASY", topics=[])
        assert result == "Title must be a string"

    def test_wrong_topics_type(self, tracker):
        result = tracker.add_problems(id=1, title="A", difficulty="EASY", topics="not a list")
        assert result == "Topics must be a list"


class TestUpdateProblems:
    def test_update_existing(self, tracker):
        tracker.add_problems(id=1, title="Two Sum", difficulty="EASY", topics=["array"])
        assert tracker.update_problem(id=1, title="Two Sum Updated", difficulty="HARD", topics=["array", "hash"]) is True
        assert tracker.problems[0]["title"] == "Two Sum Updated"
        assert tracker.problems[0]["difficulty"] == "HARD"

    def test_update_non_existent(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        assert tracker.update_problem(id=99, title="X", difficulty="HARD", topics=[]) is False

    def test_update_persists_to_file(self, tracker):
        tracker.add_problems(id=1, title="Original", difficulty="EASY", topics=[])
        tracker.update_problem(id=1, title="Changed", difficulty="HARD", topics=["new"])

        t2 = Tracker()
        assert t2.problems[0]["title"] == "Changed"
        assert t2.problems[0]["difficulty"] == "HARD"

    def test_validate_key(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        result = tracker.update_problem(id=1, title="B", difficulty="MEDIUM", topics=[], bad_key="x")
        assert result[0] == "Wrong keys in input data"

    def test_validate_value(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        result = tracker.update_problem(id=1, title="B", difficulty="WRONG", topics=[])
        assert result == "Wrong difficulty level"


class TestDeleteProblems:
    def test_delete_first(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=2, title="B", difficulty="MEDIUM", topics=[])
        tracker.add_problems(id=3, title="C", difficulty="HARD", topics=[])
        assert tracker.delete_problem(id=1) is True
        assert len(tracker.problems) == 2
        assert tracker.problems[0]["id"] in (2, 3)

    def test_delete_middle(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=2, title="B", difficulty="MEDIUM", topics=[])
        tracker.add_problems(id=3, title="C", difficulty="HARD", topics=[])
        assert tracker.delete_problem(id=2) is True
        assert len(tracker.problems) == 2

    def test_delete_last(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=2, title="B", difficulty="MEDIUM", topics=[])
        assert tracker.delete_problem(id=2) is True
        assert len(tracker.problems) == 1
        assert tracker.problems[0]["id"] == 1

    def test_delete_only_element(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        assert tracker.delete_problem(id=1) is True
        assert len(tracker.problems) == 0

    def test_delete_non_existent(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        assert tracker.delete_problem(id=99) is False

    def test_delete_empty(self, tracker):
        assert tracker.delete_problem(id=1) is False

    def test_delete_persists_to_file(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=2, title="B", difficulty="MEDIUM", topics=[])
        tracker.delete_problem(id=1)

        t2 = Tracker()
        assert len(t2.problems) == 1
        assert t2.problems[0]["id"] == 2
        assert t2.problems_index_map.get("2") == 0

    def test_delete_and_add_reuses_id(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.delete_problem(id=1)
        assert tracker.add_problems(id=1, title="A again", difficulty="HARD", topics=[]) is True
        assert len(tracker.problems) == 1


class TestDataPersistence:
    def test_add_persists(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=["math"])
        data = load_data(tracker.path)
        assert len(data) == 1
        assert data[0]["id"] == 1
        index = load_data(tracker.index_map_path)
        assert index.get("1") == 0

    def test_multiple_adds_persist(self, tracker):
        tracker.add_problems(id=1, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=2, title="B", difficulty="MEDIUM", topics=["x"])
        data = load_data(tracker.path)
        assert len(data) == 2

    def test_index_map_accuracy(self, tracker):
        tracker.add_problems(id=10, title="A", difficulty="EASY", topics=[])
        tracker.add_problems(id=20, title="B", difficulty="MEDIUM", topics=[])
        tracker.add_problems(id=30, title="C", difficulty="HARD", topics=[])
        expected = {"10": 0, "20": 1, "30": 2}
        assert dict(tracker.problems_index_map) == expected


class TestValidation:
    def test_missing_id(self, tracker):
        result = tracker.add_problems(title="A", difficulty="EASY", topics=[])
        assert "Id must be an integer" in str(result)


@pytest.fixture
def searcher(tmp_path):
    data_file = tmp_path / "problems.json"
    index_file = tmp_path / "problems_map.json"
    diff_file = tmp_path / "difficult_grouping.json"
    topic_file = tmp_path / "topic_grouping.json"

    problems = [
        {"id": 1, "title": "Two Sum", "difficulty": "EASY", "topics": ["array", "hash"]},
        {"id": 2, "title": "Three Sum", "difficulty": "MEDIUM", "topics": ["array", "two pointers"]},
        {"id": 3, "title": "Hard Problem", "difficulty": "HARD", "topics": ["dp"]},
    ]
    problems_map = {"1": 0, "2": 1, "3": 2}
    diff_group = {"EASY": ["1"], "MEDIUM": ["2"], "HARD": ["3"]}
    topic_group = {"array": ["1", "2"], "hash": ["1"], "two_pointers": ["2"], "dp": ["3"]}

    data_file.write_text(json.dumps(problems))
    index_file.write_text(json.dumps(problems_map))
    diff_file.write_text(json.dumps(diff_group))
    topic_file.write_text(json.dumps(topic_group))

    import src.config
    orig = {}
    for attr in ["DATA_FILE_PATH", "DATA_INDEX_MAP_PATH", "DATA_DIFFICULT_GROUP_PATH", "DATA_TOPIC_GROUP_PATH"]:
        orig[attr] = getattr(src.config.Settings, attr)
    src.config.Settings.DATA_FILE_PATH = str(data_file)
    src.config.Settings.DATA_INDEX_MAP_PATH = str(index_file)
    src.config.Settings.DATA_DIFFICULT_GROUP_PATH = str(diff_file)
    src.config.Settings.DATA_TOPIC_GROUP_PATH = str(topic_file)

    s = TrackerSearh()
    yield s

    for attr, val in orig.items():
        setattr(src.config.Settings, attr, val)


class TestSearch:
    def test_search_by_difficulty(self, searcher):
        result = searcher.search("easy")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_search_by_difficulty_case_insensitive(self, searcher):
        result = searcher.search("EASY")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_search_by_topic(self, searcher):
        result = searcher.search("array")
        assert len(result) == 2
        assert {p["id"] for p in result} == {1, 2}

    def test_search_by_id(self, searcher):
        result = searcher.search("1")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_search_no_match(self, searcher):
        result = searcher.search("nonexistent")
        assert result == []

    def test_search_normalizes_topics(self, searcher):
        result = searcher.search("two pointers")
        assert len(result) == 1
        assert result[0]["id"] == 2
