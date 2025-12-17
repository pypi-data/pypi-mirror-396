#!/usr/bin/env python3
""" """

import inspect

from localecmddoc.autodoc import create_module_doc_output, remove_python_code_blocks
from tests.samplemodule import expected_output, module


def test_module_output():
    output = create_module_doc_output(module, remove_pycode=True)
    assert output.strip() == expected_output.strip()


def test_pycode_block_removal():
    doc = inspect.cleandoc("""
    :::{code} python
    >>> func2(1, 2, 3, 4)

    >>> func2(1, b=4)
    :::
    """)
    tdoc = remove_python_code_blocks(doc)
    assert tdoc == inspect.cleandoc("")

    doc2 = inspect.cleandoc("""
    :::{code} python
    >>> func2(1, 2, 3, 4)

    >>> func2(1, b=4)
    :::
        
    ```python
    >>> func2(1, 2, 3, 4)

    >>> func2(1, b=4)
    ```
    ```bash
    ls
    ```
    """)
    tdoc2 = remove_python_code_blocks(doc2)
    assert tdoc2.strip() == inspect.cleandoc("""```bash\nls\n```""").strip()
