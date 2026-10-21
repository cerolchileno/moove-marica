import { useState } from "react";
import type { OpcaoOnibus } from "./RotaOnibus";

type Coordenada = {
  lat: number;
  lng: number;
};

type Resposta = {
  status: string;
  total_opcoes: number;
  melhor_opcao: OpcaoOnibus | null;
  aviso: string;
};

type Props = {
  origem: Coordenada | null;
  destino: Coordenada | null;
  onResultado: (opcao: OpcaoOnibus | null) => void;
};

export default function PlanejadorOnibus({
  origem,
  destino,
  onResultado,
}: Props) {
  const [linha, setLinha] = useState("E01");
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState<Resposta | null>(
    null
  );
  const [erro, setErro] = useState("");

  async function calcular() {
    if (!origem || !destino) {
      setErro("Selecione origem e destino primeiro.");
      return;
    }

    setCarregando(true);
    setErro("");
    setResultado(null);
    onResultado(null);

    try {
      const resposta = await fetch(
        "http://127.0.0.1:8000/api/rotas/onibus/planejar",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            origem,
            destino,
            codigo_linha: linha || null,
          }),
        }
      );

      if (!resposta.ok) {
        throw new Error(
          `Falha no planejamento: HTTP ${resposta.status}`
        );
      }

      const dados = (await resposta.json()) as Resposta;

      setResultado(dados);
      onResultado(dados.melhor_opcao);
    } catch (falha) {
      setErro(String(falha));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <section
      style={{
        padding: 16,
        background: "white",
        color: "#1f2937",
        borderRadius: 12,
      }}
    >
      <h3>Planejar viagem de ônibus</h3>

      <label htmlFor="linha-onibus">
        Linha
      </label>

      <input
        id="linha-onibus"
        value={linha}
        onChange={(evento) =>
          setLinha(evento.target.value.toUpperCase())
        }
        placeholder="E01"
        style={{
          display: "block",
          width: "100%",
          padding: 10,
          marginTop: 6,
          marginBottom: 12,
        }}
      />

      <button
        type="button"
        onClick={calcular}
        disabled={carregando || !origem || !destino}
      >
        {carregando
          ? "Calculando..."
          : "Buscar viagem de ônibus"}
      </button>

      {erro && (
        <p role="alert">{erro}</p>
      )}

      {resultado && (
        <div style={{ marginTop: 14 }}>
          {resultado.melhor_opcao ? (
            <>
              <h4>
                Linha {resultado.melhor_opcao.codigo}
              </h4>

              <p>
                Sentido: {resultado.melhor_opcao.sentido}
              </p>

              <p>
                Embarque:{" "}
                {resultado.melhor_opcao.embarque.nome}
              </p>

              <p>
                Desembarque:{" "}
                {resultado.melhor_opcao.desembarque.nome}
              </p>

              <p>
                Tempo aproximado, sem espera:{" "}
                {
                  resultado.melhor_opcao
                    .tempo_estimado_sem_espera_min
                }{" "}
                min
              </p>

              <p>
                Alternativas encontradas:{" "}
                {resultado.total_opcoes}
              </p>
            </>
          ) : (
            <p>
              Ainda não há uma sequência de paradas
              validada que permita calcular essa viagem.
            </p>
          )}

          <small>{resultado.aviso}</small>
        </div>
      )}
    </section>
  );
}