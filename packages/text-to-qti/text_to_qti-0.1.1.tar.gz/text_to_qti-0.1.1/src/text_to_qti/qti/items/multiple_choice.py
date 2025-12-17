"""Multiple choice item XML generator."""

from lxml import etree

from text_to_qti.parser.question_models import Question, QuestionType
from text_to_qti.qti.base_item import BaseItemGenerator
from text_to_qti.qti.utils import QTI_NAMESPACE, add_child
from text_to_qti.utils.errors import GenerationError


class MultipleChoiceGenerator(BaseItemGenerator):
    """Generate QTI XML for multiple choice questions."""

    def validate_question(self, question: Question) -> None:
        """Validate that question is a multiple choice question."""
        if question.type != QuestionType.MULTIPLE_CHOICE:
            raise ValueError(f"Expected MULTIPLE_CHOICE, got {question.type}")

    def generate(self, question: Question) -> etree._Element:
        """Generate multiple choice item XML.

        Args:
            question: Multiple choice question

        Returns:
            QTI item XML element

        Raises:
            GenerationError: If generation fails
        """
        try:
            self.validate_question(question)

            # Create questestinterop root element (required by QTI 1.2)
            questestinterop = etree.Element(
                "questestinterop", nsmap={None: QTI_NAMESPACE}
            )

            # Create item element as child of questestinterop
            item = etree.SubElement(questestinterop, "item")
            item.set("ident", question.id)
            item.set("title", f"Question: {question.text[:50]}")

            # Add metadata
            self._add_metadata(item, question)

            # Add presentation
            self._add_presentation(item, question)

            # Add response processing
            self._add_response_processing(item, question)

            # Add feedback
            self._add_feedback(item, question)

            return questestinterop

        except Exception as e:
            raise GenerationError(
                f"Failed to generate multiple choice item: {e}"
            ) from e

    def _add_metadata(self, item: etree._Element, question: Question) -> None:
        """Add metadata section."""
        metadata = add_child(item, "itemmetadata")
        qti_metadata = add_child(metadata, "qtimetadata")

        # Question type
        field = add_child(qti_metadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "question_type")
        add_child(field, "fieldentry", "multiple_choice_question")

        # Points
        field = add_child(qti_metadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "points_possible")
        add_child(field, "fieldentry", str(question.points))

        # Assessment question identifier reference (required by Canvas)
        field = add_child(qti_metadata, "qtimetadatafield")
        add_child(field, "fieldlabel", "assessment_question_identifierref")
        add_child(field, "fieldentry", question.id)

    def _add_presentation(self, item: etree._Element, question: Question) -> None:
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

    def _add_response_processing(
        self, item: etree._Element, question: Question
    ) -> None:
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
            raise GenerationError("Question has no correct answer")

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

    def _add_feedback(self, item: etree._Element, question: Question) -> None:
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
