import os
import re # Biblioteca para expressões regulares (limpeza de texto)
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO ---
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    print("ERRO: A variável de ambiente YOUTUBE_API_KEY não foi encontrada. Configure o arquivo .env.")
    exit(1)
youtube = build('youtube', 'v3', developerKey=api_key)

def extrair_id(url):
    """Extrai o ID do vídeo de URLs comuns ou Shorts"""
    parsed_url = urlparse(url)
    if "/shorts/" in parsed_url.path:
        return parsed_url.path.split("/shorts/")[1]
    if "v" in parse_qs(parsed_url.query):
        return parse_qs(parsed_url.query)["v"][0]
    if parsed_url.netloc == "youtu.be":
        return parsed_url.path[1:]
    return url 

def obter_titulo_video(video_id):
    """Busca o título do vídeo para nomear o arquivo"""
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            return "video_desconhecido"
            
        titulo_original = response['items'][0]['snippet']['title']
        
        # Limpa caracteres proibidos em nomes de arquivos do Windows/Linux (\ / : * ? " < > |)
        titulo_limpo = re.sub(r'[\\/*?:"<>|]', "", titulo_original)
        
        # Limita o tamanho do nome para evitar erros (máximo 50 caracteres)
        return titulo_limpo[:50].strip()
        
    except Exception as e:
        print(f"Erro ao obter título: {e}")
        return "erro_no_titulo"

def salvar_comentarios(video_id, max_resultados=50):
    titulo_video = obter_titulo_video(video_id)
    nome_arquivo = f"coments_{titulo_video}.txt"
    
    print(f"--- Iniciando coleta para: {titulo_video} ---")

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_resultados,
            textFormat="plainText"
        )
        response = request.execute()

        # Abre o arquivo para escrita (encoding='utf-8' é vital para emojis e acentos)
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            
            # Cabeçalho do arquivo para dar contexto à IA depois
            f.write(f"VÍDEO ID: {video_id}\n")
            f.write(f"TÍTULO: {titulo_video}\n")
            f.write("-" * 50 + "\n\n")

            count = 0
            for item in response.get('items', []):
                comentario = item['snippet']['topLevelComment']['snippet']
                autor = comentario['authorDisplayName']
                texto = comentario['textDisplay']
                
                # Escreve no arquivo formatado
                f.write(f"AUTOR: {autor}\n")
                f.write(f"COMENTÁRIO: {texto}\n")
                f.write("-" * 30 + "\n")
                count += 1
        
        print(f"Sucesso! {count} comentários salvos em: {nome_arquivo}")
        return nome_arquivo

    except Exception as e:
        print(f"Erro: {e}")
        return None

# --- EXECUÇÃO ---
url = input("Cole a URL do vídeo ou Shorts: ")
id_video = extrair_id(url)
arquivo_gerado = salvar_comentarios(id_video)