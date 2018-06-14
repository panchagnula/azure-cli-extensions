# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['functionapp createpreviewapp'] = """
    type: command
    short-summary: (Private Preview) Creates a basic functionapp.
    long-summary: Supports creating a basic function app. In addition supports 
                  of creating a preview Linux function app with consumption plan
    examples:
        - name: Creates Linux Consumption plan function app
          text: >
            az functionapp create -n MyUniqueAppName  -g MyResourceGroup -c MyConsumptionPlan -s MyStorgeAccount --is-linux 
"""
