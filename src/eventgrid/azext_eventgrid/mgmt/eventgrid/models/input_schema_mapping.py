# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class InputSchemaMapping(Model):
    """By default, Event Grid expects events to be in the Event Grid event schema.
    Specifying an input schema mapping enables publishing to Event Grid using a
    custom input schema. Currently, the only supported type of
    InputSchemaMapping is 'JsonInputSchemaMapping'.

    You probably want to use the sub-classes and not this class directly. Known
    sub-classes are: JsonInputSchemaMapping

    :param input_schema_mapping_type: Constant filled by server.
    :type input_schema_mapping_type: str
    """

    _validation = {
        'input_schema_mapping_type': {'required': True},
    }

    _attribute_map = {
        'input_schema_mapping_type': {'key': 'inputSchemaMappingType', 'type': 'str'},
    }

    _subtype_map = {
        'input_schema_mapping_type': {'Json': 'JsonInputSchemaMapping'}
    }

    def __init__(self):
        super(InputSchemaMapping, self).__init__()
        self.input_schema_mapping_type = None
