import type { getRepository, Review } from "./data";
export type PlanningOption = {
  key: string;
  universityId: string;
  foreign: string[];
  level: "high" | "partial";
  reviewId: string;
  href: string;
  name: string;
  foreignNames: string[];
  hours: string;
  limitations: string[];
};

// Maximum bipartite matching. Bundles are deliberately excluded until jointly reviewed.
export function choosePlan(
  options: PlanningOption[],
  selected: string[],
): PlanningOption[] {
  const keys = new Set(selected);
  const candidates = options
    .filter((option) => keys.has(option.key) && option.foreign.length === 1)
    .sort(
      (a, b) =>
        Number(b.level === "high") - Number(a.level === "high") ||
        a.reviewId.localeCompare(b.reviewId),
    );
  const byKey = new Map<string, PlanningOption[]>();
  for (const option of candidates)
    byKey.set(option.key, [...(byKey.get(option.key) ?? []), option]);
  const assigned = new Map<string, PlanningOption>();
  function augment(key: string, visited: Set<string>): boolean {
    for (const option of byKey.get(key) ?? []) {
      const foreign = option.foreign[0];
      if (visited.has(foreign)) continue;
      visited.add(foreign);
      const previous = assigned.get(foreign);
      if (!previous || augment(previous.key, visited)) {
        assigned.set(foreign, option);
        return true;
      }
    }
    return false;
  }
  for (const key of byKey.keys()) augment(key, new Set());
  return [...assigned.values()].sort(
    (a, b) =>
      Number(b.level === "high") - Number(a.level === "high") ||
      a.name.localeCompare(b.name),
  );
}

export function buildPlanningOptions(
  repository: Pick<
    ReturnType<typeof getRepository>,
    "reviews" | "universities" | "foreignCourses"
  >,
  reviewPath: (review: Review) => string,
): PlanningOption[] {
  return repository.reviews
    .filter(
      (review) =>
        ["alta_afinidade", "afinidade_parcial"].includes(
          review.conclusionClass,
        ) &&
        review.brazil.sha256 &&
        review.foreign.length === 1 &&
        review.foreign.every(
          (item) =>
            item.sha256 &&
            repository.universities.some(
              (university) =>
                university.id === item.universityId &&
                university.courses[review.brazil.courseId],
            ) &&
            !repository.foreignCourses.some(
              (course) =>
                course.universityId === item.universityId &&
                course.code === item.code &&
                course.sourceEligibility === "outside_agreement",
            ),
        ),
    )
    .map((review) => ({
      key: review.brazil.courseId + "|" + review.brazil.code,
      universityId: review.foreign[0].universityId,
      foreign: review.foreign.map((item) => item.code),
      level: review.conclusionClass === "alta_afinidade" ? "high" : "partial",
      reviewId: review.id,
      href: reviewPath(review),
      name: review.brazil.name,
      foreignNames: review.foreign.map((item) => item.name),
      hours: review.hoursComparison.reason || review.hoursComparison.state,
      limitations: [
        ...review.limitations,
        ...review.foreign.flatMap((item) =>
          [
            item.language && `Idioma: ${item.language}`,
            item.period && `Período: ${item.period}`,
            item.prerequisites && `Pré-requisitos: ${item.prerequisites}`,
          ].filter((value): value is string => Boolean(value)),
        ),
      ],
    }));
}
