import Link from "next/link";
export default function NotFound() {
  return (
    <div className="page-shell">
      <p className="eyebrow">404 / Rota não encontrada</p>
      <h1>
        Vamos encontrar
        <br />
        outro caminho.
      </h1>
      <p>Esse registro não existe na base ou o endereço mudou.</p>
      <Link className="button dark" href="/">
        Voltar ao início →
      </Link>
    </div>
  );
}
