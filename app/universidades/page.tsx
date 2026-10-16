import Link from "next/link";
import { getRepository, normalize } from "../../lib/data";
import {
  Badge,
  CourseSelect,
  Empty,
  Heading,
  Search,
  queryValue,
  type Query,
} from "../ui";
export const metadata = { title: "Universidades" };
export default async function Universities({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const repository = getRepository();
  const results = repository.universities.filter(
    (university) =>
      (!queryValue(query, "curso") ||
        university.courses[queryValue(query, "curso")]) &&
      normalize(`${university.name} ${university.country}`).includes(
        normalize(queryValue(query, "q")),
      ),
  );
  return (
    <div className="page-shell">
      <Heading eyebrow="02 / Novas coordenadas" title="Onde você quer chegar?">
        Explore instituições, requisitos de idioma e o que já foi pesquisado. A
        planilha COI indica elegibilidade por curso; vagas individuais e oferta
        de disciplinas precisam de confirmação.
      </Heading>
      <form className="filters">
        <Search
          query={queryValue(query, "q")}
          placeholder="Universidade ou país"
        />
        <CourseSelect value={queryValue(query, "curso")} />
        <button className="button dark">Filtrar →</button>
        <Link href="/universidades">Limpar</Link>
      </form>
      <p className="result-count">{results.length} instituições encontradas</p>
      <div className="university-grid">
        {results.map((university) => (
          <Link
            href={`/universidades/${university.id}`}
            className="university-card"
            key={university.id}
          >
            <span className="eyebrow">
              {university.flag} / {university.country}
            </span>
            <h2>{university.name}</h2>
            <div className="flex flex-wrap gap-2">
              {repository.courses
                .filter((course) => university.courses[course.id])
                .map((course) => (
                  <Badge key={course.id}>{course.id.toUpperCase()}</Badge>
                ))}
            </div>
            <div className="card-bottom">
              <span>
                {
                  repository.foreignCourses.filter(
                    (item) => item.universityId === university.id,
                  ).length
                }{" "}
                disciplinas no catálogo
              </span>
              <span>↗</span>
            </div>
          </Link>
        ))}
      </div>
      {!results.length && (
        <Empty>
          Nenhuma instituição encontrada. Tente outro país ou curso.
        </Empty>
      )}
    </div>
  );
}
