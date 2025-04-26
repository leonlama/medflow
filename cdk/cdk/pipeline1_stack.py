from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from constructs import Construct

class Pipeline1Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 Bucket
        uploads_bucket = s3.Bucket(self, "MedflowUploadsBucket",
                                   removal_policy=RemovalPolicy.DESTROY,
                                   auto_delete_objects=True)

        # DynamoDB Table
        patient_table = ddb.Table(
            self, "PatientTable",
            partition_key={"name": "patient_id", "type": ddb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY,
        )

        # SNS Topic for Textract notifications
        textract_topic = sns.Topic(self, "TextractNotificationTopic")

        # Role for Textract to publish to SNS
        textract_service_role = iam.Role(
            self, "TextractServiceRole",
            assumed_by=iam.ServicePrincipal("textract.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess")
            ]
        )

        # Explicitly limit access to just our SNS topic (optional but best practice)
        textract_topic.grant_publish(textract_service_role)

        # Lambda: Clean Handler
        self.clean_handler = _lambda.Function(
            self, "CleanHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="clean_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": uploads_bucket.bucket_name,
                "TABLE_NAME": patient_table.table_name,
                "TEXTRACT_ROLE_ARN": textract_service_role.role_arn,
            }
        )

        # Lambda: Textract Completion Handler
        textract_complete_handler = _lambda.Function(
            self, "TextractCompleteHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="pipeline1.handlers.textract_complete_handler.lambda_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_DAY,
            environment={
                "PATIENT_TABLE": patient_table.table_name
            }
        )

        # Assign AWSLambdaBasicExecutionRole to Textract Completion Handler
        textract_complete_handler.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
        )

        # ➡️ Add explicit permission to read Textract results
        textract_complete_handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["textract:GetDocumentAnalysis"],
                resources=["*"]
            )
        )

        # Lambda: Search Patients Handler
        search_patients_handler = _lambda.Function(
            self, "SearchPatientsHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="pipeline1.handlers.search_patients_handler.lambda_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_DAY,
            environment={
                "PATIENT_TABLE": patient_table.table_name
            }
        )

        # Permissions
        uploads_bucket.grant_read_write(self.clean_handler)
        patient_table.grant_read_write_data(self.clean_handler)
        patient_table.grant_read_write_data(textract_complete_handler)
        patient_table.grant_read_data(search_patients_handler)
        textract_topic.add_subscription(subs.LambdaSubscription(textract_complete_handler))

        # API Gateway setup
        api = apigw.RestApi(
            self, "MedflowAPI",
            rest_api_name="MedflowAPI",
            binary_media_types=["multipart/form-data"],  # ✅ Allow binary uploads
            default_cors_preflight_options=apigw.CorsOptions(  # ✅ Global CORS config
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,  # allow POST, GET, OPTIONS etc.
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
            )
        )

        api.root.add_resource("clean").add_method(
            "POST",
            apigw.LambdaIntegration(self.clean_handler)
        )

        health = api.root.add_resource("health")
        health.add_method("GET", apigw.LambdaIntegration(self.clean_handler))

        # API Gateway: /patients GET
        patients = api.root.add_resource("patients")
        patients.add_method("GET", apigw.LambdaIntegration(search_patients_handler))
