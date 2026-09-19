import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recovery_ia.api.routes import patients


class _FakeCollection:
    def __init__(self, docs):
        self._docs = docs

    def find(self):
        return iter(self._docs)


def test_list_patients_strips_mongo_id(monkeypatch):
    docs = [{"_id": "507f1f77bcf86cd799439011", "case_id": "CASE-0001", "edad": 42}]
    monkeypatch.setattr(patients, "get_patients_collection", lambda: _FakeCollection(docs))

    result = patients.list_patients()

    assert result == [{"case_id": "CASE-0001", "edad": 42}]


def test_list_patients_empty_collection(monkeypatch):
    monkeypatch.setattr(patients, "get_patients_collection", lambda: _FakeCollection([]))

    assert patients.list_patients() == []
