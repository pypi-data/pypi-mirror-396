"""imsmanifest.xml generator."""

from lxml import etree

from text_to_qti.parser.question_models import Quiz
from text_to_qti.utils.errors import GenerationError


class ManifestGenerator:
    """Generate imsmanifest.xml for QTI package."""

    CONTENT_NS = "http://www.imsglobal.org/xsd/imscp_v1p1"
    MD_NS = "http://www.imsglobal.org/xsd/imsmd_v1p2"
    XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

    def generate(
        self, quiz: Quiz, assessment_id: str = "ASSESSMENT_001"
    ) -> etree._Element:
        """Generate manifest XML (Canvas compatible format).

        Args:
            quiz: Quiz object
            assessment_id: Assessment identifier

        Returns:
            Manifest XML element

        Raises:
            GenerationError: If generation fails
        """
        try:
            # Create root manifest element with Canvas-compatible namespaces
            nsmap = {
                None: "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1",
                "lom": "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource",
                "imsmd": self.MD_NS,
                "xsi": self.XSI_NS,
            }

            manifest = etree.Element("manifest", nsmap=nsmap)
            manifest.set("identifier", "MANIFEST_001")
            manifest.set(
                "{%s}schemaLocation" % self.XSI_NS,
                "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd "  # noqa: E501
                "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd "  # noqa: E501
                "http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd",  # noqa: E501
            )

            # Add metadata
            self._add_metadata(manifest, quiz)

            # Add organizations (empty for QTI)
            etree.SubElement(manifest, "organizations")

            # Add resources (Canvas format)
            self._add_resources(manifest, assessment_id)

            return manifest

        except Exception as e:
            raise GenerationError(f"Failed to generate manifest: {e}") from e

    def _add_metadata(self, manifest: etree._Element, quiz: Quiz) -> None:
        """Add manifest metadata."""
        metadata = etree.SubElement(manifest, "metadata")

        schema = etree.SubElement(metadata, "schema")
        schema.text = "IMS Content"

        schema_version = etree.SubElement(metadata, "schemaversion")
        schema_version.text = "1.1.3"

        # LOM metadata
        lom = etree.SubElement(metadata, "{%s}lom" % self.MD_NS)
        general = etree.SubElement(lom, "{%s}general" % self.MD_NS)

        title = etree.SubElement(general, "{%s}title" % self.MD_NS)
        langstring = etree.SubElement(title, "{%s}langstring" % self.MD_NS)
        langstring.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
        langstring.text = quiz.metadata.title

    def _add_resources(self, manifest: etree._Element, assessment_id: str) -> None:
        """Add resources section (Canvas compatible format)."""
        resources = etree.SubElement(manifest, "resources")

        # Main assessment QTI resource
        assessment_resource = etree.SubElement(resources, "resource")
        assessment_resource.set("identifier", assessment_id)
        assessment_resource.set("type", "imsqti_xmlv1p2")
        assessment_resource.set("href", f"{assessment_id}/{assessment_id}.xml")

        file = etree.SubElement(assessment_resource, "file")
        file.set("href", f"{assessment_id}/{assessment_id}.xml")

        # Canvas assessment metadata resource (dependency)
        metadata_id = "ASSESSMENT_META_001"
        assessment_resource.set("href", f"{assessment_id}/{assessment_id}.xml")

        # Add dependency to metadata resource
        dependency = etree.SubElement(assessment_resource, "dependency")
        dependency.set("identifierref", metadata_id)

        # Canvas-specific assessment metadata resource
        metadata_resource = etree.SubElement(resources, "resource")
        metadata_resource.set("identifier", metadata_id)
        metadata_resource.set(
            "type", "associatedcontent/imscc_xmlv1p1/learning-application-resource"
        )
        metadata_resource.set("href", f"{assessment_id}/assessment_meta.xml")

        file = etree.SubElement(metadata_resource, "file")
        file.set("href", f"{assessment_id}/assessment_meta.xml")
