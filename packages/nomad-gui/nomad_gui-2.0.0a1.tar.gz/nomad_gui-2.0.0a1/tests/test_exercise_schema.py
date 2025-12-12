import os.path
from nomad.client import parse, normalize_all


def test_exercise_empty():
    path = os.path.join(
        os.path.dirname(__file__),
        '../src/nomad_gui/example_uploads/ui_demonstration/exercises/exercise_1_resistance.archive.json',
    )
    archive = parse(path)[0]
    normalize_all(archive)
    assert archive.data is not None


def test_exercise_complete():
    path = os.path.join(
        os.path.dirname(__file__),
        '../src/nomad_gui/example_uploads/ui_demonstration/exercises/exercise_1_resistance_completed.archive.json',
    )
    archive = parse(path)[0]
    normalize_all(archive)
    assert archive.data is not None
    assert len(archive.data.figures) == 1
    assert archive.data.student_name is not None
    assert archive.data.student_id is not None
    assert archive.metadata.entry_name == 'Exercise 1: Resistance'
    assert len(archive.metadata.references) == 1
