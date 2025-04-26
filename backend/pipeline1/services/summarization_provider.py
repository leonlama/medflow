import boto3
import json

prompt_template = """
Extract the following fields from the form text:

- patient_name
- patient_id (if any)
- date_of_birth
- symptoms
- diagnosis
- insurance_info
- address
- contact_info

Return a valid JSON structure.

Form text:
{{form_text}}
"""

def summarize_text(form_text):
    bedrock = boto3.client('bedrock-runtime')

    prompt = prompt_template.replace("{{form_text}}", form_text)

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "prompt": prompt,
            "temperature": 0.3,
            "max_tokens_to_sample": 500
        }),
        accept="application/json",
        contentType="application/json"
    )

    body = json.loads(response['body'].read())
    text = body.get('completion', "{}")

    return json.loads(text)
