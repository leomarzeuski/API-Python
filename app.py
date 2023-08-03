from flask import Flask, request, jsonify
from endesive import pdf
from OpenSSL import crypto
import requests
import tempfile
import os
import boto3

app = Flask(__name__)

s3 = boto3.client('s3')
bucket_name = 'your_bucket_name'

def load_certificate_and_key(pfx_path, password):
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    pfx = crypto.load_pkcs12(pfx_data, password)

    private_key = pfx.get_privatekey()
    certificate = pfx.get_certificate()

    return private_key, certificate

@app.route('/sign', methods=['POST'])
def sign_document():
    # Get the URL of the document to sign and the private key from the request
    document_url = request.form.get('document_url')
    pfx_password = request.form.get('pfx_password')

    # Download the document
    response = requests.get(document_url)
    document = response.content

    # Create a temporary file to store the document
    document_file = tempfile.NamedTemporaryFile(delete=False)
    document_file.write(document)
    document_file.close()

    # Load the certificate and key
    private_key, certificate = load_certificate_and_key(document_file.name, pfx_password)

    # Define the signature dictionary
    dct = {
        "sigflags": 3,
        "contact": "mak@trisoft.com.pl",
        "location": "Szczecin",
        "signingdate": "20180731082642",
        "reason": "Dokument podpisany cyfrowo",
        "signature": "Dokument podpisany cyfrowo",
        "signaturebox": (0, 0, 0, 0),
    }

    # Sign the document using endesive
    datau = open(document_file.name, "rb").read()
    datas = pdf.cms.sign(datau, dct,
                         private_key,
                         certificate,
                         [],
                         "sha256")

    # Delete the temporary file
    os.unlink(document_file.name)

    # Save the signed document to a temporary file
    signed_document_file = tempfile.NamedTemporaryFile(delete=False)
    signed_document_file.write(datau)
    signed_document_file.write(datas)
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
