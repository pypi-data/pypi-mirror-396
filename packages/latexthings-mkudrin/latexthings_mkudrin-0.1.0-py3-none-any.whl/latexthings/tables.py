def latexTable(list):
  lines = map(lambda sublist: " & ".join(map(lambda x: x.replace('&', '\\&'), sublist)), list)
  body = " \\\\\n\\hline\n".join(lines)
  res = "\\begin{tabular}{|" + "c|" * len(list[0]) + "} \\hline \n" + body + "\\\\\n\\hline\n\\end{tabular}"
  return res
