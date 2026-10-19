const availableFlags = new Set([
  "de",
  "ar",
  "bo",
  "be",
  "cl",
  "co",
  "kr",
  "us",
  "es",
  "fr",
  "nl",
  "gb",
  "ie",
  "it",
  "mx",
  "pt",
  "ro",
  "tr",
  "uy",
  "at",
  "in",
]);

/** Decorative country mark; the adjacent country name provides the label. */
export function CountryFlag({ code }: { code: string }) {
  const normalizedCode = code.toLowerCase();
  if (!availableFlags.has(normalizedCode))
    return (
      <span className="country-flag-fallback" aria-hidden="true">
        {code}
      </span>
    );
  return (
    <svg
      className="country-flag"
      viewBox="0 0 640 480"
      aria-hidden="true"
      focusable="false"
    >
      <image
        href={`/flags/${normalizedCode}.svg`}
        width="640"
        height="480"
      />
    </svg>
  );
}

