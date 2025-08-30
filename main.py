# main.py
from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai

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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(f"DEBUG: GOOGLE_API_KEY loaded: {bool(GOOGLE_API_KEY)}")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    # アプリケーションの起動は続けるが、LLM呼び出し時にエラーを返す
    pass


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
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            print("DEBUG: LLM initialized successfully.")
            response_text = model.generate_content(prompt).text
            print(f"DEBUG: LLM response received: {response_text[:50]}...")
        except Exception as e:
            response_text = f"LLMからの応答エラー: {e}"
            print(f"DEBUG: Error during LLM invocation: {e}")
    else:
        response_text = "APIキーが設定されていないため、LLMからの応答はできません。"
    

    # LLM API呼び出し部分を有効化
    if GOOGLE_API_KEY:
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key=GOOGLE_API_KEY)
            print("DEBUG: LLM initialized successfully.")
            chain = prompt_template | llm | StrOutputParser()
            response_text = chain.invoke({"user_message": user_message, "RAG_CONTEXT": RAG_CONTEXT})
            print(f"DEBUG: LLM response received: {response_text[:50]}...")
        except Exception as e:
            response_text = f"LLMからの応答エラー: {e}"
            print(f"DEBUG: Error during LLM invocation: {e}")
    else:
        response_text = "APIキーが設定されていないため、LLMからの応答はできません。"

    return jsonify({"response": response_text})

