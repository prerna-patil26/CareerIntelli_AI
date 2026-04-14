"""Skill explanation helpers for roadmap detail pages."""

from __future__ import annotations

from app.roadmap.utils import normalize_text


SKILL_DETAILS = {
    "python": {
        "why": "Python is widely used for automation, backend systems, data work, and scripting, so it creates a strong technical base.",
        "usage": "It is used in data science notebooks, backend APIs, automation scripts, and interview problem solving.",
        "learning": ["Learn syntax, functions, loops, and data structures.", "Practice small scripts and file handling.", "Build one project related to your target role."],
    },
    "statistics": {
        "why": "Statistics helps you reason about data, uncertainty, quality, and model performance.",
        "usage": "It is used in analysis, experimentation, machine learning evaluation, and interpreting trends.",
        "learning": ["Start with averages, variance, distributions, and probability.", "Learn hypothesis testing and correlation.", "Apply the concepts in dataset analysis."],
    },
    "data analysis": {
        "why": "Data analysis turns raw information into insights and decisions.",
        "usage": "It is used in reporting, product metrics, business decision making, and exploratory analysis.",
        "learning": ["Practice cleaning data and identifying patterns.", "Use spreadsheets or Python notebooks.", "Explain findings in plain language."],
    },
    "sql": {
        "why": "SQL is the standard way to work with structured data in real products.",
        "usage": "It is used in backend systems, QA validation, dashboards, and analytics pipelines.",
        "learning": ["Learn SELECT, WHERE, JOIN, GROUP BY, and subqueries.", "Practice with sample databases.", "Write queries that answer real business questions."],
    },
    "pandas": {
        "why": "Pandas makes it easier to clean, transform, and inspect tabular data efficiently.",
        "usage": "It is used in notebooks, analytics scripts, feature preparation, and reporting workflows.",
        "learning": ["Learn DataFrame basics, filtering, grouping, and merging.", "Practice with CSV datasets.", "Create a mini data cleaning project."],
    },
    "data visualization": {
        "why": "Visualization helps others understand patterns and insights quickly.",
        "usage": "It is used in dashboards, presentations, and exploratory data analysis.",
        "learning": ["Start with bar, line, scatter, and histogram charts.", "Use clear titles and axis labels.", "Practice explaining one insight per chart."],
    },
    "machine learning": {
        "why": "Machine learning allows systems to learn patterns and make predictions from data.",
        "usage": "It is used in forecasting, recommendations, classification, and anomaly detection.",
        "learning": ["Learn supervised learning basics and metrics.", "Train simple regression and classification models.", "Compare models on one project dataset."],
    },
    "projects": {
        "why": "Projects prove that you can apply knowledge to practical problems.",
        "usage": "They are used in portfolios, interviews, resumes, and real collaboration.",
        "learning": ["Pick one realistic problem.", "Build it end to end.", "Document what you learned and improved."],
    },
    "model deployment": {
        "why": "Deployment turns models from experiments into usable tools.",
        "usage": "It is used when serving predictions in apps, dashboards, or APIs.",
        "learning": ["Learn simple API deployment concepts.", "Package one model with a small interface.", "Track prediction quality after deployment."],
    },
    "testing basics": {
        "why": "Testing basics create the foundation for quality assurance work.",
        "usage": "They are used in manual testing, scenario design, and communication with developers.",
        "learning": ["Understand STLC, SDLC, and test levels.", "Write clear bug reports.", "Practice with sample web apps."],
    },
    "test cases": {
        "why": "Test cases make testing repeatable, measurable, and structured.",
        "usage": "They are used in manual QA, regression suites, and release validation.",
        "learning": ["Write positive and negative test cases.", "Cover edge cases and validation.", "Review test cases for clarity and completeness."],
    },
    "bug tracking": {
        "why": "Bug tracking keeps issues visible, actionable, and easy to reproduce.",
        "usage": "It is used in QA workflows, release management, and collaboration with engineering teams.",
        "learning": ["Learn strong bug titles and reproduction steps.", "Attach logs, screenshots, and expected vs actual behavior.", "Practice using an issue tracker."],
    },
    "api testing": {
        "why": "API testing verifies core business logic beyond the user interface.",
        "usage": "It is used in backend validation, automation, integration testing, and service quality checks.",
        "learning": ["Learn methods, status codes, and payloads.", "Use a tool like Postman.", "Validate happy path and failure cases."],
    },
    "selenium": {
        "why": "Selenium is a common tool for browser automation in QA roles.",
        "usage": "It is used in regression testing, end-to-end automation, and smoke testing.",
        "learning": ["Start with element selectors and navigation.", "Automate one user flow.", "Refactor scripts into reusable functions."],
    },
    "automation frameworks": {
        "why": "Frameworks make automation easier to scale, maintain, and reuse.",
        "usage": "They are used in large QA suites, CI pipelines, and reporting systems.",
        "learning": ["Learn page objects or reusable test layers.", "Separate test data and helpers.", "Add reporting and assertions."],
    },
    "ci/cd testing": {
        "why": "CI/CD testing helps teams catch quality issues before release.",
        "usage": "It is used in automated build pipelines and deployment validation.",
        "learning": ["Understand pipeline stages.", "Run tests automatically on commits.", "Review failed runs and artifacts."],
    },
    "performance testing": {
        "why": "Performance testing reveals system bottlenecks before users feel them.",
        "usage": "It is used in release readiness, load planning, and system tuning.",
        "learning": ["Learn load, stress, and spike testing.", "Run small benchmark tests.", "Measure latency, throughput, and failures."],
    },
    "programming basics": {
        "why": "Programming basics are required before building reliable software systems.",
        "usage": "They are used in logic building, debugging, automation, and every development task.",
        "learning": ["Learn variables, conditions, loops, and functions.", "Solve small coding exercises.", "Build tiny CLI projects."],
    },
    "data structures": {
        "why": "Data structures improve both performance and problem-solving ability.",
        "usage": "They are used in backend logic, algorithms, and technical interviews.",
        "learning": ["Learn arrays, stacks, queues, maps, and trees.", "Practice common coding problems.", "Compare time and space tradeoffs."],
    },
    "api development": {
        "why": "API development is central to backend systems and service integration.",
        "usage": "It is used in mobile apps, web frontends, and internal services.",
        "learning": ["Learn REST basics and request handling.", "Build CRUD endpoints.", "Add validation and error handling."],
    },
    "authentication": {
        "why": "Authentication protects users, data, and restricted features.",
        "usage": "It is used in login flows, protected APIs, and role-based access.",
        "learning": ["Understand sessions and tokens.", "Build login and registration flows.", "Learn basic authorization patterns."],
    },
    "system design": {
        "why": "System design helps you build scalable and maintainable software.",
        "usage": "It is used in architecture planning, performance decisions, and senior-level interviews.",
        "learning": ["Learn load balancing, caching, and databases.", "Study common architectures.", "Practice designing one real system."],
    },
    "caching": {
        "why": "Caching reduces repeated work and improves application speed.",
        "usage": "It is used in APIs, database-heavy services, and distributed systems.",
        "learning": ["Understand cache-aside basics.", "Learn expiration strategies.", "Apply caching to one small backend project."],
    },
    "deployment": {
        "why": "Deployment knowledge helps you move software from local development to real users.",
        "usage": "It is used in cloud hosting, CI/CD, release engineering, and production support.",
        "learning": ["Learn environment setup and build steps.", "Deploy one demo app.", "Monitor logs and runtime errors."],
    },
    "html": {
        "why": "HTML provides the semantic structure of every web page.",
        "usage": "It is used in page layouts, forms, accessibility, and SEO.",
        "learning": ["Learn tags, forms, tables, and semantic structure.", "Build simple pages.", "Practice accessible markup."],
    },
    "css": {
        "why": "CSS controls layout, responsiveness, and visual polish.",
        "usage": "It is used in component styling, animations, grids, and mobile adaptation.",
        "learning": ["Learn selectors, box model, flexbox, and grid.", "Style one landing page.", "Practice responsive layouts."],
    },
    "javascript": {
        "why": "JavaScript powers interaction and dynamic behavior in frontend development.",
        "usage": "It is used in forms, API calls, DOM updates, and app logic.",
        "learning": ["Learn variables, arrays, objects, and async basics.", "Manipulate the DOM.", "Build small browser projects."],
    },
    "react": {
        "why": "React is widely used for building modern component-based user interfaces.",
        "usage": "It is used in dashboards, SPAs, product interfaces, and internal tools.",
        "learning": ["Learn components, props, state, and effects.", "Build a small app.", "Fetch data and render lists."],
    },
    "api integration": {
        "why": "Frontend apps need API integration to display real application data.",
        "usage": "It is used in dashboards, forms, search, and authenticated product flows.",
        "learning": ["Use fetch to call APIs.", "Handle loading and error states.", "Connect one UI to a live API."],
    },
    "state management": {
        "why": "State management keeps larger interfaces predictable and maintainable.",
        "usage": "It is used in forms, dashboards, carts, filters, and user flows.",
        "learning": ["Start with local component state.", "Understand lifting state and shared state.", "Manage one non-trivial app flow."],
    },
    "accessibility": {
        "why": "Accessibility improves usability and inclusiveness for all users.",
        "usage": "It is used in forms, navigation, keyboard flows, and semantic page structure.",
        "learning": ["Learn headings, labels, alt text, and contrast.", "Test keyboard navigation.", "Review one page with accessibility checks."],
    },
    "performance optimization": {
        "why": "Performance optimization creates faster and smoother user experiences.",
        "usage": "It is used in frontend rendering, bundle size reduction, and perceived speed improvement.",
        "learning": ["Learn image optimization and lazy loading.", "Measure with browser tools.", "Improve one slow page."],
    },
}


def get_skill_details(skill_name: str) -> dict:
    """Return skill detail content for a skill page."""
    key = normalize_text(skill_name)
    if key in SKILL_DETAILS:
        details = SKILL_DETAILS[key]
    else:
        details = {
            "why": f"{skill_name} helps you progress toward your selected career roadmap and makes your profile more complete.",
            "usage": f"{skill_name} is used in practical project work, interviews, and role-specific execution.",
            "learning": [
                f"Start with the fundamentals of {skill_name}.",
                f"Practice {skill_name} in one small real project.",
                f"Review examples of how professionals use {skill_name} in your target role.",
            ],
        }

    return {"skill": skill_name, **details}
