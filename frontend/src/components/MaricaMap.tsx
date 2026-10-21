
import { useEffect, useMemo } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
  useMapEvents,
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";

import PontosOnibus from "./PontosOnibus";

import RotaOnibus, {
  type OpcaoOnibus,
} from "./RotaOnibus";

export type Ponto = {
  lat: number;
  lng: number;
};

type Props = {
  origem: Ponto | null;
  destino: Ponto | null;
  rota: [number, number][];
  rotaOnibus?: OpcaoOnibus | null;
  onSelecionar: (ponto: Ponto) => void;
};

const centroMarica: [number, number] = [
  -22.9194,
  -42.8186,
];

function criarIcone(cor: string) {
  return L.divIcon({
    className: "marcador-personalizado",
    html: `
      <div
        style="
          background: ${cor};
          width: 18px;
          height: 18px;
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px #0005;
        "
      ></div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function SeletorDePontos({
  onSelecionar,
}: {
  onSelecionar: (ponto: Ponto) => void;
}) {
  useMapEvents({
    click(evento) {
      onSelecionar({
        lat: evento.latlng.lat,
        lng: evento.latlng.lng,
      });
    },
  });

  return null;
}

function AjustarMapa({
  rota,
}: {
  rota: [number, number][];
}) {
  const mapa = useMap();

  useEffect(() => {
    if (rota.length > 1) {
      mapa.fitBounds(rota, {
        padding: [40, 40],
        maxZoom: 16,
      });
    }
  }, [mapa, rota]);

  return null;
}

export default function MaricaMap({
  origem,
  destino,
  rota,
  rotaOnibus = null,
  onSelecionar,
}: Props) {
  const iconeOrigem = useMemo(
    () => criarIcone("#16a34a"),
    []
  );

  const iconeDestino = useMemo(
    () => criarIcone("#dc2626"),
    []
  );

  const coordenadasAjuste = useMemo(() => {
    if (rotaOnibus) {
      return rotaOnibus.coordenadas;
    }

    return rota;
  }, [rota, rotaOnibus]);

  return (
    <MapContainer
      center={centroMarica}
      zoom={12}
      scrollWheelZoom={true}
      className="mapa"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Seleção de pontos pelo mapa */}
      <SeletorDePontos
        onSelecionar={onSelecionar}
      />

      {/* Ajusta a visualização para a rota */}
      <AjustarMapa
        rota={coordenadasAjuste}
      />

      {/* Pontos candidatos de ônibus do OpenStreetMap */}
      <PontosOnibus />

      {/* Rotas de caminhada e bicicleta */}
      {rota.length > 1 && !rotaOnibus && (
        <Polyline
          positions={rota}
          pathOptions={{
            color: "#dc2626",
            weight: 6,
            opacity: 0.9,
          }}
        />
      )}

      {/* Rota experimental de ônibus */}
      <RotaOnibus
        opcao={rotaOnibus}
      />

      {/* Marcador de origem */}
      {origem && (
        <Marker
          position={[
            origem.lat,
            origem.lng,
          ]}
          icon={iconeOrigem}
        >
          <Popup>
            <strong>Origem selecionada</strong>
            <p>
              {origem.lat.toFixed(5)},{" "}
              {origem.lng.toFixed(5)}
            </p>
          </Popup>
        </Marker>
      )}

      {/* Marcador de destino */}
      {destino && (
        <Marker
          position={[
            destino.lat,
            destino.lng,
          ]}
          icon={iconeDestino}
        >
          <Popup>
            <strong>Destino selecionado</strong>
            <p>
              {destino.lat.toFixed(5)},{" "}
              {destino.lng.toFixed(5)}
            </p>
          </Popup>
        </Marker>
      )}
    </MapContainer>
  );
}
