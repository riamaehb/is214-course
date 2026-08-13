# IS 214 Lessons — site structure

    is214-course/
    ├── assets/
    │   ├── style.css      ← shared design system (fonts, colors, diagrams, checks, nav)
    │   └── lesson.js       ← shared pagination + check/reveal interactivity
    ├── lessons/
    │   ├── topic1.html     ← Topic 1, built and finished
    │   ├── topic2.html      (add as you build them)
    │   └── ...
    └── TEMPLATE.html       ← starting point for a new topic (copy into lessons/)

## Adding a new topic

1. Copy `TEMPLATE.html` into `lessons/topicN.html`.
2. Update the `<title>`, the `Topic N` labels in the top bar, and the hero slide's title/objectives.
3. Add one `<section class="slide" id="slide-N">…</section>` per page, in order. The comment block
   in the template shows the markup for diagrams, code blocks, callouts, and both check-question
   styles — copy the pattern that fits, from either the template or `lessons/topic1.html`.
4. No JS or CSS edits needed — `lesson.js` counts however many `.slide` sections exist and wires up
   navigation and every `.check`/`.reveal-btn` automatically.

## Editing the shared look

Any change to `assets/style.css` (colors, spacing, fonts) applies to every lesson at once, since they
all link to the same file. Same for `assets/lesson.js` — fix a bug or add a feature there once, and
it's live everywhere.

## Embedding in Moodle

Each `lessons/topicN.html` is a complete, self-contained page (once the two `assets/` files are
alongside it on GitHub Pages). Embed via iframe, e.g.:

    <iframe src="https://YOUR-USERNAME.github.io/is214-course/lessons/topic1.html"
            width="100%" height="1550" style="border:0;"
            title="IS 214 Topic 1 — Programming Languages and Paradigms"></iframe>

~1550px height fits every slide without internal scrolling (needed to avoid iframe scroll-trapping —
see chat notes). Adjust per-topic if a later lesson's tallest slide differs significantly.
