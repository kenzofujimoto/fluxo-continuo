import type { NextConfig } from "next";
const config: NextConfig = {
  poweredByHeader: false,
  agentRules: false,
  turbopack: { root: process.cwd() },
  async redirects() {
    return [
      ["/index.html", "/"],
      ["/legacy-v1.html", "/"],
      ["/ementas.html", "/ementas"],
      ["/analises.html", "/comparacoes"],
      ["/cobertura.html", "/cobertura"],
      ["/pendencias.html", "/pendencias"],
      ["/idiomas.html", "/idiomas"],
    ].map(([source, destination]) => ({
      source,
      destination,
      permanent: true,
    }));
  },
};
export default config;
