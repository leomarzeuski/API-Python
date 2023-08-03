from endesive import pdf
from OpenSSL import crypto

def load_certificate_and_key(pfx_path, password):
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    pfx = crypto.load_pkcs12(pfx_data, password)

    private_key = pfx.get_privatekey()
    certificate = pfx.get_certificate()

    return private_key, certificate

def sign_pdf(input_pdf_path, output_pdf_path, private_key, certificate):
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

    # Sign the PDF
    datau = open(input_pdf_path, "rb").read()
    datas = pdf.cms.sign(datau, dct,
                         private_key,
                         certificate,
                         [],
                         "sha256")
    with open(output_pdf_path, "wb") as fp:
        fp.write(datau)
        fp.write(datas)

# Use the function to sign a PDF
private_key, certificate = load_certificate_and_key("certificate.pfx", "password")
sign_pdf("input.pdf", "output.pdf", private_key, certificate)
