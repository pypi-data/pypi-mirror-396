import typer
from typing import Optional
from pathlib import Path
import json
import logging
from thulium.api.recognize import recognize_image

app = typer.Typer(help="Thulium: Multilingual Handwriting Intelligence CLI")

@app.command()
def recognize(
    path: Path = typer.Argument(..., help="Path to image or PDF"),
    language: str = typer.Option("en", "--language", "-l", help="Language code (e.g., az, en)"),
    pipeline: str = typer.Option("default", "--pipeline", "-p", help="Pipeline configuration name"),
    device: str = typer.Option("auto", "--device", "-d", help="Computation device"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Recognize text in a document.
    """
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Simple check for PDF vs Image stub
    typer.echo(f"Processing {path} in {language}...")
    result = recognize_image(path, language, pipeline, device)
    
    output_dict = result.to_dict()
    
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, indent=2, ensure_ascii=False)
        typer.echo(f"Results saved to {output}")
    else:
        # Print to stdout
        typer.echo("--- Result ---")
        typer.echo(result.full_text)
        typer.echo("--------------")

@app.command()
def version():
    """Show version."""
    from thulium.version import __version__
    typer.echo(f"Thulium v{__version__}")

if __name__ == "__main__":
    app()
