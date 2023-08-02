from flask import Flask, request, jsonify
from endesive import pdf
import requests
import tempfile
import os
import boto3

app = Flask(__name__)

s3 = boto3.client('s3')
bucket_name = 'cyclic-lazy-erin-snail-gown-sa-east-1'

@app.route('/sign', methods=['POST'])
def sign_document():
    # Get the URL of the document to sign and the private key from the request
    document_url = request.form.get('document_url')
    private_key = request.form.get('private_key')

    # Download the document
    response = requests.get(document_url)
    document = response.content

    # Create a temporary file to store the document
    document_file = tempfile.NamedTemporaryFile(delete=False)
    document_file.write(document)
    document_file.close()

    # Sign the document using endesive
    dct = {
        "sigflags": 3,
        "contact": "mak@trisoft.com.pl",
        "location": "Szczecin",
        "signingdate": "20180731082642",
        "reason": "Dokument podpisany cyfrowo",
        "signature": "Dokument podpisany cyfrowo",
        "signaturebox": (0, 0, 0, 0),
    }
    signed_document = pdf.cms.sign(document_file.name, dct,
                                   private_key,
                                   None,
                                   [],
                                   "sha256")

    # Delete the temporary file
    os.unlink(document_file.name)

    # Save the signed document to a temporary file
    signed_document_file = tempfile.NamedTemporaryFile(delete=False)
    signed_document_file.write(signed_document)
    signed_document_file.close()

    # Upload the signed document to S3
    with open(signed_document_file.name, 'rb') as data:
        s3.upload_fileobj(data, bucket_name, 'signed_document.pdf')

    # Delete the temporary file
    os.unlink(signed_document_file.name)

    # Construct the URL of the signed document
    url = f'https://{bucket_name}.s3.amazonaws.com/signed_document.pdf'

    # Return the URL of the signed document
    return jsonify({'url': url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
