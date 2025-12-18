import os
import warnings
import logging
import time

logger = logging.getLogger(__name__)

# these submodules make sense to import from the beginning
# importing all others slow down importing parmesan significantly

import parmesan.symbols
import parmesan.accessor
import parmesan.analysis
import parmesan.processing
import parmesan.aggregate
import parmesan.processing
import parmesan.bounds
import parmesan.units
import parmesan.stats

_equation_modules = """
import parmesan.clouds
import parmesan.errors
import parmesan.gas
import parmesan.radiation
import parmesan.turbulence
import parmesan.flux
import parmesan.stability
import parmesan.vector
import parmesan.wind
"""

_load_equations = r"""
for line in [
    L for line in _equation_modules.splitlines() if (L := line.strip())
]:
    logger.debug(f"⏳ {line}...")
    exec(line.strip())
""".strip()


def load_equations():
    """
    Import all equation submodules so they're available e.g. for
    :any:`get_function`. This is useful if PARMESAN_SKIP_EQUATION_IMPORT had
    been set to not import all equations upon parmesan's initial import.
    """
    exec(_load_equations)


if os.environ.get("PARMESAN_SKIP_EQUATION_IMPORT") != "yes":
    before = time.perf_counter()

    exec(_load_equations)

    if (passed := time.perf_counter() - before) > (
        threshold := 5
    ) and not os.environ.get("PARMESAN_NO_SLOW_IMPORT_WARNING"):
        warnings.warn(
            f"Importing all of PARMESANs equations took quite long ({passed:.1f}s). "
            f"You can set the environment variable PARMESAN_SKIP_EQUATION_IMPORT=yes to skip loading the equations to speed up the import. "
            f"You will then have to import the relevant submodules yourself (e.g. `import parmesan.turbulence`) of which you want the equations to be available. "
            f"You can silence this warning by setting the environment variable PARMESAN_NO_SLOW_IMPORT_WARNING to anything before importing parmesan.",
            category=parmesan.errors.ParmesanWarning,
        )
    del before, passed, threshold
