"use client";

import Link from "next/link";
import { useState } from "react";
import styles from "./course-entry.module.css";

type EntryCourse = { id: string; name: string; stages: number[] };

export function CourseEntry({ courses }: { courses: EntryCourse[] }) {
  const [courseId, setCourseId] = useState(courses[0]?.id ?? "cc");
  const [stage, setStage] = useState("");
  const course = courses.find((item) => item.id === courseId) ?? courses[0];
  const params = new URLSearchParams({ curso: courseId });
  if (stage) params.set("etapa", stage);
  return (
    <section className={styles.shell} aria-labelledby="course-entry-title">
      <div className={styles.topline}>
        <span>Um semestre de possibilidades</span>
        <Link href="/teste-candidatura">Como se candidatar ↗</Link>
      </div>
      <header className={styles.heading}>
        <h1 id="course-entry-title">
          Seu curso.
          <br />
          <em>Seu próximo destino.</em>
        </h1>
        <p>Comece pela sua matriz. Descubra o que você pode estudar lá fora.</p>
      </header>
      <fieldset className={styles.courses}>
        <legend>01 / Escolha seu curso</legend>
        {courses.map((item, index) => (
          <label key={item.id} className={styles.card}>
            <input
              type="radio"
              name="curso"
              value={item.id}
              checked={courseId === item.id}
              onChange={() => {
                setCourseId(item.id);
                setStage("");
              }}
            />
            <span className={styles.cardBody}>
              <span className={styles.number}>
                0{index + 1}
                <span aria-hidden="true">↗</span>
              </span>
              <strong>{item.name}</strong>
              <span className={styles.choice}>
                {courseId === item.id
                  ? "Curso selecionado"
                  : "Selecionar curso"}
              </span>
            </span>
          </label>
        ))}
      </fieldset>
      <div className={styles.bottom}>
        <label className={styles.stage}>
          02 / Filtre por etapa
          <select
            value={stage}
            onChange={(event) => setStage(event.target.value)}
            name="etapa"
          >
            <option value="">Todas as etapas</option>
            {course?.stages.map((value) => (
              <option value={value} key={value}>
                {value}ª etapa
              </option>
            ))}
          </select>
        </label>
        <div className={styles.actions}>
          <Link className={styles.primary} href={`/disciplinas?${params}`}>
            Explorar disciplinas <span aria-hidden="true">→</span>
          </Link>
          <Link className={styles.secondary} href={`/teste-plano?${params}`}>
            Montar meu plano de estudos ↗
          </Link>
        </div>
      </div>
    </section>
  );
}
