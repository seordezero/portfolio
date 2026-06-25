// Projects are generated from the content/ folders by scripts/build_content.py
// into content.json. Do not edit content.json by hand — edit the folders and
// re-run the build script.
import content from "./content.json";

export interface ProjectImage {
  file: string;
  title: string;
  desc: string;
}

export interface BodyBlock {
  type: "p" | "h2";
  text: string;
}

export interface Project {
  slug: string;
  title: string;
  subtitle: string;
  year: number;
  category: "Architecture" | "Design" | "Parametric" | "Audiovisual" | "Research";
  cover: number;
  link: string;
  square: string;
  backdrop: string;
  ink: string;
  inkBackdrop: string;
  collaborators: string[];
  body: BodyBlock[];
  images: ProjectImage[];
}

export const projects: Project[] = content.projects as Project[];
