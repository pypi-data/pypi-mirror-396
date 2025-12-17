"""Main QTI generation orchestrator."""

from pathlib import Path
from typing import Optional

from text_to_qti.packager.zip_creator import ZIPCreator
from text_to_qti.parser.question_models import Quiz
from text_to_qti.qti.assessment import AssessmentGenerator
from text_to_qti.qti.canvas_metadata import CanvasMetadataGenerator
from text_to_qti.qti.manifest import ManifestGenerator
from text_to_qti.utils.errors import GenerationError


class QTIGenerator:
    """Main orchestrator for QTI generation (Canvas compatible format)."""

    ASSESSMENT_ID = "ASSESSMENT_001"

    def __init__(self, quiz: Quiz, version: str = "1.2") -> None:
        """Initialize generator.

        Args:
            quiz: Quiz object to generate QTI for
            version: QTI version (1.2 or 2.1)
        """
        self.quiz = quiz
        self.version = version

        self.assessment_gen = AssessmentGenerator()
        self.manifest_gen = ManifestGenerator()
        self.canvas_metadata_gen = CanvasMetadataGenerator()
        self.zip_creator = ZIPCreator()

    def generate(self, output_path: Optional[str] = None) -> Path:
        """Generate complete QTI package (Canvas compatible).

        Args:
            output_path: Optional output file path (default: output.zip)

        Returns:
            Path to created ZIP file

        Raises:
            GenerationError: If generation fails
        """
        try:
            if output_path is None:
                output_path = "output.zip"

            # 1. Generate assessment XML with embedded items
            assessment_xml = self.assessment_gen.generate(self.quiz)

            # 2. Generate Canvas metadata XML
            canvas_metadata_xml = self.canvas_metadata_gen.generate(
                self.quiz, self.ASSESSMENT_ID
            )

            # 3. Generate manifest XML
            manifest_xml = self.manifest_gen.generate(self.quiz, self.ASSESSMENT_ID)

            # 4. Create ZIP package
            return self.zip_creator.create_package(
                output_path,
                manifest_xml,
                assessment_xml,
                canvas_metadata_xml,
            )

        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to generate QTI package: {e}") from e
