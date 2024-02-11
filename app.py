import requests

# URL base do serviço que assina o documento
base_url = "https://lazy-erin-snail-gown.cyclic.app/sign"

# Parâmetros de query string que você quer enviar
params = {
    'pfx_file_url': 'https://6ca3c31cd443b8133af7226009438b05.cdn.bubble.io/f1690373284903x746653125219639200/22172649.pfx',
    'pfx_password': '123456',
    'pdf_url': 'https://6ca3c31cd443b8133af7226009438b05.cdn.bubble.io/f1691518862230x245229468668821700/Laudo-Lepanto-08-08-23.pdf'
}

# Monta a URL completa com os parâmetros de query string
full_url = requests.Request('POST', base_url, params=params).prepare().url

# Enviar solicitação POST
response = requests.post(full_url)

# Verificar a resposta
if response.ok:
    print('Sucesso:', response.json())
    # Aqui você pode adicionar código para manipular o documento retornado
else:
    print('Erro:', response.status_code, response.text)
