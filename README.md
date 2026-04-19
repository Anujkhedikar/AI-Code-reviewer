# AI-Code-reviewer

 A Python-based automated code review tool that analyzes source code, detects structural errors using Abstract Syntax Trees (AST), and provides intelligent refactoring suggestions and feedback using AI. The project is wrapped in a web interface built with the Reflex framework and incorporates structured Agile project management practices.

# Technologies: 
1) Python
2) Reflex (Web Framework)
3) AST (Abstract Syntax Tree) Parsing
4) Generative AI (for intelligent code suggestions)
5) Pytest (for unit testing)

# Features:
1) Static Code Analysis: Parses code to detect logical and syntax errors using a custom AST visitor pattern.
2) AI-Powered Feedback: Automatically generates context-aware improvements and refactoring advice.
3) Interactive UI: Provides a web-based dashboard for users to submit code and view reviews.
3) Built-in Quality Assurance: Includes structured templates for Agile planning, defect tracking, and unit test management.

# Development Process:
The process The development focused on combining static analysis with generative AI. The core engine was built first, using code_parse.py to break down Python code and error_detector_visitor.py to traverse the logic and flag issues. Once the analysis foundation was solid, ai_suggester.py was integrated to provide natural language feedback on the flagged code. The entire backend was then connected to a web frontend configured via rxconfig.py. Concurrently, the project lifecycle was managed using detailed Agile, testing, and defect tracking spreadsheets to maintain software quality.

# What i learned 
How to implement the Visitor design pattern to traverse and extract insights from Abstract Syntax Trees.
The intricacies of integrating AI models into a programmatic workflow to generate reliable, context-aware code suggestions.
Building and structuring full-stack Python web applications using Reflex.
Maintaining a professional development workflow by actively using Agile templates and defect trackers alongside the code.

Overall growth Building this project significantly bridged the gap between theoretical compiler concepts (like ASTs) and practical, user-facing application development. It enhanced my ability to architect a complete software development lifecycle—moving from raw parsing logic to integrating external AI systems, all while maintaining rigorous testing and documentation standards.

# What can be improved 
Expanding the AST parser to support additional programming languages beyond Python.
Enhancing the Reflex UI for a more dynamic, real-time code editing and review experience.
Integrating the tool directly with GitHub/GitLab via webhooks to automatically review Pull Requests.
Refining the AI prompts to allow for different "strictness" levels during the code review.

# How to run the project 
1. Clone the repository:
git clone https://github.com/Anujkhedikar/AI-Code-reviewer.git

2. Navigate to the project directory:
cd AI-Code-reviewer

3. Install the required dependencies:
pip install -r requirements.txt
Set up your environment variables (e.g., configuring your AI API keys if required by the suggester).

4. Initialize and run the Reflex application:
reflex init
reflex run
