
# Moove Maricá

**Sua cidade em movimento.**

Protótipo web de planejamento de rotas e mobilidade urbana desenvolvido para o município de Maricá, Rio de Janeiro, no contexto do desafio HackTown.

O Moove Maricá utiliza dados geográficos do OpenStreetMap, grafos viários e o algoritmo A* para calcular percursos entre uma origem e um destino.

O projeto contempla rotas de caminhada, roteamento experimental de bicicleta e uma estrutura inicial de integração com os ônibus municipais conhecidos como Vermelhinhos.

> **Estado do projeto:** MVP em desenvolvimento e validação. As funcionalidades de ônibus ainda não representam um sistema completo de transporte público em produção.

## 1. Objetivo

O Moove Maricá busca facilitar o planejamento de deslocamentos urbanos por meio de uma interface visual e de algoritmos de busca em grafos.

Seus objetivos são:

- Permitir que o usuário escolha origem e destino.
- Calcular percursos utilizando o algoritmo A*.
- Apresentar o trajeto em um mapa interativo.
- Informar distância e tempo estimado.
- Oferecer modalidades de caminhada e bicicleta.
- Preparar a integração com o transporte coletivo municipal.
- Criar uma base para futuras análises de mobilidade urbana.

## 2. Tecnologias utilizadas

### Frontend

- React
- TypeScript
- Vite
- React Leaflet
- Leaflet
- OpenStreetMap

### Backend

- Python
- FastAPI
- NetworkX
- OSMnx
- Pydantic
- Uvicorn

### Dados geográficos

- OpenStreetMap
- Grafos viários em formato GraphML
- GeoJSON para pontos candidatos de ônibus
- JSON para itinerários e sequências de paradas

### Desenvolvimento e testes

- Git e GitHub
- Visual Studio Code
- PowerShell
- pytest
- npm

## 3. Arquitetura

O projeto utiliza uma arquitetura cliente-servidor.

O frontend React recebe as escolhas do usuário e envia solicitações HTTP para o backend FastAPI.

O backend processa os dados, seleciona a rede viária correspondente e executa o algoritmo de cálculo de rotas.

O resultado retorna ao frontend em formato JSON, contendo informações como distância, tempo estimado e coordenadas geográficas.

Fluxo simplificado:

```text
Usuário
   |
   v
Interface React
   |
   v
Seleção de origem, destino e modalidade
   |
   v
Requisição HTTP
   |
   v
API FastAPI
   |
   v
Seleção do grafo viário
   |
   v
Associação aos nós da rede
   |
   v
Algoritmo A*
   |
   v
Caminho calculado
   |
   v
Distância, tempo e coordenadas
   |
   v
Mapa interativo Leaflet
```

## 4. Estrutura do projeto

Os principais diretórios e arquivos trabalhados no desenvolvimento são:

```text
moove-marica/
|
|-- backend/
|   |
|   |-- app/
|   |   |-- main.py
|   |   |
|   |   |-- algorithms/
|   |   |   |-- astar.py
|   |   |
|   |   |-- services/
|   |       |-- routing.py
|   |       |-- pontos_onibus.py
|   |       |-- linhas_ept.py
|   |       |-- planejador_onibus.py
|   |
|   |-- data/
|   |   |-- marica_bike_ampliado.graphml
|   |   |
|   |   |-- onibus/
|   |       |-- itinerarios_ept.json
|   |       |-- rede_onibus_preparada.json
|   |       |-- pontos_onibus_candidatos.geojson
|   |       |-- paradas_linhas_validadas.json
|   |
|   |-- scripts/
|   |   |-- importar_itinerarios_ept.py
|   |   |-- importar_pontos_onibus_osm.py
|   |   |-- preparar_validacao_e01.py
|   |   |-- importar_paradas_validadas.py
|   |   |-- validar_e01_mapa.py
|   |   |-- diagnostico_final.py
|   |
|   |-- tests/
|   |-- requirements.txt
|
|-- frontend/
|   |
|   |-- src/
|   |   |-- App.tsx
|   |   |
|   |   |-- components/
|   |       |-- MaricaMap.tsx
|   |       |-- BuscaEndereco.tsx
|   |       |-- PontosOnibus.tsx
|   |       |-- LinhasOnibus.tsx
|   |       |-- PlanejadorOnibus.tsx
|   |       |-- RotaOnibus.tsx
|   |
|   |-- package.json
|
|-- docs/
|-- README.md
|-- .gitignore
```

