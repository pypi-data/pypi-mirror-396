
import os
from importlib import resources

PART_PREFIX = 'qwen2.5-3b-instruct-q5_k_m.gguf.part_'

# Reconstruit le modèle à partir des parts installées

def rebuild_model(output_path="qwen2.5-3b-instruct-q5_k_m.gguf"):
    parts_dir = resources.files(__package__).parent
    with open(output_path, "wb") as out:
        i = 0
        while True:
            part_name = f"qwen2.5-3b-instruct-q5_k_m.gguf.part_{i:03d}"
            part_path = parts_dir.joinpath(f"local_qwen3b_part{i:03d}", part_name)
            if not part_path.is_file():
                break
            with open(part_path, "rb") as p:
                out.write(p.read())
            i += 1
    return os.path.abspath(output_path)
