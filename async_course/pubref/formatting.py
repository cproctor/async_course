# Renders a pybtex.database.Bibliography object as HTML or plain text

from pybtex.plugin import find_plugin
from pybtex.database import parse_string
APA = find_plugin('pybtex.style.formatting', 'apa7')()
HTML = find_plugin('pybtex.backends', 'html')()
TEXT = find_plugin('pybtex.backends', 'plaintext')()

outputs = {
    'html': HTML,
    'text': TEXT,
}

def format_bibtex(bibtex, output='html', exclude_fields=None):
    exclude_fields = exclude_fields or []
    bibliography = parse_string(bibtex, 'bibtex')
    if exclude_fields:
        for entry in bibliography.entries.values():
            for ef in exclude_fields:
                if ef in entry.fields.__dict__['_dict']:
                    del entry.fields.__dict__['_dict'][ef]
    formattedBib = APA.format_bibliography(bibliography)
    return "<br>".join(entry.text.render(outputs[output]) for entry in formattedBib)

