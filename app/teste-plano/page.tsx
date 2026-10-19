import { comparisonPath, disciplineKey, getRepository } from "../../lib/data";
import { buildPlanningOptions } from "../../lib/planning";
import Planner from "./planner";

export const metadata = { title: "Meu plano de estudos · Prévia MackJr" };
export default function PlanningPage() {
  const repository = getRepository();
  const options = buildPlanningOptions(repository, comparisonPath);
  return (
    <Planner
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
