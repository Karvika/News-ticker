from flask import Flask, jsonify
from flask_cors import CORS
from agent import real_news_tool_instance

app = Flask(__name__)
CORS(app)

@app.route('/api/news')
def get_news():
    news_json = real_news_tool_instance.execute()
    return news_json, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)
