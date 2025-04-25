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

        # Lambda: Upload Handler
        upload_handler = _lambda.Function(
            self, "UploadHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="pipeline1.handlers.upload_handler.lambda_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_DAY,
            environment={
                "UPLOAD_BUCKET": uploads_bucket.bucket_name,
                "PATIENT_TABLE": patient_table.table_name,
                "SNS_TOPIC_ARN": textract_topic.topic_arn,
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

        # Permissions
        uploads_bucket.grant_read_write(upload_handler)
        patient_table.grant_read_write_data(upload_handler)
        patient_table.grant_read_write_data(textract_complete_handler)
        textract_topic.grant_publish(upload_handler)
        textract_topic.add_subscription(subs.LambdaSubscription(textract_complete_handler))

        upload_handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "textract:StartDocumentTextDetection"
                ],
                resources=["*"]
            )
        )

        # API Gateway setup
        api = apigw.RestApi(
            self, "MedflowAPI",
            rest_api_name="MedflowAPI",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["POST", "OPTIONS", "GET"]
            )
        )

        clean = api.root.add_resource("clean")
        clean.add_method("POST", apigw.LambdaIntegration(upload_handler))

        health = api.root.add_resource("health")
        health.add_method("GET", apigw.LambdaIntegration(upload_handler))
