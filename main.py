# main.py
from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai # この行を追加

app = Flask(__name__)

# Function to read file content
def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

# Load the data from youkou.txt and tebiki.txt
# Assuming these files are in the same directory as main.py
YOUKOU_FILE = os.path.join(os.path.dirname(__file__), 'youkou.txt')
TEBIKI_FILE = os.path.join(os.path.dirname(__file__), 'tebiki.txt')
API_KEY_FILE = os.path.join(os.path.dirname(__file__), 'apikey.txt') # この行を追加

youkou_content = read_file_content(YOUKOU_FILE)
tebiki_content = read_file_content(TEBIKI_FILE)

# APIキーをファイルから読み込む
try:
    with open(API_KEY_FILE, 'r') as f:
        GEMINI_API_KEY = f.read().strip()
    genai.configure(api_key=GEMINI_API_KEY) # この行を修正
except FileNotFoundError:
    print(f"Warning: {API_KEY_FILE} not found. Please create it with your Gemini API key.")
    GEMINI_API_KEY = None
except Exception as e:
    print(f"Error reading API key from {API_KEY_FILE}: {e}")
    GEMINI_API_KEY = None

# Combine the content for RAG context
# For a simple prototype, we'll pass all content as context.
# For larger documents, more sophisticated chunking and retrieval would be needed.
RAG_CONTEXT = f"""
以下の情報は、補助金に関する要綱と手引きです。
--- 要綱 (youkou.txt) ---
{youkou_content}

--- 手引き (tebiki.txt) ---
{tebiki_content}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"response": "メッセージがありません。"}), 400

    # Construct the prompt for the LLM
    # The LLM (Gemini) will act as the RAG generation component
    prompt = f"""
あなたは補助金に関する質問に答えるチャットボットです。
以下の「補助金情報」を参考に、ユーザーの質問に正確に答えてください。
補助金情報に記載されていない内容については、「補助金情報には記載がありません」と答えてください。

--- 補助金情報 ---
{RAG_CONTEXT}

--- ユーザーの質問 ---
{user_message}

--- 回答 ---
"""

    # LLM API呼び出し部分を有効化
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            response_text = model.generate_content(prompt).text
        except Exception as e:
            response_text = f"LLMからの応答エラー: {e}"
    else:
        response_text = "APIキーが設定されていないため、LLMからの応答はできません。"

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)