"""Assessment XML generator."""

from lxml import etree

from text_to_qti.parser.question_models import QuestionType, Quiz
from text_to_qti.qti.utils import QTI_NAMESPACE, add_child
from text_to_qti.utils.errors import GenerationError


class AssessmentGenerator:
    """Generate QTI assessment XML structure with embedded items (Canvas compatible)."""

    def generate(self, quiz: Quiz) -> etree._Element:
        """Generate assessment XML with all items embedded.

        Args:
            quiz: Quiz object

        Returns:
            Assessment XML element

        Raises:
            GenerationError: If generation fails
        """
        try:
            # Create questestinterop root element (required by QTI 1.2)
            questestinterop = etree.Element(
                "questestinterop",
                nsmap={None: QTI_NAMESPACE},
            )
            questestinterop.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd",
            )

            # Create assessment element as child of questestinterop
            assessment = etree.SubElement(questestinterop, "assessment")
            assessment.set("ident", "ASSESSMENT_001")
            assessment.set("title", quiz.metadata.title)

            # Add metadata
            self._add_metadata(assessment, quiz)

            # Add section with embedded items (Canvas format)
            self._add_section(assessment, quiz)

            return questestinterop

        except Exception as e:
            raise GenerationError(f"Failed to generate assessment: {e}") from e

    def _add_metadata(self, assessment: etree._Element, quiz: Quiz) -> None:
        """Add assessment metadata."""
        qti_metadata = add_child(assessment, "qtimetadata")

        # Max attempts
        field = add_child(qti_metadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "cc_maxattempts")
        add_child(field, "fieldentry", "1")

        # Shuffle answers if needed
        if quiz.metadata.shuffle_answers:
            field = add_child(qti_metadata, "qtimetadatafield")
            add_child(field, "fieldlabel", "shuffle_answers")
            add_child(field, "fieldentry", "true")

    def _add_section(self, assessment: etree._Element, quiz: Quiz) -> None:
        """Add section with embedded items (Canvas compatible format)."""
        section = add_child(assessment, "section")
        section.set("ident", "root_section")

        for question in quiz.questions:
            self._add_item(section, question)

    def _add_item(self, section: etree._Element, question) -> None:
        """Add a complete item with all metadata and presentation."""
        item = add_child(section, "item")
        item.set("ident", question.id)
        item.set("title", "Question")

        # Add item metadata
        self._add_item_metadata(item, question)

        # Add presentation
        self._add_presentation(item, question)

        # Add response processing
        self._add_response_processing(item, question)

        # Add feedback
        self._add_feedback(item, question)

    def _add_item_metadata(self, item: etree._Element, question) -> None:
        """Add item metadata section."""
        itemmetadata = add_child(item, "itemmetadata")
        qtimetadata = add_child(itemmetadata, "qtimetadata")

        # Question type
        field = add_child(qtimetadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "question_type")
        question_type = self._get_question_type_entry(question.type)
        add_child(field, "fieldentry", question_type)

        # Points (as float, Canvas format)
        field = add_child(qtimetadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "points_possible")
        add_child(field, "fieldentry", f"{float(question.points)}")

        # Original answer IDs (Canvas requirement, can be empty)
        field = add_child(qtimetadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "original_answer_ids")
        add_child(field, "fieldentry", "")

        # Assessment question identifier reference
        field = add_child(qtimetadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "assessment_question_identifierref")
        add_child(field, "fieldentry", question.id)

    def _get_question_type_entry(self, question_type) -> str:
        """Map question type to Canvas QTI entry value."""
        type_map = {
            QuestionType.MULTIPLE_CHOICE: "multiple_choice_question",
            QuestionType.TRUE_FALSE: "true_false_question",
        }
        return type_map.get(question_type, "multiple_choice_question")

    def _add_presentation(self, item: etree._Element, question) -> None:
        """Add presentation section with question text and choices."""
        presentation = add_child(item, "presentation")

        # Question text
        material = add_child(presentation, "material")
        add_child(material, "mattext", question.text, texttype="text/html")

        # Response section
        response = add_child(presentation, "response_lid", rcardinality="Single")
        response.set("ident", "response1")

        # Render choices
        render = add_child(response, "render_choice")

        for choice in question.choices:
            response_label = add_child(render, "response_label")
            response_label.set("ident", f"CHOICE_{choice.letter.upper()}")

            choice_material = add_child(response_label, "material")
            add_child(choice_material, "mattext", choice.text, texttype="text/plain")

    def _add_response_processing(self, item: etree._Element, question) -> None:
        """Add response processing section for scoring."""
        resprocessing = add_child(item, "resprocessing")

        # Outcomes
        outcomes = add_child(resprocessing, "outcomes")
        decvar = add_child(outcomes, "decvar")
        decvar.set("maxvalue", "100")
        decvar.set("minvalue", "0")
        decvar.set("varname", "SCORE")
        decvar.set("vartype", "Decimal")

        # Find correct answer
        correct_choice = next((c for c in question.choices if c.is_correct), None)
        if not correct_choice:
            raise GenerationError(f"Question {question.id} has no correct answer")

        # Correct condition
        correct_cond = add_child(resprocessing, "respcondition")
        correct_cond.set("continue", "No")

        condvar = add_child(correct_cond, "conditionvar")
        varequal = add_child(
            condvar, "varequal", f"CHOICE_{correct_choice.letter.upper()}"
        )
        varequal.set("respident", "response1")

        add_child(correct_cond, "setvar", "100", action="Set", varname="SCORE")
        add_child(
            correct_cond,
            "displayfeedback",
            feedbacktype="Response",
            linkrefid="correct_fb",
        )

        # General condition for wrong answers
        general_cond = add_child(resprocessing, "respcondition")
        general_cond.set("continue", "Yes")

        condvar = add_child(general_cond, "conditionvar")
        add_child(condvar, "other")

        add_child(
            general_cond,
            "displayfeedback",
            feedbacktype="Response",
            linkrefid="general_fb",
        )

    def _add_feedback(self, item: etree._Element, question) -> None:
        """Add feedback sections."""
        # Correct feedback
        feedback = add_child(item, "itemfeedback")
        feedback.set("ident", "correct_fb")

        flow = add_child(feedback, "flow_mat")
        material = add_child(flow, "material")
        feedback_text = question.feedback or "Correct!"
        add_child(material, "mattext", feedback_text, texttype="text/html")

        # General feedback
        feedback = add_child(item, "itemfeedback")
        feedback.set("ident", "general_fb")

        flow = add_child(feedback, "flow_mat")
        material = add_child(flow, "material")
        general_text = question.feedback or "Incorrect. Please review the material."
        add_child(material, "mattext", general_text, texttype="text/html")
