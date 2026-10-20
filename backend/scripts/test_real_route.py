
from pathlib import Path
import sys

import osmnx as ox

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.algorithms.astar import calcular_astar

ARQUIVO = BASE_DIR / "data" / "marica_walk.graphml"

if not ARQUIVO.exists():
    raise FileNotFoundError(
        "Mapa não encontrado. Execute download_map.py primeiro."
    )

print("Moove Marica - Carregando mapa real...")

grafo = ox.load_graphml(ARQUIVO)

# Dois pontos de exemplo próximos ao Centro
origem = (-22.9194, -42.8186)
destino = (-22.9280, -42.8240)

no_origem = ox.distance.nearest_nodes(
    grafo, X=origem[1], Y=origem[0]
)

no_destino = ox.distance.nearest_nodes(
    grafo, X=destino[1], Y=destino[0]
)

print("Calculando rota com A*...")

caminho, distancia = calcular_astar(
    grafo, no_origem, no_destino
)

velocidade_kmh = 5
tempo_minutos = (distancia / 1000) / velocidade_kmh * 60

print("\n=== RESULTADO MOOVE MARICA ===")
print(f"Quantidade de nós na rota: {len(caminho)}")
print(f"Distância: {distancia / 1000:.2f} km")
print(f"Tempo estimado a pé: {tempo_minutos:.1f} minutos")
print("Algoritmo utilizado: A*")
