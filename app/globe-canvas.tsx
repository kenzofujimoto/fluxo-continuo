"use client";

import { useEffect, useRef, useState } from "react";
import type { GlobeInstance } from "globe.gl";
import type { Destination, Location } from "../lib/locations";

type Pin = Location & { id: string; name: string };
export default function GlobeCanvas({
  destinations,
  origin,
  selected,
  onSelect,
  hero = false,
}: {
  destinations: Destination[];
  origin: Location;
  selected?: string;
  onSelect: (id: string) => void;
  hero?: boolean;
}) {
  const container = useRef<HTMLDivElement>(null);
  const globe = useRef<GlobeInstance | null>(null);
  const callback = useRef(onSelect);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    callback.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    const element = container.current;
    if (!element) return;
    let cancelled = false;
    let cleanup = () => {};
    async function initialize() {
      try {
        const [{ default: Globe }, response] = await Promise.all([
          import("globe.gl"),
          fetch("/maps/countries.geojson"),
        ]);
        if (!response.ok) throw new Error("Geography unavailable");
        const geography = await response.json();
        if (cancelled) return;
        const instance = new Globe(element!, {
          animateIn: false,
          rendererConfig: { antialias: true, alpha: true },
        });
        globe.current = instance;
        instance
          .renderer()
          .setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        cleanup = () => {
          instance._destructor();
          globe.current = null;
        };
        instance.globeMaterial().color.set("#1b1c17");
        instance
          .backgroundColor("#00000000")
          .showAtmosphere(true)
          .atmosphereColor("#b4afa0")
          .atmosphereAltitude(0.09)
          .showGraticules(true)
          .polygonsData(geography.features)
          .polygonCapColor(() => (hero ? "#353530" : "#393a34"))
          .polygonSideColor(() => "#25251f")
          .polygonStrokeColor(() => "#8c8a7a")
          .polygonAltitude(0.001)
          .polygonsTransitionDuration(0)
          .pointAltitude(0.009)
          .pointRadius(0.38)
          .pointsTransitionDuration(0)
          .pointLabel((point) => {
            const label = document.createElement("span");
            label.textContent = (point as Pin).name;
            return label;
          })
          .onPointClick((point) => {
            if ((point as Pin).id !== "origin")
              callback.current((point as Pin).id);
          })
          .onPointHover((point) => {
            element!.style.cursor = point ? "pointer" : "grab";
          })
          .arcStartLat(origin.lat)
          .arcStartLng(origin.lng)
          .arcEndLat("lat")
          .arcEndLng("lng")
          .arcColor(() => "#e63322")
          .arcStroke(0.12)
          .arcAltitudeAutoScale(0.24)
          .pointOfView({ lat: 16, lng: -24, altitude: hero ? 1.95 : 2.05 });
        const controls = instance.controls();
        controls.enableZoom = false;
        controls.enablePan = false;
        controls.autoRotate = false;
        const resize = new ResizeObserver(() =>
          instance.width(element!.clientWidth).height(element!.clientHeight),
        );
        resize.observe(element!);
        instance.width(element!.clientWidth).height(element!.clientHeight);
        let visible = true;
        const update = () => {
          if (visible && !document.hidden) instance.resumeAnimation();
          else instance.pauseAnimation();
        };
        const observer = new IntersectionObserver((entries) => {
          visible = entries[0].isIntersecting;
          update();
        });
        observer.observe(element!);
        document.addEventListener("visibilitychange", update);
        const lost = (event: Event) => {
          event.preventDefault();
          setState("error");
          instance.pauseAnimation();
        };
        instance
          .renderer()
          .domElement.addEventListener("webglcontextlost", lost);
        cleanup = () => {
          resize.disconnect();
          observer.disconnect();
          document.removeEventListener("visibilitychange", update);
          instance
            .renderer()
            .domElement.removeEventListener("webglcontextlost", lost);
          instance._destructor();
          globe.current = null;
        };
        setState("ready");
      } catch (error) {
        cleanup();
        console.error("Unable to initialize destination globe", error);
        if (!cancelled) setState("error");
      }
    }
    void initialize();
    return () => {
      cancelled = true;
      cleanup();
    };
  }, [hero, origin.lat, origin.lng]);

  useEffect(() => {
    const instance = globe.current;
    if (!instance || state !== "ready") return;
    const pins = destinations
      .filter((item) => item.location)
      .map((item) => ({ ...item.location!, id: item.id, name: item.name }));
    instance
      .pointsData([
        ...pins,
        { ...origin, id: "origin", name: "Alphaville · ponto de partida" },
      ])
      .pointColor((point) =>
        (point as Pin).id === "origin"
          ? "#f1ece3"
          : (point as Pin).id === selected
            ? "#c8fa3d"
            : "#f13c2b",
      )
      .pointRadius((point) => ((point as Pin).id === selected ? 0.75 : 0.38))
      .arcsData(
        hero
          ? [
              ...pins.filter((point) => point.id === selected),
              ...pins.filter((point) => point.id !== selected).slice(0, 4),
            ]
          : pins.filter((point) => point.id === selected),
      );
    const target = pins.find((point) => point.id === selected);
    if (target && !hero)
      instance.pointOfView(
        { lat: target.lat, lng: target.lng, altitude: 2.05 },
        matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 650,
      );
  }, [destinations, selected, state, hero, origin]);

  return (
    <>
      <div ref={container} className="globe-canvas" aria-hidden="true" />
      {state !== "ready" && (
        <div className="globe-status" role="status">
          <span className="eyebrow">
            {state === "loading"
              ? "Preparando suas coordenadas…"
              : "Globo indisponível neste navegador"}
          </span>
          <p>
            {state === "error"
              ? "Todos os destinos continuam disponíveis na lista."
              : "O mundo está logo ali."}
          </p>
        </div>
      )}
    </>
  );
}
