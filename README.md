# Moove Maricá

**Sua cidade em movimento.**

Protótipo web de planejamento de mobilidade urbana para Maricá (RJ), desenvolvido para o desafio HackTown.

O projeto permite visualizar um mapa interativo da cidade, pesquisar endereços e calcular rotas de caminhada utilizando o algoritmo A* sobre uma rede de ruas obtida do OpenStreetMap.

## Tecnologias

**Frontend**
- React 19
- TypeScript
- Vite
- React Leaflet
- Leaflet

**Backend**
- Python
- FastAPI
- OSMnx
- NetworkX
- pytest

**Dados geográficos**
- OpenStreetMap
- Grafos de ruas armazenados localmente em arquivos GraphML

## Funcionalidades implementadas

- Mapa interativo de Maricá.
- Seleção de origem e destino.
- Busca de endereços com sugestões.
- Cálculo de rotas de caminhada utilizando A*.
- Visualização das rotas no mapa.
- Exibição da distância e do tempo estimado de caminhada.
- Validação de pontos fora da cobertura atual da rede.
- Expansão experimental do mapa por integração de grafos regionais.

## Pré-requisitos

- Windows com PowerShell
- Git
- Node.js compatível com Vite 6
- Python 3.13

## Instalação

Clone o repositório:

```powershell
git clone https://github.com/cerolchileno/moove-marica.git
cd moove-marica
```

### Backend

Abra um terminal PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Frontend

Abra outro terminal PowerShell na pasta principal do projeto:

```powershell
cd frontend
npm install
```

## Preparação dos mapas

Os arquivos GraphML não estão incluídos no repositório e precisam ser gerados localmente.

### 1. Gerar o mapa original

No terminal, dentro da pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m scripts.download_map
```

Esse comando gera:

`backend/data/marica_walk.graphml`

O mapa original cobre uma região de Maricá e não representa necessariamente todo o município.

### 2. Gerar o mapa regional

```powershell
.\.venv\Scripts\python.exe -m scripts.download_regiao
```

Esse comando gera:

`backend/data/marica_walk_cordeirinho.graphml`

O mapa regional amplia a cobertura na região de Cordeirinho/Balneário Bambuí.

### 3. Integrar os mapas

```powershell
.\.venv\Scripts\python.exe -m scripts.integrar_grafos
```

Esse comando gera:

`backend/data/marica_walk_integrado.graphml`

A integração preserva os mapas de origem. O arquivo integrado é experimental e pode conter componentes desconectados.

**Observação:** os downloads dependem da disponibilidade do serviço OpenStreetMap/Overpass e podem falhar por timeout.

## Executar o aplicativo

### Terminal 1 — Backend

Dentro da pasta `backend`:

```powershell
$env:MOOVE_GRAPH_FILE = "marica_walk_integrado.graphml"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Documentação interativa da API:

http://127.0.0.1:8000/docs

Se quiser utilizar o mapa original, execute o backend sem configurar `MOOVE_GRAPH_FILE` em um novo terminal.

### Terminal 2 — Frontend

Dentro da pasta `frontend`:

```powershell
npm run dev
```

Abra:

http://localhost:5173

## Testes

Para executar os testes automatizados do backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Para verificar a compilação do frontend:

```powershell
cd frontend
npm run build
```

## Limitações atuais

- A cobertura geográfica ainda não inclui todas as ruas de Maricá.
- Algumas partes do mapa integrado podem estar desconectadas.
- A validação de cobertura considera a distância até o nó mais próximo do grafo.
- O tempo de caminhada utiliza uma velocidade média estimada de 5 km/h.
- A busca de endereços depende da disponibilidade do serviço externo de geocodificação.
- As modalidades bicicleta e ônibus ainda não possuem roteamento implementado.
- Ainda não há informações de trânsito em tempo real.

## Próximas etapas

- Expandir e validar a cobertura da rede de ruas.
- Melhorar a correspondência entre pontos selecionados e vias.
- Implementar rotas para bicicletas.
- Adicionar planejamento de viagens de ônibus.
- Desenvolver funcionalidades multimodais.
- Aprimorar a interface para dispositivos móveis.
- Avaliar a transformação do projeto em aplicativo móvel.

## Repositório

https://github.com/cerolchileno/moove-marica

## Licenciamento dos dados

Os dados geográficos são provenientes do OpenStreetMap e estão sujeitos à licença Open Database