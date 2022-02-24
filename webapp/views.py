from webapp import app


@app.route('/', methods=['GET'])
def home():
    return 'Hello World!'
