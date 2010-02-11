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
project = u'Trawl'
copyright = u'2010, Paul J. Davis'

version = '0.2'
release = '0.2.0'

exclude_trees = []
pygments_style = 'sphinx'
html_theme = 'default'

htmlhelp_basename = 'Trawldoc'

latex_documents = [
  ('index', 'Trawl.tex', u'Trawl Documentation', u'Paul J. Davis', 'manual'),
]

