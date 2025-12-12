from nomad.config.models.plugins import SchemaPackageEntryPoint


class DemoSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from .demo_schema import m_package

        return m_package


demo_schema = DemoSchemaPackageEntryPoint(
    name='Demo Schema',
    description='Just a small demo schema for the new GUI.',
)


class ValuesTestSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from .values_test_schema import m_package

        return m_package


values_test_schema = ValuesTestSchemaPackageEntryPoint(
    name='Values test schema',
    description='A schema that is used for the GUI e2e tests related to quantity values.',
)


class ExerciseSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from .exercise_schema import m_package

        return m_package


exercise_schema = ExerciseSchemaPackageEntryPoint(
    name='Exercise Schema',
    description='A schema for the exercise data.',
)
