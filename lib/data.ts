import { z } from "zod";
import dataset from "../data.json";
import reviewIndex from "../syllabi/pareceres-index.json";
import programIndex from "../syllabi/programas.json";
import documentIndex from "../syllabi/records.json";
import pendingIndex from "../syllabi/pendencias-documentais.json";

const optionalText = z.string().nullish();
const rowSchema = z.looseObject({
  id: z
    .string()
    .optional()
    .transform((value) => value || undefined),
  name: z.string(),
  semester: z.number().optional(),
  hours: z.number().nullish(),
  syllabusUrl: optionalText,
  abstract: optionalText,
  kind: optionalText,
});
const courseSchema = z.looseObject({
  id: z.string(),
  name: z.string(),
  matrix: z.string(),
  source: z.string(),
  rows: z.array(rowSchema),
});
const languageSchema = z.looseObject({
  required: optionalText,
  acceptedTests: optionalText,
  minimumScore: optionalText,
  notes: optionalText,
  source: optionalText,
  dataIssue: z.boolean().optional(),
  mlcAccepted: z.boolean().nullish(),
});
const universitySchema = z.looseObject({
  id: z.string(),
  name: z.string(),
  country: z.string(),
  flag: z.string(),
  website: optionalText,
  catalogUrl: optionalText,
  courses: z.record(z.string(), z.boolean()),
  language: languageSchema,
  availabilityNote: optionalText,
});
const foreignSchema = z.looseObject({
  universityId: z.string(),
  code: z.string(),
  name: z.string(),
  topics: optionalText,
  source: z.string(),
  contactHours: z.number().nullish(),
  credits: z.union([z.string(), z.number()]).nullish(),
  period: optionalText,
  limitations: optionalText,
});
const matchSchema = z
  .looseObject({
    courseId: z.string(),
    mackCode: z.string(),
    mackName: z.string(),
    universityId: z.string(),
    foreignCode: z.string(),
    status: z.string(),
    evidence: z.string(),
  })
  .transform((match) => ({
    ...match,
    mackCode: match.mackCode || match.mackName,
  }));
const datasetSchema = z.object({
  meta: z.looseObject({
    asOf: z.string(),
    semester: z.string(),
    institutionalDisclaimer: z.string(),
  }),
  courses: z.array(courseSchema).min(1),
  universities: z.array(universitySchema).min(1),
  foreignCourses: z.array(foreignSchema),
  matches: z.array(matchSchema),
});
const hoursSchema = z.looseObject({
  value: z.number().nullish(),
  unit: optionalText,
  basis: optionalText,
  note: optionalText,
  contactTotal: z.number().nullish(),
  ects: z.number().nullish(),
  totalWorkload: z.number().nullish(),
  hourLengthMinutes: z.number().nullish(),
});
const reviewSchema = z.looseObject({
  id: z.string(),
  type: z.string(),
  brazil: z.looseObject({
    courseId: z.string(),
    code: z.string(),
    name: z.string(),
    courseName: z.string(),
    source: z.string(),
    sha256: optionalText,
    documentYear: z.number().nullish(),
    documentTitle: optionalText,
    location: optionalText,
    hours: hoursSchema,
    topics: z.array(z.string()),
  }),
  foreign: z.array(
    z.looseObject({
      universityId: z.string(),
      university: z.string(),
      code: z.string(),
      name: z.string(),
      source: z.string(),
      sha256: optionalText,
      location: optionalText,
      academicYear: optionalText,
      language: optionalText,
      period: optionalText,
      prerequisites: optionalText,
      hours: hoursSchema,
    }),
  ),
  topics: z.array(
    z.looseObject({
      brTopic: z.string(),
      status: z.string(),
      essential: z.boolean().optional(),
      foreignEvidence: optionalText,
      foreignLocation: optionalText,
      note: optionalText,
      scopeExamined: optionalText,
    }),
  ),
  conclusionClass: z.string(),
  institutionalStatus: z.string(),
  synthesis: z.string(),
  justification: optionalText,
  confidence: z.string(),
  confidenceRationale: optionalText,
  limitations: z.array(z.string()),
  openQuestions: z.array(z.string()).optional(),
  reviewedAt: z.string(),
  practical: z.record(z.string(), z.unknown()).optional(),
  hoursComparison: z.looseObject({ state: z.string(), reason: optionalText }),
  secondReview: z
    .looseObject({ required: z.boolean(), reason: optionalText })
    .optional(),
  brazilDocumentCurrent: z.boolean().optional(),
  method: optionalText,
});
const programSchema = z.looseObject({
  source: optionalText,
  sha256: optionalText,
  documentYear: z.number().nullish(),
  current: z.boolean().optional(),
  currencyNote: optionalText,
  ementa: optionalText,
  topics: z.array(z.string()).optional(),
  hourUnit: optionalText,
  hours: z.number().nullish(),
  status: optionalText,
});
const pendingRow = z.object({
  code: z.string(),
  name: z.string(),
  category: z.string(),
  label: z.string(),
  detail: optionalText,
  source: optionalText,
});
export type Review = z.infer<typeof reviewSchema>;
export type University = z.infer<typeof universitySchema>;
export type Course = z.infer<typeof courseSchema>;
export type Discipline = z.infer<typeof rowSchema>;
export const parseDataset = (value: unknown) => datasetSchema.parse(value);
let cached: ReturnType<typeof loadRepository> | undefined;

