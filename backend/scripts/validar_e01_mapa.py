
import csv
import json
import threading
import webbrowser
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from urllib.parse import urlparse


BASE = Path(__file__).resolve().parents[1]
PASTA = BASE / "data" / "onibus"

GEOJSON = PASTA / "pontos_onibus_candidatos.geojson"
CSV_SAIDA = PASTA / "validacao_e01.csv"

HOST = "127.0.0.1"
PORTA = 8765


HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moove Maricá - Validação E01</title>

<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<style>
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: Arial, sans-serif;
    color: #1f2937;
  }

  header {
    padding: 12px 20px;
    background: #111827;
    color: white;
  }

  header h1 {
    margin: 0;
    font-size: 20px;
  }

  header p {
    margin: 5px 0 0;
    font-size: 13px;
  }

  .layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    height: calc(100vh - 75px);
  }

  aside {
    overflow-y: auto;
    padding: 18px;
    background: #f9fafb;
    border-right: 1px solid #ddd;
  }

  #mapa {
    width: 100%;
    height: 100%;
  }

  button, select, input {
    padding: 10px;
    border-radius: 7px;
    border: 1px solid #ccc;
    font-size: 14px;
  }

  button {
    cursor: pointer;
    background: #2563eb;
    color: white;
    border: none;
    margin: 4px 0;
  }

  button:hover {
    background: #1d4ed8;
  }

  .secundario {
    background: #475569;
  }

  .perigo {
    background: #dc2626;
  }

  .campo {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 14px;
  }

  .acoes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .lista {
    padding-left: 22px;
    font-size: 13px;
  }

  .lista li {
    margin-bottom: 8px;
  }

  .aviso {
    background: #fef3c7;
    padding: 12px;
    border-radius: 8px;
    font-size: 13px;
  }

  @media (max-width: 800px) {
    .layout {
      grid-template-columns: 1fr;
      grid-template-rows: 350px 1fr;
      height: auto;
    }

    #mapa {
      height: 65vh;
    }
  }
</style>
</head>

<body>
<header>
  <h1>Moove Maricá | Conferência da E01</h1>
  <p>Seleção manual de paradas candidatas - Centro × Ponta Negra</p>
</header>

<div class="layout">
  <aside>
    <h2>Montar sequência</h2>

    <p class="aviso">
      Confirme cada parada e sua ordem antes de selecioná-la.
      A proximidade com a rua não comprova atendimento pela EPT.
    </p>

    <div class="campo">
      <label for="sentido">Sentido</label>
      <select id="sentido">
        <option value="ida">Ida</option>
        <option value="volta">Volta</option>
      </select>
    </div>

    <div class="campo">
      <label for="busca">Buscar nome ou ID</label>
      <input
        id="busca"
        placeholder="Digite parte do nome ou ID"
      />
      <button id="buscar" class="secundario">
        Localizar ponto
      </button>
    </div>

    <div class="acoes">
      <button id="desfazer" class="secundario">
        Desfazer último
      </button>

      <button id="limpar" class="perigo">
        Limpar sentido
      </button>
    </div>

    <button id="salvar">
      Salvar CSV de validação
    </button>

    <p id="mensagem" role="status"></p>

    <h3>Paradas selecionadas</h3>
    <ol id="lista" class="lista"></ol>
  </aside>

  <div id="mapa"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const mapa = L.map("mapa").setView(
  [-22.9194, -42.8186],
  12
);

L.tileLayer(
  "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    attribution: "&copy; OpenStreetMap contributors"
  }
).addTo(mapa);

const camada = L.layerGroup().addTo(mapa);
const marcadores = new Map();
const pontos = new Map();

const selecao = {
  ida: [],
  volta: []
};

const campoSentido = document.getElementById("sentido");
const campoBusca = document.getElementById("busca");
const lista = document.getElementById("lista");
const mensagem = document.getElementById("mensagem");

function sentidoAtual() {
  return campoSentido.value;
}

function atualizarLista() {
  lista.innerHTML = "";

  for (const id of selecao[sentidoAtual()]) {
    const ponto = pontos.get(id);
    const item = document.createElement("li");

    item.textContent = ponto
      ? `${ponto.nome || "Sem nome"} (ID ${id})`
      : `ID ${id}`;

    lista.appendChild(item);
  }
}

function selecionar(id) {
  const sentido = sentidoAtual();

  if (selecao[sentido].includes(id)) {
    mensagem.textContent =
      "Este ponto já está selecionado neste sentido.";
    return;
  }

  selecao[sentido].push(id);
  mensagem.textContent =
    `Ponto ${id} adicionado à ${sentido}.`;

  atualizarLista();
}

async function carregarPontos() {
  const resposta = await fetch("/pontos");

  if (!resposta.ok) {
    throw new Error("Não foi possível carregar os pontos.");
  }

  const dados = await resposta.json();

  for (const feature of dados.features || []) {
    const prop = feature.properties || {};
    const coords = feature.geometry?.coordinates || [];

    if (coords.length < 2 || prop.id == null) {
      continue;
    }

    const id = String(prop.id);
    const lng = Number(coords[0]);
    const lat = Number(coords[1]);

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      continue;
    }

    const ponto = {
      id,
      nome: prop.nome || "",
      lat,
      lng
    };

    pontos.set(id, ponto);

    const marcador = L.circleMarker(
      [lat, lng],
      {
        radius: 5,
        color: "#ea580c",
        fillColor: "#fb923c",
        fillOpacity: 0.85
      }
    );

    marcador.bindPopup(
      `<strong>${id}</strong><br>
       Clique em "Adicionar ponto" no painel de seleção.`
    );

    marcador.on("click", () => {
      selecionar(id);
    });

    marcador.addTo(camada);
    marcadores.set(id, marcador);
  }

  mensagem.textContent =
    `${pontos.size} pontos candidatos carregados.`;
}

