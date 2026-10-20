# Moove Maricá

**Sua cidade em movimento.**

Protótipo web de planejamento de mobilidade urbana para Maricá (RJ), desenvolvido para o desafio HackTown.

## Stack
- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI
- Próximas etapas: Leaflet/OpenStreetMap, grafo viário, A*, trânsito simulado e integração multimodal

## Executar no Windows (PowerShell)

Pré-requisitos: Node.js LTS, Python 3.12 ou 3.13, Git.

**Terminal 1 — backend**
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Acesse http://127.0.0.1:8000/docs

**Terminal 2 — frontend**
```powershell
cd frontend
npm install
npm run dev
```
Acesse http://localhost:5173

## Git / GitHub
Este ZIP **não contém histórico Git**. Inicialize o repositório local depois de extrair:
```powershell
git init -b main
git add .
git commit -m "chore: bootstrap moove-marica web and api"
```
Crie um repositório vazio no GitHub (sem README), depois:
```powershell
git remote add origin https://github.com/cerolchileno/moove-marica.git
git push -u origin main
```

## Estado atual
Frontend conectado à rota `/api/status` do backend. Ainda **não** há mapa, roteamento ou integração com os sistemas públicos.
