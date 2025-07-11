import json
import frappe
from frappe import _

# Import the original LMS method
from lms.lms.doctype.lms_quiz.lms_quiz import quiz_summary as lms_quiz_summary_original

@frappe.whitelist()
def quiz_summary(quiz, results):
    quiz_details = frappe.db.get_value(
        "LMS Quiz",
        quiz,
        ["total_marks", "passing_percentage", "lesson", "course", "custom_pcat_quiz"],
        as_dict=1,
    )

    # If this is a PCAT quiz, run your own logic
    if quiz_details.custom_pcat_quiz:
        return pcat_quiz_summary(quiz, results)
    
    # Otherwise, run the original LMS submission flow
    return lms_quiz_summary_original(quiz, results)


# def pcat_quiz_summary(quiz, results):
#     import json as pyjson
#     results = pyjson.loads(results)
#     category_scores = {}

#     for result in results:
#         question = result.get("question_name")
#         selected_option = result.get("answer")

#         category = frappe.db.get_value("LMS Question", question, "custom_pcat_question_category")
#         if not category:
#             continue

#         option_value = frappe.db.get_value(
#             "RIASEC Answer Options",
#             {"option": selected_option},
#             "value"
#         ) or 0

#         category_scores[category] = category_scores.get(category, 0) + option_value

#     dominant_category = None
#     if category_scores:
#         dominant_category = max(category_scores, key=category_scores.get)

#     # sort & get top 3
#     top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
#     top_three_categories = [{"category": cat, "score": score} for cat, score in top_categories[:3]]

#     submission = frappe.new_doc("PCAT Submission")
#     submission.user = frappe.session.user
#     submission.dominant_riasec_category = dominant_category or "Not Determined"
#     submission.total_score = sum(category_scores.values())
#     submission.submission_date = frappe.utils.now()
#     submission.top_three_categories = pyjson.dumps(top_three_categories)  # assuming JSON field

#     for result in results:
#         question = result.get("question_name")
#         selected_option = result.get("answer")
#         category = frappe.db.get_value("LMS Question", question, "custom_pcat_question_category")

#         option_value = frappe.db.get_value(
#             "RIASEC Answer Options",
#             {"option": selected_option},
#             "value"
#         ) or 0

#         submission.append("pcat_answers", {
#             "question": question,
#             "selected_option": selected_option,
#             "riasec_category": category,
#             "score": option_value
#         })

#     submission.insert()
#     frappe.db.commit()

#     return {
#         "dominant_category": dominant_category or "Not Determined",
#         "top_three_categories": top_three_categories,
#         "total_score": submission.total_score,
#         "category_scores": category_scores,
#         "is_pcat_quiz": True
#     }



def pcat_quiz_summary(quiz, results):
    import json as pyjson
    results = pyjson.loads(results)
    category_scores = {}

    for result in results:
        question = result.get("question_name")
        selected_option = result.get("answer")

        category = frappe.db.get_value("LMS Question", question, "custom_pcat_question_category")
        if not category:
            continue

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

    submission.insert()
    frappe.db.commit()

    return {
        "dominant_category": dominant_category or "Not Determined",
        "top_categories": top_categories[:top_count],
        "total_score": submission.total_score,
        "category_scores": category_scores,
        "is_pcat_quiz": True
    }
