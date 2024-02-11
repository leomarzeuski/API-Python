import requests

# Parâmetros de exemplo que você gostaria de adicionar à URL
parametros_url = {'param1': 'valor1', 'param2': 'valor2'}

# URL do seu serviço Flask hospedado no Cyclic, com parâmetros de query string
url_do_servico = 'https://lazy-erin-snail-gown.cyclic.app/sign'
url_com_parametros = requests.Request('POST', url_do_servico, params=parametros_url).prepare().url

# Substitua estes placeholders pelos valores reais
pfx_file_url = 'https://seuservidor.com/caminho/para/seu/arquivo.pfx'
pfx_password = 'senhaDoPFX'
pdf_url = 'https://seuservidor.com/caminho/para/o/documento.pdf'

# Preparando os dados para enviar na solicitação POST
dados = {
    'pfx_file_url': pfx_file_url,
    'pfx_password': pfx_password,
    'pdf_url': pdf_url
}

# Realizando a solicitação POST
response = requests.post(url_com_parametros, json=dados)

# Verificando a resposta
if response.status_code == 200:
    print("Sucesso:", response.json())
else:
    print("Erro:", response.status_code, response.text)