**Observação:** esta estrutura representa os módulos desenvolvidos ou preparados durante o projeto. Alguns arquivos experimentais devem ser conferidos na branch utilizada para a demonstração.

## 5. Como funciona o algoritmo A*

O A* (A-star) é um algoritmo de busca de caminhos em grafos.

No Moove Maricá, a rede de ruas é representada como um grafo:

- **Nós:** representam pontos ou interseções da rede viária.
- **Arestas:** representam conexões entre esses pontos.
- **Pesos:** representam o custo de percorrer uma conexão, como sua distância.

O objetivo é encontrar um caminho de custo mínimo entre os nós associados à origem e ao destino.

### 5.1. Função de avaliação

O algoritmo A* utiliza:

```text
f(n) = g(n) + h(n)
```

Onde:

- `f(n)` é o custo total estimado para alcançar o destino passando pelo nó `n`.
- `g(n)` é o custo acumulado desde a origem até o nó `n`.
- `h(n)` é uma estimativa do custo restante até o destino.

Na busca por menor distância, uma heurística possível é a distância geográfica em linha reta até o destino.

Para preservar a garantia de menor custo, a heurística precisa ser admissível, isto é, não pode superestimar o custo real restante.

### 5.2. Etapas do cálculo

1. O usuário informa origem e destino.
2. O backend recebe as coordenadas.
3. O sistema seleciona o grafo da modalidade.
4. As coordenadas são associadas a nós próximos da rede.
5. O A* inicia a busca a partir do nó de origem.
6. O algoritmo avalia os nós candidatos utilizando `f(n)`.
7. Os custos acumulados são atualizados quando um caminho melhor é encontrado.
8. Ao alcançar o destino, o caminho é reconstruído.
9. O backend calcula a distância e estima o tempo.
10. As coordenadas do percurso são enviadas ao frontend.

### 5.3. Por que utilizar A*?

O A* é adequado para problemas de roteamento porque combina:

- O custo já percorrido.
- Uma estimativa do custo restante.
- Uma estratégia de busca orientada ao destino.

Com uma heurística apropriada, ele pode explorar menos nós que uma busca sem orientação heurística.

### 5.4. Limitações

A qualidade da rota depende da qualidade e da conectividade dos dados geográficos.

Um percurso matematicamente válido no grafo não significa necessariamente que seja o mais seguro, acessível ou adequado às condições reais da via.

O algoritmo não incorpora automaticamente congestionamentos, obras, segurança viária ou condições de acessibilidade.

## 6. Construção da rede viária

O projeto utiliza dados do OpenStreetMap para representar a rede de circulação de Maricá.

Esses dados são organizados em grafos que permitem pesquisar caminhos entre pontos geográficos.

O projeto trabalha com redes específicas para diferentes modalidades.

### Caminhada

Utiliza um grafo de deslocamento a pé, carregado pelo backend a partir de um arquivo GraphML.

### Bicicleta

Utiliza um grafo próprio, armazenado em:

```text
backend/data/marica_bike_ampliado.graphml
```

O roteamento de bicicleta é experimental.

Ainda são necessárias verificações adicionais sobre segurança, permissões de circulação, sentidos das vias e conectividade.

### Associação das coordenadas aos nós

Como o usuário seleciona coordenadas geográficas e o A* trabalha com nós, o backend procura nós próximos da origem e do destino.

Essa etapa permite transformar posições no mapa em pontos utilizáveis pelo algoritmo.

A rota calculada é então convertida em coordenadas para desenhar o percurso no Leaflet.

## 7. Cálculo da distância e do tempo

A distância de uma rota é obtida a partir dos custos das conexões percorridas no grafo.

O tempo é uma estimativa baseada na distância e nos parâmetros de velocidade adotados para a modalidade.

A relação básica é:

```text
tempo = distância / velocidade
```

