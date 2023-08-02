from flask import Flask, request, send_file
from endesive import pdf
import requests
import tempfile
import os

app = Flask(__name__)

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

    # Return the signed document as a file download
    return send_file(signed_document, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
