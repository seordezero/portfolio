# Sebastián Ortiz de Zevallos — Portfolio

Static portfolio site built with [Astro](https://astro.build).

## Local development

Requires Node 20.3+ or 22 LTS.

```bash
# Install dependencies (first time only)
npm install

# Start the dev server at http://localhost:4321
npm run dev

# Build for production
npm run build

# Preview the production build locally
npm run preview
```

## Project structure

```
.
├── public/              Static assets served as-is (favicon, images)
├── src/
│   ├── data/
│   │   └── projects.ts  Single source of truth for all projects
│   ├── layouts/
│   │   └── Base.astro   Header + footer wrapper
│   ├── pages/
│   │   ├── index.astro      Homepage (project index)
│   │   ├── about.astro      About page
│   │   ├── contact.astro    Contact page
│   │   └── projects/
│   │       ├── index.astro      /projects (full list)
│   │       └── [slug].astro     /projects/[slug] (one per project)
│   └── styles/
│       └── global.css   Site-wide stylesheet
├── astro.config.mjs
├── package.json
└── tsconfig.json
```

## Adding a new project

Open `src/data/projects.ts` and add an entry:

```ts
{
  slug: "url-friendly-slug",
  title: "Project Title",
  subtitle: "Optional descriptive subtitle",
  year: 2026,
  category: "Architecture", // or "Parametric" | "Audiovisual" | "Research"
  description: "A paragraph describing the project.",
}
```

Astro will automatically generate `/projects/url-friendly-slug` at build time.

## Deployment

Connected to Cloudflare Pages — pushes to `main` deploy automatically.
