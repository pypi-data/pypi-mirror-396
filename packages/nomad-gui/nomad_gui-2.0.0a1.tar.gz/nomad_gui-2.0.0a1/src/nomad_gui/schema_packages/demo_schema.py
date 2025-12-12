from nomad.datamodel.data import Schema
from nomad.metainfo import (
    SchemaPackage,
    Quantity,
    Section,
    MSection,
    SubSection,
)


m_package = SchemaPackage()


class EmployerDetails(MSection):
    department = Quantity(type=str, description='Department within the employer.')
    address = Quantity(type=str, description='Address of the employer.')
    city = Quantity(type=str, description='City of the employer.')


class Position(MSection):
    from_date = Quantity(type=str, description='Start date of the position.')
    to_date = Quantity(type=str, description='End date of the position.')
    employer = Quantity(type=str, description='Employer of the position.')
    occupation = Quantity(type=str, description='Occupation of the position.')
    employer_details = SubSection(
        sub_section=EmployerDetails, description='Details of the employer.'
    )


class Author(Schema):
    m_def = Section(
        a_layout={
            'type': 'container',
            'children': [
                {
                    'type': 'card',
                    'xs': 6,
                    'title': 'About',
                    'children': [
                        {
                            'type': 'quantity',
                            'property': 'first_name',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'last_name',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'email',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'affiliation',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'orcid',
                            'component': 'Id',
                            'editable': True,
                        },
                    ],
                },
                {
                    'type': 'container',
                    'xs': 6,
                    'children': [
                        {'type': 'imagePreview', 'property': 'image'},
                        {
                            'type': 'quantity',
                            'property': 'image',
                            'editable': True,
                        },
                    ],
                },
                {
                    'type': 'text',
                    'content': 'Short biography',
                    'variant': 'h1',
                },
                {'type': 'richText', 'property': 'biography'},
                {'type': 'text', 'content': 'Circum vitae', 'variant': 'h1'},
                {
                    'type': 'sub_section',
                    'property': 'cv',
                    'label': 'Position',
                    'repeats': True,
                    'layout': {
                        'type': 'card',
                        'children': [
                            {
                                'type': 'container',
                                'xs': 4,
                                'children': [
                                    {
                                        'type': 'quantity',
                                        'property': 'from_date',
                                        'component': {
                                            'Datetime': {
                                                'variant': 'date',
                                            }
                                        },
                                        'editable': True,
                                    },
                                    {
                                        'type': 'quantity',
                                        'property': 'to_date',
                                        'component': {
                                            'Datetime': {
                                                'variant': 'date',
                                            }
                                        },
                                        'editable': True,
                                    },
                                ],
                            },
                            {
                                'type': 'container',
                                'xs': 8,
                                'children': [
                                    {
                                        'type': 'quantity',
                                        'property': 'employer',
                                        'editable': True,
                                    },
                                    {
                                        'type': 'quantity',
                                        'property': 'occupation',
                                        'editable': True,
                                    },
                                    {
                                        'type': 'sub_section',
                                        'property': 'employer_details',
                                        'label': 'Employer details',
                                        'layout': {
                                            'type': 'card',
                                            'children': [
                                                {
                                                    'type': 'quantity',
                                                    'property': 'department',
                                                    'editable': True,
                                                },
                                                {
                                                    'type': 'quantity',
                                                    'property': 'address',
                                                    'editable': True,
                                                },
                                                {
                                                    'type': 'quantity',
                                                    'property': 'city',
                                                    'editable': True,
                                                },
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        }
    )

    first_name = Quantity(type=str, description='First name of the author.')
    last_name = Quantity(type=str, description='Last name of the author.')
    email = Quantity(type=str, description='Email address of the author.')
    affiliation = Quantity(type=str, description='Affiliation of the author.')
    orcid = Quantity(type=str, description='ORCID of the author.')

    biography = Quantity(type=str, description='Biography of the author.')

    image = Quantity(type=str, description='URL to an image of the author.')

    cv = SubSection(sub_section=Position, repeats=True, description='CV of the author.')

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        archive.metadata.entry_name = f'{self.first_name} {self.last_name}'
        archive.metadata.references = [f'https://orcid.org/{self.orcid}']


m_package.__init_metainfo__()
