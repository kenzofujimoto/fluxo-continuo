"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { Component, useState, type ReactNode } from "react";
import type { Destination, Location } from "../lib/locations";
import { CountryFlag } from "./country-flag";
const Canvas = dynamic(() => import("./globe-canvas"), {
  ssr: false,
  loading: () => (
    <div className="globe-status" role="status">
      Preparando o globo…
    </div>
  ),
});
class GlobeBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: Error) {
    console.error("Destination globe unavailable", error);
  }
  render() {
    return this.state.failed ? (
      <div className="globe-status" role="status">
        <p>Globo indisponível.</p>
        <span>Explore todos os destinos pela lista.</span>
      </div>
    ) : (
      this.props.children
    );
  }
}

export function DestinationGlobe({
  destinations,
  origin,
  hero = false,
}: {
  destinations: Destination[];
  origin: Location;
  hero?: boolean;
}) {
  const [selectedId, setSelectedId] = useState<string>();
  const [showGlobe, setShowGlobe] = useState(true);
  const selected =
    destinations.find((item) => item.id === selectedId) ??
    destinations.find((item) => item.location && /coimbra/i.test(item.name)) ??
    destinations.find((item) => item.location);
  const mapped = destinations.filter((item) => item.location).length;
  return (
    <div className={hero ? "destination-hero" : "destination-explorer"}>
      {!hero && (
        <div className="explorer-toolbar">
          <p className="eyebrow">
            {destinations.length} destinos / {mapped} no globo
          </p>
          <div className="view-toggle" aria-label="Visualização">
            <button
              type="button"
              aria-pressed={showGlobe}
              onClick={() => setShowGlobe(true)}
            >
              Globo
            </button>
            <button
              type="button"
              aria-pressed={!showGlobe}
              onClick={() => setShowGlobe(false)}
            >
              Lista
            </button>
          </div>
        </div>
      )}
      <div className="explorer-content">
        {showGlobe && (
          <div className="globe-stage">
            <GlobeBoundary>
              <Canvas
                destinations={destinations}
                origin={origin}
                selected={selected?.id}
                onSelect={setSelectedId}
                hero={hero}
              />
            </GlobeBoundary>
            <span className="globe-coordinate eyebrow">
              {hero ? "ALPHAVILLE → MUNDO" : "ARRASTE PARA EXPLORAR"}
            </span>
            {selected && (
              <article className="globe-selection" aria-live="polite">
                <span className="eyebrow">
                  <span className="status-dot" /> Destino em foco
                </span>
                <h3>{selected.name}</h3>
                <p>
                  {selected.location?.city ? `${selected.location.city}, ` : ""}
                  {selected.country}
                </p>
                <Link href={`/universidades/${selected.id}`}>
                  Conhecer instituição <span>↗</span>
                </Link>
                <small>
                  {!selected.location
                    ? "Localização pendente"
                    : selected.location.precision === "city"
                      ? "Localização aproximada · cidade"
                      : "Ponto institucional · campus de oferta a confirmar"}
                </small>
                {selected.location?.locationNote && (
                  <small>{selected.location.locationNote}</small>
                )}
                {selected.location && (
                  <a
                    className="geo-source"
                    href={selected.location.source}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Fonte da localização ↗
                  </a>
                )}
              </article>
            )}
            <p className="globe-caption">
              Trajetos ilustrativos. Não representam rotas aéreas.
              {origin.precision === "city" &&
                " Origem aproximada na cidade de Barueri."}
              {!hero &&
                " Elegibilidade e afinidade curricular são verificações distintas."}
            </p>
            <button
              type="button"
              className="globe-reset"
              onClick={() =>
                setSelectedId(destinations.find((item) => item.location)?.id)
              }
              aria-label="Focar primeiro destino"
            >
              ⌖
            </button>
          </div>
        )}
        <div
          className={hero ? "hero-destination-list" : "destination-list"}
          aria-label="Lista de destinos"
        >
          {hero && (
            <span className="eyebrow">
              Explore os destinos · seleção pelo teclado
            </span>
          )}
          {(hero
            ? destinations.filter((item) => item.location).slice(0, 5)
            : destinations
          ).map((item) => (
            <div
              key={item.id}
              className={`destination-row ${item.id === selected?.id ? "is-selected" : ""}`}
            >
              <button
                type="button"
                aria-pressed={item.id === selected?.id}
                onClick={() => {
                  setSelectedId(item.id);
                }}
              >
                <span className="destination-mark" aria-hidden="true">
                  <CountryFlag code={item.flag} />
                </span>
                <span>
                  <strong>{item.name}</strong>
                  <small>
                    {item.location?.city ? `${item.location.city}, ` : ""}
                    {item.country}
                  </small>
                  {!hero && (
                    <small>
                      {item.catalogCount} disciplinas no catálogo
                      {!item.location && " · localização pendente"}
                    </small>
                  )}
                </span>
              </button>
              <Link
                href={`/universidades/${item.id}`}
                aria-label={`Conhecer ${item.name}`}
              >
                ↗
              </Link>
            </div>
          ))}
          {!destinations.length && (
            <p className="empty">
              Nenhuma instituição encontrada. Ajuste os filtros.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
