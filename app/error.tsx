"use client";
export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="page-shell">
      <p className="eyebrow">Consulta interrompida</p>
      <h1>Não foi possível carregar a pesquisa.</h1>
      <p>
        Ocorreu um erro na leitura dos dados. Tente novamente; se persistir, a
        base precisa ser verificada.
      </p>
      <button className="button dark" onClick={reset}>
        Tentar novamente →
      </button>
    </div>
  );
}
