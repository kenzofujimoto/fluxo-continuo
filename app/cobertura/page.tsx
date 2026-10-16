import Link from "next/link";
import { getRepository } from "../../lib/data";
import { Heading } from "../ui";
export const metadata = { title: "Cobertura da pesquisa" };
export default function Coverage() {
  const repository = getRepository();
  return (
    <div className="page-shell">
      <Heading eyebrow="07 / Retrato da base" title="Até onde já olhamos.">
        Indicadores calculados dos registros versionados. Quantidade de
        documentos não mede equivalência e não representa cobertura integral dos
        catálogos.
      </Heading>
      <div className="stats-strip inset">
        {[
          [
            repository.stats.individualSyllabi,
            "ementas estrangeiras individuais identificadas",
          ],
          [repository.stats.reviews, "pareceres documentados"],
          [repository.stats.homologated, "homologações registradas"],
        ].map(([value, text]) => (
          <div key={text}>
            <strong>{value}</strong>
            <span>{text}</span>
          </div>
        ))}
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Curso</th>
              <th>Disciplinas</th>
              <th>Instituições elegíveis</th>
              <th>Candidatas registradas</th>
              <th>Pareceres</th>
            </tr>
          </thead>
          <tbody>
            {repository.courses.map((course) => (
              <tr key={course.id}>
                <td>
                  <Link href={`/disciplinas?curso=${course.id}`}>
                    {course.name}
                  </Link>
                </td>
                <td>{course.rows.length}</td>
                <td>
                  {
                    repository.universities.filter(
                      (university) => university.courses[course.id],
                    ).length
                  }
                </td>
                <td>
                  {
                    repository.matches.filter(
                      (match) => match.courseId === course.id,
                    ).length
                  }
                </td>
                <td>
                  <Link href={`/comparacoes?curso=${course.id}`}>
                    {
                      repository.reviews.filter(
                        (review) => review.brazil.courseId === course.id,
                      ).length
                    }{" "}
                    →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="notice">
        <strong>Denominadores diferentes</strong>
        <p>
          “Ementa individual” é a classificação documental em records.json.
          “Parecer” é uma análise cadastrada, que pode combinar mais de uma
          disciplina estrangeira. “Pendente prioritária” vem do inventário de
          pendências; não abrange automaticamente todo o catálogo estrangeiro.
        </p>
      </div>
      <Link className="button dark" href="/pendencias">
        Ver o que falta →
      </Link>
    </div>
  );
}
