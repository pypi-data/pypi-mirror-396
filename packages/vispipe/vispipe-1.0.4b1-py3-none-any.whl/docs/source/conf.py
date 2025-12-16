# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VisPipe'
author = 'Gramm, Joshua'
release = '1.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc",
              "numpydoc",
              "sphinx_autodoc_typehints",
              "sphinx.ext.autosummary",
              "sphinx.ext.autosectionlabel",
              "sphinx.ext.extlinks"
              ]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_theme_options = {
   "pygment_light_style": "tango",
   "pygment_dark_style": "monokai"
}
numpydoc_show_class_members = False
autodoc_member_order="bysource"
autoclass_content = 'both'
autosummary_generate_overwrite=False

rst_prolog = """
.. include:: <s5defs.txt>
"""

html_css_files = ['css/colors.css']

extlinks = {"pint_units":("https://github.com/hgrecco/pint/blob/master/pint/default_en.txt",None)}


