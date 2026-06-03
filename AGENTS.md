## Cursor Cloud specific instructions

This is a static HTML site (soccer recruitment profile) with no build system, package manager, or backend. The entire application is a single `index.html` file styled with Tailwind CSS loaded via CDN.

### Running the dev server

Serve the site with any static HTTP server from the repo root:

```
python3 -m http.server 8080
```

Then open `http://localhost:8080/` in Chrome.

### Key notes

- **No dependencies to install.** There is no `package.json`, `requirements.txt`, or any dependency file.
- **No lint, test, or build steps.** The project has no automated tests, linter config, or build pipeline.
- **Tailwind CSS is loaded from CDN** (`https://cdn.tailwindcss.com`), so internet access is required for styling to render.
- **Images** (`IMG_3925.jpg`, `aaron-shot-4.jpg`) are committed directly in the repo root.
