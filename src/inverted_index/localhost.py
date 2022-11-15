from flask import Flask, jsonify, request
app = Flask(__name__)

import index_builder

@app.route('/query', methods = ['POST'])
def query():
    #access your DB get your results here
    json = request.get_json()
    data = index_builder.handle_query(json['query'])
    return jsonify(data)
if __name__ == '__main__':
    port = 8000 #the custom port you want
    app.run(host='0.0.0.0', port=port)