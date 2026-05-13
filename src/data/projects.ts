export interface Project {
  slug: string;
  title: string;
  subtitle?: string;
  year: number;
  category: "Architecture" | "Parametric" | "Audiovisual" | "Research";
}

export const projects: Project[] = [
  {
    slug: "secciones-de-sonido",
    title: "Secciones de Sonido",
    subtitle: "un experimento en tres tiempos",
    year: 2026,
    category: "Audiovisual",
  },
  {
    slug: "cph-mothership",
    title: "CPH Mothership",
    subtitle: "IAAC research project",
    year: 2024,
    category: "Architecture",
  },
  {
    slug: "algoritmia",
    title: "Algoritmia",
    subtitle: "thesis project, PUCP",
    year: 2023,
    category: "Research",
  },
];
