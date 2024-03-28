from flask import Flask, request, make_response
from flask_cors import CORS
from assistant import handle_user_query

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST', 'OPTIONS'])
def query():
    if request.method == 'OPTIONS':
        print("flight")
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Assuming the content is text/plain, read it
    text_data = request.data.decode('utf-8')
    response_text = handle_user_query(text_data)
    return response_text, 200

if __name__ == '__main__':
    app.run(port=8000, debug=True)
