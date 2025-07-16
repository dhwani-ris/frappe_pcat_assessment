import json
import frappe
import logging
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
        
        if quiz_details.custom_pcat_quiz:
            logger.info(f"Processing PCAT quiz: {quiz}")
            pcat_quiz_summary(quiz, results)
        
        # Otherwise, run the original LMS submission flow
        logger.info(f"Processing standard LMS quiz: {quiz}")
        original_result = lms_quiz_summary_original(quiz, results)
        
        # If this is a PCAT quiz, mark the LMS submission as PCAT
        if quiz_details.custom_pcat_quiz and original_result.get("submission"):
            try:
                # Use db.set_value to avoid triggering validation again
                frappe.db.set_value(
                    "LMS Quiz Submission", 
                    original_result["submission"], 
                    "custom_is_pcat_submission", 
                    1
                )
                logger.info(f"Marked LMS submission {original_result['submission']} as PCAT submission")
            except Exception as e:
                logger.error(f"Error marking submission as PCAT: {str(e)}")
        
        return original_result
        
    except Exception as e:
        logger.error(f"Error in quiz_summary for quiz {quiz}: {str(e)}")
        frappe.throw(_("Error processing quiz submission. Please try again."))


def pcat_quiz_summary(quiz, results):
    """
    Process PCAT quiz submission and calculate RIASEC category scores.
    
    Args:
        quiz (str): Quiz name
        results (str): JSON string of quiz results
        
    Returns:
        dict: PCAT quiz summary with top categories
    """
    try:
        import json as pyjson
        results = pyjson.loads(results)
        category_scores = {}

    # Validate results
        if not results or not isinstance(results, list):
            frappe.throw(_("Invalid quiz results format"))
        
        for result in results:
            question = result.get("question_name")
            selected_option = result.get("answer")
            
            # Validate question exists and is a PCAT question
            if not question:
                continue
                
            question_doc = frappe.db.get_value(
                "LMS Question", 
                question, 
                ["custom_is_pcat_question", "custom_pcat_question_category"], 
                as_dict=1
            )
            
            if not question_doc or not question_doc.custom_is_pcat_question:
                logger.warning(f"Question {question} is not a PCAT question, skipping")
                continue
                
            category = question_doc.custom_pcat_question_category
            if not category:
                logger.warning(f"Question {question} has no PCAT category assigned")
                continue

            # Get option value with validation
            option_value = frappe.db.get_value(
                "RIASEC Answer Options",
                {"option": selected_option},
                "value"
            ) or 0

            category_scores[category] = category_scores.get(category, 0) + option_value

        dominant_category = None
        if category_scores:
            dominant_category = max(category_scores, key=category_scores.get)

        submission = frappe.new_doc("PCAT Submission")
        submission.user = frappe.session.user
        submission.quiz = quiz
        submission.dominant_riasec_category = dominant_category or "Not Determined"
        submission.total_score = sum(category_scores.values())
        submission.submission_date = frappe.utils.now()

        # Sort categories by score (highest first)
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        # Always add exactly top 3 categories to the child table
        top_count = 3
        
        # Ensure we have at least 3 categories (fill with empty if needed)
        while len(top_categories) < top_count:
            top_categories.append(("No Category", 0))
        
        # Add exactly 3 rows to the child table
        for idx, (category, score) in enumerate(top_categories[:top_count], start=1):
            submission.append("top_doctop_count_categories", {
                "riasec_category": category,
                "score": score
            })

        # add individual answers
        for result in results:
            question = result.get("question_name")
            selected_option = result.get("answer")
            category = frappe.db.get_value("LMS Question", question, "custom_pcat_question_category")
            option_value = frappe.db.get_value(
                "RIASEC Answer Options",
                {"option": selected_option},
                "value"
            ) or 0

            submission.append("pcat_answers", {
                "question": question,
                "selected_option": selected_option,
                "riasec_category": category,
                "score": option_value
            })

        # Insert the submission after all answers are appended
        submission.insert()
        frappe.db.commit()
        
        logger.info(f"PCAT submission created successfully for user {frappe.session.user}")
        
        return {
            "dominant_category": dominant_category or "Not Determined",
            "top_categories": top_categories[:top_count],
            "total_score": submission.total_score,
            "category_scores": category_scores,
            "is_pcat_quiz": True,
            "quiz": quiz
        }
        
    except Exception as e:
        logger.error(f"Error in pcat_quiz_summary for quiz {quiz}: {str(e)}")
        frappe.db.rollback()
        frappe.throw(_("Error processing PCAT quiz submission. Please try again."))
