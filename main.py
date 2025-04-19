import re


class TangramPuzzle:
    def __init__(self, file_name):
        self.file_name = file_name

        with open(file_name, "r") as file:
            content = file.read()
        pattern_all = r'\\PieceTangram(?:\[[^\]]*\])?(?:<[^>]*>)?\(.*?\)\{.*?\}'
        lines = re.findall(pattern_all, content)

        print("7 Shapes Data")
        for l in lines:
            print(l)
        print("\n\n\n")

        # Detailed pattern with named groups
        pattern = re.compile(
            r'\\PieceTangram(?:\[[^\]]*\])?'             # Optional [..]
            r'(?:<(?P<transform>[^>]*)>)?'                # Optional <...> transformations
            r'\((?P<coords>.*?)\)'                        # (x, y)
            r'\{(?P<shape>.*?)\}'                         # {shape}
        )

        # Piece type mapping (to resolve names like TangGrandTri → Large triangle 1, etc.)
        shape_counter = {
            "TangGrandTri": 0,
            "TangPetTri": 0
        }

        shape_map = {
            "TangGrandTri": "Large triangle",
            "TangMoyTri": "Medium triangle",
            "TangPetTri": "Small triangle",
            "TangCar": "Square",
            "TangPara": "Parallelogram"
        }

        self.transformations = {}

        for line in lines:
            match = pattern.search(line)
            if match:
                shape_raw = match.group("shape")
                transform = match.group("transform") or ""

                # Extract transformation values
                xflip = False
                rotate = 0

                for item in transform.split(","):
                    if "=" in item:
                        key, value = item.strip().split("=")
                        key = key.strip()
                        value = value.strip()

                        if key == "xscale":
                            xflip = True
                        elif key == "rotate":
                            try:
                                rotate = int(value) % 360
                            except:
                                rotate = 0

                # Build the piece name key
                if shape_raw in shape_counter:
                    shape_counter[shape_raw] += 1
                    piece_name = f"{shape_map[shape_raw]} {shape_counter[shape_raw]}"
                else:
                    piece_name = shape_map.get(shape_raw, shape_raw)

                # Add to dictionary
                self.transformations[piece_name] = {
                    "rotate": rotate,
                    "xflip": xflip
                }

        #print for verification
        # for name, transform in self.transformations.items():
        #     print(f"{name}: {transform}")

        print("transformation Dictionary")
        print(self.transformations)

# Example usage
puzzle = TangramPuzzle("Second.tex")
