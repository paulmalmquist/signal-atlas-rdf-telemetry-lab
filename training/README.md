# Training materials

- `Signal_Atlas_Training.pptx`: 26 editable slides with presenter notes on every slide.
- `Signal_Atlas_Training.pdf`: rendered copy of the slides, without presenter notes.
- `../docs/TRAINING_GUIDE.md`: eight labs, a capstone, teach-back rubric and all 12 query answers.
- `../docs/EXPERT_CAPTURE.md`: a structured session to capture the SME's knowledge as definitions, mappings, queries and tests.

To rebuild the PowerPoint, install the separately scoped authoring dependency and run:

```bash
npm install --no-save --package-lock=false pptxgenjs@4.0.0
node training/build_deck.js
```

The runtime application does not need Node or this authoring package. Screenshot assets are supplied alongside the script. Refresh them using `scripts/check_browser.py` and crop/replace the corresponding `*-screen.png` assets when the app changes. A normal PowerPoint/LibreOffice export can create the PDF. Both formats were rendered and visually checked for this delivery; 26 speaker-note parts were confirmed in the PowerPoint file.
