
import { useRef, useState } from "react";
import MaricaMap, { type Ponto } from "./components/MaricaMap";
import "./App.css";

type Transporte = "caminhada" | "onibus" | "bicicleta";

type ResultadoRota = {
  algoritmo: string;
  modalidade: string;
  distancia_m: number;
  tempo_min: number;
  coordenadas: [number, number][];
};

const API_URL = "http://127.0.0.1:8000";

function formatarPonto(ponto: Ponto | null) {
  if (!ponto) return "Clique no mapa para selecionar";

  return `${ponto.lat.toFixed(5)}, ${ponto.lng.toFixed(5)}`;
}

export default function App() {
  const [origem, setOrigem] = useState<Ponto | null>(null);
  const [destino, setDestino] = useState<Ponto | null>(null);
  const [transporte, setTransporte] =
    useState<Transporte>("caminhada");
  const [horario, setHorario] = useState("08:00");
  const [mensagem, setMensagem] = useState(
    "Selecione a origem clicando no mapa."
  );

  const [resultado, setResultado] =
    useState<ResultadoRota | null>(null);
  const [carregando, setCarregando] = useState(false);

  const requisicaoAtual = useRef<AbortController | null>(null);

  function cancelarRotaAnterior() {
    requisicaoAtual.current?.abort();
    requisicaoAtual.current = null;
    setCarregando(false);
    setResultado(null);
  }

  function selecionarPonto(ponto: Ponto) {
    cancelarRotaAnterior();

    if (!origem) {
      setOrigem(ponto);
      setMensagem("Agora selecione o destino.");
    } else {
      setDestino(ponto);
      setMensagem("Pontos selecionados. Pronto para planejar.");
    }
  }

  function limpar() {
    cancelarRotaAnterior();
    setOrigem(null);
    setDestino(null);
    setMensagem("Selecione a origem clicando no mapa.");
  }

  async function planejar() {
    if (!origem || !destino) {
      setMensagem("Selecione origem e destino primeiro.");
      return;
    }

    if (transporte !== "caminhada") {
      setMensagem(
        "Por enquanto, o cálculo está disponível apenas para caminhada."
      );
      return;
    }

    cancelarRotaAnterior();

    const controlador = new AbortController();
    requisicaoAtual.current = controlador;

    setCarregando(true);
    setMensagem("Calculando a melhor rota pelas ruas de Maricá...");

    try {
      const resposta = await fetch(`${API_URL}/api/rotas`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controlador.signal,
        body: JSON.stringify({
          origem,
          destino,
        }),
      });

      if (!resposta.ok) {
        const erro = await resposta.json().catch(() => null);

        throw new Error(
          erro?.detail || "Não foi possível calcular a rota."
        );
      }

      const dados: ResultadoRota = await resposta.json();

      if (requisicaoAtual.current !== controlador) return;

      setResultado(dados);
      setMensagem("Rota calculada com sucesso!");
    } catch (erro) {
      if (controlador.signal.aborted) return;

      if (requisicaoAtual.current !== controlador) return;

      setMensagem(
        erro instanceof Error
          ? erro.message
          : "Erro ao conectar com o servidor."
      );
    } finally {
      if (requisicaoAtual.current === controlador) {
        requisicaoAtual.current = null;
        setCarregando(false);
      }
    }
  }

  return (
    <div className="aplicacao">
      <header className="cabecalho">
        <div className="identidade">
          <div className="simbolo">M</div>
          <div>
            <h1>Moove Marica</h1>
            <p>Sua cidade em movimento.</p>
          </div>
        </div>
        <span className="etiqueta">Mobilidade inteligente</span>
      </header>

      <div className="conteudo">
        <aside className="painel">
          <div className="painel-titulo">
            <span className="sobretitulo">PLANEJADOR DE ROTAS</span>
            <h2>Para onde vamos?</h2>
            <p>Planeje seu deslocamento por Maricá.</p>
          </div>

          <div className="campos">
            <div className="campo">
              <span className="ponto origem" />
              <div>
                <label>Origem</label>
                <strong>{formatarPonto(origem)}</strong>
              </div>
            </div>

            <div className="campo">
              <span className="ponto destino" />
              <div>
                <label>Destino</label>
                <strong>{formatarPonto(destino)}</strong>
              </div>
            </div>
          </div>

          <button
            className="botao-secundario"
            onClick={limpar}
          >
            Limpar pontos
          </button>

          <h3>Como deseja viajar?</h3>

          <div className="transportes">
            {([
              ["caminhada", "🚶", "A pé"],
              ["onibus", "🚌", "Ônibus"],
              ["bicicleta", "🚲", "Bicicleta"],
            ] as const).map(([id, icone, titulo]) => (
              <button
                key={id}
                className={
                  transporte === id
                    ? "transporte selecionado"
                    : "transporte"
                }
                onClick={() => {
                  cancelarRotaAnterior();
                  setTransporte(id);
                  setMensagem(
                    id === "caminhada"
                      ? "Modo caminhada selecionado."
                      : "Modalidade em desenvolvimento."
                  );
                }}
                aria-pressed={transporte === id}
              >
                <span>{icone}</span>
                <span>{titulo}</span>
              </button>
            ))}
          </div>

          <h3>Horário de partida</h3>

          <input
            className="horario"
            type="time"
            value={horario}
            onChange={(evento) => setHorario(evento.target.value)}
          />

          <div className="aviso">
            <strong>Trânsito inteligente</strong>
            <p>
              Em breve, os horários serão utilizados na
              simulação de trânsito.
            </p>
          </div>

          <button
            className="botao-principal"
            onClick={planejar}
            disabled={carregando}
          >
            {carregando
              ? "Calculando rota..."
              : "Planejar minha rota →"}
          </button>

          <p className="mensagem" role="status">
            {mensagem}
          </p>

          {resultado && (
            <div className="resultado-rota">
              <h3>Resumo da sua rota</h3>

              <div className="resultado-dados">
                <div>
                  <span>Distância</span>
                  <strong>
                    {(resultado.distancia_m / 1000).toFixed(2)} km
                  </strong>
                </div>

                <div>
                  <span>Tempo estimado</span>
                  <strong>
                    {resultado.tempo_min.toFixed(1)} min
                  </strong>
                </div>
              </div>

              <p>
                Calculado com {resultado.algoritmo} sobre a
                rede de ruas do OpenStreetMap.
              </p>
            </div>
          )}

          <div className="rodape-painel">
            Moove Marica · HackTown
          </div>
        </aside>

        <main className="area-mapa">
          <MaricaMap
            origem={origem}
            destino={destino}
            rota={resultado?.coordenadas ?? []}
            onSelecionar={selecionarPonto}
          />

          <div className="mapa-instrucao">
            <span className="bolinha-vermelha" />
            Clique no mapa para selecionar os pontos
          </div>
        </main>
      </div>
    </div>
  );
}