Quando a distância está em metros e a velocidade em metros por minuto, o resultado é expresso em minutos.

Essas estimativas não representam medições de trânsito em tempo real.

## 8. Interface e funcionalidades

### Seleção de origem e destino

O usuário pode selecionar os pontos de partida e chegada por meio do mapa e da interface de busca de endereços.

### Mapa interativo

O aplicativo utiliza React Leaflet e OpenStreetMap para apresentar:

- A região de Maricá.
- Marcadores de origem e destino.
- Percursos calculados.
- Pontos candidatos de ônibus.

### Caminhada

A modalidade de caminhada utiliza o roteamento baseado no grafo viário e no algoritmo A*.

### Bicicleta

A modalidade de bicicleta utiliza uma rede própria e apresenta resultados experimentais.

### Resumo da rota

O frontend apresenta dados retornados pelo backend, incluindo:

- Modalidade.
- Distância.
- Tempo estimado.
- Geometria do percurso.

## 9. Integração experimental com ônibus

O Moove Maricá possui uma estrutura inicial voltada aos ônibus municipais conhecidos como Vermelhinhos.

### 9.1. Itinerários da EPT

Foram preparados scripts para coletar e organizar descrições textuais de itinerários divulgados pela Empresa Pública de Transportes de Maricá (EPT).

Fonte de referência:

https://www.eptmarica.rj.gov.br/index.php/vermelhinhos/itinerarios

### 9.2. Pontos candidatos

Foram extraídos pontos identificados no OpenStreetMap como pontos de ônibus.

Esses registros são armazenados em GeoJSON e podem ser exibidos no mapa.

**Importante:** um ponto de ônibus presente no OpenStreetMap não é, por si só, uma parada confirmada de determinada linha da EPT.

### 9.3. Validação das paradas

Foram preparados recursos para organizar a conferência manual de pontos e sequências de paradas.

A linha E01, Centro × Ponta Negra, foi escolhida como piloto dessa validação.

### 9.4. Planejador experimental

A estrutura de planejamento de ônibus considera sequências cadastradas de paradas, origem, destino e possibilidades de embarque e desembarque.

Sem sequências devidamente confirmadas, o sistema não deve apresentar uma rota como validada.

As conexões experimentais entre paradas não substituem a geometria oficial percorrida pelo veículo.

### 9.5. Limitações atuais do módulo

Ainda são necessários:

- Validação das paradas atendidas por cada linha.
- Confirmação da ordem das paradas em cada sentido.
- Geometrias confiáveis dos itinerários.
- Integração com horários operacionais.
- Tratamento de baldeações.
- Testes de viagens reais.

Portanto, o módulo de ônibus não deve ser apresentado como um roteador completo e validado do transporte municipal.

## 10. Executar o projeto

### Pré-requisitos

- Python compatível com as dependências do backend.
- Node.js e npm.
- Git.
- Arquivos de grafos necessários para as modalidades.
- Dependências Python e JavaScript instaladas.

Os comandos abaixo são destinados ao Windows com PowerShell.

### 10.1. Clonar o repositório

```powershell
git clone https://github.com/cerolchileno/moove-marica.git

cd moove-marica
```

Para trabalhar em uma branch de desenvolvimento, selecione a branch correspondente após verificar quais estão disponíveis:

```powershell
git branch -a
```

### 10.2. Preparar o backend

Abra um terminal na pasta `backend`:

```powershell
cd backend

py -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

O backend precisa encontrar o grafo de caminhada.

Caso o arquivo esteja na pasta `backend` com o nome abaixo, configure:

```powershell
$env:MOOVE_GRAPH_FILE = "marica_walk_integrado.graphml"
```

Se o arquivo estiver em outro local, utilize o caminho correspondente.

Inicie o servidor:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Documentação interativa da API:

http://127.0.0.1:8000/docs

### 10.3. Preparar o frontend

Abra outro terminal na pasta `frontend`:

```powershell
cd frontend

npm install

