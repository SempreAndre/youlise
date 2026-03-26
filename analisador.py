import google.generativeai as genai
import os

from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO ---
# Trazendo chave do ambiente
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERRO: A variável de ambiente GEMINI_API_KEY não foi encontrada. Configure o arquivo .env.")
    exit(1)

genai.configure(api_key=api_key)

# Inicializando o modelo (o Gemini Pro é ótimo para texto)
model = genai.GenerativeModel('models/gemini-2.5-flash') 

def carregar_comentarios(nome_arquivo):
    """Lê o arquivo de texto gerado pelo coletor"""
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return None

def analisar_comentarios(texto_comentarios):
    """Envia os dados para o Gemini processar"""
    
    print("\n--- Enviando para o Gemini (aguarde)... ---")
    
    # Aqui está o "segredo": Engenharia de Prompt para guiar a IA
    prompt = f"""
    Você é um assistente de análise de dados especializado em feedback de usuários.
    Analise os seguintes comentários extraídos de um vídeo do YouTube e gere um relatório estruturado.
    
    O relatório deve conter:
    1. **Sentimento Geral**: (Defina se a maioria é Positiva, Negativa ou Neutra e dê uma porcentagem estimada).
    2. **Principais Tópicos**: (Liste os 3 assuntos mais falados).
    3. **Destaques**: (Resuma o que os usuários mais gostaram ou reclamaram).
    4. **Sugestão de Ação**: (Com base no feedback, o que o criador do vídeo deveria fazer no próximo?).

    DADOS DOS COMENTÁRIOS:
    {texto_comentarios}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na análise: {e}"

# --- FLUXO PRINCIPAL ---
print("Arquivos disponíveis na pasta:")
# Lista apenas arquivos .txt para facilitar
arquivos_txt = [f for f in os.listdir() if f.endswith('.txt')]
for f in arquivos_txt:
    print(f" - {f}")

arquivo_escolhido = input("\nDigite o nome do arquivo para analisar (ou copie da lista acima): ")

conteudo = carregar_comentarios(arquivo_escolhido)

if conteudo:
    resultado = analisar_comentarios(conteudo)
    print("\n" + "="*40)
    print("RELATÓRIO DE ANÁLISE DO GEMINI")
    print("="*40 + "\n")
    print(resultado)