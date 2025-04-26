import boto3

def extract_text_from_pdf(file_path):
    textract = boto3.client('textract')
    with open(file_path, 'rb') as document:
        response = textract.analyze_document(
            Document={'Bytes': document.read()},
            FeatureTypes=["FORMS"]
        )
    
    lines = []
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])

    return "\n".join(lines)