npm run dev
```

Acesse:

http://localhost:5173

O backend e o frontend devem estar em execução simultaneamente.

## 11. Endpoints da API

Os principais endpoints desenvolvidos ou previstos na integração são:

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/api/rotas` | Calcular rota de caminhada ou bicicleta |
| GET | `/api/onibus/pontos` | Consultar pontos candidatos de ônibus |
| GET | `/api/onibus/linhas` | Consultar catálogo de itinerários |
| POST | `/api/rotas/onibus/planejar` | Consultar planejamento experimental de ônibus |

A disponibilidade efetiva dos endpoints depende da versão do backend em execução.

Consulte `/docs` para verificar quais endpoints estão ativos.

## 12. Testes e validação

### Backend

Na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Frontend

Na pasta `frontend`:

```powershell
npm run build
```

### Diagnóstico de integração

Se o script estiver presente na branch utilizada:

```powershell
.\.venv\Scripts\python.exe scripts\diagnostico_final.py
```

Os testes e o diagnóstico devem ser executados antes de uma demonstração pública.

Não se deve interpretar a existência de um arquivo de teste como garantia de que todos os testes passaram.

## 13. Situação do desenvolvimento

| Funcionalidade | Estado |
|---|---|
| Interface React | Implementada |
| Mapa Leaflet/OpenStreetMap | Implementado |
| Seleção de origem e destino | Implementada |
| Busca de endereços | Implementada |
| Algoritmo A* | Implementado |
| Roteamento de caminhada | Implementado |
| Roteamento de bicicleta | Experimental |
| Distância e tempo estimado | Implementados |
| Importação de itinerários EPT | Preparada |
| Pontos candidatos de ônibus | Importados |
| Planejamento de ônibus | Experimental |
| Validação oficial das paradas | Pendente |
| Horários e baldeações | Pendentes |
| Simulação de trânsito | Pendente |
| Integração de dados demográficos | Pendente |

O estado de implementação não substitui a verificação final de funcionamento da branch utilizada.

## 14. Limitações técnicas

Este projeto é um protótipo e apresenta limitações que devem ser consideradas:

1. A cobertura do roteamento depende dos grafos disponíveis.
2. Nem todas as conexões viárias foram verificadas presencialmente.
3. A rede de bicicleta ainda exige validação de segurança.
4. As estimativas de tempo não incorporam trânsito em tempo real.
5. O sistema ainda não utiliza dados demográficos no cálculo das rotas.
6. Os pontos candidatos de ônibus não equivalem a paradas oficiais confirmadas.
7. O módulo de ônibus ainda não dispõe de horários e geometrias completas.
8. O aplicativo não deve ser utilizado como fonte exclusiva para decisões de deslocamento que dependam de acessibilidade ou segurança.

## 15. Próximas etapas

As prioridades de evolução incluem:

- Validar os itinerários e as paradas da EPT.
- Incorporar horários dos Vermelhinhos.
- Implementar baldeações entre linhas.
- Desenvolver simulação de trânsito por período do dia.
- Integrar dados demográficos e indicadores territoriais.
- Melhorar a avaliação de segurança das rotas de bicicleta.
- Adicionar critérios de acessibilidade.
- Comparar rotas alternativas.
- Ampliar testes automatizados.
- Preparar implantação e demonstração pública estável.

## 16. Demonstração no HackTown

A demonstração do MVP deve priorizar:

1. Apresentar o problema de mobilidade em Maricá.
2. Selecionar origem e destino.
3. Calcular uma rota de caminhada.
4. Exibir o percurso, a distância e o tempo estimado.
5. Demonstrar uma rota experimental de bicicleta.
6. Mostrar a preparação para integração dos Vermelhinhos.
7. Explicar as limitações atuais e o plano de evolução.

A principal contribuição técnica do projeto é combinar uma interface geográfica interativa com um mecanismo de cálculo de rotas baseado em grafos e no algoritmo A*.

## 17. Fontes de dados

- OpenStreetMap: https://www.openstreetmap.org/
- EPT Maricá: https://www.eptmarica.rj.gov.br/
- NetworkX: https://networkx.org/
- OSMnx: https://osmnx.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Leaflet: https://leafletjs.com/

## 18. Repositório

GitHub:

https://github.com/cerolchileno/moove-marica

---

**Moove Maricá — Sua cidade em movimento.**

Protótipo de mobilidade urbana desenvolvido para apresentação no HackTown.
