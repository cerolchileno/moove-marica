
import { useState } from "react";
import type { FormEvent } from "react";

export type EnderecoEncontrado = {
  nome: string;
  lat: number;
  lng: number;
};

type Props = {
  titulo: string;
  onSelecionar: (endereco: EnderecoEncontrado) => void;
};

export default function BuscaEndereco({
  titulo,
  onSelecionar,
}: Props) {
  const [texto, setTexto] = useState("");
  const [resultados, setResultados] = useState<EnderecoEncontrado[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  async function pesquisar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    if (texto.trim().length < 3) {
      setErro("Digite pelo menos 3 caracteres.");
      return;
    }

    setCarregando(true);
    setErro("");
    setResultados([]);

    try {
      const resposta = await fetch(
        `http://127.0.0.1:8000/api/enderecos?q=${encodeURIComponent(texto.trim())}`
      );

      if (!resposta.ok) {
        throw new Error("Não foi possível realizar a pesquisa.");
      }

      const dados: { resultados: EnderecoEncontrado[] } =
        await resposta.json();

      setResultados(dados.resultados);

      if (dados.resultados.length === 0) {
        setErro("Nenhum endereço encontrado.");
      }
    } catch {
      setErro("Erro ao pesquisar. Verifique se o backend está ligado.");
    } finally {
      setCarregando(false);
    }
  }

  function selecionar(endereco: EnderecoEncontrado) {
    setTexto(endereco.nome);
    setResultados([]);
    onSelecionar(endereco);
  }

  return (
    <div className="busca-endereco">
      <form onSubmit={pesquisar}>
        <label>{titulo}</label>

        <div className="busca-linha">
          <input
            type="text"
            value={texto}
            placeholder={`Pesquisar ${titulo.toLowerCase()}...`}
            onChange={(evento) => setTexto(evento.target.value)}
          />

          <button type="submit" disabled={carregando}>
            {carregando ? "Buscando..." : "Buscar"}
          </button>
        </div>
      </form>

      {erro && <p className="busca-erro">{erro}</p>}

      {resultados.length > 0 && (
        <div className="busca-resultados">
          {resultados.map((endereco, indice) => (
            <button
              type="button"
              key={`${endereco.lat}-${endereco.lng}-${indice}`}
              onClick={() => selecionar(endereco)}
            >
              📍 {endereco.nome}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
