module.exports = {
  // TypeScript and JavaScript files
  '*.{js,jsx,ts,tsx}': [
    'eslint --fix',
    'prettier --write',
  ],

  // JSON, Markdown, CSS, and other files
  '*.{json,md,css,scss,yaml,yml}': [
    'prettier --write',
  ],

  // Python files (for processing-engine)
  '*.py': [
    'python -m black --check',
    'python -m flake8',
  ],
};
