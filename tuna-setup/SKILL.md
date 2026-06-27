---
name: tuna-setup
description: >
  This skill should be used when adding the Tuna visual devtools overlay (@suryanewa/tuna)
  to a Vite or Next.js project. This includes installing the package and wiring the overlay
  component into the correct layout/root file, ensuring it renders only in development.
  Trigger phrases:
  "add tuna", "install tuna", "set up tuna", "tuna overlay", "add @suryanewa/tuna",
  "visual devtools overlay", "tuna next.js", "tuna vite".
---

# Tuna Setup

Install and wire the Tuna visual devtools overlay (`@suryanewa/tuna`) into a Vite or
Next.js project, restricted to development only.

Docs reference: https://github.com/suryanewa/tuna

## Runtime convention

This project uses **Bun** as the runtime. Always substitute Bun for npm:
- Install: `bun install @suryanewa/tuna` (NOT `npm install`)

## Dev-only principle

Tuna self-guards its display and only renders in development by default (it auto-detects
`process.env.NODE_ENV` and `import.meta.env.DEV` since v0.7.2). However, a *static* import
still pulls the package into the production JS bundle. To keep Tuna fully out of production
builds (no shipped code), use a **lazy/dynamic import gated by the framework's dev flag**.
Never add the `force` prop (it shows Tuna in production).

## Workflow

1. Detect the framework by looking for config files:
   - Next.js → `next.config.*` (and `app/` or `pages/`)
   - Vite → `vite.config.*`
2. Install the package:
   ```bash
   bun install @suryanewa/tuna
   ```
3. Wire the overlay into the target file (see framework sections below).
4. Verify by running the dev server (`bun run dev`) and pressing **Alt+D**
   (or **Option+D** on macOS) to toggle edit mode.

Do not add Tuna to production layouts, error boundaries, or `_document` files. Render it
once, at the app root, inside `<body>` (Next.js) or the root component fragment (Vite).

## Next.js (App Router)

Target file: `app/layout.tsx` (the root layout). Add inside `<body>`, after `{children}`.
Use `next/dynamic` so the component is a separate chunk, gated by `NODE_ENV`:

```tsx
import dynamic from "next/dynamic";

const Tuna = dynamic(
  () => import("@suryanewa/tuna").then((m) => m.Tuna),
  { ssr: false }
);

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        {process.env.NODE_ENV === "development" && <Tuna />}
      </body>
    </html>
  );
}
```

Notes:
- `ssr: false` is required — Tuna is a browser-only overlay.
- The `NODE_ENV` render gate ensures the lazy chunk is never requested in production.
- Preserve any existing `<html>`/`<body>` attributes (lang, className, fonts). Only add
  the `Tuna` import and the gated render line.

## Next.js (Pages Router)

Target file: `pages/_app.tsx`. Same `next/dynamic` pattern, gated by `NODE_ENV`, rendered
once at the end of the component:

```tsx
import dynamic from "next/dynamic";

const Tuna = dynamic(
  () => import("@suryanewa/tuna").then((m) => m.Tuna),
  { ssr: false }
);

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      {process.env.NODE_ENV === "development" && <Tuna />}
    </>
  );
}
```

## Vite

Target file: the root component, typically `src/App.tsx`. Use `React.lazy` + `Suspense`,
gated by `import.meta.env.DEV` so Vite's bundler statically eliminates the branch in
production builds:

```tsx
import { lazy, Suspense } from "react";

const Tuna = lazy(() =>
  import("@suryanewa/tuna").then((m) => ({ default: m.Tuna }))
);

export default function App() {
  return (
    <>
      {/* existing app content */}
      {import.meta.env.DEV && (
        <Suspense fallback={null}>
          <Tuna />
        </Suspense>
      )}
    </>
  );
}
```

Notes:
- `import.meta.env.DEV` is replaced statically at build time; the production build drops
  the entire branch, so `@suryanewa/tuna` is not shipped to production.
- For Astro / SvelteKit (also Vite-based), the same `import.meta.env.DEV` gate applies;
  load the React component only in dev.

## Component props (optional, defaults are correct)

Only pass props if the default behavior is insufficient. Do not pass `force`.

| Prop | Default | Use |
| --- | --- | --- |
| `port` | 9223 | WebSocket port for MCP bridge (change only if port conflicts) |
| `hotkey` | "alt+d" | Toggle hotkey |
| `fidelity` | "standard" | Output detail: "minimal" \| "standard" \| "full" |
| `position` | "bottom-right" | Toolbar position |
| `defaultOpen` | false | Open toolbar on mount |
| `force` | false | FORBIDDEN here — would show Tuna in production |

## Verification checklist

- `@suryanewa/tuna` appears in `package.json` dependencies.
- Overlay renders exactly once, at the app root (no duplicate mounts).
- Dev gate is in place (`process.env.NODE_ENV === "development"` for Next.js,
  `import.meta.env.DEV` for Vite).
- `force` prop is NOT set anywhere.
- Production build (`bun run build`) does NOT emit the Tuna chunk (check the build output
  for `@suryanewa/tuna` — it should be absent).
- In `bun run dev`, pressing Alt+D toggles Tuna edit mode and element selection works.