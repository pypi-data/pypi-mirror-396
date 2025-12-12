import plotly.express as px
from nomad.metainfo import Section
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.datamodel.data import Schema
from nomad.metainfo import (
    SchemaPackage,
    Quantity,
    Section,
    MSection,
    SubSection,
    Datetime,
)
from nomad.utils import strip
from nomad.datamodel.hdf5 import HDF5Dataset
from nomad.metainfo import Section
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import H5WebAnnotation


m_package = SchemaPackage()


class Measurement(MSection):
    voltage = Quantity(
        type=float, default=0, unit='V', description='Voltage of the measurement.'
    )
    current = Quantity(
        type=float, default=0, unit='A', description='Current of the measurement.'
    )


class HSection(ArchiveSection):
    m_def = Section(
        a_h5web=H5WebAnnotation(axes='x', signal='y', auxiliary_signals=['y_err'])
    )

    x = Quantity(
        type=HDF5Dataset, unit='s', a_h5web=H5WebAnnotation(long_name='my_x_label (s)')
    )

    y = Quantity(
        type=HDF5Dataset, unit='m', a_h5web=H5WebAnnotation(long_name='my_y_label (m)')
    )

    y_err = Quantity(
        type=HDF5Dataset, unit='m', a_h5web=H5WebAnnotation(long_name='my_y_err_label')
    )


class Exercise(Schema, PlotSection):
    student_name = Quantity(type=str, description='Name of the student.')
    student_id = Quantity(type=str, description='ID of the student.')
    exercise_date = Quantity(type=Datetime, description='Date of the exercise.')

    measurements = SubSection(
        sub_section=Measurement,
        repeats=True,
        description='Measurements of the experiment.',
    )

    notes = Quantity(type=str, description='Notes of the experiment.')
    hdf5 = SubSection(
        sub_section=HSection,
        repeats=False,
        description='hdf5 data',
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        num_points = 100
        import numpy as np

        dummy_x = np.linspace(0, (num_points - 1) * 0.1, num_points)
        dummy_y = np.sin(dummy_x) * 5.0
        dummy_y_err = np.cos(dummy_x) * 10.0
        archive.data.hdf5 = HSection()
        archive.data.hdf5.x = dummy_x
        archive.data.hdf5.y = dummy_y
        archive.data.hdf5.y_err = dummy_y_err

        if len(self.measurements) == 0:
            self.measurements.append(Measurement())

        measurements = [
            (m.voltage.magnitude, m.current.magnitude)
            for m in self.measurements
            if m.voltage is not None and m.current is not None
        ]

        if len(measurements) == 0:
            return

        plot = px.line(
            x=[m[0] for m in measurements],
            y=[m[1] for m in measurements],
            labels={'x': 'Voltage (V)', 'y': 'Current (A)'},
            title='Voltage over Current',
        )
        self.figures.append(
            PlotlyFigure(label='Voltage over Current', figure=plot.to_plotly_json())
        )

    m_def = Section(
        a_layout={
            'type': 'container',
            'children': [
                {
                    'md': 8,
                    'type': 'container',
                    'children': [
                        {
                            'type': 'markdown',
                            'content': strip("""
                        ## Introduction

                        Ohm's Law is a fundamental relationship in electrical
                        circuits, stating that the current flowing through a
                        conductor is directly proportional to the voltage applied
                        across it. In other words, the resistance of a conductor
                        remains constant as long as its temperature and other
                        physical conditions remain unchanged.

                        In this experiment, you will verify Ohm's Law by measuring
                        the current flowing through a resistor at different applied
                        voltages. By plotting the current against the voltage,
                        you should obtain a linear relationship, the slope of
                        which represents the resistance of the resistor.
                    """),
                        },
                        {
                            'type': 'image',
                            'src': 'https://www.tehencom.com/Companies/Keithley/DMM6500/Keithley_DMM6500_XL.jpg',
                        },
                    ],
                },
                {
                    'type': 'card',
                    'md': 4,
                    'title': 'About',
                    'children': [
                        {
                            'type': 'quantity',
                            'property': 'student_name',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'student_id',
                            'editable': True,
                        },
                        {
                            'type': 'quantity',
                            'property': 'exercise_date',
                            'editable': True,
                        },
                    ],
                },
                {
                    'md': 8,
                    'type': 'table',
                    'label': 'measurement',
                    'title': 'Measurements',
                    'property': 'measurements',
                    'columns': [
                        {
                            'property': 'voltage',
                            'editable': True,
                        },
                        {
                            'property': 'current',
                            'displayUnit': 'mA',
                            'editable': True,
                        },
                    ],
                },
                {
                    'md': 4,
                    'type': 'markdown',
                    'content': strip("""
                        ## Materials
                        - Power supply
                        - Resistor
                        - Ammeter
                        - Voltmeter
                        - Switch
                        - Connecting wires

                        ## Procedure

                        1. Connect the resistor to the power supply.
                        2. Set the power supply to the desired voltage.
                        3. Measure the current flowing through the resistor.
                        4. Record the voltage and current values.
                        5. Repeat steps 2-4 for different voltages.
                    """),
                },
                {
                    'type': 'markdown',
                    'content': strip("""
                        ## Analysis and Discussion

                        - Is the relationship between voltage and current linear?
                        - What is the value of the resistance obtained from the slope of the graph?
                        - How does your calculated resistance compare to the known value of the resistor (if available)?
                        - What are the possible sources of error in the experiment? How could these errors be minimized?

                        Write down your notes and observations in the field below.
                    """),
                },
                {
                    'type': 'richText',
                    'property': 'notes',
                },
                {
                    'type': 'plot',
                    'property': 'figures',
                },
                {
                    'type': 'hdf5',
                    'property': 'hdf5',
                },
            ],
        }
    )


m_package.__init_metainfo__()
