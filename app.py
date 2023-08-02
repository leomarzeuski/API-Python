import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from sign_pdf import generate_key_and_sign, load_certificate_and_key

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('form.html')


@app.route('/sign', methods=['POST'])
def sign():
    # Processar o arquivo de certificado carregado
    pfx_file = request.files['pfx_file']
    pfx_filename = secure_filename(pfx_file.filename)
    pfx_path = os.path.join('./pfx', pfx_filename)
    pfx_file.save(pfx_path)

    # Substitua pela senha correta para o arquivo PKCS#12
    password = request.form['password']

    # Definir o caminho do arquivo de saída
    output_dir = './output'
    # Cria o diretório se ele não existir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{pfx_filename}.pdf')

    generate_key_and_sign(pfx_path, password, output_file)

    return 'Signature generated successfully!'


if __name__ == '__main__':
    app.run(debug=True)
