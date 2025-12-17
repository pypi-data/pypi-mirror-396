"""CLI for text-to-QTI converter."""

import sys

import click
from rich.console import Console
from rich.progress import Progress

from text_to_qti.parser.markdown_parser import MarkdownParser
from text_to_qti.parser.syntax_validator import SyntaxValidator
from text_to_qti.qti.generator import QTIGenerator
from text_to_qti.utils.errors import TextToQTIError

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """Text to QTI Converter - Convert markdown quizzes to QTI format for Canvas."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output ZIP file path (default: output.zip)",
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate syntax, don't generate QTI",
)
@click.option(
    "--qti-version",
    type=click.Choice(["1.2", "2.1"]),
    default="1.2",
    help="QTI version to generate",
)
def convert(
    input_file: str, output: str, validate_only: bool, qti_version: str
) -> None:
    """Convert a text file to QTI package."""
    try:
        with Progress() as progress:
            task = progress.add_task("Processing...", total=4)

            # Step 1: Validate
            progress.update(task, description="[cyan]Validating syntax...")
            validator = SyntaxValidator()
            try:
                validator.validate_file(input_file)
            except TextToQTIError as e:
                console.print(f"[red]✗ Validation Error: {e}")
                sys.exit(1)
            progress.advance(task)

            if validate_only:
                console.print("[green]✓ Validation successful!")
                return

            # Step 2: Parse
            progress.update(task, description="[cyan]Parsing questions...")
            parser = MarkdownParser()
            try:
                quiz = parser.parse_file(input_file)
            except TextToQTIError as e:
                console.print(f"[red]✗ Parse Error: {e}")
                sys.exit(1)
            progress.advance(task)

            # Step 3: Generate QTI
            progress.update(task, description="[cyan]Generating QTI XML...")
            try:
                generator = QTIGenerator(quiz, version=qti_version)
            except TextToQTIError as e:
                console.print(f"[red]✗ Generation Error: {e}")
                sys.exit(1)
            progress.advance(task)

            # Step 4: Package
            progress.update(task, description="[cyan]Creating ZIP package...")
            output_path = output or "output.zip"
            try:
                result_path = generator.generate(output_path)
            except TextToQTIError as e:
                console.print(f"[red]✗ Error: {e}")
                sys.exit(1)
            progress.advance(task)

        console.print(f"[green]✓ QTI package created: {result_path}")
        console.print(f"[yellow]Total questions: {len(quiz.questions)}")
        console.print(f"[yellow]Total points: {quiz.get_total_points()}")

    except TextToQTIError as e:
        console.print(f"[red]✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}")
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file: str) -> None:
    """Validate a text file syntax."""
    try:
        validator = SyntaxValidator()
        validator.validate_file(input_file)
        console.print("[green]✓ Validation successful!")
    except TextToQTIError as e:
        console.print(f"[red]✗ Validation Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
