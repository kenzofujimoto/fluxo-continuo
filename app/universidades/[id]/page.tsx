import Link from "next/link";
import { CountryFlag } from "../../country-flag";
import { notFound } from "next/navigation";
import { getRepository } from "../../../lib/data";
import {
  Badge,
  Heading,
  Pagination,
  ReviewCard,
  Search,
  Source,
  pageNumber,
  queryValue,
  type Query,
} from "../../ui";
export default async function UniversityDetail({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<Query>;
}) {
  const { id } = await params;
  const query = await searchParams;
  const repository = getRepository();
  const university = repository.universities.find((item) => item.id === id);
  if (!university) notFound();
  const foreign = repository.foreignCourses.filter(
    (item) =>
      item.universityId === id &&
      item.name
        .toLocaleLowerCase()
        .includes(queryValue(query, "q").toLocaleLowerCase()),
  );
  const page = pageNumber(query, foreign.length);
  const reviews = repository.reviews.filter((review) =>
    review.foreign.some((item) => item.universityId === id),
  );
  return (
    <div className="page-shell">
      <Link className="back-link" href="/universidades">
        ← Todas as universidades
      </Link>
      <Heading
        eyebrow={
          <>
            <CountryFlag code={university.flag} /> / {university.country}
          </>
        }
        title={university.name}
      >
        {university.availabilityNote}
      </Heading>
      <div className="detail-grid">
        <section className="panel">
          <h2>Elegibilidade e fontes</h2>
          <div className="flex flex-wrap gap-2">
            {repository.courses
              .filter((course) => university.courses[course.id])
              .map((course) => (
                <Badge key={course.id} tone="lime">
                  {course.name}
                </Badge>
              ))}
          </div>
          {!Object.values(university.courses).some(Boolean) && (
            <p>
              Nenhum dos quatro cursos consta como elegível na planilha
              consultada.
            </p>
          )}
          <p>
            Uma disciplina no catálogo não garante acesso do intercambista ou
            oferta no semestre desejado.
          </p>
          <Source url={university.website}>Site institucional ↗</Source>
          <br />
          <Source url={university.catalogUrl}>Catálogo acadêmico ↗</Source>
        </section>
        <section className="panel">
          <h2>Idioma e matrícula</h2>
          <p>{university.language.required || "Requisito não informado"}</p>
          <p>{university.language.acceptedTests}</p>
          <p>
            <strong>Mínimo: </strong>
            {university.language.minimumScore || "A confirmar"}
          </p>
          {university.language.dataIssue && (
            <Badge>Inconsistência na fonte: confirmar requisito</Badge>
          )}
          <p>{university.language.notes}</p>
          <Source url={university.language.source} />
        </section>
      </div>
      <section className="section compact">
        <h2>{reviews.length} pareceres documentados</h2>
        <div className="review-grid">
          {reviews.slice(0, 6).map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
        {reviews.length > 6 && (
          <Link className="text-link" href={`/comparacoes?universidade=${id}`}>
            Ver todos os pareceres →
          </Link>
        )}
        {!reviews.length && (
          <p className="muted">
            Ainda não há análise documentada. Isso não constitui avaliação de
            compatibilidade.
          </p>
        )}
      </section>
      <section>
        <h2>Disciplinas do catálogo</h2>
        <form className="filters">
          <Search query={queryValue(query, "q")} />
          <button className="button dark">Buscar →</button>
        </form>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Disciplina</th>
                <th>Conteúdo registrado</th>
                <th>Oferta e horas</th>
              </tr>
            </thead>
            <tbody>
              {foreign.slice((page - 1) * 36, page * 36).map((item) => (
                <tr key={item.code}>
                  <td>
                    <strong>{item.name}</strong>
                    <br />
                    <Source url={item.source}>{item.code} ↗</Source>
                  </td>
                  <td>
                    {item.topics || "Programa integral ainda não registrado."}
                  </td>
                  <td>
                    {item.period || "Período a confirmar"}
                    <br />
                    {item.contactHours == null
                      ? "Horas de contato não informadas"
                      : `${item.contactHours} h de contato (registro preliminar; conferir parecer)`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!foreign.length && (
            <p className="empty">Nenhuma disciplina encontrada.</p>
          )}
        </div>
        <Pagination
          total={foreign.length}
          page={page}
          query={query}
          base={`/universidades/${id}`}
        />
      </section>
    </div>
  );
}
