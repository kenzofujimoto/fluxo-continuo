"use client";

import { useId } from "react";

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
  const filterId = `country-duotone-${useId().replace(/:/g, "")}`;
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
      <defs>
        <filter id={filterId} colorInterpolationFilters="sRGB">
          <feColorMatrix type="saturate" values="0" />
          <feComponentTransfer>
            <feFuncR type="discrete" tableValues="0.902 0.945" />
            <feFuncG type="discrete" tableValues="0.2 0.925" />
            <feFuncB type="discrete" tableValues="0.133 0.890" />
          </feComponentTransfer>
        </filter>
      </defs>
      <image
        href={`/flags/${normalizedCode}.svg`}
        width="640"
        height="480"
        filter={`url(#${filterId})`}
      />
    </svg>
  );
}
