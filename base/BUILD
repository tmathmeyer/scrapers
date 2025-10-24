langs("Python")

py_library (
  name = "html",
  srcs = [ "html.py" ],
  deps = [ "//pylib/types:types" ],
  python_packages = [
    "requests",
  ],
)

py_library (
  name = "tables",
  srcs = [ "tables.py" ],
  deps = [
    ":html",
    "//pylib/types:types",
  ],
)