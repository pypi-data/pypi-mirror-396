import re

class ASON:
    @staticmethod
    def load(path):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return ASON._parse(text)

    @staticmethod
    def save(path, obj):
        with open(path, "w", encoding="utf-8") as f:
            f.write(ASON._serialize(obj))

    # --- Private helpers ---
    @staticmethod
    def _parse(text):
        obj_stack = []
        current = {}
        stack = []
        key = None

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("{"):
                new_obj = {}
                if obj_stack:
                    if key:
                        obj_stack[-1][key] = new_obj
                        key = None
                    else:
                        raise ValueError("Syntax error: key missing before {")
                obj_stack.append(new_obj)
            elif line.startswith("}"):
                current = obj_stack.pop()
                if obj_stack:
                    current = obj_stack[-1]
            elif ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v == "{":
                    key = k
                    continue
                # numbers
                if re.match(r"^\d+$", v):
                    v = int(v)
                elif re.match(r"^\d+\.\d+$", v):
                    v = float(v)
                # string
                elif v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                if obj_stack:
                    obj_stack[-1][k] = v
                else:
                    current[k] = v
        if obj_stack:
            return obj_stack[0]
        return current

    @staticmethod
    def _serialize(obj, indent=0):
        spacing = "  " * indent
        if isinstance(obj, dict):
            lines = ["{"]
            for k, v in obj.items():
                lines.append(spacing + f"  {k}: {ASON._serialize(v, indent+1)}")
            lines.append(spacing + "}")
            return "\n".join(lines)
        elif isinstance(obj, list):
            return "[" + ", ".join(ASON._serialize(i, 0) for i in obj) + "]"
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return str(obj)
