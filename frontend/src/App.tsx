
import { useRef, useState } from "react";
import MaricaMap, { type Ponto } from "./components/MaricaMap";
import BuscaEndereco from "./components/BuscaEndereco";
import "./App.css";
import PontosOnibus from "./components/PontosOnibus";

type Transporte = "caminhada" | "onibus" | "bicicleta";

type ResultadoRota = {
  algoritmo: string;
  modalidade: string;
  distancia_m: number;
  tempo_min: number;
  coordenadas: [number, number][];
  experimental?: boolean;
};

const API_URL = "http://127.0.0.1:8000";

function formatarPonto(ponto: Ponto | null) {
  if (!ponto) {
    return "Clique no mapa ou pesquise um endereço";
  }

  return `${ponto.lat.toFixed(5)}, ${ponto.lng.toFixed(5)}`;
}

export default function App() {
  const [origem, setOrigem] = useState<Ponto | null>(null);
  const [destino, setDestino] = useState<Ponto | null>(null);

  const [transporte, setTransporte] =
    useState<Transporte>("caminhada");

  const [horario, setHorario] = useState("08:00");

  const [mensagem, setMensagem] = useState(
    "Selecione a origem no mapa ou pesquise um endereço."
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

  // Seleção de pontos clicando no mapa
  function selecionarPonto(ponto: Ponto) {
    cancelarRotaAnterior();

    if (!origem) {
      setOrigem(ponto);
      setMensagem("Agora selecione o destino.");
    } else {
      setDestino(ponto);
      setMensagem(
        "Pontos selecionados. Pronto para planejar."
      );
    }
  }

  // Seleção da origem pela pesquisa de endereços
  function selecionarOrigemBusca(ponto: Ponto) {
    cancelarRotaAnterior();
    setOrigem(ponto);

    setMensagem(
      destino
        ? "Nova origem selecionada. Pronto para planejar."
        : "Origem selecionada. Agora escolha o destino."
    );
  }

  // Seleção do destino pela pesquisa de endereços
  function selecionarDestinoBusca(ponto: Ponto) {
    cancelarRotaAnterior();
    setDestino(ponto);

    setMensagem(
      origem
        ? "Destino selecionado. Pronto para planejar."
        : "Destino selecionado. Agora escolha a origem."
    );
  }

  // Limpar os pontos e a rota calculada
  function limpar() {
    cancelarRotaAnterior();

    setOrigem(null);
    setDestino(null);

    setMensagem(
      "Selecione a origem no mapa ou pesquise um endereço."
    );
  }

  // Calcular rota utilizando o backend FastAPI
  async function planejar() {
    if (!origem || !destino) {
      setMensagem(
        "Selecione origem e destino primeiro."
      );
      return;
    }

    // Ônibus ainda não possui roteamento implementado
    if (transporte === "onibus") {
      setMensagem(
        "O cálculo de rotas de ônibus ainda está em desenvolvimento."
      );
      return;
    }

    cancelarRotaAnterior();

    const controlador = new AbortController();
    requisicaoAtual.current = controlador;

    setCarregando(true);
    setMensagem(
      transporte === "bicicleta"
        ? "Calculando rota experimental de bicicleta..."
        : "Calculando a melhor rota pelas ruas de Maricá..."
    );

    try {
      const resposta = await fetch(
        `${API_URL}/api/rotas`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          signal: controlador.signal,
          body: JSON.stringify({
            origem,
            destino,
            modalidade: transporte,
          }),
        }
      );

      if (!resposta.ok) {
        const erro = await resposta
          .json()
          .catch(() => null);

        throw new Error(
          typeof erro?.detail === "string"
            ? erro.detail
            : "Não foi possível calcular a rota."
        );
      }

      const dados: ResultadoRota =
        await resposta.json();

      if (requisicaoAtual.current !== controlador) {
        return;
      }

      setResultado(dados);

      setMensagem(
        dados.experimental
          ? "Rota experimental de bicicleta calculada!"
          : "Rota calculada com sucesso!"
      );
    } catch (erro) {
      if (controlador.signal.aborted) {
        return;
      }

      if (requisicaoAtual.current !== controlador) {
        return;
      }

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

        <span className="etiqueta">
          Mobilidade inteligente
        </span>
      </header>

      <div className="conteudo">
        <aside className="painel">
          <div className="painel-titulo">
            <span className="sobretitulo">
              PLANEJADOR DE ROTAS
            </span>

            <h2>Para onde vamos?</h2>

            <p>
              Planeje seu deslocamento por Maricá.
            </p>
          </div>

          {/* Pesquisa de origem e destino */}
          <div className="pesquisas-endereco">
            <BuscaEndereco
              titulo="Origem"
              onSelecionar={selecionarOrigemBusca}
            />

            <BuscaEndereco
              titulo="Destino"
              onSelecionar={selecionarDestinoBusca}
            />
          </div>

          {/* Coordenadas dos pontos selecionados */}
          <div className="campos">
            <div className="campo">
              <span className="ponto origem" />

              <div>
                <label>Origem</label>
                <strong>
                  {formatarPonto(origem)}
                </strong>
              </div>
            </div>

            <div className="campo">
              <span className="ponto destino" />

              <div>
                <label>Destino</label>
                <strong>
                  {formatarPonto(destino)}
                </strong>
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
                      : id === "bicicleta"
                        ? "Modo bicicleta experimental selecionado."
                        : "Modalidade de ônibus em desenvolvimento."
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
            onChange={(evento) =>
              setHorario(evento.target.value)
            }
          />

          <div className="aviso">
            <strong>Trânsito inteligente</strong>

            <p>
              Em breve, os horários serão utilizados
              na simulação de trânsito.
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

          {/* Resultado do algoritmo A* */}
          {resultado && (
            <div className="resultado-rota">
              <h3>Resumo da sua rota</h3>

              {resultado.experimental && (
                <p role="note">
                  ⚠️ Rota de bicicleta experimental.
                  O trajeto ainda não foi validado
                  quanto à segurança, às permissões
                  de circulação e aos sentidos das vias.
                </p>
              )}

              <div className="resultado-dados">
                <div>
                  <span>Distância</span>

                  <strong>
                    {(
                      resultado.distancia_m / 1000
                    ).toFixed(2)}{" "}
                    km
                  </strong>
                </div>

                <div>
                  <span>Tempo estimado</span>

                  <strong>
                    {resultado.tempo_min.toFixed(1)}{" "}
                    min
                  </strong>
                </div>
              </div>

              <p>
                Calculado com {resultado.algoritmo}{" "}
                sobre a rede de ruas do OpenStreetMap.
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
            Clique no mapa ou pesquise um endereço
          </div>
        </main>
      </div>
    </div>
  );
}
