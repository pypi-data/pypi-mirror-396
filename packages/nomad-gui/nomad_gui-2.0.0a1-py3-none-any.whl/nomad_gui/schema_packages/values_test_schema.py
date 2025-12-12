import numpy as np

from nomad.config.models.plugins import SchemaPackageEntryPoint
from nomad.datamodel.data import Schema
from nomad.metainfo import (
    SchemaPackage,
    Quantity,
    MSection,
    SubSection,
    Reference,
    MEnum,
    Datetime,
    JSON,
    File,
    URL,
    Capitalized,
    Bytes,
    Dimension,
    Unit,
)


m_package = SchemaPackage()


class Referenced(MSection):
    pass


class QuantityTypes(MSection):
    float_quantity = Quantity(type=float, unit='m')
    float_list_quantity = Quantity(type=float, shape=['*'], unit='m')
    np_quantity = Quantity(type=np.float64, unit='m')
    np_matrix = Quantity(type=np.float64, shape=[3, 3], unit='m')

    string_quantity = Quantity(type=str)
    enum_quantity = Quantity(type=MEnum('one', 'two', 'three'))
    bool_quantity = Quantity(type=bool)
    int_quantity = Quantity(type=int)
    datatime_quantity = Quantity(type=Datetime)

    float_with_default = Quantity(type=float, default=1.87, unit='m')
    int_with_default = Quantity(type=int, default=42)
    string_with_default = Quantity(type=str, default='default value')

    url_quantity = Quantity(type=URL)
    file_quantity = Quantity(type=File)
    capitalized_quantity = Quantity(type=Capitalized)
    bytes_quantity = Quantity(type=Bytes)
    json_quantity = Quantity(type=JSON)
    dimension_quantity = Quantity(type=Dimension)
    unit_quantity = Quantity(type=Unit)

    section_reference = Quantity(type=Reference(Referenced))


class ASection(MSection):
    string_quantity = Quantity(type=str)


class Main(Schema):
    quantity_types = SubSection(sub_section=QuantityTypes)
    sub_section = SubSection(sub_section=ASection)
    repeated_sub_section = SubSection(sub_section=ASection, repeats=True)
    empty_sub_section = SubSection(sub_section=ASection)
    empty_repeated_sub_section = SubSection(sub_section=ASection, repeats=True)
    referenced = SubSection(sub_section=Referenced)


m_package.__init_metainfo__()
