from datetime import datetime
from flask import Flask, request
from OpenSSL import crypto
import os
import requests
from reportlab.pdfgen import canvas
import boto3

s3 = boto3.client('s3')
bucket_name = "cyclic-cute-puce-colt-tutu-sa-east-1"

app = Flask(__name__)

folder = './output'

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

        local_file = f'{folder}/pfx_{current_date_time}'

        os.makedirs(folder, exist_ok=True)

        local_filename = transform_pfx_in_pdf(pfx_file_url, local_file)

        output_file = f'{local_file}.pdf'

        generate_key_and_sign(local_filename, pfx_password, output_file)

        return 'Signature generated successfully!', 200
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
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    pfx = crypto.load_pkcs12(pfx_data, password)

    private_key = pfx.get_privatekey()
    certificate = pfx.get_certificate()

    return private_key, certificate

def create_pdf(signature, output_file):
    c = canvas.Canvas(output_file)

    for i, (key, value) in enumerate(signature.items()):
        c.drawString(100, 800 - i * 100, f'{key}: {value}')

    c.save()

    with open(output_file, "rb") as f:
        s3.put_object(Body=f.read(), Bucket=bucket_name, Key=output_file)

def generate_key_and_sign(pfx_path, password, output_file):
    private_key, certificate = load_certificate_and_key(pfx_path, password)

    signature = {
        'name/cpf': certificate.get_subject().CN,
        'type': certificate.get_subject().OU,
        'bir': certificate.get_subject().O,
        'address': certificate.get_subject().L,
        'signature_text': certificate.get_subject().ST
    }

    create_pdf(signature, output_file)

if __name__ == '__main__':
    app.run(debug=True)
