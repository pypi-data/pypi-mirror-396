"""QTI ZIP package creator."""

import zipfile
from pathlib import Path

from lxml import etree

from text_to_qti.qti.utils import element_to_string
from text_to_qti.utils.errors import GenerationError


class ZIPCreator:
    """Create QTI ZIP packages for Canvas import (Canvas compatible format)."""

    ASSESSMENT_ID = "ASSESSMENT_001"

    def create_package(
        self,
        output_path: str,
        manifest_xml: etree._Element,
        assessment_xml: etree._Element,
        canvas_metadata_xml: etree._Element,
    ) -> Path:
        """Create QTI ZIP package (Canvas compatible format).

        Args:
            output_path: Path for output ZIP file
            manifest_xml: imsmanifest.xml element
            assessment_xml: Assessment XML element with embedded items
            canvas_metadata_xml: Canvas assessment_meta.xml element

        Returns:
            Path to created ZIP file

        Raises:
            GenerationError: If packaging fails
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add manifest at root
                manifest_str = element_to_string(manifest_xml, with_declaration=True)
                zf.writestr("imsmanifest.xml", manifest_str)

                # Add assessment with embedded items (Canvas format)
                assessment_str = element_to_string(
                    assessment_xml, with_declaration=True
                )
                zf.writestr(
                    f"{self.ASSESSMENT_ID}/{self.ASSESSMENT_ID}.xml", assessment_str
                )

                # Add Canvas-specific metadata
                metadata_str = element_to_string(
                    canvas_metadata_xml, with_declaration=True
                )
                zf.writestr(f"{self.ASSESSMENT_ID}/assessment_meta.xml", metadata_str)

            return output_file

        except Exception as e:
            raise GenerationError(f"Failed to create ZIP package: {e}") from e
