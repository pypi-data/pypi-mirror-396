import os.path
from nomad.client import parse, normalize_all


def test_authors():
    path = os.path.join(
        os.path.dirname(__file__),
        '../src/nomad_gui/example_uploads/ui_demonstration/authors/markus.archive.yaml',
    )
    archive = parse(path)[0]
    normalize_all(archive)

    assert archive.data.first_name == 'Markus'
    assert archive.metadata.entry_name == 'Markus Scheidgen'
    assert archive.metadata.entry_type == 'Author'
    assert len(archive.metadata.references) == 1
