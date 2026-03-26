# YOUlise - Analisador de Comentários do YouTube

O **YOUlise** é uma aplicação que extrai e analisa comentários de vídeos e Shorts do YouTube utilizando inteligência artificial. Com ele, você pode entender rapidamente o sentimento do público (elogios, reclamações, "vibe" geral) e interagir em um chat para fazer perguntas específicas sobre o que os usuários estão falando no vídeo.

## O que o projeto faz?

O projeto possui duas formas de utilização:

1. **Interface Web Interativa (Principal)**: Uma aplicação web fácil de usar construída com Streamlit (`app.py`), onde você insere o link de um vídeo e a IA gera um relatório inicial resumido. Além disso, conta com um chat interativo para "conversar" com a IA e tirar dúvidas específicas sobre os comentários.
2. **Uso via Terminal / Scripts**: 
   - `coletor.py`: Um script que baixa os comentários de um vídeo e salva em um arquivo texto (`.txt`).
   - `analisador.py`: Lê os arquivos de texto salvos pelo coletor e gera um relatório estruturado no próprio terminal.

## Tecnologias Utilizadas

- **Python** como linguagem principal.
- **[Streamlit](https://streamlit.io/)** para a criação da interface visual web interativa.
- **YouTube Data API v3** (`google-api-python-client`) para extração dos comentários dos vídeos.
- **Google Generative AI - Gemini 2.5 Flash** (`google-generativeai`) para analisar o sentimento e responder perguntas sobre os comentários de forma inteligente.

## Como executar

### 1. Pré-requisitos
Certifique-se de ter o Python instalado em seu computador. Em seguida, instale as bibliotecas necessárias via arquivo de requisitos. Abra o terminal na pasta do projeto e execute:
```bash
pip install -r requirements.txt
```

> **Atenção (Segurança):** O projeto utiliza variáveis de ambiente para proteger as credenciais de API. Você deve renomear o arquivo `.env.example` para `.env` e inserir as suas próprias chaves do Google AI Studio (Gemini) e do Google Cloud Console (YouTube API).

### 2. Rodando a Aplicação Web
Para iniciar a interface web de forma simples e rápida (no Windows), basta dar um duplo clique no arquivo:
- `iniciar_app.bat`

Ou, você pode abrir o terminal na raiz da pasta e rodar o comando:
```bash
streamlit run app.py
```
O seu navegador padrão abrirá automaticamente a interface do Analisador de Vídeos.

### 3. Usando pelo Terminal (Opcional)
Se preferir usar as ferramentas separadas sem a interface web:
- Rode `python coletor.py` para salvar comentários em um `.txt` informando o link de um vídeo.
- Em seguida, rode `python analisador.py` e digite o nome do arquivo gerado para obter o relatório no terminal.
- O arquivo `check_api.py` serve apenas para verificar quais modelos do Gemini estão disponíveis para sua chave.

## Estrutura dos Arquivos

- `app.py`: Aplicação web principal (Streamlit).
- `coletor.py`: Script para baixar comentários via YouTube API.
- `analisador.py`: Script para analisar os comentários baixados usando Gemini.
- `check_api.py`: Validador dos modelos disponíveis no Google Generative AI.
- `iniciar_app.bat`: Script em lote do Windows para iniciar a aplicação automaticamente.
- `coments_*.txt`: Arquivos gerados pelo coletor (armazenam os comentários puros do vídeo).
