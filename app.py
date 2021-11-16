"""
IAC to deploy TechChallenge Application
"""

#!/usr/bin/env python3
import os
from aws_cdk import core
from cdk_stacks.network import NetworkStack

from cdk_stacks.application import (
    AppStackProperties,
    AppStack
)

env=core.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

environment_name = "dev"
tags = [
    ['Application', 'TechChallengeApp'],
    ['Environment', environment_name.capitalize()],
    ['Department', 'Recruitment'],
    ['Organization', 'Servian']
]


app = core.App()

network_stack = NetworkStack(app, f"TechChallengeAppNetwork{environment_name.capitalize()}")

app_config = AppStackProperties(
    vpc=network_stack.vpc,
    load_balancer=network_stack.load_balancer
)

site_none_stack = AppStack(
    app, f"TechChallengeAppPlatform{environment_name.capitalize()}",
    properties=app_config
)

# default tagging of all stacks
for stack in [network_stack, site_none_stack]:
    for ix in tags:
        core.Tags.of(stack).add(ix[0], ix[1])

core.Tags.of(site_none_stack).add("Customer", "Servian-Cloud-Engineering")

app.synth()
