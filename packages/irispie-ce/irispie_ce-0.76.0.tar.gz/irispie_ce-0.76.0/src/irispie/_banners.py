r"""
Prepare function to print an edition-specific warning
"""


import importlib.metadata as _md
import re as _re
import functools as _ft
import warnings as _wa

_BANNER = {
    "de": (
        "\n\n"
        "=================================================================\n"
        " You are using IrisPie Developer Edition.\n"
        " This edition is intended for development and testing only.\n"
        " It may be used solely by registered developers.\n"
        " Contact info@ogresearch.com for more information.\n"
        "=================================================================\n\n"
    ),
    "ce": (
        "\n\n"
        "=================================================================\n"
        " You are using IrisPie Community Edition.\n"
        " Free for personal, educational, and non-commercial use only.\n"
        " Registration is required for commercial or institutional use.\n"
        " Contact info@ogresearch.com for more information.\n"
        "=================================================================\n\n"
    ),
    "re": (
        "\n\n"
        "=================================================================\n"
        " You are using IrisPie Registered Edition.\n"
        " Licensed for use by organizations that have completed\n"
        " registration with OGResearch.\n"
        " Internal use and redistribution within the organization\n"
        " are permitted. External redistribution is prohibited.\n"
        " Contact info@ogresearch.com for more information.\n"
        "=================================================================\n\n"
    ),
    "pe": (
        "\n\n"
        "=================================================================\n"
        " You are using IrisPie Private Edition.\n"
        " This edition may only be used internally by staff members\n"
        " of OGResearch or by approved contractors and affiliated\n"
        " institutions.\n"
        "=================================================================\n\n"
    ),
}

distribution_generator = (
    i for i in _md.distributions()
    if _re.match("irispie-[dcrp]e$", i.name)
)
distribution = next(distribution_generator, None, )

if not distribution:
    raise Exception("Cannot determine the irispie distribution", )

edition = distribution.name[-2:]
version = distribution.version + "-" + edition
__version__ = version
__doc__ = distribution.metadata["description"]

irispie_edition_warning = _ft.partial(_wa.warn, _BANNER[edition], UserWarning, )


