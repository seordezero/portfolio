# Editing the portfolio

All projects come from the folders in `content/projects/`. To add, edit, or
remove a project you only touch these folders — never the code.

## Add a new project

1. Create a folder `content/projects/<slug>/` (the `<slug>` becomes the URL,
   e.g. `my-new-project` → `/projects/my-new-project`). Use lowercase and
   dashes, no spaces.
2. Drop the images inside (`.jpg`, `.jpeg`, or `.png`). They are shown in
   filename order, so name them `01.jpg`, `02.jpg`, … if order matters.
3. (Optional) For any image add a text file with the **same name** for its
   caption, e.g. `01.txt`:

   ```
   Title of the image
   A longer description that shows next to the zoomed image.
   ```

4. Add a `project.txt` describing the project:

   ```
   Year: 2024
   Category: Architecture        (Architecture | Design | Parametric | Audiovisual | Research)
   Title: My New Project
   Subtitle: a short subtitle
   Cover: 1                       (optional — which image is the catalog thumbnail)
   Collaborators: Ada Lovelace, Alan Turing   (optional)
   Link: https://example.com      (optional — an external link button)

   First paragraph of the description.

   # A Chapter Heading
   Another paragraph. Leave a blank line between paragraphs.
   ```

5. Tell me to push. A **new project automatically gets a fresh colour and
   background** from the palette (existing projects keep theirs — assignments
   are remembered in `content/assignments.json`).

## Edit / remove

- Edit the `.txt` files or swap images in a folder to change a project.
- Delete a folder to remove a project.

## Regenerate (done before pushing)

```
npm run content      # processes images + rebuilds content.json
```

This writes the 512×512 thumbnails and capped full-res images into
`public/images/` and regenerates `src/data/content.json`. The site renders
entirely from that file.
