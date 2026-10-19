"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useState } from "react";
import type { Destination, Location } from "../../lib/locations";
import styles from "./preview.module.css";

const Canvas = dynamic(() => import("../globe-canvas"), {
  ssr: false,
  loading: () => (
    <p className={styles.loading} role="status">
      Preparando o globo…
    </p>
  ),
});

export function PreviewGlobe({
  destinations,
  origin,
}: {
  destinations: Destination[];
  origin: Location;
}) {
  const mapped = destinations.filter((destination) => destination.location);
  const [selectedId, setSelectedId] = useState(
    mapped.find((destination) => /coimbra/i.test(destination.name))?.id ??
      mapped[0]?.id,
  );
  const selected = mapped.find((destination) => destination.id === selectedId);

  return (
    <div className={styles.globe}>
      <div className={styles.stage}>
        <Canvas
          destinations={mapped}
          origin={origin}
          selected={selectedId}
          onSelect={setSelectedId}
          hero
        />
      </div>
      <div className={styles.destination}>
        <label
          htmlFor="preview-destination"
          className={styles.destinationLabel}
        >
          Escolha um destino
        </label>
        <select
          id="preview-destination"
          value={selectedId ?? ""}
          onChange={(event) => setSelectedId(event.target.value)}
        >
          {mapped.map((destination) => (
            <option key={destination.id} value={destination.id}>
              {destination.name}
            </option>
          ))}
        </select>
        <div aria-live="polite">
          {selected ? (
            <Link
              href={`/universidades/${selected.id}`}
              aria-label={`Conhecer ${selected.name}`}
            >
              Conhecer <span aria-hidden="true">↗</span>
            </Link>
          ) : (
            <Link href="/universidades">Ver destinos ↗</Link>
          )}
        </div>
      </div>
    </div>
  );
}
