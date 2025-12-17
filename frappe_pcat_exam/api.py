import json
import logging

import frappe
from frappe import _

# Import the original LMS method
from lms.lms.doctype.lms_quiz.lms_quiz import quiz_summary as lms_quiz_summary_original

# Set up logging
logger = logging.getLogger(__name__)


@frappe.whitelist()
def quiz_summary(quiz, results):
	"""
	Override the default LMS quiz summary to handle PCAT quizzes.

	Args:
	    quiz (str): Quiz name
	    results (str): JSON string of quiz results

	Returns:
	    dict: Quiz summary results
	"""
	try:
		quiz_details = frappe.db.get_value(
			"LMS Quiz",
			quiz,
			["total_marks", "passing_percentage", "lesson", "course", "custom_pcat_quiz"],
			as_dict=1,
		)

		if not quiz_details:
			frappe.throw(_("Quiz not found"))

		# Otherwise, run the original LMS submission flow
		logger.info(f"Processing standard LMS quiz: {quiz}")
		original_result = lms_quiz_summary_original(quiz, results)

		if quiz_details.custom_pcat_quiz:
			logger.info(f"Processing PCAT quiz: {quiz}")
			pcat_quiz_summary(quiz, results)

		# If this is a PCAT quiz, mark the LMS submission as PCAT
		if quiz_details.custom_pcat_quiz and original_result.get("submission"):
			try:
				# Use db.set_value to avoid triggering validation again
				frappe.db.set_value(
					"LMS Quiz Submission", original_result["submission"], "custom_is_pcat_submission", 1
				)
				logger.info(f"Marked LMS submission {original_result['submission']} as PCAT submission")
			except Exception as e:
				logger.error(f"Error marking submission as PCAT: {e!s}")

		return original_result

	except Exception as e:
		logger.error(f"Error in quiz_summary for quiz {quiz}: {e!s}")
		frappe.throw(_("Error processing quiz submission. Please try again."))


def pcat_quiz_summary(quiz, results):
	"""Process PCAT quiz submission and calculate RIASEC category scores."""
	try:
		parsed_results = _validate_and_parse_results(results)
		category_scores = _calculate_category_scores(parsed_results)
		dominant_category = max(category_scores, key=category_scores.get) if category_scores else None
		top_categories = _get_sorted_top_categories(category_scores)

		submission = _create_submission_doc(quiz, category_scores, dominant_category)
		_add_top_categories_to_submission(submission, top_categories)
		_add_individual_answers(submission, parsed_results)

		submission.insert(ignore_permissions=True)
		frappe.db.commit()
		logger.info(f"PCAT submission created successfully for user {frappe.session.user}")

		return _build_response(dominant_category, top_categories, submission, category_scores, quiz)

	except Exception as e:
		logger.error(f"Error in pcat_quiz_summary for quiz {quiz}: {e!s}")
		frappe.db.rollback()
		frappe.throw(_("Error processing PCAT quiz submission. Please try again."))


def _validate_and_parse_results(results):
	"""Parse and validate quiz results JSON."""
	parsed = json.loads(results)
	if not parsed or not isinstance(parsed, list):
		frappe.throw(_("Invalid quiz results format"))
	return parsed


def _calculate_category_scores(results):
	"""Calculate RIASEC category scores from quiz results."""
	category_scores = {}

	for result in results:
		question = result.get("question_name")
		selected_option = result.get("answer")

		if not question:
			continue

		category = _get_question_category(question)
		if not category:
			continue

		option_value = _get_option_value(selected_option)
		category_scores[category] = category_scores.get(category, 0) + option_value

	return category_scores


def _get_question_category(question):
	"""Get PCAT category for a question with validation."""
	question_doc = frappe.db.get_value(
		"LMS Question", question, ["custom_is_pcat_question", "custom_pcat_question_category"], as_dict=1
	)

	if not question_doc or not question_doc.custom_is_pcat_question:
		logger.warning(f"Question {question} is not a PCAT question, skipping")
		return None

	if not question_doc.custom_pcat_question_category:
		logger.warning(f"Question {question} has no PCAT category assigned")
		return None

	return question_doc.custom_pcat_question_category


def _get_option_value(selected_option):
	"""Get score value for selected answer option."""
	return frappe.db.get_value("RIASEC Answer Options", {"option": selected_option}, "value") or 0


def _get_sorted_top_categories(category_scores):
	"""Sort categories by score and order, returning top 3."""
	if not category_scores:
		return [("No Category", 0)] * 3

	category_orders = {
		cat: frappe.db.get_value("PCAT Question Category", cat, "category_order") or 999
		for cat in category_scores.keys()
	}

	top_categories = sorted(category_scores.items(), key=lambda x: (-x[1], category_orders[x[0]]))

	while len(top_categories) < 3:
		top_categories.append(("No Category", 0))

	return top_categories


def _create_submission_doc(quiz, category_scores, dominant_category):
	"""Create PCAT submission document with basic fields."""
	submission = frappe.new_doc("PCAT Submission")
	submission.user = frappe.session.user
	submission.quiz = quiz
	submission.dominant_riasec_category = dominant_category or "Not Determined"
	submission.total_score = sum(category_scores.values())
	submission.submission_date = frappe.utils.now()
	return submission


def _add_top_categories_to_submission(submission, top_categories):
	"""Add top 3 categories to submission child table."""
	for _idx, (category, score) in enumerate(top_categories[:3], start=1):
		submission.append("top_doctop_count_categories", {"riasec_category": category, "score": score})


def _add_individual_answers(submission, results):
	"""Add individual answer details to submission."""
	for result in results:
		question = result.get("question_name")
		selected_option = result.get("answer")
		category = frappe.db.get_value("LMS Question", question, "custom_pcat_question_category")
		option_value = frappe.db.get_value("RIASEC Answer Options", {"option": selected_option}, "value") or 0

		submission.append(
			"pcat_answers",
			{
				"question": question,
				"selected_option": selected_option,
				"riasec_category": category,
				"score": option_value,
			},
		)


def _build_response(dominant_category, top_categories, submission, category_scores, quiz):
	"""Build the response dictionary for PCAT quiz summary."""
	return {
		"dominant_category": dominant_category or "Not Determined",
		"top_categories": top_categories[:3],
		"total_score": submission.total_score,
		"category_scores": category_scores,
		"is_pcat_quiz": True,
		"quiz": quiz,
	}
