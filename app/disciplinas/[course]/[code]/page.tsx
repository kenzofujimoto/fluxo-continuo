import Link from "next/link";
import { notFound } from "next/navigation";
import {
  disciplineKey,
  getDiscipline,
  getRepository,
  label,
} from "../../../../lib/data";
import { Badge, Heading, ReviewCard, Source } from "../../../ui";
export default async function DisciplineDetail({
  params,
}: {
  params: Promise<{ course: string; code: string }>;
}) {
  const { course: courseId, code } = await params;
  const discipline = getDiscipline(courseId, code);
  if (!discipline) notFound();
  const { course, row, program } = discipline;
  const repository = getRepository();
  const key = disciplineKey(row);
  const reviews = repository.reviews.filter(
    (review) =>
      review.brazil.courseId === courseId && review.brazil.code === key,
  );
  const matches = repository.matches.filter(
    (match) => match.courseId === courseId && match.mackCode === key,
  );
  const pending = repository.pending.brazil[courseId]?.rows.find(
    (item) => item.code === key,
  );
  return (
    <div className="page-shell">
      <Link className="back-link" href={`/disciplinas?curso=${courseId}`}>
        ← {course.name}
      </Link>
      <Heading
        eyebrow={`${course.name} / ${row.semester ?? "—"}ª etapa`}
        title={row.name}
      >
        <span className="mono">{row.id ?? "Código não informado"}</span> ·{" "}
        {row.hours ?? "—"} h na matriz · confirmar unidade e vigência
      </Heading>
      <div className="detail-grid">
        <section className="panel">
          <h2>Ementa brasileira</h2>
          <Badge tone={program?.current ? "lime" : ""}>
            {pending?.label ?? "Vigência a verificar"}
          </Badge>
          <p>
            {program?.ementa ||
              row.abstract ||
              "Ementa integral ainda não vinculada."}
          </p>
          {program?.topics && (
            <ul className="topic-list">
              {program.topics.map((topic, index) => (
                <li key={index}>{topic}</li>
              ))}
            </ul>
          )}
          <Source url={program?.source ?? row.syllabusUrl ?? course.source} />
          <p className="muted">
            {program?.currencyNote ?? pending?.detail ?? course.matrix}
          </p>
          <p className="mono hash">
            SHA-256: {program?.sha256 ?? "não registrado"}
          </p>
        </section>
        <aside className="panel dark-panel">
          <p className="eyebrow">O caminho da análise</p>
          <h2>
            {reviews.length} pareceres.
            <br />
            {matches.length} candidatas.
          </h2>
          <p>
            Indícios por título ajudam a encontrar possibilidades. A comparação
            de conteúdo exige programas completos e revisão.
          </p>
          <Link
            href={`/comparacoes?curso=${courseId}&q=${encodeURIComponent(row.name)}`}
          >
            Consultar análises →
          </Link>
          <Link href="/pendencias">Ver lacunas documentais →</Link>
        </aside>
      </div>
      <section className="section compact">
        <h2>Pareceres documentados</h2>
        {reviews.length ? (
          <div className="review-grid">
            {reviews.map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        ) : (
          <p className="empty">
            Ainda não há parecer documentado para esta disciplina. Ausência de
            parecer não significa incompatibilidade.
          </p>
        )}
      </section>
      <section>
        <h2>Candidatas registradas</h2>
        <p className="muted">
          Triagem preliminar. O status de candidata não confirma equivalência
          nem oferta em 2027.2.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Disciplina estrangeira</th>
                <th>Instituição</th>
                <th>Indício</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((match, index) => {
                const foreign = repository.foreignCourses.find(
                  (item) =>
                    item.universityId === match.universityId &&
                    item.code === match.foreignCode,
                );
                const university = repository.universities.find(
                  (item) => item.id === match.universityId,
                );
                return (
                  <tr key={index}>
                    <td>
                      <strong>{foreign?.name ?? match.foreignCode}</strong>
                      <br />
                      <Source url={foreign?.source}>
                        {match.foreignCode} ↗
                      </Source>
                    </td>
                    <td>
                      <Link href={`/universidades/${match.universityId}`}>
                        {university?.name ?? match.universityId}
                      </Link>
                    </td>
                    <td>
                      {label(match.status)}
                      <p className="muted">{match.evidence}</p>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {!matches.length && (
            <p className="empty">
              Nenhuma candidata registrada para esta disciplina.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
