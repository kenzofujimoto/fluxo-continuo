import type { Metadata } from "next";
import Link from "next/link";
import { getDestinations } from "../../lib/destinations";
import { universityLocations } from "../../lib/locations";
import { PreviewGlobe } from "./preview-globe";
import styles from "./preview.module.css";

export const metadata: Metadata = {
  title: "Prévia do início",
  robots: { index: false, follow: false },
};

export default function HomePreview() {
  return (
    <section className={styles.hero} aria-labelledby="preview-title">
      <div className={styles.copy}>
        <p className={styles.eyebrow}>Seu próximo capítulo</p>
        <h1 id="preview-title">
          Seu próximo semestre,
          <br />
          <em>mais longe.</em>
        </h1>
        <p className={styles.intro}>
          Explore universidades e compare disciplinas para seu intercâmbio.
        </p>
        <div className={styles.actions}>
          <Link href="/universidades" className={styles.primary}>
            Explorar destinos <span aria-hidden="true">↗</span>
          </Link>
          <Link href="/comparacoes" className={styles.secondary}>
            Comparar ementas <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
      <PreviewGlobe
        destinations={getDestinations()}
        origin={universityLocations.origin}
      />
    </section>
  );
}
