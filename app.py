import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

import os
from dotenv import load_dotenv

load_dotenv()

# --- SUAS CHAVES (Carregadas via .env) ---
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not YOUTUBE_KEY or not GEMINI_KEY:
    st.error("Chaves de API ausentes. Configure o arquivo .env com YOUTUBE_API_KEY e GEMINI_API_KEY.")
    st.stop()

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="YOUlise", page_icon="🎬", layout="centered")

import base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

bg_base64 = get_base64_of_bin_file('assets/bg.png')

custom_style = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .stMarkdown, .stText, p, label {{
                text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
            }}
            h1, h2, h3 {{
                text-shadow: 2px 2px 5px rgba(0,0,0,0.9);
            }}
            .stTextInput > div > div > input {{
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border: 1px solid #c0a062;
            }}
            h3 {{
                color: #e2c27b !important;
            }}
            </style>
            """
st.markdown(custom_style, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🎬 YOUlise</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>Uma nova forma de analisar videos no youtube</h3>", unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO (MEMÓRIA DO APP) ---
# Isso garante que o app não "esqueça" os dados quando ela fizer uma pergunta
if "comentarios_cache" not in st.session_state:
    st.session_state["comentarios_cache"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --- FUNÇÕES ---

# 1. Extração de ID
def extrair_id(url):
    if not url: return None
    parsed_url = urlparse(url)
    if "/shorts/" in parsed_url.path:
        return parsed_url.path.split("/shorts/")[1]
    if "v" in parse_qs(parsed_url.query):
        return parse_qs(parsed_url.query)["v"][0]
    if parsed_url.netloc == "youtu.be":
        return parsed_url.path[1:]
    return url 

# 2. Busca no YouTube (COM CACHE)
# O @st.cache_data faz o Streamlit lembrar do resultado se o video_id for o mesmo
@st.cache_data(show_spinner=False)
def buscar_comentarios(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
        request = youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=100, textFormat="plainText"
        )
        response = request.execute()
        comentarios = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response.get('items', [])]
        return "\n".join(comentarios)
    except Exception as e:
        return None

# 3. Análise Inicial (Resumo)
@st.cache_data(show_spinner=False)
def gerar_resumo_inicial(texto_comentarios):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash') 
        prompt = f"""
        Analise estes comentários do YouTube e faça um resumo simples e direto.
        Responda em Tópicos com emojis.
        
        1. O que estão elogiando? 🥰
        2. O que estão reclamando? 😡
        3. Qual a "vibe" geral?
        
        COMENTÁRIOS:
        {texto_comentarios}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# 4. Função do Chat (Perguntas Específicas)
def perguntar_ao_chat(pergunta_usuario, contexto_comentarios):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_chat = f"""
    Você é um assistente analisando comentários de um vídeo.
    Use APENAS o contexto abaixo para responder a pergunta do usuário.
    Se a informação não estiver nos comentários, diga que não encontrou.

    CONTEXTO DOS COMENTÁRIOS:
    {contexto_comentarios}

    PERGUNTA DO USUÁRIO:
    {pergunta_usuario}
    """
    try:
        response = model.generate_content(prompt_chat)
        return response.text
    except Exception as e:
        return "Desculpe, tive um erro ao processar a pergunta."

# --- INTERFACE ---

url_video = st.text_input("Link do Youtube:", placeholder="Cole o link e aperte Enter ou clique em Analisar")
botao_analisar = st.button("✨ Analisar Agora")

# Lógica Principal
if botao_analisar and url_video:
    id_video = extrair_id(url_video)
    
    with st.spinner('Baixando comentários... ☕'):
        comentarios = buscar_comentarios(id_video)
        
        if comentarios:
            # Salva na memória para o chat usar depois
            st.session_state["comentarios_cache"] = comentarios
            # Limpa o histórico de chat anterior se for um vídeo novo
            st.session_state["chat_history"] = [] 
            
            with st.spinner('Gerando resumo... 🧠'):
                resumo = gerar_resumo_inicial(comentarios)
                st.session_state["resumo_atual"] = resumo # Salva o resumo
        else:
            st.error("Erro ao ler comentários. Verifique o link.")

# --- EXIBIÇÃO DO RESUMO ---
if "resumo_atual" in st.session_state and st.session_state["comentarios_cache"]:
    st.markdown("### 📊 Relatório Inicial")
    st.markdown(st.session_state["resumo_atual"])
    st.markdown("---")
    
    # --- ÁREA DE CHAT (PERGUNTAS) ---
    st.markdown("### 💬 Tire suas dúvidas sobre os comentários")
    st.write("Exemplos: 'Alguém reclamou do áudio?', 'Falaram sobre o preço?', 'Quais dúvidas apareceram?'")

    # Exibe o histórico da conversa
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Campo para ela digitar a pergunta
    if prompt := st.chat_input("Pergunte algo sobre os comentários..."):
        # 1. Mostra a pergunta dela na tela
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # 2. IA processa a resposta usando o contexto salvo
        with st.chat_message("assistant"):
            with st.spinner("Lendo os comentários novamente..."):
                resposta = perguntar_ao_chat(prompt, st.session_state["comentarios_cache"])
                st.markdown(resposta)
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})