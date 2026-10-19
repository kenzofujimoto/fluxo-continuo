import { comparisonPath, disciplineKey, getRepository } from "../../lib/data";
import { buildPlanningOptions } from "../../lib/planning";
import Planner from "./planner";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = await searchParams;
  const courses = getRepository().courses;
  const course = courses.find((item) => item.id === query.curso) ?? courses[0];
  return { title: `Meu plano de estudos · ${course.name}` };
}
export default async function PlanningPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const repository = getRepository();
  const params = await searchParams;
  const course =
    repository.courses.find((course) => course.id === params.curso) ??
    repository.courses[0];
  const requestedStage = typeof params.etapa === "string" ? params.etapa : "";
  const initialStage =
    /^\d+$/.test(requestedStage) &&
    course.rows.some((row) => String(row.semester ?? 0) === requestedStage)
      ? requestedStage
      : "all";
  const options = buildPlanningOptions(repository, comparisonPath);
  return (
    <Planner
      key={course.id + ":" + initialStage}
      initialCourseId={course.id}
      initialStage={initialStage}
      courses={repository.courses.map((course) => ({
        id: course.id,
        name: course.name,
        rows: course.rows.map((row) => ({
          key: course.id + "|" + disciplineKey(row),
          name: row.name,
          stage: row.semester ?? 0,
        })),
      }))}
      options={options}
      universities={repository.universities.map((university) => ({
        id: university.id,
        name: university.name,
        country: university.country,
        language: university.language.required || "Idioma a confirmar",
      }))}
    />
  );
}
