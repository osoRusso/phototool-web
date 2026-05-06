from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ler-dorsal")
async def ler_dorsal(req: Request):
    try:
        # 1. Verifica se a chave da API foi configurada na Vercel
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"numero": "Erro", "status": "err", "error": "Falta a GEMINI_API_KEY nas variáveis da Vercel."}
        
        # 2. Configura a IA
        genai.configure(api_key=api_key)
        modelo = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. Lê os dados enviados pelo navegador
        dados = await req.json()
        base64_image = dados.get("image")
        mime_type = dados.get("mimeType", "image/jpeg")

        if not base64_image:
             return {"numero": "Erro", "status": "err", "error": "O servidor não recebeu a imagem."}

        # 4. Chama o Gemini
        PROMPT_TEXT = """
        Você é um especialista em ler números de dorsais em fotos de mountain bike.
        A imagem mostra um recorte focado no dorsal.
        Concentre-se nos NÚMEROS GRANDES no centro. Ignore textos menores, nomes e sujeira/barro/cabos.
        Retorne APENAS os dígitos do número (ex: 142). Nada mais. Nenhuma explicação.
        Se estiver completamente ilegível, retorne NONE.
        """
        
        conteudo_gemini = [
            PROMPT_TEXT,
            {"mime_type": mime_type, "data": base64_image}
        ]
        
        resposta = modelo.generate_content(conteudo_gemini)
        texto = resposta.text.strip().replace('\n', '')
        
        numero = ''.join(filter(str.isdigit, texto))
        
        if numero:
            return {"numero": numero, "status": "ok"}
        else:
            return {"numero": "Sem número", "status": "none"}
            
    except Exception as e:
        # Se algo der errado, captura o erro técnico e manda para o front-end
        erro_detalhado = traceback.format_exc()
        print("Erro Interno:", erro_detalhado) # Fica salvo nos logs da Vercel
        return {"numero": "Erro", "status": "err", "error": str(e)}