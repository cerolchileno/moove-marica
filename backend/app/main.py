from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Moove Maricá API", version="0.1.0", description="API de mobilidade urbana de Maricá")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])

@app.get("/")
def home():
    return {"projeto": "Moove Maricá", "status": "online", "mensagem": "API funcionando!"}

@app.get("/api/status")
def status():
    return {"sistema": "Moove Maricá", "backend": "FastAPI", "status": "operacional", "modulos": {"mapa": "pendente", "rotas": "pendente", "transito": "pendente", "multimodal": "pendente"}}
