
import { useEffect, useMemo, useState } from "react";

type Itinerario = {
  sentido: string;
  percurso_textual: string;
  trechos: string[];
  validado: boolean;
};

type Linha = {
  id: string;
  codigo: string;
  nome: string;
  itinerarios: Itinerario[];
  status: string;
};

type Resposta = {
  total: number;
  linhas: Linha[];
  aviso: string;
};

export default function LinhasOnibus() {
  const [linhas, setLinhas] = useState<Linha[]>([]);
  const [busca, setBusca] = useState("");
  const [selecionada, setSelecionada] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true;

    fetch("http://127.0.0.1:8000/api/onibus/linhas")
      .then(async (resposta) => {
        if (!resposta.ok) {
          throw new Error(
            `Erro ao consultar linhas: ${resposta.status}`
          );
        }

        return resposta.json() as Promise<Resposta>;
      })
      .then((dados) => {
        if (ativo) {
          setLinhas(dados.linhas);
        }
      })
      .catch((falha) => {
        if (ativo) {
          setErro(String(falha));
        }
      });

    return () => {
      ativo = false;
    };
  }, []);

  const filtradas = useMemo(() => {
    const termo = busca.trim().toLowerCase();

    return linhas.filter((linha) =>
      `${linha.codigo} ${linha.nome}`
        .toLowerCase()
        .includes(termo)
    );
  }, [linhas, busca]);

  const linhaAtual = linhas.find(
    (linha) => linha.id === selecionada
  );

  return (
    <section
      style={{
        padding: 16,
        background: "#ffffff",
        color: "#1f2937",
        borderRadius: 12,
        maxHeight: 420,
        overflowY: "auto",
      }}
    >
      <h2>Vermelhinhos de Maricá</h2>

      <p>
        Consulte as linhas e os itinerários
        textuais publicados pela EPT.
      </p>

      <input
        type="search"
        placeholder="Buscar linha E01, bairro..."
        value={busca}
        onChange={(evento) =>
          setBusca(evento.target.value)
        }
        style={{
          width: "100%",
          padding: 10,
          marginBottom: 12,
        }}
      />

      {erro && (
        <p role="alert">
          Não foi possível carregar as linhas: {erro}
        </p>
      )}

      <select
        value={selecionada}
        onChange={(evento) =>
          setSelecionada(evento.target.value)
        }
        style={{
          width: "100%",
          padding: 10,
        }}
      >
        <option value="">
          Selecione uma linha
        </option>

        {filtradas.map((linha) => (
          <option key={linha.id} value={linha.id}>
            {linha.codigo} — {linha.nome}
          </option>
        ))}
      </select>

      {linhaAtual && (
        <div style={{ marginTop: 16 }}>
          <h3>
            {linhaAtual.codigo} — {linhaAtual.nome}
          </h3>

          {linhaAtual.itinerarios.map(
            (itinerario, indice) => (
              <div
                key={`${itinerario.sentido}-${indice}`}
                style={{ marginBottom: 18 }}
              >
                <h4>
                  Sentido: {itinerario.sentido}
                </h4>

                <ol>
                  {itinerario.trechos.map(
                    (trecho, posicao) => (
                      <li key={posicao}>
                        {trecho}
                      </li>
                    )
                  )}
                </ol>
              </div>
            )
          )}

          <small>
            Os trechos representam referências
            do itinerário, não paradas de
            embarque confirmadas.
          </small>
        </div>
      )}
    </section>
  );
}
