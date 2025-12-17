def generate_table(data: list[list[str]]) -> str:
    if not data or not data[0]:
        return ""

    num_columns = len(data[0])

    alignment_str = "|" + "|".join(["c"] * num_columns) + "|"

    latex_lines = []
    latex_lines.append("\\begin{table}[h]")
    latex_lines.append("\\centering")
    latex_lines.append(f"\\begin{{tabular}}{{{alignment_str}}}")
    latex_lines.append("\\hline")

    for i, row in enumerate(data):
        escaped_row = [escape_latex(str(cell)) for cell in row]
        latex_lines.append(" & ".join(escaped_row) + " \\\\")
        latex_lines.append("\\hline")

    latex_lines.append("\\end{tabular}")
    latex_lines.append("\\end{table}")

    return "\n".join(latex_lines)


def escape_latex(text):
    special_chars = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "^": "\\textasciicircum{}",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "\\": "\\textbackslash{}",
    }

    result = str(text)
    for char, escaped in special_chars.items():
        result = result.replace(char, escaped)

    return result


def generate_image(image_path: str, width: str = "0.8\\textwidth", caption: str = None) -> str:
    latex_lines = []
    latex_lines.append("\\begin{figure}[h]")
    latex_lines.append("\\centering")
    latex_lines.append(f"\\includegraphics[width={width}]{{{escape_latex(image_path)}}}")
    
    if caption:
        latex_lines.append(f"\\caption{{{escape_latex(caption)}}}")
    
    latex_lines.append("\\end{figure}")
    
    return "\n".join(latex_lines)

