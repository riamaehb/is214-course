# IS 214 Programming Exercises guide

Static site for GitHub Pages. No build step.

    index.html                overview of PE3 to the final interpreter
    pe3.html, pe4.html, pe5.html, final.html
                              one plain page per exercise (same style as the study guides);
                              pe3.html includes the language designer and the language.json download
    reference.html            language rules and conventions (the single source of truth)
    downloads/selftest.py     self-test that students run on their own files
    assets/style.css          shared with the study guides
    assets/form.css, designer.js   used only by pe3.html

PE6 (bug fixing) is a separate exercise in Moodle and is mentioned only on index.html.

Upload the folder contents to a repository root (for example `is214-exercises`) and enable Pages
from `main` and `/ (root)`. The study guides can link to it, and Moodle can link to `index.html`.

The language.json format (schema version 1.0) is described in `reference.html`.
