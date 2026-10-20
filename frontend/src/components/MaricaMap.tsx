
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export type Ponto = {
  lat: number;
  lng: number;
};

type Props = {
  origem: Ponto | null;
  destino: Ponto | null;
  onSelecionar: (ponto: Ponto) => void;
};

const centroMarica: [number, number] = [-22.9194, -42.8186];

const criarIcone = (cor: string) =>
  L.divIcon({
    className: "marcador-personalizado",
    html: `<div style="background:${cor};width:18px;height:18px;border:3px solid white;border-radius:50%;box-shadow:0 2px 8px #0005"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

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

export default function MaricaMap({
  origem,
  destino,
  onSelecionar,
}: Props) {
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

      <SeletorDePontos onSelecionar={onSelecionar} />

      {origem && (
        <Marker
          position={[origem.lat, origem.lng]}
          icon={criarIcone("#16a34a")}
        >
          <Popup>Origem selecionada</Popup>
        </Marker>
      )}

      {destino && (
        <Marker
          position={[destino.lat, destino.lng]}
          icon={criarIcone("#dc2626")}
        >
          <Popup>Destino selecionado</Popup>
        </Marker>
      )}
    </MapContainer>
  );
}
