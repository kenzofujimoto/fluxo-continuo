"use client";
import Link from "next/link";
import { useState } from "react";
import { choosePlan, type PlanningOption } from "../../lib/planning";
import styles from "./planner.module.css";
type Props = {
  courses: {
    id: string;
    name: string;
    rows: { key: string; name: string; stage: number }[];
  }[];
  options: PlanningOption[];
  universities: {
    id: string;
    name: string;
    country: string;
    language: string;
  }[];
};
export default function Planner({ courses, options, universities }: Props) {
  const [courseId, setCourseId] = useState(courses[0].id);
  const [stage, setStage] = useState("all");
  const [selected, setSelected] = useState<string[]>([]);
  const course = courses.find((item) => item.id === courseId)!;
  const visible = course.rows.filter(
    (row) => stage === "all" || String(row.stage) === stage,
  );
  const validSelected = selected.filter((key) =>
    course.rows.some((row) => row.key === key),
  );
  const ranked = universities
    .map((university) => ({
      ...university,
      plan: choosePlan(
        options.filter((option) => option.universityId === university.id),
        validSelected,
      ),
    }))
    .filter((university) => university.plan.length)
    .sort(
      (a, b) =>
        b.plan.length - a.plan.length ||
        b.plan.filter((item) => item.level === "high").length -
          a.plan.filter((item) => item.level === "high").length ||
        a.name.localeCompare(b.name),
    );
  const toggle = (key: string) =>
    setSelected((current) =>
      current.includes(key)
        ? current.filter((item) => item !== key)
        : [...current, key],
    );
  return (
    <main className={styles.page}>
      <nav>
        <Link href="/teste-inicio">← Início da prévia</Link>
        <Link href="/teste-candidatura">Como se candidatar ↗</Link>
      </nav>
      <header>
        <p className={styles.eyebrow}>Prévia local / seu próximo semestre</p>
        <h1>
          Seu plano,
          <br />
          <em>mais longe.</em>
        </h1>
        <p>
          Marque o que falta cursar. Descubra destinos com afinidade documentada
          para conversar com sua coordenação.
        </p>
      </header>
      <div className={styles.layout}>
        <section
          className={styles.selection}
          aria-label="Disciplinas pendentes"
        >
          <h2>01. O que falta cursar?</h2>
          <label>
            Seu curso
            <select
              value={courseId}
              onChange={(event) => {
                setCourseId(event.target.value);
                setSelected([]);
                setStage("all");
              }}
            >
              {courses.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Visualizar etapa
            <select
              value={stage}
              onChange={(event) => setStage(event.target.value)}
            >
              <option value="all">Todas as etapas</option>
              {[...new Set(course.rows.map((row) => row.stage))]
                .sort((a, b) => a - b)
                .map((value) => (
                  <option key={value} value={value}>
                    {value ? `${value}ª etapa` : "Sem etapa"}
                  </option>
                ))}
            </select>
          </label>
          <p className={styles.hint}>
            O filtro só muda a lista. As disciplinas marcadas em outras etapas
            continuam no plano. Trocar de curso limpa a seleção.
          </p>
          <div className={styles.actions}>
            <button
              onClick={() =>
                setSelected((current) => [
                  ...new Set([...current, ...visible.map((row) => row.key)]),
                ])
              }
            >
              Marcar esta lista
            </button>
            <button onClick={() => setSelected([])}>Limpar seleção</button>
          </div>
          <p role="status">
            {validSelected.length} disciplinas selecionadas ·{" "}
            {
              validSelected.filter(
                (key) => !visible.some((row) => row.key === key),
              ).length
            }{" "}
            fora do filtro
          </p>
          <div className={styles.list}>
            {visible.map((row) => (
              <label className={styles.row} key={row.key}>
                <input
                  type="checkbox"
                  checked={validSelected.includes(row.key)}
                  onChange={() => toggle(row.key)}
                />
                <span>
                  {row.name}
                  <small>
                    {row.stage ? `${row.stage}ª etapa` : "Etapa não informada"}
                  </small>
                </span>
              </label>
            ))}
          </div>
        </section>
        <section aria-label="Destinos sugeridos" className={styles.results}>
          <h2>02. Onde faz sentido estudar?</h2>
          <p className={styles.hint}>
            Máximo de disciplinas distintas entre pareceres individuais
            elegíveis. Uma disciplina estrangeira só entra uma vez por destino.
            Combinações de várias matérias ficam fora desta prévia. Alta e
            parcial são afinidades, não dispensas.
          </p>
          {!validSelected.length ? (
            <div className={styles.empty}>
              Seu mapa começa nas matérias.
              <br />
              <small>Selecione ao menos uma disciplina à esquerda.</small>
            </div>
          ) : !ranked.length ? (
            <div className={styles.empty}>
              Ainda não há pareceres de afinidade alta ou parcial para esta
              seleção.
              <br />
              <small>
                Ausência de parecer não significa incompatibilidade.{" "}
                <Link href="/disciplinas">
                  Explore as disciplinas e suas fontes ↗
                </Link>
              </small>
            </div>
          ) : (
            ranked.map((university, index) => (
              <article className={styles.card} key={university.id}>
                <p className={styles.eyebrow}>
                  {String(index + 1).padStart(2, "0")} / {university.country}
                </p>
                <h3>{university.name}</h3>
                <p className={styles.score}>
                  <strong>{university.plan.length}</strong> de{" "}
                  {validSelected.length} disciplinas selecionadas
                </p>
                <p>
                  {
                    university.plan.filter((item) => item.level === "high")
                      .length
                  }{" "}
                  alta ·{" "}
                  {
                    university.plan.filter((item) => item.level === "partial")
                      .length
                  }{" "}
                  parcial · {validSelected.length - university.plan.length} sem
                  cobertura neste plano
                </p>
                <p className={styles.hint}>
                  {university.language}. Oferta no semestre, acesso do
                  intercambista, pré-requisitos e carga horária precisam ser
                  confirmados.
                </p>
                <details>
                  <summary>Ver matérias e evidências</summary>
                  {university.plan.map((item) => (
                    <div className={styles.evidence} key={item.reviewId}>
                      <h4>{item.name}</h4>
                      <p>
                        ↳ {item.foreignNames.join(" + ")} · afinidade{" "}
                        {item.level === "high" ? "alta" : "parcial"}
                      </p>
                      <p>Carga horária: {item.hours}</p>
                      <details>
                        <summary>Limitações e condições</summary>
                        <ul>
                          {item.limitations.map((limitation, i) => (
                            <li key={i}>{limitation}</li>
                          ))}
                        </ul>
                      </details>
                      <Link href={item.href}>Ler parecer e fontes ↗</Link>
                    </div>
                  ))}
                </details>
                <Link href={"/universidades/" + university.id}>
                  Conhecer universidade ↗
                </Link>
              </article>
            ))
          )}
          <aside className={styles.note}>
            Rascunho para orientação. O ranking maximiza a quantidade de
            disciplinas, sem otimizar a qualidade em empates entre combinações.
            Não verifica choque de horários, limite de créditos, calendário nem
            aprovação institucional. Leve a seleção à coordenação antes de
            definir seu plano oficial.
          </aside>
        </section>
      </div>
    </main>
  );
}
