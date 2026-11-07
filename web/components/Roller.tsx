const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

/** A stamped counter. Each digit steps in whole line-heights; `places` keeps the width steady. */
export function Roller({ value, places, label }: { value: number; places: number; label: string }) {
  const digits = String(value).padStart(places, "0").split("");
  return (
    <>
      <span className="sr-only">{label}</span>
      <span className="roller" aria-hidden="true">
        {digits.map((digit, i) => (
          <span
            key={i}
            className="roller-digit"
            style={{ transform: `translateY(-${Number(digit)}em)` }}
          >
            {DIGITS.map((d) => <b key={d}>{d}</b>)}
          </span>
        ))}
      </span>
    </>
  );
}
