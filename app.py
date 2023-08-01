from datetime import datetime
from flask import Flask, request, jsonify
from OpenSSL import crypto
import os
import requests
from endesive import pdf
import boto3

s3 = boto3.client('s3')
bucket_name = "cyclic-weak-pear-pig-tux-sa-east-1"

app = Flask(__name__)

folder = '/tmp'

def set_current_date_time():
    current_datetime = datetime.now()
    current_date_time = current_datetime.strftime("%Y%m%d_%H%M%S")
    return current_date_time

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    try:
        if request.method == 'POST':
            data = request.get_json()
            pfx_file_url = data.get('pfx_file_url')
            pfx_password = data.get('pfx_password')
        else:
            pfx_file_url = request.args.get('pfx_file_url')
            pfx_password = request.args.get('pfx_password')

        if not pfx_file_url:
            return 'pfx_file_url is required', 400

        if not pfx_password:
            return 'pfx_password is required', 400

        current_date_time = set_current_date_time()

        local_file = f'/tmp/pfx_{current_date_time}'

        os.makedirs(folder, exist_ok=True)

        local_filename = transform_pfx_in_pdf(pfx_file_url, local_file)

        output_file = f'{local_file}.pdf'

        signature = generate_key_and_sign(local_filename, pfx_password, output_file)

        return jsonify({'message': 'Signature generated successfully!', 'signature': signature}), 200
    except Exception as e:
        app.logger.error(f'Error: {e}')
        return str(e), 500

def transform_pfx_in_pdf(pfx_file_url, local_file):
    local = f'{local_file}.pfx'
    download_file(pfx_file_url, local)
    return local

def download_file(url, local_filename):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        s3.put_object(Body=response.content, Bucket=bucket_name, Key=local_filename)


def load_certificate_and_key(pfx_path, password):
    # Get the PFX file from S3
    pfx_file = s3.get_object(Bucket=bucket_name, Key=pfx_path)
    pfx_data = pfx_file['Body'].read()

    pfx = crypto.load_pkcs12(pfx_data, password)

    private_key = pfx.get_privatekey()
    certificate = pfx.get_certificate()

    return private_key, certificate

#teste
def generate_key_and_sign(pfx_path, password, output_file):
    private_key, certificate = load_certificate_and_key(pfx_path, password)

    # Create an empty PDF
    c = canvas.Canvas(output_file)
    c.save()

    # Sign the PDF
    with open(output_file, "rb+") as f:
        pdf.sign(datau=f.read(),
                 udct={"sigflags": 3},
                 key=private_key,
                 cert=certificate,
                 othercerts=[],
                 algomd="sha256",
                 hsm=None,
                 password=password,
                 efitz=None,
                 name=certificate.get_subject().CN,
                 location=certificate.get_subject().L,
                 reason=certificate.get_subject().ST,
                 contact=certificate.get_subject().emailAddress,
                 signerflags=pdf.fpdf.PDF_SIGNER_CERTIFICATE)

    # Upload the signed PDF to S3
    with open(output_file, "rb") as f:
        s3.put_object(Body=f.read(), Bucket=bucket_name, Key=output_file)

    signature = {
        'id': str(certificate.get_serial_number()),  # Add the certificate ID
        'name/cpf': certificate.get_subject().CN,
        'type': certificate.get_subject().OU,
        'bir': certificate.get_subject().O,
        'address': certificate.get_subject().L,
        'signature_text': certificate.get_subject().ST
    }

    return signature  # Return the signature


if __name__ == '__main__':
    app.run(debug=True)
