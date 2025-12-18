import warnings
from speciesfinder.speciesfinder_run import speciesfinder as _speciesfinder

warnings.warn(
    "KmerFinder is deprecated and will be removed in 2026. "
    "Please migrate to SpeciesFinder.",
    DeprecationWarning,
    stacklevel=2,
)

def run():
    return _speciesfinder()