import json
from pathlib import Path
import sys

import bpy


def main() -> None:
    action, = sys.argv[sys.argv.index("--") + 1:]
    scene = bpy.context.scene
    if action == "fixture":
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = 4
        scene.cycles.use_denoising = False
        bpy.ops.wm.save_as_mainfile(filepath="/output/scene.blend")
        return

    if action == "inspect":
        result = {
            "object_count": len(scene.objects),
            "mesh_count": sum(obj.type == "MESH" for obj in scene.objects),
            "has_camera": scene.camera is not None,
        }
        Path("/output/scene.json").write_text(json.dumps(result), encoding="utf-8")
        return

    if action != "render" or not scene.camera:
        raise ValueError("The scene must have a camera and use a supported action")

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.use_multiview = False
    scene.render.use_sequencer = False
    scene.render.use_compositing = False
    scene.render.filepath = "/output/render.png"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
