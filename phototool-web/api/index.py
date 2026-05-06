from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Permite que o frontend se comunique com esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A Vercel vai injetar a sua chave de forma segura aqui
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Usando o modelo rápido
modelo = genai.GenerativeModel('gemini-2.5-flash')

PROMPT_TEXT = """
Você é um especialista em ler números de dorsais em fotos de mountain bike.
A imagem mostra um recorte focado no dorsal.
Concentre-se nos NÚMEROS GRANDES no centro. Ignore textos menores, nomes e sujeira/barro/cabos.
Retorne APENAS os dígitos do número (ex: 142). Nada mais. Nenhuma explicação.
Se estiver completamente ilegível, retorne NONE.
"""

@app.post("/api/ler-dorsal")
async def ler_dorsal(req: Request):
    dados = await req.json()
    base64_image = dados.get("image")
    mime_type = dados.get("mimeType", "image/jpeg")

    try:
        conteudo_gemini = [
            PROMPT_TEXT,
            {"mime_type": mime_type, "data": base64_image}
        ]
        
        # Faz a chamada para a IA
        resposta = modelo.generate_content(conteudo_gemini)
        texto = resposta.text.strip().replace('\n', '')
        
        # Extrai apenas os números (remove qualquer letra acidental)
        numero = ''.join(filter(str.isdigit, texto))
        
        if numero:
            return {"numero": numero, "status": "ok"}
        else:
            return {"numero": "Sem número", "status": "none"}
            
    except Exception as e:
        return {"numero": "Erro", "status": "err", "error": str(e)}