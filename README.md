# Frappe PCAT Exam

A Frappe app for creating RIASEC-based personality assessment quizzes on top of the LMS (Learning Management System). This app extends the existing LMS functionality to provide specialized personality career assessment tests.

## Features

- **RIASEC Personality Assessment**: Create quizzes based on Holland's RIASEC (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) personality types
- **PCAT Question Categories**: Organize questions by RIASEC categories for targeted assessment
- **Dynamic Scoring**: Automatic calculation of personality type scores based on user responses
- **Top Categories Analysis**: Identify and display the top 3 personality categories for each user
- **Integration with LMS**: Seamlessly integrates with existing Frappe LMS functionality
- **Custom Question Types**: Support for PCAT-specific question types and answer options

## Prerequisites

- Frappe Framework (v16+)
- Frappe LMS app installed
- Python 3.10+

## Installation

### Using Bench (Recommended)

```bash
# Navigate to your bench directory
cd $PATH_TO_YOUR_BENCH

# Get the app
bench get-app frappe_pcat_exam https://github.com/your-org/frappe_pcat_exam --branch main

# Install the app
bench install-app frappe_pcat_exam

# Build assets
bench build
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-org/frappe_pcat_exam.git

# Copy to your bench apps directory
cp -r frappe_pcat_exam $PATH_TO_YOUR_BENCH/apps/

# Install the app
bench install-app frappe_pcat_exam
```

## Setup

### 1. Create PCAT Question Categories

First, create the RIASEC categories:

1. Go to **PCAT Question Category** in the desk
2. Create categories for each RIASEC type:
   - Realistic (R)
   - Investigative (I)
   - Artistic (A)
   - Social (S)
   - Enterprising (E)
   - Conventional (C)

### 2. Set Up RIASEC Answer Options

1. Go to **RIASEC Answer Options** in the desk
2. Create answer options with appropriate values for each category

### 3. Create PCAT Questions

1. Go to **LMS Question** in the desk
2. Check the "Is PCAT Question" checkbox
3. Select the appropriate PCAT Question Category
4. Add your question and answer options

### 4. Create PCAT Quiz

1. Go to **LMS Quiz** in the desk
2. Check the "PCAT Quiz" checkbox
3. Add your PCAT questions to the quiz

## Usage

### For Students/Users

1. Access the PCAT quiz through the LMS interface
2. Answer questions based on your preferences and personality
3. Submit the quiz to receive your RIASEC personality assessment
4. View your top 3 personality categories and scores

### For Administrators

1. **View Submissions**: Check PCAT Submission records to see user results
2. **Analyze Results**: Review top categories and scores for each user
3. **Generate Reports**: Use the data for career counseling and guidance

## Configuration

### Custom Fields

The app adds several custom fields to existing doctypes:

- **LMS Question**: 
  - `custom_is_pcat_question` (Checkbox)
  - `custom_pcat_question_category` (Link to PCAT Question Category)

- **LMS Quiz**:
  - `custom_pcat_quiz` (Checkbox)

### Permissions

The app uses standard Frappe permissions. Ensure users have appropriate access to:
- PCAT Question Category
- RIASEC Answer Options
- PCAT Submission
- PCAT Submission Answer
- PCAT Top Categories

## API Reference

### Quiz Summary Override

The app overrides the default LMS quiz summary method to provide PCAT-specific functionality:

```python
@frappe.whitelist()
def quiz_summary(quiz, results):
    # Returns PCAT-specific results with top 3 categories
```

### Response Format

PCAT quiz submissions return:

```json
{
    "dominant_category": "Social",
    "top_categories": [
        ["Social", 25],
        ["Artistic", 20],
        ["Investigative", 15]
    ],
    "total_score": 60,
    "category_scores": {
        "Social": 25,
        "Artistic": 20,
        "Investigative": 15
    },
    "is_pcat_quiz": true
}
```

## Troubleshooting

### Common Issues

1. **Questions not showing in quiz**: Ensure the "Is PCAT Question" checkbox is checked
2. **Categories not calculating**: Verify RIASEC Answer Options have proper values
3. **Top 3 not displaying**: Check that questions are assigned to PCAT categories

### Logs

Check Frappe logs for detailed error information:

```bash
bench tail-logs
```

### Code Style

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript
- Write meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- RIASEC-based quiz functionality
- Top 3 categories analysis
- Integration with Frappe LMS
