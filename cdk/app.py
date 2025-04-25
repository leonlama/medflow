#!/usr/bin/env python3
import aws_cdk as cdk
from cdk.pipeline1_stack import Pipeline1Stack

app = cdk.App()
Pipeline1Stack(app, "Pipeline1Stack")
app.synth()
