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

youkou_content = read_file_content(YOUKOU_FILE)
tebiki_content = read_file_content(TEBIKI_FILE)

# APIキーを環境変数から読み込む
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Error: GEMINI_API_KEY environment variable not set.")
    # 環境変数が設定されていない場合の処理をここに記述
    # 例: アプリケーションを終了させる、エラーメッセージを表示するなど
    # デプロイ環境では必須なので、設定されていない場合は動作しないようにするのが一般的です。


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
    # 開発環境でのみ実行されるように変更
    # RenderではGunicornがアプリを起動するため、この行はデプロイ時には実行されません。
    # app.run(debug=True)
    pass