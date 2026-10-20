import { useEffect, useState } from "react";
import "./App.css";

type StatusAPI = { sistema: string; backend: string; status: string; modulos: Record<string, string> };

function App() {
  const [dados, setDados] = useState<StatusAPI | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/status")
      .then((resposta) => { if (!resposta.ok) throw new Error("Falha na resposta da API"); return resposta.json(); })
      .then((resultado: StatusAPI) => setDados(resultado))
      .catch(() => setErro("Não foi possível conectar à API."));
  }, []);

  return (
    <main className="container">
      <header><span className="marca">M</span><div><h1>Moove Maricá</h1><p>Sua cidade em movimento.</p></div></header>
      <section className="painel">
        <h2>Central de mobilidade</h2>
        <p>Planeje seus deslocamentos por Maricá com rotas inteligentes e diferentes transportes.</p>
        <div className="status"><span className="indicador" />{dados ? `API ${dados.status}` : erro || "Conectando ao servidor..."}</div>
        <h3>Módulos do sistema</h3>
        {dados && <div className="modulos">{Object.entries(dados.modulos).map(([nome, situacao]) => <div className="modulo" key={nome}><strong>{nome}</strong><span>{situacao}</span></div>)}</div>}
      </section>
      <footer>HackTown | Desafio de Mobilidade Urbana</footer>
    </main>
  );
}
export default App;
