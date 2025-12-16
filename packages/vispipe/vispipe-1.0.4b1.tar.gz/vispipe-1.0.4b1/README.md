# Visulization Pipeline


## Instillation

To install, clone the repo into a directory and then pip install the cloned repo like any other python package.
```
pip install vispipe
```

## Getting started

Included in VisPipe are the sphinx source files for the documentation. To build run the following commands:
```
pip install sphinx numpydoc sphinx_autodoc_typehints pydata_sphinx_theme
cd src/docs
sphinx-build -M html ./source ./build

```

The HTML files will be generated and the homepage will be located at ```vispipe\src\docs\build\html\index.html```.