import { CircleMarker, Polyline, Popup } from "react-leaflet";

export type ParadaRota = {
  id: string;
  nome: string;
  lat: number;
  lng: number;
};

export type OpcaoOnibus = {
  codigo: string;
  sentido: string;
  embarque: ParadaRota;
  desembarque: ParadaRota;
  paradas_intermediarias: ParadaRota[];
  distancia_caminhada_reta_m: number;
  distancia_onibus_aproximada_m: number;
  tempo_estimado_sem_espera_min: number;
  coordenadas: [number, number][];
  experimental: boolean;
};

type Props = {
  opcao: OpcaoOnibus | null;
};

export default function RotaOnibus({ opcao }: Props) {
  if (!opcao) {
    return null;
  }

  return (
    <>
      <Polyline
        positions={opcao.coordenadas}
        pathOptions={{
          color: "#f97316",
          weight: 5,
          dashArray: "10 8",
        }}
      />

      <CircleMarker
        center={[
          opcao.embarque.lat,
          opcao.embarque.lng,
        ]}
        radius={9}
        pathOptions={{
          color: "#15803d",
          fillColor: "#22c55e",
          fillOpacity: 1,
        }}
      >
        <Popup>
          <strong>Embarque candidato</strong>
          <p>{opcao.embarque.nome}</p>
          <p>Linha {opcao.codigo}</p>
        </Popup>
      </CircleMarker>

      <CircleMarker
        center={[
          opcao.desembarque.lat,
          opcao.desembarque.lng,
        ]}
        radius={9}
        pathOptions={{
          color: "#b91c1c",
          fillColor: "#ef4444",
          fillOpacity: 1,
        }}
      >
        <Popup>
          <strong>Desembarque candidato</strong>
          <p>{opcao.desembarque.nome}</p>
        </Popup>
      </CircleMarker>
    </>
  );
}