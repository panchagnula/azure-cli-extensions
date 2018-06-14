# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                get_resource_name_completion_list, file_type,
                                                get_three_state_flag, get_enum_type)

# pylint: disable=unused-import

import azext_functionapp._help


class FunctionAppExtCommandLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        functionapp_custom = CliCommandType(
            operations_tmpl='azext_functionapp.custom#{}')
        super(FunctionAppExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=functionapp_custom,
                                                     min_profile="2017-03-10-profile")

    def load_command_table(self, _):
        with self.command_group('functionapp') as g:
            g.custom_command('createpreviewapp', 'create_function')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('functionapp createpreviewapp') as c:
            c.argument('plan', options_list=['--plan', '-p'], configured_default='appserviceplan',
                   completer=get_resource_name_completion_list('Microsoft.Web/serverFarms'),
                   help="name or resource id of the function app service plan. Use 'appservice plan create' to get one")
            c.argument('new_app_name', options_list=['--name', '-n'], help='name of the new function app')
            c.argument('storage_account', options_list=['--storage-account', '-s'],
                    help='Provide a string value of a Storage Account in the provided Resource Group. Or Resource ID of a Storage Account in a different Resource Group')
            c.argument('consumption_plan_location', options_list=['--consumption-plan-location', '-c'],
                    help="Geographic location where Function App will be hosted. Use 'functionapp list-consumption-locations' to view available locations.")
            c.argument('is_linux', action='store_true', required=False, help='host functionapp on Linux worker')
            c.argument('runtime', help='The function runtime stack. Currently supported for Linux apps only', arg_type=get_enum_type(['dotnet', 'node', 'python']))
 
COMMAND_LOADER_CLS = FunctionAppExtCommandLoader
