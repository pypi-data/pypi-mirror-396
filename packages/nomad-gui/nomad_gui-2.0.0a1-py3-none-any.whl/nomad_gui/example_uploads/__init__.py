from nomad.config.models.plugins import ExampleUploadEntryPoint

ui_demonstration_example_upload = ExampleUploadEntryPoint(
    title='UI Demonstration Examples',
    category='Demonstrations',
    description='This upload contains files and entries that demonstrate the capabilities of the NOMAD GUI.',
    path='example_uploads/ui_demonstration/*',
)
