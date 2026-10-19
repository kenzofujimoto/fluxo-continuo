import { filteredPageMetadata } from "../../lib/page-metadata";
import Link from "next/link";
import { availableStages, filterByStage, parseStage } from "../../lib/stages";
import {
  disciplineKey,
  disciplinePath,
  getRepository,
  searchDisciplines,
} from "../../lib/data";
import {
  Badge,
  CourseSelect,
  Empty,
  Heading,
  Pagination,
  Search,
  pageNumber,
  queryValue,
  type Query,
} from "../ui";
export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  return filteredPageMetadata("Disciplinas", await searchParams);
}
export default async function Disciplines({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const degree = queryValue(query, "curso");
  const stage = parseStage(queryValue(query, "etapa"));
  const courses = getRepository().courses.filter(
    (course) => !degree || course.id === degree,
  );
  const stages = availableStages(courses.flatMap((course) => course.rows));
  const results = filterByStage(
    searchDisciplines(queryValue(query, "q"), degree),
    stage,
  );
  const page = pageNumber(query, results.length);
  const { reviews, pending } = getRepository();
  return (
    <div className="page-shell">
      <Heading eyebrow="01 / Sua matriz curricular" title="Daqui para o mundo.">
        Escolha uma disciplina para consultar sua ementa, candidatas
        estrangeiras e análises documentadas.
      </Heading>
      <form className="filters">
        <Search query={queryValue(query, "q")} />
        <CourseSelect value={degree} />
        <label>
          Etapa da matriz
          <select name="etapa" defaultValue={stage}>
            <option value="">Todas as etapas</option>
            {stages.map((value) => (
              <option key={value} value={value}>
                {value}ª etapa
              </option>
            ))}
            <option value="nao-informada">Etapa não informada</option>
          </select>
        </label>
        <button className="button dark" type="submit">
          Buscar →
        </button>
        <Link className="reset" href="/disciplinas">
          Limpar
        </Link>
      </form>
      <p className="result-count">
        {results.length} disciplinas encontradas · matrizes de Alphaville
      </p>
      <div className="discipline-list">
        {results.slice((page - 1) * 36, page * 36).map(({ course, row }) => {
          const key = disciplineKey(row);
          const count = reviews.filter(
            (review) =>
              review.brazil.courseId === course.id &&
              review.brazil.code === key,
          ).length;
          const status = pending.brazil[course.id]?.rows.find(
            (item) => item.code === key,
          );
          return (
            <Link
              className="discipline-row"
              key={`${course.id}|${key}`}
              href={disciplinePath(course.id, row)}
            >
              <span className="eyebrow">
                {course.id.toUpperCase()} /{" "}
                {row.semester
                  ? `${row.semester}ª etapa`
                  : "Etapa não informada"}
              </span>
              <div>
                <h2>{row.name}</h2>
                <span className="muted">
                  {row.id ?? "Sem código informado"} ·{" "}
                  {status?.label ?? "Documentação a verificar"}
                </span>
              </div>
              <Badge tone={count ? "lime" : ""}>
                {count ? `${count} pareceres` : "Sem parecer"}
              </Badge>
              <span className="arrow">↗</span>
            </Link>
          );
        })}
      </div>
      {results.length === 0 && (
        <Empty>
          Não encontramos disciplinas com esses filtros. Tente outro nome ou
          selecione todos os cursos.
        </Empty>
      )}
      <Pagination
        total={results.length}
        page={page}
        query={query}
        base="/disciplinas"
      />
    </div>
  );
}
