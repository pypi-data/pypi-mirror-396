"""
Resume templates for the Agentic Resume Builder.

This module provides default resume templates with standard sections
and explanatory comments to guide users.
"""

from typing import Dict


class ResumeTemplates:
    """Collection of resume templates."""

    @staticmethod
    def get_template(template_type: str = "professional") -> str:
        """
        Get a resume template by type.

        Args:
            template_type: Type of template (professional, academic, technical)

        Returns:
            str: Markdown template content

        Raises:
            ValueError: If template type is not recognized
        """
        templates = {
            "professional": ResumeTemplates.professional_template(),
            "academic": ResumeTemplates.academic_template(),
            "technical": ResumeTemplates.technical_template(),
        }

        if template_type not in templates:
            raise ValueError(
                f"Unknown template type: {template_type}. "
                f"Available types: {', '.join(templates.keys())}"
            )

        return templates[template_type]

    @staticmethod
    def list_templates() -> Dict[str, str]:
        """
        List all available templates with descriptions.

        Returns:
            Dict[str, str]: Mapping of template names to descriptions
        """
        return {
            "professional": "General professional resume for most industries",
            "academic": "Academic resume with focus on research and publications",
            "technical": "Technical resume emphasizing projects and technologies",
        }

    @staticmethod
    def professional_template() -> str:
        """
        Get the professional resume template.

        Returns:
            str: Professional template in Markdown format
        """
        return """# Your Full Name

your.email@example.com | (555) 123-4567 | City, State

LinkedIn: https://linkedin.com/in/yourprofile | GitHub: https://github.com/yourusername

## Summary

<!-- Write a brief professional summary (2-3 sentences) highlighting your key strengths,
     years of experience, and what you bring to potential employers. Focus on impact
     and quantifiable achievements. -->

A results-driven professional with X years of experience in [your field]. Proven track
record of [key achievement with metrics]. Skilled in [core competencies] with a passion
for [what drives you professionally].

## Experience

<!-- List your work experiences in reverse chronological order (most recent first).
     For each position, include:
     - Company name as a heading (###)
     - Job title and employment dates
     - 3-5 bullet points describing achievements (not just responsibilities)
     - Use action verbs and quantify results with numbers, percentages, or metrics
     - Focus on IMPACT: What changed because of your work? -->

### Company Name

Software Engineer | Jan 2020 - Present

*City, State*

- Developed and launched [feature/product] that increased [metric] by X%, resulting in [business impact]
- Led a team of X engineers to deliver [project] ahead of schedule, reducing [cost/time] by Y%
- Implemented [technical solution] that improved [performance metric] by Z%, affecting [number] users
- Collaborated with [teams/stakeholders] to [achieve specific outcome with measurable results]

**Technologies:** Python, JavaScript, React, PostgreSQL, AWS

### Previous Company Name

Junior Software Engineer | Jun 2018 - Dec 2019

*City, State*

- Built [feature/component] that handled [volume/scale] with [performance metric]
- Optimized [system/process] reducing [metric] by X% and saving $Y annually
- Contributed to [project] serving [number] users with [uptime/reliability metric]

**Technologies:** Java, Spring Boot, MySQL, Docker

## Education

<!-- List your educational background in reverse chronological order.
     Include degree, major, institution, graduation date, and relevant honors/GPA if strong. -->

### University Name

Bachelor of Science | Computer Science | 2014 - 2018

*GPA: 3.8/4.0*

- Dean's List (all semesters)
- Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering

## Skills

<!-- Organize skills by category. Focus on skills relevant to your target role.
     Be honest - only list skills you can confidently discuss in an interview. -->

**Programming Languages:**
- Python, JavaScript, TypeScript, Java, SQL

**Frameworks & Libraries:**
- React, Node.js, Django, Flask, Spring Boot

**Tools & Technologies:**
- Git, Docker, Kubernetes, AWS, PostgreSQL, MongoDB

**Soft Skills:**
- Team Leadership, Agile/Scrum, Technical Writing, Cross-functional Collaboration

## Projects

<!-- Optional: Include significant personal or open-source projects that demonstrate your skills.
     Focus on projects with measurable impact or interesting technical challenges. -->

### Project Name

*Brief description of the project and its purpose*

- Built [what you built] using [technologies]
- Achieved [measurable outcome: users, performance, recognition]
- Open source: [GitHub link if applicable]

## Certifications

<!-- Optional: List relevant professional certifications with issuing organization and date. -->

- AWS Certified Solutions Architect - Associate (2023)
- Certified Scrum Master (CSM) (2022)

## Awards & Recognition

<!-- Optional: Include notable awards, recognitions, or achievements. -->

- Employee of the Quarter, Q2 2023 - Recognized for exceptional performance on [project]
- Hackathon Winner, Company Internal Hackathon 2022 - Built [winning project]
"""

    @staticmethod
    def academic_template() -> str:
        """
        Get the academic resume template.

        Returns:
            str: Academic template in Markdown format
        """
        return """# Your Full Name

your.email@example.com | (555) 123-4567 | City, State

LinkedIn: https://linkedin.com/in/yourprofile | Google Scholar: [your profile link]

## Summary

<!-- Write a brief academic summary highlighting your research interests, expertise,
     and academic achievements. Focus on your contributions to your field. -->

Dedicated researcher with expertise in [research area] and [number] years of experience
in [specific domain]. Published [number] peer-reviewed papers with [citation count] citations.
Passionate about [research interests] with proven ability to [key strength].

## Education

<!-- List your degrees in reverse chronological order, including current degree if pursuing. -->

### University Name

Ph.D. in [Field] | Expected 2025

*Advisor: Dr. [Name]*

- Dissertation: "[Title of your dissertation]"
- Research Focus: [Brief description of research area]
- GPA: 4.0/4.0

### University Name

Master of Science | [Field] | 2018 - 2020

*Thesis: "[Title of your thesis]"*

- GPA: 3.9/4.0
- Relevant Coursework: [List key courses]

### University Name

Bachelor of Science | [Field] | 2014 - 2018

*Magna Cum Laude, GPA: 3.8/4.0*

## Research Experience

<!-- Detail your research positions, focusing on contributions and outcomes. -->

### Graduate Research Assistant

University Name | Sep 2020 - Present

*Advisor: Dr. [Name]*

- Conducted research on [topic] resulting in [number] publications in top-tier conferences
- Developed [method/algorithm/system] that improved [metric] by X%
- Collaborated with [number] researchers on [project] funded by [funding source]
- Mentored [number] undergraduate students on research projects

### Research Intern

Company/Institution Name | Summer 2019

- Investigated [research question] under supervision of [mentor name]
- Implemented [technical contribution] achieving [measurable result]
- Co-authored paper accepted to [conference/journal]

## Publications

<!-- List publications in reverse chronological order using standard citation format. -->

### Peer-Reviewed Conference Papers

1. **Your Name**, Co-author Name. "Paper Title." *Conference Name (Abbreviation)*, Year. [Best Paper Award]

2. Co-author Name, **Your Name**, Co-author Name. "Paper Title." *Conference Name*, Year.

### Journal Articles

1. **Your Name**, Co-author Name. "Article Title." *Journal Name*, Volume(Issue), Pages, Year. DOI: [link]

### Workshop Papers & Posters

1. **Your Name**, Co-author Name. "Paper Title." *Workshop Name at Conference*, Year.

## Teaching Experience

<!-- List teaching roles and responsibilities. -->

### Teaching Assistant

University Name | Course Name | Fall 2021, Spring 2022

- Assisted professor with course of [number] students
- Led weekly discussion sections and office hours
- Graded assignments and exams, provided detailed feedback
- Received teaching evaluation score of X/5.0

## Technical Skills

**Programming Languages:**
- Python, R, MATLAB, C++, Java

**Research Tools:**
- TensorFlow, PyTorch, scikit-learn, Jupyter, LaTeX

**Specialized Skills:**
- Machine Learning, Statistical Analysis, Data Visualization, Experimental Design

## Grants & Funding

<!-- List research grants and funding you've received or contributed to. -->

- NSF Graduate Research Fellowship, $138,000, 2021-2024
- University Research Grant, $10,000, 2022

## Service & Leadership

<!-- Include academic service, conference organization, reviewing, etc. -->

- Reviewer: [Conference/Journal Names], 2022-Present
- Student Volunteer: [Conference Name], 2021
- President: [Student Organization], 2019-2020

## Awards & Honors

- Best Paper Award, [Conference Name], 2023
- Graduate Fellowship, University Name, 2020-2024
- Summa Cum Laude, University Name, 2018
"""

    @staticmethod
    def technical_template() -> str:
        """
        Get the technical resume template.

        Returns:
            str: Technical template in Markdown format
        """
        return """# Your Full Name

your.email@example.com | (555) 123-4567 | City, State

LinkedIn: https://linkedin.com/in/yourprofile | GitHub: https://github.com/yourusername | Portfolio: https://yourwebsite.com

## Summary

<!-- Write a technical summary highlighting your engineering expertise, specializations,
     and key technical achievements. Focus on technologies and measurable impact. -->

Full-stack software engineer with X years of experience building scalable web applications
and distributed systems. Specialized in [technologies/domains] with proven ability to deliver
high-impact features serving [scale: users/requests/data]. Passionate about [technical interests]
and writing clean, maintainable code.

## Technical Skills

<!-- List technical skills prominently. Organize by category and proficiency level. -->

**Languages:**
- Expert: Python, JavaScript/TypeScript, SQL
- Proficient: Java, Go, Rust
- Familiar: C++, Ruby

**Frontend:**
- React, Vue.js, Next.js, HTML5, CSS3, Tailwind CSS
- State Management: Redux, Zustand, React Query
- Testing: Jest, React Testing Library, Cypress

**Backend:**
- Node.js, Express, Django, Flask, FastAPI
- REST APIs, GraphQL, WebSockets, gRPC
- Microservices Architecture, Event-Driven Systems

**Databases:**
- PostgreSQL, MySQL, MongoDB, Redis
- Database Design, Query Optimization, Migrations

**DevOps & Cloud:**
- AWS (EC2, S3, Lambda, RDS, CloudFront), Google Cloud Platform
- Docker, Kubernetes, Terraform, CI/CD (GitHub Actions, Jenkins)
- Monitoring: Prometheus, Grafana, DataDog

**Tools & Practices:**
- Git, Linux, Agile/Scrum, TDD, Code Review
- System Design, Performance Optimization, Security Best Practices

## Experience

<!-- Focus on technical achievements and the technologies used. Quantify impact. -->

### Company Name

Senior Software Engineer | Jan 2021 - Present

*City, State*

- Architected and built [system/feature] using [technologies] serving [number] users with [performance metric]
- Reduced API response time by X% through [technical approach], improving user experience for [number] users
- Led migration from [old tech] to [new tech], resulting in [metric improvement] and $Y cost savings
- Implemented [technical solution] that increased system throughput by Z requests/second
- Mentored [number] junior engineers on [technical topics] and code review best practices

**Tech Stack:** Python, React, PostgreSQL, Redis, AWS, Docker, Kubernetes

### Previous Company Name

Software Engineer | Jun 2018 - Dec 2020

*City, State*

- Developed [feature/service] handling [volume] with [latency/uptime metric]
- Built [component] using [technology] that reduced [metric] by X%
- Optimized database queries reducing load time from X seconds to Y milliseconds
- Implemented automated testing suite increasing code coverage from X% to Y%

**Tech Stack:** Node.js, Vue.js, MongoDB, AWS Lambda, CircleCI

## Projects

<!-- Highlight significant technical projects with links to code/demos. -->

### Open Source Project Name

*[Brief description] - [GitHub stars/downloads/users if applicable]*

[GitHub: github.com/username/project] | [Demo: project-demo.com]

- Built [what you built] using [technologies]
- Achieved [measurable outcome: performance, adoption, recognition]
- Implemented [interesting technical challenge you solved]
- [Number] GitHub stars, [number] contributors

**Technologies:** [List key technologies]

### Personal Project Name

*[Brief description and purpose]*

[GitHub: github.com/username/project] | [Live: project.com]

- Created [what you created] to solve [problem]
- Handles [scale/volume] with [performance characteristic]
- Features [key technical features]

**Technologies:** [List key technologies]

## Education

### University Name

Bachelor of Science | Computer Science | 2014 - 2018

*GPA: 3.7/4.0*

- Relevant Coursework: Algorithms, Data Structures, Operating Systems, Computer Networks, Database Systems
- Senior Project: [Project name and brief description]

## Certifications

<!-- List relevant technical certifications. -->

- AWS Certified Solutions Architect - Professional (2023)
- Kubernetes Certified Application Developer (CKAD) (2022)
- MongoDB Certified Developer (2021)

## Open Source Contributions

<!-- Highlight contributions to well-known open source projects. -->

- **[Project Name]**: Contributed [feature/fix] ([PR link]) - [impact/adoption]
- **[Project Name]**: Fixed [bug] affecting [number] users ([PR link])
- **[Project Name]**: Improved [aspect] by [metric] ([PR link])

## Speaking & Writing

<!-- Optional: Include technical talks, blog posts, or tutorials. -->

- "Talk Title" - [Conference/Meetup Name], 2023 ([slides/video link])
- "Blog Post Title" - [Platform], 2023 - [number] views ([link])
- Technical tutorial series on [topic] - [number] readers ([link])

## Awards & Recognition

- Hackathon Winner, [Hackathon Name] 2022 - Built [project] in 48 hours
- Top Contributor, [Open Source Project], 2021
- Engineering Excellence Award, [Company Name], 2020
"""
