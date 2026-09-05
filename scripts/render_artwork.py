"""Optional artwork export: first install cairosvg in a separate tooling environment."""
from pathlib import Path
try:
    import cairosvg
except ImportError:
    raise SystemExit('Install the optional renderer: python -m pip install cairosvg')
assets = Path(__file__).resolve().parents[1] / 'assets'
cairosvg.svg2png(url=str(assets / 'banner.svg'), write_to=str(assets / 'social-preview.png'))
print(assets / 'social-preview.png')
