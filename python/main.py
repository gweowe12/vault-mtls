from flask import Flask, render_template, request, make_response
import ssl
import requests

app = Flask(__name__)

config = {
    "DEBUG": True  # run app in debug mode
}

app.config.from_mapping(config)

@app.route('/')
def hello():
    response = make_response(f'Hello World!', 200)
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    app.debug = True
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='../cert/ca.crt')
    ssl_context.load_cert_chain(certfile=f'../cert/server.crt', keyfile=f'../cert/server.key')
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    app.run(host="0.0.0.0", port=8443, ssl_context=ssl_context, use_reloader=True, extra_files=[f'../cert/server.crt'])
