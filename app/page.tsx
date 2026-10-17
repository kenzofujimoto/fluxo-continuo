import Link from "next/link";
import { getRepository } from "../lib/data";
import { ReviewCard } from "./ui";
import { DestinationGlobe } from "./destination-globe";
import { getDestinations } from "../lib/destinations";
import { universityLocations } from "../lib/locations";
export default function Home() {
  const { stats, courses, reviews, meta } = getRepository();
  return (
    <>
      <section className="hero globe-hero">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="status-dot" /> Seu próximo capítulo · 2027.2
          </p>
          <h1>
            O mundo é<br />
            parte da sua
            <br />
            <em>formação.</em>
          </h1>
          <p>
            Encontre destinos, conheça as disciplinas e construa seu plano de
            intercâmbio com informação que dá para conferir.
          </p>
          <div className="hero-actions">
            <Link className="button signal" href="/universidades">
              Explorar destinos <span>↗</span>
            </Link>
            <Link className="text-link" href="/comparacoes">
              Comparar ementas →
            </Link>
          </div>
          <p className="hero-footnote">
            Acesso livre. Fontes abertas. Decisões bem informadas.
          </p>
        </div>
        <DestinationGlobe
          destinations={getDestinations()}
          origin={universityLocations.origin}
          hero
        />
      </section>
      <section className="stats-strip" aria-label="A pesquisa em números">
        {[
          [stats.universities, "universidades"],
          [stats.disciplines, "disciplinas Mackenzie"],
          [stats.foreignCourses, "disciplinas estrangeiras"],
          [stats.reviews, "pareceres documentados"],
        ].map(([value, text]) => (
          <div key={text}>
            <strong>{Number(value).toLocaleString("pt-BR")}</strong>
            <span>{text}</span>
          </div>
        ))}
      </section>
      <section className="section">
        <div className="section-title">
          <div>
            <p className="eyebrow">01 / Comece pelo seu curso</p>
            <h2>
              Seu caminho,
              <br />
              <em>novas coordenadas.</em>
            </h2>
          </div>
          <p>
            Da sua matriz curricular às possibilidades lá fora. Explore os
            registros e veja o que já foi pesquisado.
          </p>
        </div>
        <div className="course-grid">
          {courses.map((course, i) => (
            <Link
              key={course.id}
              href={`/disciplinas?curso=${course.id}`}
              className="course-card"
            >
              <span className="eyebrow">0{i + 1} / Alphaville</span>
              <h3>{course.name}</h3>
              <div className="card-bottom">
                <span>{course.rows.length} disciplinas</span>
                <span className="round-arrow">↗</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
      <section className="section cream-section">
        <div className="section-title">
          <div>
            <p className="eyebrow">02 / Conteúdo antes de conclusões</p>
            <h2>
              Compare com
              <br />
              <em>evidências.</em>
            </h2>
          </div>
          <Link className="text-link" href="/comparacoes">
            Ver todos os pareceres ↗
          </Link>
        </div>
        <div className="review-grid">
          {reviews
            .filter((review) => review.brazil.courseId === "cc")
            .slice(0, 3)
            .map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
        </div>
        <div className="notice">
          <strong>Uma afinidade não é uma equivalência aprovada.</strong>
          <p>
            São {stats.homologated} homologações registradas. Ementas, horas,
            matrícula e aprovação institucional precisam ser verificadas
            separadamente.
          </p>
        </div>
      </section>
      <section className="section next-step">
        <p className="eyebrow">03 / Pesquisa em movimento</p>
        <h2>
          Boa informação
          <br />
          também mostra <em>o que falta.</em>
        </h2>
        <div>
          <p>
            {stats.missingPriority.toLocaleString("pt-BR")} programas
            estrangeiros prioritários ainda precisam de documentação. Veja as
            lacunas, as fontes e os próximos passos.
          </p>
          <Link className="button lime" href="/pendencias">
            Consultar pendências ↗
          </Link>
        </div>
        <span className="eyebrow">
          Base de referência: {meta.asOf} · consulta pública
        </span>
      </section>
    </>
  );
}
