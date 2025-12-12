# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley data files.
"""
import pathlib


data_dir = pathlib.Path(__file__).parent / "-static"


def readme_pdf(culture: str) -> pathlib.Path:
    """
    Return the path to the README file for a given culture.

    :param culture: The two-letter culture code.
    """
    for culture_ in (culture, "en"):
        if (result := data_dir / f"README/{culture_}.pdf").exists():
            return result

    raise RuntimeError("no readme file found")
