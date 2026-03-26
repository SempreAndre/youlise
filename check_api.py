import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERRO: A variável de ambiente GEMINI_API_KEY não foi encontrada. Configure o arquivo .env.")
    exit(1)

genai.configure(api_key=api_key)

print("--- Modelos Disponíveis para Geração de Texto ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Nome: {m.name}")