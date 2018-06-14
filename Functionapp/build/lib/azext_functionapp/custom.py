# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import threading

from knack.log import get_logger
from knack.util import CLIError

from binascii import hexlify
from os import urandom

from msrestazure.tools import is_valid_resource_id, parse_resource_id

from azure.mgmt.web.models import (AppServicePlan, SkuDescription, SiteConfig, Site, NameValuePair)

from azure.cli.core.commands import LongRunningOperation

from azure.cli.core.commands.client_factory import get_mgmt_service_client

from azure.cli.command_modules.appservice.custom import (
    list_consumption_locations,
    _validate_and_get_connection_string,
    _set_remote_or_local_git,
    update_app_settings,
    _get_site_credential,
    _get_scm_url,
    get_sku_name,
    list_publish_profiles,
    get_site_configs)


logger = get_logger(__name__)

# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements,too-many-branches

def web_client_factory(cli_ctx, **_):
    from azure.mgmt.web import WebSiteManagementClient
    return get_mgmt_service_client(cli_ctx, WebSiteManagementClient)


def create_function(cmd, resource_group_name, name, storage_account, is_linux,
                    plan=None, consumption_plan_location=None, runtime=None,
                    deployment_source_url=None, deployment_source_branch='master',
                    deployment_local_git=None, deployment_container_image_name=None):
    # pylint: disable=too-many-statements
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')
    if bool(plan) == bool(consumption_plan_location):
        raise CLIError("usage error: --plan NAME_OR_ID | --consumption-plan-location LOCATION")

    site_config = SiteConfig(app_settings=[])
    functionapp_def = Site(location=None, site_config=site_config)
    client = web_client_factory(cmd.cli_ctx)

    if consumption_plan_location:
        locations = list_consumption_locations(cmd)
        location = next((l for l in locations if l['name'].lower() == consumption_plan_location.lower()), None)
        if location is None:
            raise CLIError("Location is invalid. Use: az functionapp list-consumption-locations")
        functionapp_def.location = consumption_plan_location
        functionapp_def.kind = 'functionapp'
        if is_linux and not runtime:
            raise CLIError("usage error: --runtime RUNTIME required for linux functions apps with cosumption plan.")
    else:
        if is_valid_resource_id(plan):
            plan = parse_resource_id(plan)['name']
        plan_info = client.app_service_plans.get(resource_group_name, plan)
        if not plan_info:
            raise CLIError("The plan '{}' doesn't exist".format(plan))
        location = plan_info.location
        is_linux = plan_info.reserved if plan_info.reserved else is_linux
        functionapp_def.server_farm_id = plan
        functionapp_def.location = location

    con_string = _validate_and_get_connection_string(cmd.cli_ctx, resource_group_name, storage_account)
    if is_linux:
        functionapp_def.kind = 'functionapp,linux'
        site_config.app_settings.append(NameValuePair('FUNCTIONS_EXTENSION_VERSION', 'beta'))
        if consumption_plan_location:
            site_config.app_settings.append(NameValuePair('FUNCTIONS_WORKER_RUNTIME', runtime))
        else:
            site_config.app_settings.append(NameValuePair('MACHINEKEY_DecryptionKey',
                                                          str(hexlify(urandom(32)).decode()).upper()))
            if deployment_container_image_name:
                site_config.app_settings.append(NameValuePair('DOCKER_CUSTOM_IMAGE_NAME',
                                                              deployment_container_image_name))
                site_config.app_settings.append(NameValuePair('FUNCTION_APP_EDIT_MODE', 'readOnly'))
                site_config.app_settings.append(NameValuePair('WEBSITES_ENABLE_APP_SERVICE_STORAGE', 'false'))
            else:
                site_config.app_settings.append(NameValuePair('WEBSITES_ENABLE_APP_SERVICE_STORAGE', 'true'))
                site_config.linux_fx_version = 'DOCKER|appsvc/azure-functions-runtime'
    else:
        functionapp_def.kind = 'functionapp'
        site_config.app_settings.append(NameValuePair('FUNCTIONS_EXTENSION_VERSION', '~1'))

    # adding appsetting to site to make it a function
    site_config.app_settings.append(NameValuePair('AzureWebJobsStorage', con_string))
    site_config.app_settings.append(NameValuePair('AzureWebJobsDashboard', con_string))
    site_config.app_settings.append(NameValuePair('WEBSITE_NODE_DEFAULT_VERSION', '6.5.0'))

    if consumption_plan_location is None:
        site_config.always_on = True
    else:
        site_config.app_settings.append(NameValuePair('WEBSITE_CONTENTAZUREFILECONNECTIONSTRING',
                                                      con_string))
        site_config.app_settings.append(NameValuePair('WEBSITE_CONTENTSHARE', name.lower()))

    poller = client.web_apps.create_or_update(resource_group_name, name, functionapp_def)
    functionapp = LongRunningOperation(cmd.cli_ctx)(poller)

    # TODO: Add link here
    if(consumption_plan_location and is_linux):
        logger.warning('''Your function app has been created but is not active until content is published using
                       Azure Portal or the Functions Core Tools.''')
    else:
        _set_remote_or_local_git(cmd, functionapp, resource_group_name, name, deployment_source_url,
                                 deployment_source_branch, deployment_local_git)

    return functionapp
