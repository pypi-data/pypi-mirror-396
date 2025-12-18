def create_document(content, document_class, packages):
    packages_tex = ""
    for package in packages:
        packages_tex = packages_tex + r"\usepackage{" + package + "}\n"
    return r"""
\documentclass{""" + document_class + r"""}
""" + packages_tex + r"""
\begin{document}
""" + "\n".join(content) + r"""
\end{document}
"""


def create_table(table):
    table_code = ""
    for row in table:
        table_code = table_code + " & ".join(row) + r" \\" + "\n" + r"\hline" + "\n"
    return r"""
\begin{table}
\begin{tabular}{|""" + "c|" * len(table[0]) + r"""}
\hline
""" + table_code + r"""
\end{tabular}
\end{table}
"""


def create_image(url):
    return r"""
\begin{figure}
\includegraphics{""" + url + r"""}
\end{figure}
"""
