from flask import Flask, render_template, request, make_response
import ssl
import requests

src = "service-a"
src_port = 7443
des = "service-b"
des_port = 8443

app = Flask(__name__)

config = {
    "DEBUG": True  # run app in debug mode
}

app.config.from_mapping(config)

@app.route('/')
def hello():
    response = make_response(f'Hello from "{src}"', 200)
    response.mimetype = "text/plain"
    return response

@app.route('/w-mtls')
def withMTLS():
    try:
      result = requests.get(f'https://{des}.example.com:{des_port}',
        cert=(f'../cert/{src}.crt', f'../cert/{src}.key'),
        verify='../cert/ca.crt')
      print(result)
      msg = result.text

    except requests.exceptions.RequestException as e:
      msg = str(e)

    response = make_response(msg, 200)
    response.mimetype = "text/plain"
    return response

@app.route('/wo-cert-mtls')
def withOutCertMTLS():
    try:
      result = requests.get(f'https://{des}.example.com:{des_port}', 
                            verify='../cert/ca.crt')
      print(result)
      msg = result.text

    except requests.exceptions.RequestException as e:
      msg = str(e)

    response = make_response(msg, 200)
    response.mimetype = "text/plain"
    return response

@app.route('/wo-ca-mtls')
def withOutCAMTLS():
    try:
      result = requests.get(f'https://{des}.example.com:{des_port}',
                            cert=(f'../cert/{src}.crt', f'../cert/{src}.key'))
      print(result)
      msg = result.text

    except requests.exceptions.RequestException as e:
      msg = str(e)

    response = make_response(msg, 200)
    response.mimetype = "text/plain"
    return response
            
if __name__ == "__main__":
    app.debug = True
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='../cert/ca.crt')
    ssl_context.load_cert_chain(certfile=f'../cert/{src}.crt', keyfile=f'../cert/{src}.key', password='')
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    app.run(host="0.0.0.0", port=src_port, ssl_context=ssl_context, use_reloader=True, extra_files=[f'../cert/{src}.crt'])
