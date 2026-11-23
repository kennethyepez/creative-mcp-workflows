# Blender & ArtCraft MCP

Two Model Context Protocol integrations that turn Gemini requests into Blender renders, editable 3D meshes and native edits across 17 ArtCraft applications. Each job runs in an isolated container in a dedicated test environment.

**Kenneth Yepez · Engineering portfolio**

## The problem

A chat assistant can describe a creative edit, but delivering the result means opening the right application, working on the right input, and checking the exported file. Giving a remote assistant desktop or shell access would also put unrelated files and services within reach. With 17 editors, configuring a separate connector for each would add setup and make permissions harder to review.

The solution gives Gemini two purpose-built connectors. Blender renders, inspects and exports approved scenes. ArtCraft exposes one catalog for native creation and editing across the suite. A separate passkey-protected file portal lets users upload a document, ask Gemini to edit it by reference, and download the result.

| Workflow | Observed result |
| --- | --- |
| **Blender** | Gemini Task returned a downloadable **GLB 2.0** from the isolated Blender worker. The sample contains **one mesh and 12 triangles**. A separate render produced a **256 × 256 PNG**. |
| **ArtCraft Suite** | One connector exposed **53 creation and editing operations** across **17 apps**. A test batch verified **54 native steps** in 17 separate containers. A Gemini request separately ran two ordered WordCraft edits in one revision. |
| **Private files** | A synthetic PDF went through browser upload, a Gemini-triggered edit, and authenticated download. The first page rotated **90° clockwise** and retained its text. |

## Screenshots

### Blender authorization

The authorization screen presents the approved-scene workflow and asks the user to confirm access with a passkey.

![Blender authorization screen showing approved-scene tools and the Authorize with passkey button](evidence/screenshots/blender-authorization.jpg)

**[Download the original sample GLB](evidence/samples/blender-sample-cube.glb?raw=1).** The mesh was exported by Blender and downloaded through Gemini Task. The image below comes from a separate render of the same sample scene.

![Blender Cycles render of a gray sample cube, 256 by 256 pixels](evidence/samples/blender-sample-render.png)

### ArtCraft file editing

The private portal shows a completed PDF edit and offers a separate download for the result. This capture contains only the synthetic acceptance-test files.

![ArtCraft portal showing the edited sample PDF ready to download, alongside the upload control](evidence/screenshots/artcraft-file-result.jpg)

## Review the implementation

- [Architecture and security controls](docs/architecture.md) covers the trust boundaries, file handling, and trade-offs.
- [Acceptance evidence](docs/verification.md) records what was checked from Gemini, what ran in the container suite, and what reviewers can reproduce offline.
- [ArtCraft operation validation](review/artcraft/authoring.mjs) and [contract tests](review/artcraft/authoring.test.mjs) show how ordered requests are converted into a typed, bounded job payload.
- [Blender scene task](review/blender/blender-task.py) and [GLB exporter](review/blender/export-glb.py) show the inspection, headless rendering and mesh export.
- [VectorCraft tool contract](review/artcraft/vector-svg.mjs) shows the bounded SVG creation inputs and their conversion to a native operation.

The public repository is a technical case study with selected implementation code and synthetic artifacts. It runs review checks locally without accounts or access to the private deployment.
