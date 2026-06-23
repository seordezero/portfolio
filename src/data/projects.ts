export interface Project {
  slug: string;
  title: string;
  subtitle?: string;
  year: number;
  category: "Architecture" | "Design" | "Parametric" | "Audiovisual" | "Research";
}

export const projects: Project[] = [
  { slug: "secciones-de-sonido",         title: "Secciones de Sonido",         subtitle: "un experimento en tres tiempos",     year: 2026, category: "Audiovisual"  },
  { slug: "tres-xemeneies",              title: "Tres Xemeneies de Sant Adrià", subtitle: "competition entry — Innovation Hub", year: 2024, category: "Architecture" },
  { slug: "cph-mothership",              title: "CPH Mothership",               subtitle: "X-Urban Studio, IAAC",                year: 2023, category: "Architecture" },
  { slug: "master-advanced-architecture", title: "Master in Advanced Architecture", subtitle: "IAAC, Barcelona",                year: 2023, category: "Research"     },
  { slug: "algoritmia",                  title: "Algoritmia",                   subtitle: "final year project, PUCP",            year: 2021, category: "Research"     },
  { slug: "la-bienvenida",               title: "La Bienvenida",                subtitle: "club house & condo, Peru",            year: 2021, category: "Architecture" },
  { slug: "jiron-tumbes",                title: "Jirón Tumbes",                 subtitle: "studio restoration, Barranco",        year: 2021, category: "Architecture" },
  { slug: "foldable-breakfast-table",    title: "Foldable Breakfast Table",     subtitle: "furniture for a 25 m² apartment",     year: 2021, category: "Design"       },
  { slug: "fable",                       title: "faBle",                        subtitle: "self-assembling CNC furniture",       year: 2020, category: "Design"       },
  { slug: "workshop-pucp-eth-zurich",    title: "Workshop PUCP — ETH Zürich",   subtitle: "A Room for Archeologists and Kids",   year: 2018, category: "Architecture" },
];
