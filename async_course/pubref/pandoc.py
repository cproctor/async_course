import subprocess
from django.conf import settings
from .temp_file import TempFile

class PandocConversionError(Exception):
    pass

def markdown_to_html(markdown):
    """Formats `source` using pandoc, including citeproc.
    """
    with TempFile(2) as fhs:
        fin, fout = fhs
        fin.write_text(markdown)
        cmd = (
            "{} --citeproc --metadata link-citations=true --bibliography {} "
            "--csl {} --from markdown --to html {} --out {}"
        ).format(
            settings.PANDOC, 
            settings.BIBLIOGRAHY,
            settings.CSL,
            fin, 
            fout
        )
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise PandocConversionError(e.stdout)
        return fout.read_text()

def replace_reference_link(source, pub):
    """Replaces #ref-{slug} in anchor hrefs with the publication's canonical URL.
    """
    return source.replace(f"#ref-{pub.slug}", pub.get_absolute_url())
