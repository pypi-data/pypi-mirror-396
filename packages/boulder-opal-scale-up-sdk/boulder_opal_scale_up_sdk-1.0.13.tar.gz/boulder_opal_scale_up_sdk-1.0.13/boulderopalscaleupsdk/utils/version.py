# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.


from importlib import metadata


def get_version(package_name: str, strip_local: bool = False) -> str:
    """Get package version from installed package metadata.

    Parameters
    ----------
    package_name : str
        Name of the package (e.g., "boulder-opal-scale-up-sdk")
    strip_local : bool, optional
        If True, remove local version identifiers (e.g., +dev, +local), by default False

    Returns
    -------
    str
        Version string

    Raises
    ------
    metadata.PackageNotFoundError
        If package is not installed
    """
    version = metadata.version(package_name)

    # Strip local version identifiers if requested
    if strip_local:
        # Remove everything after + (local version identifier)
        version = version.split("+")[0]

    return version
