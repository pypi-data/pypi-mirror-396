def wrapLatex(text):
    return """
\\documentclass{article}

\\usepackage{graphicx} %package to manage images
\\graphicspath{ {./images/} }

\\usepackage[rightcaption]{sidecap}

\\usepackage{wrapfig}

\\begin{document}
""" + text + """
\\end{document}
"""
