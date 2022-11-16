from flask import Flask, jsonify, request
app = Flask(__name__)

import index_builder

@app.route('/query/', methods = ['POST'])
def query():
    #access your DB get your results here
    data = request.get_json()
    data = index_builder.handle_query(data['query'])
    return jsonify(data)

if __name__ == '__main__':
    port = 8000 #the custom port you want
    #app.run(host='0.0.0.0', port=port)
    
    # TODO (Caleb): Flask and Metapy do not like each other. Metapy hangs when ranker.score() is called while the
    # Flask app is running.

    #app.run(host='127.0.0.1', port=port, debug=True)

    #index_builder.handle_query("test")