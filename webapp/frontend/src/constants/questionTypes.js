/**
 * Question type constants for objective questions
 * These values must match the ObjectiveQuestionType enum in the backend
 */
export const QUESTION_TYPES = {
  ENVIRONMENT: 'environment',
  PERIOD: 'period',
  EMOTION: 'emotion'
};

/**
 * Array of all valid question types for validation
 */
export const VALID_QUESTION_TYPES = Object.values(QUESTION_TYPES);

/**
 * Check if a question type is valid
 * @param {string} type - The question type to validate
 * @returns {boolean} - True if the type is valid
 */
export const isValidQuestionType = (type) => {
  return VALID_QUESTION_TYPES.includes(type);
};
