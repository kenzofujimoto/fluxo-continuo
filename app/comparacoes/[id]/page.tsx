import Link from "next/link";
import { notFound } from "next/navigation";
import { getComparison, label } from "../../../lib/data";
import { Badge, Heading, Source, conclusionTone } from "../../ui";
export default async function ComparisonDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const review = getComparison(id);
  if (!review) notFound();
  const count = (status: string) =>
    review.topics.filter((topic) => topic.status === status).length;
  return (
    <div className="page-shell comparison-detail">
      <Link className="back-link" href="/comparacoes">
        ← Todos os pareceres
      </Link>
      <Heading
        eyebrow={`${review.brazil.courseName} / parecer preliminar`}
        title={review.brazil.name}
      >
        <div className="flex flex-wrap gap-2">
          <Badge tone={conclusionTone(review.conclusionClass)}>
            {label(review.conclusionClass)}
          </Badge>
          <Badge>{label(review.institutionalStatus)}</Badge>
        </div>
      </Heading>
      <div className="synthesis">
        <span className="eyebrow">Leitura do parecer</span>
        <p>{review.synthesis}</p>
        <span className="muted">
          Confiança {review.confidence} · revisado em {review.reviewedAt}
        </span>
      </div>
      <div className="detail-grid">
        <section className="panel">
          <p className="eyebrow">Origem / Mackenzie</p>
          <h2>{review.brazil.name}</h2>
          <p>
            {review.brazil.code} · {review.brazil.courseName}
          </p>
          <p>{review.brazil.documentTitle}</p>
          <p>
            <strong>Vigência:</strong>{" "}
            {review.brazilDocumentCurrent
              ? "Vinculada no parecer"
              : "Não confirmada para a matriz atual"}
          </p>
          <p>
            <strong>Horas declaradas:</strong>{" "}
            {review.brazil.hours.value ?? "Não informadas"}{" "}
            {label(review.brazil.hours.unit ?? "")} ·{" "}
            {label(review.brazil.hours.basis ?? "")}
          </p>
          <p className="muted">{review.brazil.hours.note}</p>
          <Source url={review.brazil.source} />
          <p className="muted">{review.brazil.location}</p>
          <p className="hash mono">
            SHA-256: {review.brazil.sha256 ?? "não registrado"}
          </p>
        </section>
        <section className="panel">
          <p className="eyebrow">
            Destino /{" "}
            {review.foreign.length > 1
              ? "Combinação de disciplinas"
              : "Disciplina estrangeira"}
          </p>
          {review.foreign.map((foreign) => (
            <div
              className="foreign-document"
              key={`${foreign.universityId}|${foreign.code}`}
            >
              <h2>{foreign.name}</h2>
              <p>
                <Link href={`/universidades/${foreign.universityId}`}>
                  {foreign.university}
                </Link>{" "}
                · {foreign.code}
              </p>
              <p>
                {foreign.academicYear ?? "Ano a confirmar"} ·{" "}
                {foreign.language ?? "Idioma a confirmar"}
              </p>
              <p>
                <strong>Contato:</strong>{" "}
                {foreign.hours.contactTotal == null
                  ? "Não informado"
                  : `${foreign.hours.contactTotal} h`}{" "}
                · <strong>ECTS:</strong> {foreign.hours.ects ?? "Não informado"}
              </p>
              <p className="muted">{foreign.hours.note}</p>
              <Source url={foreign.source} />
              <p className="muted">{foreign.location}</p>
              <p className="hash mono">
                SHA-256: {foreign.sha256 ?? "não registrado"}
              </p>
            </div>
          ))}
        </section>
      </div>
      <div className="notice">
        <strong>Horas: {label(review.hoursComparison.state)}</strong>
        <p>{review.hoursComparison.reason}</p>
        <p>
          ECTS mede carga total de trabalho. Não equivale a horas de contato e
          não é convertido automaticamente.
        </p>
      </div>
      <section className="section compact">
        <div className="section-title">
          <div>
            <p className="eyebrow">Evidência por tópico</p>
            <h2>O que os documentos mostram.</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {["coberto", "parcial", "nao_encontrado", "nao_verificavel"].map(
              (status) => (
                <Badge key={status} tone={status === "coberto" ? "lime" : ""}>
                  {count(status)} {label(status).toLowerCase()}
                </Badge>
              ),
            )}
          </div>
        </div>
        <div className="topic-comparison">
          {review.topics.map((topic, index) => (
            <article className="topic-pair" key={index}>
              <div>
                <span className="eyebrow">
                  Mackenzie / tópico {String(index + 1).padStart(2, "0")}
                </span>
                <h3>{topic.brTopic}</h3>
                {topic.essential && (
                  <span className="muted">Tópico essencial</span>
                )}
              </div>
              <div>
                <Badge
                  tone={
                    topic.status === "coberto"
                      ? "lime"
                      : topic.status === "parcial"
                        ? "amber"
                        : ""
                  }
                >
                  {label(topic.status)}
                </Badge>
                <p>
                  {topic.foreignEvidence ||
                    "Sem evidência específica registrada."}
                </p>
                <p className="mono evidence-location">
                  {topic.foreignLocation ?? topic.scopeExamined}
                </p>
                <p className="muted">{topic.note}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
      <div className="detail-grid">
        <section className="panel">
          <h2>Limitações e próximos passos</h2>
          <ul className="topic-list">
            {review.limitations.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
          {review.openQuestions?.length ? (
            <>
              <h3>Perguntas em aberto</h3>
              <ul className="topic-list">
                {review.openQuestions.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </>
          ) : null}
        </section>
        <section className="panel">
          <h2>Condições acadêmicas</h2>
          {review.practical && (
            <dl className="facts">
              {Object.entries(review.practical).map(([key, value]) => (
                <div key={key}>
                  <dt>
                    {(
                      {
                        period: "Período",
                        language: "Idioma",
                        enrolment: "Matrícula",
                        prerequisites: "Pré-requisitos",
                        offer2027: "Oferta 2027",
                      } as Record<string, string>
                    )[key] ?? label(key)}
                  </dt>
                  <dd>
                    {typeof value === "string"
                      ? label(value)
                      : JSON.stringify(value)}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          <h3>Revisão e rastreabilidade</h3>
          <p>{review.confidenceRationale}</p>
          <p>{review.method}</p>
          {review.secondReview?.required && (
            <p>
              <strong>Segunda revisão pendente:</strong>{" "}
              {review.secondReview.reason}
            </p>
          )}
          <details>
            <summary>Justificativa completa</summary>
            <p>{review.justification}</p>
          </details>
        </section>
      </div>
    </div>
  );
}
