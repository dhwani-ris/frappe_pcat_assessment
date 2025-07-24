// PCAT Quiz Client Script  
// Cache for question types to avoid repeated DB calls
const questionTypeCache = new Map();
let isProcessingQuizChange = false;

frappe.ui.form.on('LMS Quiz', {
    refresh: function(frm) {
        initializeQuizForm(frm);
    },
    
    custom_pcat_quiz: function(frm) {
        handleQuizTypeChange(frm);
    }
});

frappe.ui.form.on('LMS Quiz Question', {
    question: function(frm, cdt, cdn) {
        validateQuestionSelection(frm, cdt, cdn);
    }
});

/**
 * Initialize quiz form with appropriate filters and validations
 */
function initializeQuizForm(frm) {
    // Clear cache when form loads
    questionTypeCache.clear();
    
    // Apply filter based on current quiz type
    applyQuestionFilter(frm);
    
    // Setup form indicators
    updateFormIndicators(frm);
}

/**
 * Handle quiz type change with loading state and cleanup
 */
async function handleQuizTypeChange(frm) {
    if (isProcessingQuizChange) return;
    
    isProcessingQuizChange = true;
    
    // Apply new filter
    applyQuestionFilter(frm);
    
    // Clean existing incompatible questions
    await cleanIncompatibleQuestions(frm);
    
    // Update form indicators
    updateFormIndicators(frm);
    
    isProcessingQuizChange = false;
}

/**
 * Apply question filter based on quiz type
 */
function applyQuestionFilter(frm) {
    if (!frm || !frm.set_query) return;
    
    frm.set_query('question', 'questions', function() {
        const filters = frm.doc.custom_pcat_quiz 
            ? { 'custom_is_pcat_question': 1 }
            : { 'custom_is_pcat_question': 0 };
            
        return { filters };
    });
}

/**
 * Clean incompatible questions with batched operations and caching
 */
async function cleanIncompatibleQuestions(frm) {
    if (!frm.doc.questions?.length) return;
    
    const questionsToCheck = frm.doc.questions.filter(row => row.question);
    if (!questionsToCheck.length) return;
    
    // Batch get question types (cache hits first)
    const questionTypes = await batchGetQuestionTypes(questionsToCheck.map(row => row.question));
    
    // Identify rows to remove
    const rowsToRemove = [];
    questionsToCheck.forEach((row, index) => {
        const isPcatQuestion = questionTypes[index];
        const shouldRemove = frm.doc.custom_pcat_quiz 
            ? !isPcatQuestion
            : isPcatQuestion;
            
        if (shouldRemove) {
            rowsToRemove.push(row.idx - 1);
        }
    });
    
    // Remove rows in batch (reverse order to maintain indices)
    if (rowsToRemove.length > 0) {
        removeRowsBatch(frm, rowsToRemove);
    }
}

/**
 * Batch get question PCAT status with caching
 */
async function batchGetQuestionTypes(questionIds) {
    const uncachedIds = questionIds.filter(id => !questionTypeCache.has(id));
    
    // Fetch uncached question PCAT status in batch
    if (uncachedIds.length > 0) {
        try {
            const response = await frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'LMS Question',
                    fields: ['name', 'custom_is_pcat_question'],
                    filters: { 'name': ['in', uncachedIds] },
                    limit_page_length: uncachedIds.length
                }
            });
            
            // Cache the results
            if (response.message) {
                response.message.forEach(question => {
                    questionTypeCache.set(question.name, question.custom_is_pcat_question);
                });
            }
        } catch (error) {
            console.error('Error fetching question types:', error);
            frappe.show_alert({
                message: __('Error loading question data. Please refresh and try again.'),
                indicator: 'red'
            });
            throw error;
        }
    }
    
    // Return PCAT status from cache
    return questionIds.map(id => questionTypeCache.get(id));
}

/**
 * Validate question selection with debouncing
 */
const validateQuestionSelection = frappe.utils.debounce(async function(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row?.question) return;
    
    const questionTypes = await batchGetQuestionTypes([row.question]);
    const isPcatQuestion = questionTypes[0];
    
    if (isPcatQuestion === undefined) {
        removeRow(frm, cdn);
        return;
    }
    
    const shouldRemove = frm.doc.custom_pcat_quiz 
        ? !isPcatQuestion
        : isPcatQuestion;
        
    if (shouldRemove) {
        removeRow(frm, cdn);
    }
}, 300);

/**
 * Remove multiple rows efficiently
 */
function removeRowsBatch(frm, rowIndices) {
    if (!rowIndices.length) return;
    
    // Sort in descending order to avoid index shifting
    const sortedIndices = [...rowIndices].sort((a, b) => b - a);
    
    const grid = frm.get_field('questions').grid;
    sortedIndices.forEach(idx => {
        if (grid.grid_rows[idx]) {
            grid.grid_rows[idx].remove();
        }
    });
    frm.refresh_field('questions');
}

/**
 * Remove single row safely
 */
function removeRow(frm, cdn) {
    const grid_row = frm.get_field('questions').grid.get_row(cdn);
    if (grid_row) {
        grid_row.remove();
        frm.refresh_field('questions');
    }
}

/**
 * Update form visual indicators
 */
function updateFormIndicators(frm) {
    const field = frm.get_field('custom_pcat_quiz');
    if (!field) return;
    
    // Update field description
    const description = frm.doc.custom_pcat_quiz
        ? 'Only PCAT questions will be available for selection'
        : 'All questions except PCAT questions will be available';
        
    field.set_description(description);
}



/**
 * Cleanup function for form destruction
 */
frappe.ui.form.on('LMS Quiz', {
    onload: function(frm) {
        // Store cleanup function
        frm._pcat_cleanup = function() {
            questionTypeCache.clear();
            isProcessingQuizChange = false;
        };
    },
    
    before_submit: function(frm) {
        // Validate before submission
        if (frm.doc.custom_pcat_quiz && frm.doc.questions) {
            const hasNonPcatQuestions = frm.doc.questions.some(row => 
                row.question && !questionTypeCache.get(row.question)
            );
            
            if (hasNonPcatQuestions) {
                frappe.throw(__('PCAT quiz cannot contain non-PCAT questions'));
            }
        }
    }
});

// Global cleanup on page unload
$(window).on('beforeunload', function() {
    questionTypeCache.clear();
});
