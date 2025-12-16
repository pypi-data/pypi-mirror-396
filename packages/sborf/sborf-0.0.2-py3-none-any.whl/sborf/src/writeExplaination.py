import math
import tempfile
import webbrowser
import os

def visualize_codons(sequence, scores):
    # sequence: list of codons, e.g. ["AAA","AAC","AAA","UGG",...]
    # scores:   list of floats of same length

    max_abs = max(abs(s) for s in scores) or 1

    def score_to_color(score):
        x = abs(score) / max_abs
        x = min(max(x, 0), 1)
        if score > 0:
            r = 255 - int(120 * x)
            g = 255
            b = 255 - int(120 * x)
        elif score < 0:
            r = 255
            g = 255 - int(120 * x)
            b = 255 - int(120 * x)
        else:
            return "rgb(255,255,255)"
        return f"rgb({r},{g},{b})"

    html = [
        "<html><body>",
        "<h2>Codon Score Visualization</h2>",
        "<table border='1' cellpadding='6' style='border-collapse:collapse'>",
        "<tr><th>Position</th><th>Codon</th><th>Score</th></tr>"
    ]

    for i, (codon, score) in enumerate(zip(sequence, scores)):
        color = score_to_color(score)
        html.append(
            f"<tr>"
            f"<td style='background:{color}'>{i}</td>"
            f"<td style='background:{color}'>{codon}</td>"
            f"<td style='background:{color}'>{score}</td>"
            f"</tr>"
        )

    html.extend(["</table>", "</body></html>"])
    document = "\n".join(html)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        f.write(document.encode("utf-8"))
        path = f.name

    webbrowser.open("file://" + os.path.abspath(path))


def write_codons_visualization(sequence, scores,outfile):
    # sequence: list of codons, e.g. ["AAA","AAC","AAA","UGG",...]
    # scores:   list of floats of same length

    max_abs = max(abs(s) for s in scores) #or 1

    def score_to_color(score):
        x = abs(score) / max_abs
        x = min(max(x, 0), 1)
        if score > 0:
            r = 255 - int(120 * x)
            g = 255
            b = 255 - int(120 * x)
        elif score < 0:
            r = 255
            g = 255 - int(120 * x)
            b = 255 - int(120 * x)
        else:
            return "rgb(255,255,255)"
        return f"rgb({r},{g},{b})"

    html = [
        "<html><body>",
        "<h2>Codon Score Visualization</h2>",
        "<table border='1' cellpadding='6' style='border-collapse:collapse'>",
        "<tr><th>Position</th><th>Codon</th><th>Score</th></tr>"
    ]

    for i, (codon, score) in enumerate(zip(sequence, scores)):
        color = score_to_color(score)
        html.append(
            f"<tr>"
            f"<td style='background:{color}'>{i}</td>"
            f"<td style='background:{color}'>{codon}</td>"
            f"<td style='background:{color}'>{score}</td>"
            f"</tr>"
        )

    html.extend(["</table>", "</body></html>"])
    document = "\n".join(html)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(document)