# Acceptance evidence

The end-to-end integration was exercised on November 22, 2026 with synthetic inputs and dedicated container workloads.

| Check | How it was verified |
| --- | --- |
| Blender from Gemini | The user authorized the connector with a passkey. Gemini submitted an approved sample scene for rendering and checked its status. The worker reported completion and a 35,013-byte PNG at 256 × 256. The runtime was independently checked. |
| Blender job isolation | A separate smoke test checked that the input file could not be written, an unrelated canary file was invisible, the container only had loopback networking, and the scene bytes were unchanged after rendering. |
| ArtCraft native execution | The suite batch ran 17 jobs in 17 separate containers and checked 54 before-and-after native operation steps. Some steps repeated an operation, so the distinct catalog size is 53. |
| ArtCraft from Gemini | An authorized WordCraft request ran two named operations in order, appending and then replacing text. The same connector later initiated the PDF edit described below. |
| Private file round trip | Uploaded the synthetic original in the browser, used Gemini to request a 90° rotation, waited for the isolated PdfCraft job, and downloaded the result from the authenticated portal. A PDF parser verified the rotation and the preserved text. |
| Authorization regressions | Automated checks covered invalid WebAuthn signatures, challenge replay, unexpected origins, OAuth resource scoping, and access to file bytes through a human session. |

The [published Blender PNG](../evidence/samples/blender-sample-render.png) comes from a separate local replay of the approved cube fixture with the same native task. The replay used a networkless container and a read-only input mount, and the resulting PNG decoded at 256 × 256 pixels.

## ArtCraft native coverage

The suite ran one ordered workflow per app. These are the steps recorded as verified by the runner.

| App | Workflow |
| --- | --- |
| AniCraft | Add a layer, draw a shape, rename the layer |
| CadCraft | Draw a line and a rectangle, move entities |
| Craft Anything | Write a brief, set the plan, write a handoff |
| DeckCraft | Add a slide and a text box, set the slide title |
| DesignCraft | Add a page and a text frame, replace the primary text |
| EffectCraft | Add a composition and a text layer, set layer opacity |
| FigCraft | Add a frame and text, rename the layer |
| FilmCraft | Add a sequence, a track, and a marker |
| GridCraft | Set a cell, write a table, style a range |
| LightCraft | Create and rename an album, adjust sample exposure |
| MaterialCraft | Add two color nodes, change one color, blend the nodes |
| PdfCraft | Insert a page, add text, rotate the page, set the title |
| PhotoCraft | Create a canvas, adjust brightness and saturation, add a brightness layer |
| SoundCraft | Add and rename a track, add a marker |
| TextureCraft | Add a fill, rename the layer, recolor the fill |
| VectorCraft | Draw and recolor a shape, add text |
| WordCraft | Append and replace text, insert a table |

## Review the PDF

[Original PDF](../evidence/samples/pdfcraft-original.pdf) · [Edited PDF](../evidence/samples/pdfcraft-edited.pdf)

Both documents contain the same one-page studio note. The original is upright and the exported page is rotated clockwise. In a viewer with auto-rotation, inspect the page properties or use the check below.

```bash
python -m venv .venv
# Activate the environment, then install the verification dependency.
python -m pip install -r review/requirements.txt
python review/verify_pdf.py
```

## Run the ArtCraft contract tests

With Node.js 22.12 or newer, from the repository root:

```bash
npm ci
npm test
```

These tests cover the app catalog, ordered edits, malformed requests, unsupported operations, incorrect arguments, and the plain-text spreadsheet rule. Native editor execution is covered by the separate acceptance runs above. The public excerpt adapts the validator for standalone Node use, including JSON imports and an input size check before parsing.
