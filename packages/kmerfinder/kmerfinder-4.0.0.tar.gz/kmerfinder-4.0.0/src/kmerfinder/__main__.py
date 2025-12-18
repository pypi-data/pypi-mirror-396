import warnings
import sys
from speciesfinder.speciesfinder_run import speciesfinder

def main():
    warnings.warn(
        "KmerFinder is deprecated and will be removed in 2026. "
        "Please use `speciesfinder` instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Forward all command-line arguments to SpeciesFinder
    sys.exit(speciesfinder())

if __name__ == "__main__":
    main()