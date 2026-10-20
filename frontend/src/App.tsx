
import { useState } from "react";
import MaricaMap, { type Ponto } from "./components/MaricaMap";
import "./App.css";

type Transporte = "caminhada" | "onibus" | "bicicleta";

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

  function selecionarPonto(ponto: Ponto) {
    if (!origem) {
      setOrigem(ponto);
      setMensagem("Agora selecione o destino.");
    } else {
      setDestino(ponto);
      setMensagem("Pontos selecionados. Pronto para planejar.");
    }
  }

  function limpar() {
    setOrigem(null);
    setDestino(null);
    setMensagem("Selecione a origem clicando no mapa.");
  }

  function planejar() {
    if (!origem || !destino) {
      setMensagem("Selecione origem e destino primeiro.");
      return;
    }

    setMensagem(
      "Pontos definidos! O cálculo viário será integrado na próxima etapa."
    );
  }

  return (
    <div className="aplicacao">
      <header className="cabecalho">
        <div className="identidade">
          <div className="simbolo">M</div>
          <div>
            <h1>moove maricá</h1>
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

          <button className="botao-secundario" onClick={limpar}>
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
                onClick={() => setTransporte(id)}
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
              Na próxima etapa, os horários serão utilizados
              na simulação de trânsito.
            </p>
          </div>

          <button className="botao-principal" onClick={planejar}>
            Planejar minha rota →
          </button>

          <p className="mensagem" role="status">{mensagem}</p>

          <div className="rodape-painel">
            Moove Maricá · HackTown
          </div>
        </aside>

        <main className="area-mapa">
          <MaricaMap
            origem={origem}
            destino={destino}
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
