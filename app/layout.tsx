import type { Metadata } from "next";
import Link from "next/link";
import "@fontsource/space-grotesk/400.css";
import "@fontsource/space-grotesk/500.css";
import "@fontsource/space-grotesk/600.css";
import "@fontsource/space-grotesk/700.css";
import "@fontsource/dm-serif-display/400.css";
import "@fontsource/dm-serif-display/400-italic.css";
import "@fontsource/jetbrains-mono/400.css";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Fluxo Contínuo — seu próximo semestre começa aqui",
    template: "%s · Fluxo Contínuo",
  },
  description:
    "Explore universidades, consulte ementas e compare disciplinas com evidências e fontes oficiais. Projeto independente de apoio à mobilidade acadêmica Mackenzie.",
};
const links = [
  ["/disciplinas", "Disciplinas"],
  ["/universidades", "Universidades"],
  ["/comparacoes", "Comparar"],
  ["/ementas", "Ementas"],
  ["/idiomas", "Idiomas"],
];
export default function Layout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <a className="skip-link" href="#conteudo">
          Ir para o conteúdo
        </a>
        <div className="topline">
          <span>Pesquisa aberta · mobilidade acadêmica</span>
          <span>Horizonte 2027.2</span>
        </div>
        <header className="site-header">
          <Link className="brand" href="/" aria-label="Fluxo Contínuo, início">
            <span className="brand-symbol" aria-hidden="true">
              f/
            </span>
            <span>
              fluxo
              <br />
              contínuo<span className="brand-dot">.</span>
            </span>
          </Link>
          <nav aria-label="Navegação principal">
            {links.map(([href, text]) => (
              <Link key={href} href={href}>
                {text}
              </Link>
            ))}
          </nav>
          <Link className="header-cta" href="/pendencias">
            O que falta <span aria-hidden="true">↗</span>
          </Link>
        </header>
        <main id="conteudo">{children}</main>
        <footer className="site-footer">
          <div>
            <Link className="footer-brand" href="/">
              fluxo contínuo<span>.</span>
            </Link>
            <p>
              Mais mundo.
              <br />
              Mais possibilidades.
            </p>
          </div>
          <div>
            <p className="eyebrow">Explore com contexto</p>
            <Link href="/cobertura">Cobertura da pesquisa ↗</Link>
            <Link href="/pendencias">Pendências documentais ↗</Link>
            <Link href="/metodologia">Fontes e metodologia ↗</Link>
          </div>
          <div className="footer-note">
            <BadgeText />
            Projeto independente de apoio acadêmico. Não representa o Mackenzie,
            a MackJr ou uma decisão institucional. A coordenação e a COI decidem
            o aproveitamento de estudos.
          </div>
          <div className="footer-base">
            Dados versionados · fontes rastreáveis · acesso público
            <span>Feito para ir além ↗</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
function BadgeText() {
  return <p className="eyebrow">Pesquisa, não homologação</p>;
}
