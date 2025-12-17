"""Canvas-specific assessment metadata XML generator."""

from lxml import etree

from text_to_qti.parser.question_models import Quiz
from text_to_qti.utils.errors import GenerationError


class CanvasMetadataGenerator:
    """Generate Canvas-specific assessment_meta.xml file."""

    def generate(
        self, quiz: Quiz, assessment_id: str = "ASSESSMENT_001"
    ) -> etree._Element:
        """Generate Canvas assessment metadata XML.

        Args:
            quiz: Quiz object
            assessment_id: Assessment identifier

        Returns:
            Canvas metadata XML element

        Raises:
            GenerationError: If generation fails
        """
        try:
            quiz_elem = etree.Element(
                "quiz",
                identifier=assessment_id,
                xmlns="http://canvas.instructure.com/xsd/cccv1p0",
            )
            quiz_elem.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd",
            )

            # Basic quiz metadata
            self._add_basic_metadata(quiz_elem, quiz)

            # Assignment metadata
            self._add_assignment_metadata(quiz_elem, assessment_id)

            return quiz_elem

        except Exception as e:
            raise GenerationError(f"Failed to generate Canvas metadata: {e}") from e

    def _add_basic_metadata(self, quiz_elem: etree._Element, quiz: Quiz) -> None:
        """Add basic quiz metadata."""
        # Title
        title = etree.SubElement(quiz_elem, "title")
        title.text = quiz.metadata.title

        # Description
        description = etree.SubElement(quiz_elem, "description")
        description.text = quiz.metadata.description or ""

        # Quiz settings
        self._add_quiz_settings(quiz_elem, quiz)

    def _add_quiz_settings(self, quiz_elem: etree._Element, quiz: Quiz) -> None:
        """Add quiz settings."""
        # Due date (optional)
        due_at = etree.SubElement(quiz_elem, "due_at")
        due_at.text = ""

        # Shuffle answers
        shuffle = etree.SubElement(quiz_elem, "shuffle_answers")
        shuffle.text = "true" if quiz.metadata.shuffle_answers else "false"

        # Scoring policy
        scoring = etree.SubElement(quiz_elem, "scoring_policy")
        scoring.text = "keep_highest"

        # Hide results
        hide_results = etree.SubElement(quiz_elem, "hide_results")
        hide_results.text = ""

        # Quiz type
        quiz_type = etree.SubElement(quiz_elem, "quiz_type")
        quiz_type.text = "graded_survey"

        # Points possible
        points = etree.SubElement(quiz_elem, "points_possible")
        points.text = str(float(quiz.get_total_points()))

        # Lockdown browser settings
        etree.SubElement(quiz_elem, "require_lockdown_browser").text = "false"
        etree.SubElement(quiz_elem, "require_lockdown_browser_for_results").text = (
            "false"
        )
        etree.SubElement(quiz_elem, "require_lockdown_browser_monitor").text = "false"
        etree.SubElement(quiz_elem, "lockdown_browser_monitor_data").text = ""

        # Show correct answers
        etree.SubElement(quiz_elem, "show_correct_answers").text = "true"
        etree.SubElement(quiz_elem, "anonymous_submissions").text = "false"
        etree.SubElement(quiz_elem, "could_be_locked").text = "true"
        etree.SubElement(quiz_elem, "disable_timer_autosubmission").text = "false"

        # Attempts
        etree.SubElement(quiz_elem, "allowed_attempts").text = "1"

        # Navigation
        etree.SubElement(quiz_elem, "one_question_at_a_time").text = "false"
        etree.SubElement(quiz_elem, "cant_go_back").text = "false"

        # Availability
        etree.SubElement(quiz_elem, "available").text = "true"
        etree.SubElement(quiz_elem, "one_time_results").text = "false"
        etree.SubElement(quiz_elem, "show_correct_answers_last_attempt").text = "false"
        etree.SubElement(quiz_elem, "only_visible_to_overrides").text = "false"
        etree.SubElement(quiz_elem, "module_locked").text = "false"

    def _add_assignment_metadata(
        self, quiz_elem: etree._Element, assessment_id: str
    ) -> None:
        """Add Canvas assignment metadata."""
        assignment = etree.SubElement(quiz_elem, "assignment")
        assignment.set("identifier", f"ASSIGNMENT_{assessment_id}")

        # Title
        title = etree.SubElement(assignment, "title")
        title.text = quiz_elem.find("title").text

        # Dates
        etree.SubElement(assignment, "due_at").text = ""
        etree.SubElement(assignment, "lock_at").text = ""
        etree.SubElement(assignment, "unlock_at").text = ""
        etree.SubElement(assignment, "module_locked").text = "false"
        etree.SubElement(assignment, "all_day_date").text = ""

        # Workflow
        etree.SubElement(assignment, "workflow_state").text = "published"

        # Assignment overrides
        etree.SubElement(assignment, "assignment_overrides")

        # Quiz reference
        quiz_ref = etree.SubElement(assignment, "quiz_identifierref")
        quiz_ref.text = assessment_id

        # Extensions
        etree.SubElement(assignment, "allowed_extensions").text = ""
        etree.SubElement(assignment, "has_group_category").text = "false"

        # Points and grading
        points = etree.SubElement(assignment, "points_possible")
        points.text = quiz_elem.find("points_possible").text

        etree.SubElement(assignment, "grading_type").text = "points"
        etree.SubElement(assignment, "all_day").text = "true"
        etree.SubElement(assignment, "submission_types").text = "online_quiz"
        etree.SubElement(assignment, "position").text = "1"

        # Plagiarism tools
        etree.SubElement(assignment, "turnitin_enabled").text = "false"
        etree.SubElement(assignment, "vericite_enabled").text = "false"

        # Peer review
        etree.SubElement(assignment, "peer_review_count").text = "0"
        etree.SubElement(assignment, "peer_reviews").text = "false"
        etree.SubElement(assignment, "automatic_peer_reviews").text = "false"
        etree.SubElement(assignment, "anonymous_peer_reviews").text = "false"
        etree.SubElement(assignment, "grade_group_students_individually").text = "false"

        # Copying and grading
        etree.SubElement(assignment, "freeze_on_copy").text = "false"
        etree.SubElement(assignment, "omit_from_final_grade").text = "false"
        etree.SubElement(assignment, "hide_in_gradebook").text = "false"
        etree.SubElement(assignment, "intra_group_peer_reviews").text = "false"
        etree.SubElement(assignment, "only_visible_to_overrides").text = "false"
        etree.SubElement(assignment, "post_to_sis").text = "false"

        # Moderation and grading
        etree.SubElement(assignment, "moderated_grading").text = "false"
        etree.SubElement(assignment, "grader_count").text = "0"
        etree.SubElement(assignment, "grader_comments_visible_to_graders").text = "true"
        etree.SubElement(assignment, "anonymous_grading").text = "false"
        etree.SubElement(assignment, "graders_anonymous_to_graders").text = "false"
        etree.SubElement(assignment, "grader_names_visible_to_final_grader").text = (
            "true"
        )
        etree.SubElement(assignment, "anonymous_instructor_annotations").text = "false"

        # Post policy
        post_policy = etree.SubElement(assignment, "post_policy")
        etree.SubElement(post_policy, "post_manually").text = "false"

        # Assignment group reference
        asg_group_ref = etree.SubElement(quiz_elem, "assignment_group_identifierref")
        asg_group_ref.text = "DEFAULT_GROUP"

        # Assignment overrides (empty)
        etree.SubElement(quiz_elem, "assignment_overrides")
