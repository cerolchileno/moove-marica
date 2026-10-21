
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.services.geocoding import buscar_enderecos

from app.services.routing import calcular_rota


app = FastAPI(
    title="Moove Marica API",
    description="API de mobilidade urbana e roteamento inteligente.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Coordenada(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class RequisicaoRota(BaseModel):
    origem: Coordenada
    destino: Coordenada


@app.get("/api/status")
def status():
    return {
        "aplicativo": "Moove Marica",
        "status": "online",
    }


@app.post("/api/rotas")
def criar_rota(requisicao: RequisicaoRota):
    try:
        return calcular_rota(
            origem_lat=requisicao.origem.lat,
            origem_lng=requisicao.origem.lng,
            destino_lat=requisicao.destino.lat,
            destino_lng=requisicao.destino.lng,
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=503,
            detail=str(erro),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro),
        ) from erro


@app.get("/api/enderecos")
def pesquisar_enderecos(q: str):
    if len(q.strip()) < 3:
        raise HTTPException(
            status_code=422,
            detail="Digite pelo menos 3 caracteres.",
        )

    try:
        return {
            "resultados": buscar_enderecos(q)
        }
    except Exception as erro:
        raise HTTPException(
            status_code=503,
            detail="Serviço de busca indisponível no momento.",
        ) from erro
