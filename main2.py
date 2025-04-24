import re
from fractions import Fraction
import math


class TangramPuzzle:
    def __init__(self, file_name):
        self.file_name = file_name

        # Read the content of the file
        with open(file_name, "r") as file:
            content = file.read()

        # Regular expression to match all pieces in the file
        pattern_all = r'\\PieceTangram(?:\[[^\]]*\])?(?:<[^>]*>)?\(.*?\)\{.*?\}'
        lines = re.findall(pattern_all, content)

        print("7 Shapes Data")
        for l in lines:
            print(l)
        print("\n\n\n")

        # regular expression  to capture transform, coordinates, and shape
        pattern = re.compile(
            r'\\PieceTangram(?:\[[^\]]*\])?'
            r'(?:<(?P<transform>[^>]*)>)?'
            r'\((?P<coords>.*?)\)'
            r'\{(?P<shape>.*?)\}'
        )

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
        self.coordinates = {}
        self.simplified_coordinates = {}  # New dictionary for simplified coordinates

        for line in lines:
            match = pattern.search(line)
            if match:
                shape_raw = match.group("shape")
                transform = match.group("transform") or ""
                coords_raw = match.group("coords")
                # Extract transformation values (rotate, xflip)
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

                # piece name (Large triangle 1,Large triangle 2,etc)
                if shape_raw in shape_counter:
                    shape_counter[shape_raw] += 1
                    piece_name = f"{shape_map[shape_raw]} {shape_counter[shape_raw]}"
                else:
                    piece_name = shape_map.get(shape_raw, shape_raw)
                # Parse coordinates from coords_raw
                coord_pairs = coords_raw.split(";")
                coords_list = []
                simplified_coords_list = []  # store simplified version of coordinates

                for pair in coord_pairs:
                    if pair.strip():
                        x_str, y_str = pair.strip().split(",")
                        coords_list.append((x_str.strip(), y_str.strip()))
                        # Apply the simplification to the coordinates
                        simplified_x = self.simplify_expression(x_str.strip())
                        simplified_y = self.simplify_expression(y_str.strip())
                        simplified_coords_list.append((simplified_x, simplified_y))

                # Store transformations
                self.transformations[piece_name] = {
                    "rotate": rotate,
                    "xflip": xflip
                }

                self.coordinates[piece_name] = coords_list
                self.simplified_coordinates[piece_name] = simplified_coords_list

        # Print transformation and coordinates for Debugging
        print("Transformation Dictionary")
        print(self.transformations)
        print("\nCoordinates Dictionary")
        print(self.coordinates)
        print("\nSimplified Coordinates Dictionary")
        print(self.simplified_coordinates)

        # coordinates to numeric converison
        numeric_coordinates = self.convert_coordinates_to_numbers()
        print("\nNumeric Coordinates:")
        print(numeric_coordinates)
        shapes_dict = {}
        for shape, anchor in numeric_coordinates.items():
            vertices = self.get_shape_vertices_by_type(anchor, shape)
            shapes_dict[shape] = vertices
        print("\n Vertices dictionary before transformation:")
        print(shapes_dict)
        vertices_a_transformation = self.apply_transformations(shapes_dict, self.transformations)
        print("\nVertices dictionary after transformation:\n")
        print(vertices_a_transformation)
        piece_data = [(name, vertices, self.get_leftmost_topmost(vertices)) for name, vertices in
                      vertices_a_transformation.items()]
        sorted_pieces = sorted(piece_data, key=lambda item: (-item[2][1], item[2][0]))

        # Create a new dictionary with vertices ordered clockwise
        self.clockwise_pieces = {}
        for name, vertices, _ in sorted_pieces:
            self.clockwise_pieces[name] = self.sort_clockwise(vertices)

        print("\nOriginal Pieces (sorted by leftmost topmost vertex):")
        for name, vertices, _ in sorted_pieces:
            print(f"{name}: {vertices}")

        print("\nPieces with Vertices Ordered Clockwise:")
        print(self.clockwise_pieces)

    def simplify_expression(self, expr):
        # Replace 'sqrt(2)' with '√2'
        expr = expr.replace('sqrt(2)', '√2')
        # Simplify expressions where multiplication by zero occurs
        if re.fullmatch(r'0\s*\*\s*√2', expr) or re.fullmatch(r'0\s*\*.*', expr):
            return '0'

        # Simplify fractions
        def simplify_frac(match):
            num, den = map(int, match.groups())
            if den == 0:
                return match.group(0)  # Handle division by zero
            frac = Fraction(num, den)
            if frac.numerator == 0:
                return "0"
            return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"

        # Apply simplifications to the expression or coordinate
        expr = re.sub(r'(-?\d+)/(\d+)', simplify_frac, expr)
        expr = re.sub(r'(-?\d+/\d+)\s*\*\s*([^+\-*/()]+)', r'(\1)*\2', expr)
        expr = re.sub(r'([+-]?)1\*', r'\1', expr)
        expr = re.sub(r'([^*/+-]+)/1\b', r'\1', expr)
        expr = re.sub(r'\(([^)]+)\)/1', r'\1', expr)
        expr = re.sub(r'\+0(?!\d)', '', expr)
        expr = re.sub(r'^0\+', '', expr)
        expr = re.sub(r'^\((.*?)\)$', r'\1', expr)

        return expr

    def convert_to_number(self, expr):
        # Replace `√2` with the numerical value of sqrt(2)
        expr = expr.replace('√2', str(math.sqrt(2)))

        # Handle expressions like a + b*sqrt(2)
        try:
            return eval(expr)
        except:
            return None

    def convert_coordinates_to_numbers(self):
        # Convert all simplified coordinates into numerical values.
        numeric_coordinates = {}

        for piece_name, simplified_coords in self.simplified_coordinates.items():
            numeric_coords = []
            for simplified_x, simplified_y in simplified_coords:
                numeric_x = self.convert_to_number(simplified_x)
                numeric_y = self.convert_to_number(simplified_y)
                numeric_coords.append((numeric_x, numeric_y))

            numeric_coordinates[piece_name] = numeric_coords

        return numeric_coordinates

    def get_shape_vertices_by_type(self, anchor, shape=None):
        # findng the vertices of shape using coordinates
        x, y = anchor[0]
        if shape in ['Large triangle 1', 'Large triangle 2']:
            return [(x, y), (x + 2, y), (x, y + 2)]
        elif shape in ['Small triangle 1', 'Small triangle 2']:
            return [(x, y), (x + 1, y), (x, y + 1)]
        elif shape == 'Medium triangle':
            return [(x, y), (x + 2, y), (x + 1, y + 1)]
        elif shape == 'Square':
            return [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
        elif shape == 'Parallelogram':
            return [(x, y), (x + 1, y), (x + 2, y + 1), (x + 1, y + 1)]

    def apply_transformations(self, original_pieces, transformations):
        transformed_pieces = {}
        for piece_name, transform in transformations.items():
            original_vertices = original_pieces.get(piece_name, [])
            transformed_vertices = []

            # Apply rotation
            rotate_angle = transform["rotate"]
            if rotate_angle != 0:
                theta = math.radians(rotate_angle)
                cos_theta = math.cos(theta)
                sin_theta = math.sin(theta)

                for x, y in original_vertices:
                    new_x = x * cos_theta - y * sin_theta
                    new_y = x * sin_theta + y * cos_theta
                    new_x = round(new_x, 10)
                    new_y = round(new_y, 10)
                    transformed_vertices.append((new_x, new_y))
            else:
                transformed_vertices = original_vertices.copy()

            # Apply x-flip
            if transform["xflip"]:
                flipped_vertices = []
                for x, y in transformed_vertices:
                    flipped_vertices.append((-x, y))
                transformed_vertices = flipped_vertices

            transformed_pieces[piece_name] = transformed_vertices

        return transformed_pieces

    def get_leftmost_topmost(self, vertices):
        return max(vertices, key=lambda v: (v[1], -v[0]))

    def sort_clockwise(self, vertices):
        if len(vertices) <= 1:
            return vertices
        # Find the leftmost topmost vertex for arrangements or soring
        start = self.get_leftmost_topmost(vertices)
        remaining = [v for v in vertices if v != start]

        def sort_key(v):
            dx = v[0] - start[0]
            dy = v[1] - start[1]
            angle = math.atan2(dy, dx)
            distance = dx ** 2 + dy ** 2
            return (-angle, distance)

        remaining_sorted = sorted(remaining, key=sort_key)
        return [start] + remaining_sorted

    def _get_bounds(self):
        all_x = [x for vertices in self.clockwise_pieces.values() for x, _ in vertices]
        all_y = [y for vertices in self.clockwise_pieces.values() for _, y in vertices]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        def extend(val, direction):
            floor_val = math.floor(val)
            fractional = val - floor_val

            if direction == 'up':
                if fractional <= 0.5:
                    return floor_val + 1
                else:
                    return floor_val + 1.5
            else:
                if fractional >= 0.5:
                    return floor_val
                else:
                    return floor_val - 0.5

        left = extend(min_x, 'down')
        right = extend(max_x, 'up')
        bottom = extend(min_y, 'down')
        top = extend(max_y, 'up')

        return left, right, bottom, top

    def draw_pieces(self, output_filename):
        left, right, bottom, top = self._get_bounds()
        print("File Created", output_filename)
        with open(output_filename, 'w') as f:
            # Write LaTeX document header
            f.write("\\documentclass{article}\n")
            f.write("\\usepackage{tikz}\n")
            f.write("\\usepackage[margin=1cm]{geometry}\n")
            f.write("\\begin{document}\n")
            f.write("\\begin{center}\n")
            f.write("\\begin{tikzpicture}\n")  # Removed scale=0.5
            f.write(f"\\draw[step=0.5cm,gray,very thin] ({left:.1f},{bottom:.1f}) grid ({right:.1f},{top:.1f});\n")
            f.write("\\fill[red] (0,0) circle[radius=2pt];\n")
            for piece_name, vertices in self.clockwise_pieces.items():
                f.write("\\filldraw[fill=gray!20] ")
                path = ' -- '.join(f"({x:.10f},{y:.10f})" for x, y in vertices)
                f.write(path + " -- cycle;\n")
            f.write("\\end{tikzpicture}\n")
            f.write("\\end{center}\n")
            f.write("\\end{document}\n")

    def draw_outline(self, output_tex_file):
        all_vertices = []
        for vertices in self.clockwise_pieces.values():
            all_vertices.extend(vertices)
        outline_vertices = self._compute_convex_hull(all_vertices)
        x_coords = [x for (x, y) in outline_vertices]
        y_coords = [y for (x, y) in outline_vertices]
        x_min, x_max = self._compute_grid_bounds(min(x_coords), max(x_coords))
        y_min, y_max = self._compute_grid_bounds(min(y_coords), max(y_coords))
        tikz_code = self._generate_outline_tikz(outline_vertices, x_min, x_max, y_min, y_max)

        with open(output_tex_file, 'w') as f:
            f.write(tikz_code)

    def solved_puzzle(self, file_name):
        self.draw_pieces("draw_pieces_after_outline1.tex")

    def _compute_grid_bounds(self, min_val, max_val):
        def extend(val, direction):
            floor_val = math.floor(val)
            fractional = val - floor_val

            if direction == 'up':
                if fractional <= 0.5:
                    return floor_val + 1
                else:
                    return floor_val + 1.5
            else:
                if fractional >= 0.5:
                    return floor_val
                else:
                    return floor_val - 0.5

        min_bound = extend(min_val, 'down')
        max_bound = extend(max_val, 'up')
        return min_bound, max_bound

        min_bound = math.floor(min_val) - 0.5
        max_bound = adjust_bound(max_val)[1]
        return min_bound, max_bound

    def _compute_convex_hull(self, points):
        points = sorted(set(points))
        if len(points) <= 1:
            return points

        lower = []
        for p in points:
            while len(lower) >= 2 and self._cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and self._cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        return lower[:-1] + upper[:-1]

    def _cross(self, o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def _generate_outline_tikz(self, vertices, x_min, x_max, y_min, y_max):
        tikz = [
            r"\documentclass{article}",
            r"\usepackage{tikz}",
            r"\begin{document}",
            r"\begin{tikzpicture}[scale=1]",
            rf"\draw[step=0.5cm,gray,very thin] ({x_min},{y_min}) grid ({x_max},{y_max});",
            r"\filldraw[red] (0,0) circle (1pt);",
            r"\draw[thick] " + " -- ".join(f"({x:.6f},{y:.6f})" for (x, y) in vertices) + " -- cycle;",
            r"\end{tikzpicture}",
            r"\end{document}"
        ]
        return "\n".join(tikz)



p = TangramPuzzle('First.tex')
p.draw_pieces('First_piece_on_grid1.tex')
p.draw_outline("First_outline_on_grid1.tex")
p.solved_puzzle('First_outline_on_grid1.tex')