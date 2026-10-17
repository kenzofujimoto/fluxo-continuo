import Link from "next/link";
import { getRepository } from "../../lib/data";
import { Badge, CourseSelect, Heading, queryValue, type Query } from "../ui";
export const metadata = { title: "O que falta pesquisar" };
export default async function Pending({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const { pending, courses, stats } = getRepository();
  return (
    <div className="page-shell">
      <Heading
        eyebrow="06 / Pesquisa em movimento"
        title="O que falta para comparar."
      >
        Para analisar uma equivalência, precisamos de programas completos,
        vigência, horas comparáveis e condições de matrícula. Estas são as
        lacunas registradas na base.
      </Heading>
      <div className="stats-strip inset">
        <div>
          <strong>{stats.missingPriority.toLocaleString("pt-BR")}</strong>
          <span>ementas estrangeiras prioritárias pendentes</span>
        </div>
        <div>
          <strong>{stats.blockedCrossings.toLocaleString("pt-BR")}</strong>
          <span>cruzamentos sem catálogo suficiente</span>
        </div>
      </div>
      <section className="section compact">
        <h2>Antes de uma decisão institucional</h2>
        <ol className="steps">
          <li>
            <strong>Obter os dois programas completos.</strong> Conteúdo
            programático, bibliografia, avaliação e fonte oficial identificável.
          </li>
          <li>
            <strong>Confirmar vigência e contexto.</strong> Matriz, campus, ano
            acadêmico e nível de ensino.
          </li>
          <li>
            <strong>Conferir a base das horas.</strong> Horas de contato,
            duração da hora e período. Créditos ECTS ficam separados.
          </li>
          <li>
            <strong>Confirmar a matrícula.</strong> Semestre, idioma,
            pré-requisitos e acesso para intercambistas.
          </li>
          <li>
            <strong>Revisar e submeter.</strong> Confrontar cada tópico,
            registrar limites e obter decisão da coordenação e da COI.
          </li>
        </ol>
      </section>
      <section>
        <h2>Documentação brasileira</h2>
        <form className="filters">
          <CourseSelect value={queryValue(query, "curso")} />
          <button className="button dark">Filtrar →</button>
        </form>
        {courses
          .filter(
            (course) =>
              !queryValue(query, "curso") ||
              course.id === queryValue(query, "curso"),
          )
          .map((course) => {
            const rows = pending.brazil[course.id]?.rows ?? [];
            const categories = [...new Set(rows.map((row) => row.category))];
            return (
              <article className="panel pending-course" key={course.id}>
                <h3>{course.name}</h3>
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <Badge key={category}>
                      {rows.filter((row) => row.category === category).length} ·{" "}
                      {rows.find((row) => row.category === category)?.label}
                    </Badge>
                  ))}
                </div>
                <details>
                  <summary>Consultar disciplinas com pendências</summary>
                  <ul className="topic-list">
                    {rows
                      .filter((row) => row.category !== "vigente_vinculada")
                      .map((row) => (
                        <li key={row.code}>
                          <strong>{row.name}</strong> · {row.label}
                          <p>{row.detail}</p>
                        </li>
                      ))}
                  </ul>
                </details>
                <p className="muted">
                  Coordenação: {pending.brazil[course.id]?.contact}
                </p>
              </article>
            );
          })}
      </section>
      <section className="section compact">
        <h2>Instituições com lacunas</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Instituição</th>
                <th>Ementas prioritárias ausentes</th>
                <th>Cruzamentos bloqueados</th>
              </tr>
            </thead>
            <tbody>
              {pending.foreign.map((university) => (
                <tr key={university.universityId}>
                  <td>
                    <Link href={`/universidades/${university.universityId}`}>
                      {university.name}
                    </Link>
                    <p className="muted">{university.country}</p>
                  </td>
                  <td>
                    {university.missingSyllabi.length}
                    <details>
                      <summary>Ver disciplinas</summary>
                      <ul>
                        {university.missingSyllabi.map((item) => (
                          <li key={item.code}>
                            {item.name} · {item.reason}
                          </li>
                        ))}
                      </ul>
                    </details>
                  </td>
                  <td>{university.insufficientCatalogueCrossings}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <div className="notice">
        <strong>Pendências COI</strong>
        <ul>
          {pending.coi.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