function loadRepository() {
  const data = parseDataset(dataset);
  const reviews = z
    .object({ pareceres: z.array(reviewSchema) })
    .parse(reviewIndex).pareceres;
  const programs = z
    .object({ brazil: z.record(z.string(), programSchema) })
    .parse(programIndex).brazil;
  const records = z
    .object({
      foreign: z.array(
        z.looseObject({
          universityId: z.string(),
          foreignCode: z.string(),
          status: z.string(),
          sha256: optionalText,
          reason: optionalText,
          source: optionalText,
        }),
      ),
    })
    .parse(documentIndex).foreign;
  const pending = z
    .object({
      brazil: z.record(
        z.string(),
        z.object({ contact: z.string(), rows: z.array(pendingRow) }),
      ),
      foreign: z.array(
        z.object({
          universityId: z.string(),
          name: z.string(),
          country: z.string(),
          insufficientCatalogueCrossings: z.number(),
          missingSyllabi: z.array(
            z.looseObject({
              code: z.string(),
              name: z.string(),
              reason: z.string(),
              source: optionalText,
            }),
          ),
        }),
      ),
      coi: z.array(z.string()),
    })
    .parse(pendingIndex);
  return {
    ...data,
    reviews,
    programs,
    records,
    pending,
    stats: {
      universities: data.universities.length,
      disciplines: data.courses.reduce(
        (total, course) => total + course.rows.length,
        0,
      ),
      foreignCourses: data.foreignCourses.length,
      reviews: reviews.length,
      homologated: reviews.filter(
        (review) => review.institutionalStatus === "homologado",
      ).length,
      individualSyllabi: records.filter(
        (record) => record.status === "ementa_individual",
      ).length,
      missingPriority: pending.foreign.reduce(
        (sum, university) => sum + university.missingSyllabi.length,
        0,
      ),
      blockedCrossings: pending.foreign.reduce(
        (sum, university) => sum + university.insufficientCatalogueCrossings,
        0,
      ),
    },
  };
}

export function getRepository() {
  return (cached ??= loadRepository());
}
export const normalize = (text: string) =>
  text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
export const disciplineKey = (row: Discipline) => row.id ?? row.name;
export const disciplinePath = (courseId: string, row: Discipline) =>
  `/disciplinas/${encodeURIComponent(courseId)}/${encodeURIComponent(disciplineKey(row))}`;
export const comparisonId = (id: string) =>
  Buffer.from(id).toString("base64url");
export const comparisonPath = (review: Review) =>
  `/comparacoes/${comparisonId(review.id)}`;
export function getComparison(id: string) {
  return getRepository().reviews.find(
    (review) => comparisonId(review.id) === id,
  );
}
export function getDiscipline(courseId: string, key: string) {
  const course = getRepository().courses.find(
    (course) => course.id === courseId,
  );
  let row = course?.rows.find((row) => disciplineKey(row) === key);
  if (!row && key.includes("%")) {
    try {
      const decodedKey = decodeURIComponent(key);
      row = course?.rows.find(
        (candidate) => disciplineKey(candidate) === decodedKey,
      );
    } catch {
      return undefined;
    }
  }
  return course && row
    ? {
        course,
        row,
        program: getRepository().programs[`${courseId}|${disciplineKey(row)}`],
      }
    : undefined;
}
export function searchDisciplines(query = "", courseId = "") {
  return getRepository()
    .courses.filter((course) => !courseId || course.id === courseId)
    .flatMap((course) =>
      course.rows
        .filter((row) =>
          normalize(`${row.name} ${row.id ?? ""}`).includes(normalize(query)),
        )
        .map((row) => ({ course, row })),
    );
}
export function safeSource(value: string | null | undefined) {
  if (!value) return undefined;
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? value : undefined;
  } catch {
    return undefined;
  }
}
export function label(value: string) {
  const labels: Record<string, string> = {
    coberto: "Coberto",
    parcial: "Parcial",
    nao_encontrado: "Não encontrado",
    nao_verificavel: "Não verificável",
    afinidade_parcial: "Afinidade parcial",
    alta_afinidade: "Alta afinidade",
    evidencia_insuficiente: "Evidência insuficiente",
    afinidade_insuficiente: "Afinidade insuficiente",
    baixa_afinidade: "Baixa afinidade",
    nao_comparavel: "Não comparável",
    comparavel: "Comparável",
    comparavel_condicional: "Comparável sob condições",
    em_analise: "Em análise",
    indicio_titulo: "Indício por título",
    nao_verificado: "Não verificado",
    hora_relogio: "hora-relógio",
    hora_aula: "hora-aula",
    semestre: "semestre",
    candidata_forte: "Candidata forte",
    candidata: "Candidata",
    aguardando_validacao_institucional: "Aguardando validação institucional",
    ementa_individual: "Ementa individual",
    pagina_com_conteudo: "Página com conteúdo parcial",
    catalogo_ou_matriz: "Catálogo ou matriz",
    indisponivel: "Fonte indisponível",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}
