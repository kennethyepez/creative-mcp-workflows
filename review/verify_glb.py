import hashlib
import json
from pathlib import Path
import struct

sample = Path(__file__).resolve().parents[1] / "evidence/samples/blender-sample-cube.glb"
data = sample.read_bytes()

magic, version, length = struct.unpack_from("<4sII", data)
if (magic, version, length) != (b"glTF", 2, len(data)):
    raise SystemExit("Invalid GLB header")
json_length, json_type = struct.unpack_from("<I4s", data, 12)
bin_header = 20 + json_length
bin_length, bin_type = struct.unpack_from("<I4s", data, bin_header)
if json_type != b"JSON" or bin_type != b"BIN\0" or bin_header + 8 + bin_length != len(data):
    raise SystemExit("Invalid GLB chunks")

document = json.loads(data[20:bin_header])
if document["asset"]["version"] != "2.0" or document["buffers"] != [{"byteLength": bin_length}]:
    raise SystemExit("Unexpected GLB version or buffer")
if len(document["meshes"]) != 1:
    raise SystemExit("Expected one mesh")
primitive, = document["meshes"][0]["primitives"]
accessor = document["accessors"][primitive["attributes"]["POSITION"]]
view = document["bufferViews"][accessor["bufferView"]]
if accessor["componentType"] != 5126 or accessor["type"] != "VEC3" or accessor["count"] != 36:
    raise SystemExit("Expected 36 positions for 12 triangles")
start = bin_header + 8 + view.get("byteOffset", 0)
end = start + view["byteLength"]
positions = list(struct.iter_unpack("<3f", data[start:end]))
if len(positions) != accessor["count"] or len(set(positions)) != 8:
    raise SystemExit("Expected eight unique vertices in the cube")

sha256 = hashlib.sha256(data).hexdigest()
if sha256 != "5e8373e48e8a414fdc3037ae8d6fbb1b5452233fda7a67e2e9e1181eaa7f8f93":
    raise SystemExit("File checksum does not match the acceptance artifact")
print(f"GLB 2.0: one mesh, 12 triangles, {len(data)} bytes, SHA-256 {sha256}")
