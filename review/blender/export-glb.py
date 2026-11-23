"""Write the evaluated scene's static triangle meshes as an embedded GLB."""

import json
import struct
from pathlib import Path

import bpy


MAX_BYTES = 512 * 1024
VEC3 = struct.Struct("<3f")


def gltf_coordinates(point):
    return point.x, point.z, -point.y


def append_vectors(document, binary, vectors, include_bounds=False):
    offset = len(binary)
    for vector in vectors:
        binary.extend(VEC3.pack(*vector))
    view_index = len(document["bufferViews"])
    document["bufferViews"].append({
        "buffer": 0, "byteOffset": offset, "byteLength": len(binary) - offset,
        "target": 34962,
    })
    accessor = {
        "bufferView": view_index, "componentType": 5126,
        "count": len(vectors), "type": "VEC3",
    }
    if include_bounds:
        axes = list(zip(*vectors))
        accessor["min"] = [min(axis) for axis in axes]
        accessor["max"] = [max(axis) for axis in axes]
    index = len(document["accessors"])
    document["accessors"].append(accessor)
    return index


def export_mesh(obj, document, binary):
    mesh = obj.to_mesh()
    try:
        mesh.calc_loop_triangles()
        if not mesh.loop_triangles:
            return
        if len(binary) + len(mesh.loop_triangles) * 6 * VEC3.size >= MAX_BYTES:
            raise ValueError("Mesh exceeds the GLB size limit")
        transform = obj.matrix_world
        mirrored = transform.to_3x3().determinant() < 0
        positions = []
        normals = []
        for triangle in mesh.loop_triangles:
            a, b, c = (transform @ mesh.vertices[index].co for index in triangle.vertices)
            if mirrored:
                b, c = c, b
            normal = (b - a).cross(c - a)
            if not normal.length_squared:
                continue
            positions.extend(gltf_coordinates(point) for point in (a, b, c))
            normals.extend([gltf_coordinates(normal.normalized())] * 3)
        if not positions:
            return
        position_index = append_vectors(document, binary, positions, include_bounds=True)
        normal_index = append_vectors(document, binary, normals)
        mesh_index = len(document["meshes"])
        document["meshes"].append({
            "name": obj.name,
            "primitives": [{"attributes": {"POSITION": position_index, "NORMAL": normal_index}}],
        })
        document["scenes"][0]["nodes"].append(len(document["nodes"]))
        document["nodes"].append({"name": obj.name, "mesh": mesh_index})
    finally:
        obj.to_mesh_clear()


def main():
    document = {
        "asset": {"version": "2.0", "generator": "Blender MCP"},
        "scene": 0, "scenes": [{"nodes": []}], "nodes": [], "meshes": [],
        "bufferViews": [], "accessors": [],
    }
    binary = bytearray()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            export_mesh(obj.evaluated_get(depsgraph), document, binary)
    if not document["meshes"]:
        raise ValueError("The scene has no triangles to export")
    document["buffers"] = [{"byteLength": len(binary)}]
    metadata = json.dumps(document, separators=(",", ":"), allow_nan=False).encode("utf-8")
    metadata += b" " * (-len(metadata) % 4)
    length = 28 + len(metadata) + len(binary)
    if length > MAX_BYTES:
        raise ValueError("GLB exceeds the size limit")
    with Path("/output/model.glb").open("wb") as output:
        output.write(struct.pack("<4sII", b"glTF", 2, length))
        output.write(struct.pack("<I4s", len(metadata), b"JSON"))
        output.write(metadata)
        output.write(struct.pack("<I4s", len(binary), b"BIN\0"))
        output.write(binary)


if __name__ == "__main__":
    main()
