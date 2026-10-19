/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { getRepository } from "../../lib/data";
import styles from "./preview.module.css";

export const metadata = { title: "Estudo de bandeiras · MackJr" };
const variants = [
  {
    id: "original",
    label: "01 / Cores originais",
    folder: "flags",
    description: "As cores de cada país, com reconhecimento imediato.",
  },
  {
    id: "brand",
    label: "02 / Paleta MackJr",
    folder: "flags-preview",
    description: "Vermelho, papel e carvão, preservando as divisões de cor.",
  },
] as const;

type FlagVariant = (typeof variants)[number];
function Flag({
  code,
  variant,
  large = false,
}: {
  code: string;
  variant: FlagVariant;
  large?: boolean;
}) {
  return (
    <img
      className={large ? styles.largeFlag : styles.flag}
      src={`/${variant.folder}/${code.toLowerCase()}.svg`}
      width={large ? 80 : 32}
      height={large ? 60 : 24}
      alt=""
    />
  );
}

export default function FlagPreview() {
  const universities = getRepository().universities;
  const countries = [
    ...new Map(
      universities.map((university) => [university.flag, university]),
    ).values(),
  ];
  const selected = ["DE", "IT", "FR"].map((code) =>
    universities.find((university) => university.flag.toUpperCase() === code)!,
  );
  return (
    <div className={`page-shell ${styles.page}`}>
      <Link className="back-link" href="/universidades">
        ← Voltar aos destinos
      </Link>
      <header className={styles.intro}>
        <span className={styles.eyebrow}>
          Laboratório visual / Prévia local
        </span>
        <h1>
          Mesma bandeira.
          <br />
          <em>Duas linguagens.</em>
        </h1>
        <p>
          Compare as cores originais com a paleta MackJr nos contextos do site.
          Este estudo ainda não altera as bandeiras das páginas de destinos.
        </p>
        <a className={styles.jump} href="#todas">
          Explorar os 21 países ↓
        </a>
      </header>
      <section aria-labelledby="context-title">
        <div className={styles.sectionHeading}>
          <span className={styles.eyebrow}>01 / No contexto</span>
          <h2 id="context-title">Do detalhe ao destino.</h2>
        </div>
        <div className={styles.columns}>
          {variants.map((variant) => (
            <section
              className={styles.variant}
              key={variant.id}
              aria-label={variant.label}
            >
              <div className={styles.variantHeading}>
                <h3>{variant.label}</h3>
                <p>{variant.description}</p>
              </div>
              <div className={styles.detail}>
                <span className={styles.eyebrow}>
                  <Flag code="de" variant={variant} /> / Alemanha
                </span>
                <h2>
                  Leibniz Universität
                  <br />
                  Hannover
                </h2>
                <p>
                  Uma amostra do cabeçalho de universidade, com a bandeira em
                  seu tamanho de uso.
                </p>
                <span className={styles.sampleLabel}>
                  Cabeçalho / 32 × 24 px
                </span>
              </div>
              <div className={styles.cards}>
                {selected.map((university) => (
                  <article className={styles.card} key={university.id}>
                    <div className={styles.eyebrow}>
                      <Flag code={university.flag} variant={variant} />{" "}
                      {university.country}
                    </div>
                    <h3>{university.name}</h3>
                    <span className={styles.cardFooter}>
                      Explorar destino <span aria-hidden="true">↗</span>
                    </span>
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      </section>
      <section
        id="todas"
        className={styles.sheet}
        aria-labelledby="sheet-title"
      >
        <div className={styles.sectionHeading}>
          <span className={styles.eyebrow}>02 / Coleção completa</span>
          <h2 id="sheet-title">21 países, lado a lado.</h2>
          <p>Os mesmos desenhos, com suas faixas e símbolos preservados.</p>
        </div>
        <div className={styles.countryGrid}>
          {countries.map((country) => (
            <article key={country.flag} className={styles.country}>
              <div className={styles.countryTitle}>
                <h3>{country.country}</h3>
                <span>{country.flag.toUpperCase()}</span>
              </div>
              <div className={styles.flagPair}>
                {variants.map((variant) => (
                  <figure key={variant.id}>
                    <Flag code={country.flag} variant={variant} large />
                    <figcaption>
                      {variant.id === "original" ? "Original" : "MackJr"}
                    </figcaption>
                  </figure>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>
      <footer className={styles.note}>
        Estudo visual · Arquivos locais · Nenhuma alteração aplicada aos
        destinos
      </footer>
    </div>
  );
}
