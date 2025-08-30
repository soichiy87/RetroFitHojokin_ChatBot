import google.generativeai as genai
import os

# apikey.txt からAPIキーを読み込む
API_KEY_FILE = os.path.join(os.path.dirname(__file__), 'apikey.txt')
try:
    with open(API_KEY_FILE, 'r') as f:
        GEMINI_API_KEY = f.read().strip()
    genai.configure(api_key=GEMINI_API_KEY)
except FileNotFoundError:
    print(f"Error: {API_KEY_FILE} not found. Please create it with your Gemini API key.")
    GEMINI_API_KEY = None
except Exception as e:
    print(f"Error reading API key from {API_KEY_FILE}: {e}")
    GEMINI_API_KEY = None

if GEMINI_API_KEY:
    print("利用可能なGeminiモデル:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  モデル名: {m.name}")
            print(f"  説明: {m.description}")
            print(f"  入力トークン制限: {m.input_token_limit}")
            print(f"  出力トークン制限: {m.output_token_limit}")
            print(f"  サポートされている生成メソッド: {m.supported_generation_methods}")
            print("-" * 30)
else:
    print("APIキーが設定されていないため、モデルリストを取得できません。")