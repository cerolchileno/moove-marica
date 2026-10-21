
import { useEffect, useState } from "react";
import { CircleMarker, Popup } from "react-leaflet";

type PontoOnibus = {
  type: "Feature";
  geometry: {
    type: "Point";
    coordinates: [number, number];
  };
  properties: {
    id: string;
    nome: string | null;
    status: string;
  };
};

type RespostaAPI = {
  type: "FeatureCollection";
  features: PontoOnibus[];
};

export default function PontosOnibus() {
  const [pontos, setPontos] = useState<PontoOnibus[]>([]);

  useEffect(() => {
    let ativo = true;

    async function carregarPontos() {
      try {
        const resposta = await fetch(
          "http://127.0.0.1:8000/api/onibus/pontos?limite=1000"
        );

        if (!resposta.ok) {
          throw new Error(
            `Erro HTTP ${resposta.status}`
          );
        }

        const dados: RespostaAPI =
          await resposta.json();

        if (ativo) {
          setPontos(dados.features);
        }
      } catch (erro) {
        console.error(
          "Erro ao carregar pontos de ônibus:",
          erro
        );
      }
    }

    carregarPontos();

    return () => {
      ativo = false;
    };
  }, []);

  return (
    <>
      {pontos.map((ponto) => {
        const [longitude, latitude] =
          ponto.geometry.coordinates;

        return (
          <CircleMarker
            key={ponto.properties.id}
            center={[latitude, longitude]}
            radius={5}
            pathOptions={{
              color: "#b45309",
              fillColor: "#f59e0b",
              fillOpacity: 0.8,
              weight: 1,
            }}
          >
            <Popup>
              <strong>
                {ponto.properties.nome ||
                  "Ponto de ônibus"}
              </strong>
              <p>
                Ponto candidato do OpenStreetMap.
                Ainda não validado pela EPT.
              </p>
            </Popup>
          </CircleMarker>
        );
      })}
    </>
  );
}
