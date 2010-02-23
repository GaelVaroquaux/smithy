import sys, os
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage'
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Smithy'
copyright = u'2010, Paul J. Davis'

version = '0.4'
release = '0.4.1'

exclude_trees = []
pygments_style = 'sphinx'
html_theme = 'default'

htmlhelp_basename = 'Smithydocs'

latex_documents = [
  ('index', 'Smithy.tex', u'Smithy Documentation', u'Paul J. Davis', 'manual'),
]

