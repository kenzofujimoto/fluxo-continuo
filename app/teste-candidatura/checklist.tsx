"use client";
import { useState } from "react";
import styles from "./preview.module.css";
const documents = [
  "Foto JPEG",
  "Passaporte PDF",
  "Carta de motivação por destino",
  "Carta de recomendação por destino",
  "Plano de estudos por destino",
  "Histórico e traduções aplicáveis",
  "Certificado de idioma ou isenção comprovada + termo",
  "Termo de compromisso assinado",
];
export function Checklist() {
  const [checked, setChecked] = useState<string[]>([]);
  return (
    <div className={styles.checklist}>
      <div className={styles.progress}>
        <strong aria-live="polite">
          {checked.length} de {documents.length} preparados
        </strong>
        <span>Até 10 MB por arquivo · PDFs, exceto foto</span>
      </div>
      {documents.map((document) => (
        <label key={document}>
          <input
            type="checkbox"
            checked={checked.includes(document)}
            onChange={() =>
              setChecked((current) =>
                current.includes(document)
                  ? current.filter((item) => item !== document)
                  : [...current, document],
              )
            }
          />
          <span>{document}</span>
        </label>
      ))}
    </div>
  );
}
