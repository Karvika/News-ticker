from flask import Flask, jsonify
from flask_cors import CORS
from agent import NewsUpdateTool

app = Flask(__name__)
CORS(app)

news_tool = NewsUpdateTool()

@app.route('/api/news')
def get_news():
    news_json = news_tool.execute()
    return news_json, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)
