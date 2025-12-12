import os.path
from nomad.client import parse, normalize_all

from nomad_gui.schema_packages.values_test_schema import Referenced


def test_schema():
    path = os.path.join(
        os.path.dirname(__file__),
        '../src/nomad_gui/example_uploads/ui_demonstration/entry-data.archive.yaml',
    )
    archive = parse(path)[0]
    normalize_all(archive)

    assert archive.data.quantity_types.float_quantity.m == 1.87
    assert archive.data.quantity_types.string_quantity == 'Hello World'
    assert archive.data.quantity_types.section_reference.m_def == Referenced.m_def
