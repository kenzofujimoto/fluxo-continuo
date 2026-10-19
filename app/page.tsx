import Link from "next/link";
import { getRepository } from "../lib/data";
import { getDestinations } from "../lib/destinations";
import { universityLocations } from "../lib/locations";
import { PreviewGlobe } from "./teste-inicio/preview-globe";
import styles from "./teste-inicio/preview.module.css";
import homeStyles from "./home.module.css";

export default function Home() {
  const { courses } = getRepository();
  return (
    <>
      <section className={styles.hero} aria-label="Explore seu próximo destino">
        <div className={styles.copy}>
          <p className={styles.eyebrow}>MackJr · Fluxo contínuo</p>
          <h1>
            Seu próximo semestre,
            <br />
            <em>mais longe.</em>
          </h1>
          <p className={styles.intro}>
            Explore destinos e encontre possibilidades para o seu plano de
            estudos.
          </p>
          <div className={styles.actions}>
            <Link className={styles.primary} href="#cursos">
              Escolher meu curso <span aria-hidden="true">↓</span>
            </Link>
            <Link className={styles.secondary} href="/universidades">
              Explorar destinos ↗
            </Link>
          </div>
        </div>
        <PreviewGlobe
          destinations={getDestinations()}
          origin={universityLocations.origin}
        />
      </section>
      <section className="section" id="cursos" aria-labelledby="courses-title">
        <div className="section-title">
          <div>
            <p className="eyebrow">Comece pelo seu curso</p>
            <h2 id="courses-title">
              Seu curso,
              <br />
              <em>novas possibilidades.</em>
            </h2>
          </div>
          <p>
            Explore suas disciplinas e filtre pela etapa que você está cursando.
          </p>
        </div>
        <div className="course-grid">
          {courses.map((course, index) => (
            <Link
              key={course.id}
              href={`/disciplinas?curso=${course.id}`}
              className="course-card"
            >
              <span className="eyebrow">0{index + 1} / Alphaville</span>
              <h3>{course.name}</h3>
              <div className="card-bottom">
                <span>Explorar disciplinas</span>
                <span className="round-arrow" aria-hidden="true">
                  ↗
                </span>
              </div>
            </Link>
          ))}
        </div>
        <div className={homeStyles.supportLinks}>
          <Link className="text-link" href="/candidatura">
            Como se candidatar ↗
          </Link>
          <Link className="text-link" href="/plano">
            Montar meu plano de estudos ↗
          </Link>
        </div>
      </section>
    </>
  );
}
