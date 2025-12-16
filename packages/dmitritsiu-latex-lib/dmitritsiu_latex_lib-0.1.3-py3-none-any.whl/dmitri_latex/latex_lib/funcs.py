from typing import Any


def generate_table(data: list[list[Any]]) -> str:
    if not data:
        return ""

    num_columns = len(data[0])
    col_format = "|" + "c|" * num_columns
    rows = [" & ".join(map(str, row)) + " \\\\" for row in data]
    body = "\n\\hline\n".join(rows)

    return (
        f"\\begin{{center}}"
        f"\\begin{{tabular}}{{{col_format}}}\n"
        f"\\hline\n"
        f"{body}\n"
        f"\\hline\n"
        f"\\end{{tabular}}"
        f"\\end{{center}}"
    )


def generate_image(filepath: str, caption: str = "Image generated from my Python lib!", width: str = "0.5\\textwidth") -> str:
    return (
        f"\\begin{{figure}}[h!]\n"
        f"\\centering\n"
        f"\\includegraphics[width={width}]{{{filepath}}}\n"
        f"\\caption{{{caption}}}\n"
        f"\\end{{figure}}"
    )


def create_document(*content_blocks: str) -> str:
    preamble = (
        "\\documentclass{article}\n"
        "\\usepackage{graphicx}\n"  # Необходим для картинок
        "\\begin{document}\n"
    )
    postamble = "\n\\end{document}"

    body = "\n\n".join(content_blocks)

    return preamble + body + postamble
