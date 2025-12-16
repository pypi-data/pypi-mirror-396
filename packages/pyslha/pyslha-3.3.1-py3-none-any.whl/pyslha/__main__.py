###############################################################################
## Main function for module testing

from . import *
from . import __version__ as PYSLHA_VERSION

import argparse
ap = argparse.ArgumentParser(usage="Test PySLHA file parsing")
ap.add_argument("INFILES", nargs="*", help="files to try parsing")
ap.add_argument("--version", action="version", version=PYSLHA_VERSION)
args = ap.parse_args()

for sf in args.INFILES:
    doc = read(sf)
    print(doc)
    print("")

    for bname, b in sorted(doc.blocks.items()):
        print(b)
        print("")

    print(list(doc.blocks.keys()))

    print(doc.blocks["MASS"].get(25))
    print("")

    for p in sorted(doc.decays.values()):
        print(p)
        print("")

    print(writeSLHA(doc, ignorenobr=True))
