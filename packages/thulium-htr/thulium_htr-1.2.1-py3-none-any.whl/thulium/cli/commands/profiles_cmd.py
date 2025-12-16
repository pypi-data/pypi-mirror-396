# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Language Profiles CLI Command.

This module provides commands to inspect and list supported languages within
the Thulium ecosystem. It interfaces with the `thulium.data.language_profiles`
module to retrieve metadata.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

import typer

from thulium.data.language_profiles import (
    get_language_profile,
    get_languages_by_region,
    get_languages_by_script,
    list_supported_languages,
    validate_language_profile,
)

logger = logging.getLogger(__name__)

app = typer.Typer(help="Manage and inspect language profiles.")


@app.command(name="list")
def list_languages(
    script: Optional[str] = typer.Option(
        None,
        "--script",
        "-s",
        help="Filter languages by script (e.g., Latin, Cyrillic).",
    ),
    region: Optional[str] = typer.Option(
        None,
        "--region",
        "-r",
        help="Filter languages by region (e.g., Scandinavia, Caucasus).",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: 'table', 'json', or 'csv'.",
    ),
) -> None:
    """
    List supported languages with optional filtering.
    """
    if script:
        languages = get_languages_by_script(script)
        typer.echo(f"Languages using {script} script:")
    elif region:
        languages = get_languages_by_region(region)
        typer.echo(f"Languages in {region} region:")
    else:
        languages = list_supported_languages()
        typer.echo(f"All supported languages ({len(languages)}):")

    if not languages:
        typer.echo("No languages found.")
        return

    # Gather data
    profiles_data = []
    for code in sorted(languages):
        try:
            profile = get_language_profile(code)
            profiles_data.append({
                "code": code,
                "name": profile.name,
                "script": profile.script,
                "direction": profile.direction,
                "vocab_size": profile.get_vocab_size(),
            })
        except Exception:
            # Fallback if profile loading fails
            profiles_data.append({
                "code": code,
                "name": "Unknown",
                "script": "?",
                "direction": "?",
                "vocab_size": 0,
            })

    # Render Output
    if output_format == "json":
        typer.echo(json.dumps(profiles_data, indent=2, ensure_ascii=False))
        return

    if output_format == "csv":
        typer.echo("code,name,script,direction,vocab_size")
        for p in profiles_data:
            typer.echo(f"{p['code']},{p['name']},{p['script']},{p['direction']},{p['vocab_size']}")
        return

    # Table
    typer.echo("-" * 75)
    typer.echo(f"{'Code':<6} {'Name':<30} {'Script':<15} {'Dir':<5} {'Vocab':<8}")
    typer.echo("-" * 75)
    for p in profiles_data:
        typer.echo(
            f"{p['code']:<6} {p['name']:<30} {p['script']:<15} {p['direction']:<5} {p['vocab_size']:<8}"
        )
    typer.echo("-" * 75)


@app.command(name="show")
def show_profile(
    language: str = typer.Argument(..., help="ISO language code (e.g., 'en')."),
) -> None:
    """
    Show detailed information about a specific language profile.
    """
    try:
        profile = get_language_profile(language)
    except Exception as e:
        logger.error("Profile not found for '%s': %s", language, e)
        raise typer.Exit(1)

    typer.secho(f"\nLanguage Profile: {profile.name} ({profile.code})", bold=True)
    typer.echo("=" * 60)
    typer.echo(f"Script:           {profile.script}")
    typer.echo(f"Direction:        {profile.direction}")
    typer.echo(f"Tokenizer:        {profile.tokenizer_type}")
    typer.echo(f"Default Decoder:  {profile.default_decoder}")
    typer.echo(f"Vocabulary Size:  {profile.get_vocab_size()}")
    
    if profile.notes:
        typer.echo(f"\nNotes: {profile.notes}")

    typer.secho("\nAlphabet Preview:", bold=True)
    chars = "".join(profile.alphabet[:60])
    typer.echo(f"  {chars}...")

    # Validate
    try:
        validate_language_profile(profile)
        typer.secho("\nStatus: VALIDATED", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"\nStatus: INVALID ({e})", fg=typer.colors.RED)