document.getElementById("buscar").onclick = () => {
  const termo = campoBusca.value.trim().toLowerCase();

  if (!termo) {
    return;
  }

  const encontrado = [...pontos.values()].find(
    ponto =>
      ponto.id.toLowerCase().includes(termo) ||
      ponto.nome.toLowerCase().includes(termo)
  );

  if (!encontrado) {
    mensagem.textContent = "Nenhum ponto encontrado.";
    return;
  }

  mapa.setView(
    [encontrado.lat, encontrado.lng],
    17
  );

  marcadores.get(encontrado.id)?.openPopup();
};

document.getElementById("desfazer").onclick = () => {
  selecao[sentidoAtual()].pop();
  atualizarLista();
};

document.getElementById("limpar").onclick = () => {
  if (!confirm("Limpar a sequência deste sentido?")) {
    return;
  }

  selecao[sentidoAtual()] = [];
  atualizarLista();
};

campoSentido.onchange = atualizarLista;

document.getElementById("salvar").onclick = async () => {
  if (
    selecao.ida.length < 2 &&
    selecao.volta.length < 2
  ) {
    mensagem.textContent =
      "Selecione pelo menos duas paradas em um sentido.";
    return;
  }

  const resposta = await fetch("/salvar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(selecao)
  });

  const dados = await resposta.json();

  mensagem.textContent = resposta.ok
    ? dados.mensagem
    : dados.erro || "Falha ao salvar.";
};

carregarPontos().catch(erro => {
  mensagem.textContent = erro.message;
});
</script>
</body>
</html>
"""


def carregar_pontos():
    if not GEOJSON.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {GEOJSON}"
        )

    return json.loads(
        GEOJSON.read_text(encoding="utf-8")
    )


def salvar_csv(selecao):
    pontos = carregar_pontos().get("features", [])

    por_id = {}

    for feature in pontos:
        propriedades = feature.get("properties") or {}
        identificador = propriedades.get("id")

        if identificador is not None:
            por_id[str(identificador)] = feature

    linhas = []

    for sentido in ("ida", "volta"):
        ids = selecao.get(sentido, [])

        if not isinstance(ids, list):
            raise ValueError(
                "A sequência deve ser uma lista."
            )

        if len(ids) == 1:
            raise ValueError(
                f"O sentido {sentido} precisa de "
                "pelo menos duas paradas."
            )

        if len(ids) != len(set(map(str, ids))):
            raise ValueError(
                f"Existem pontos repetidos na {sentido}."
            )

        for ordem, identificador in enumerate(
            ids,
            start=1,
        ):
            identificador = str(identificador)

            if identificador not in por_id:
                raise ValueError(
                    f"Ponto desconhecido: {identificador}"
                )

            feature = por_id[identificador]
            propriedades = feature.get("properties") or {}
            lng, lat = feature["geometry"]["coordinates"][:2]

            linhas.append({
                "id": identificador,
                "nome": propriedades.get("nome") or "",
                "referencia": propriedades.get("referencia") or "",
                "lat": lat,
                "lng": lng,
                "status": "candidato_nao_validado",
                "pertence_e01": "SIM",
                "sentido": sentido,
                "ordem": ordem,
                "observacoes": "Conferir evidência de validação",
            })

    if not linhas:
        raise ValueError("Nenhuma parada selecionada.")

    # Preserva o CSV anterior antes de substituir.
    if CSV_SAIDA.exists():
        backup = CSV_SAIDA.with_suffix(".csv.bak")
        backup.write_bytes(CSV_SAIDA.read_bytes())

    with CSV_SAIDA.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=[
                "id",
                "nome",
                "referencia",
                "lat",
                "lng",
                "status",
                "pertence_e01",
                "sentido",
                "ordem",
                "observacoes",
            ],
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(linhas)

    return len(linhas)


class Servidor(BaseHTTPRequestHandler):
    def responder_json(self, dados, codigo=200):
        corpo = json.dumps(
            dados,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(codigo)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(corpo)),
        )
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = urlparse(self.path).path

        if caminho == "/":
            corpo = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(corpo)),
            )
            self.end_headers()
            self.wfile.write(corpo)
            return

        if caminho == "/pontos":
            self.responder_json(carregar_pontos())
            return

        self.responder_json(
            {"erro": "Página não encontrada."},
            404,
        )

    def do_POST(self):
        caminho = urlparse(self.path).path

        if caminho != "/salvar":
            self.responder_json(
                {"erro": "Endpoint não encontrado."},
                404,
            )
            return

        try:
            tamanho = int(
                self.headers.get(
                    "Content-Length", "0"
                )
            )

            if tamanho <= 0 or tamanho > 100000:
                raise ValueError(
                    "Tamanho de requisição inválido."
                )

            dados = json.loads(
                self.rfile.read(tamanho)
            )

            quantidade = salvar_csv(dados)

            self.responder_json({
                "mensagem": (
                    f"{quantidade} paradas exportadas "
                    "para validacao_e01.csv."
                )
            })

        except (ValueError, KeyError, TypeError) as erro:
            self.responder_json(
                {"erro": str(erro)},
                422,
            )


def iniciar():
    carregar_pontos()

    servidor = ThreadingHTTPServer(
        (HOST, PORTA),
        Servidor,
    )

    endereco = f"http://{HOST}:{PORTA}"

    print("Validador E01 iniciado.")
    print("Abra:", endereco)
    print("Pressione Ctrl+C para encerrar.")

    threading.Timer(
        1,
        lambda: webbrowser.open(endereco),
    ).start()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar()
