"""
Strands Agent tools for resume manipulation.

This module provides tools that can be used by the Strands Agent to interact
with and modify resume documents during the interactive session.
"""

import re
from typing import Any, Dict, List, Optional

from agentic_resume_builder.exceptions import MarkdownParseError
from agentic_resume_builder.markdown_processor import MarkdownProcessor
from agentic_resume_builder.models import Achievement, ResumeDocument


class ResumeAgentTools:
    """Collection of tools for the Strands Agent to manipulate resumes."""

    def __init__(self, markdown_processor: MarkdownProcessor):
        """
        Initialize the agent tools.

        Args:
            markdown_processor: MarkdownProcessor instance for document manipulation
        """
        self.processor = markdown_processor

    def update_resume_section(
        self,
        document: ResumeDocument,
        section_name: str,
        content: str,
        position: Optional[int] = None,
    ) -> ResumeDocument:
        """
        Update a specific section of the resume.

        This tool allows the agent to modify resume sections while preserving
        the overall document structure. The position parameter controls where
        new content is inserted within the section.

        Args:
            document: The ResumeDocument to update
            section_name: Name of the section to update (case-insensitive)
            content: New content for the section
            position: Optional position for insertion (0-based index).
                     If None, replaces entire section content.
                     If provided, inserts at that position within the section.

        Returns:
            ResumeDocument: Updated document with modified section

        Raises:
            MarkdownParseError: If section update fails

        Requirements: 4.1, 8.2, 8.3
        """
        # If position is None, replace entire section
        if position is None:
            return self.processor.update_section(document, section_name, content)

        # If position is specified, we need to insert at that position
        # First, get the current section
        current_section = self.processor.get_section(document, section_name)

        if current_section is None:
            # Section doesn't exist, create it with the content
            return self.processor.update_section(document, section_name, content)

        # Split current content into lines
        current_lines = current_section.content.split("\n") if current_section.content else []

        # Insert new content at the specified position
        # Ensure position is within bounds
        insert_pos = max(0, min(position, len(current_lines)))

        # Split new content into lines
        new_lines = content.split("\n")

        # Insert new lines at position
        updated_lines = current_lines[:insert_pos] + new_lines + current_lines[insert_pos:]

        # Join back into content
        updated_content = "\n".join(updated_lines)

        # Update the section with the new content
        return self.processor.update_section(document, section_name, updated_content)

    def add_experience_item(
        self,
        document: ResumeDocument,
        company: str,
        role: str,
        period: str,
        achievements: List[str],
        location: Optional[str] = None,
        technologies: Optional[List[str]] = None,
    ) -> ResumeDocument:
        """
        Add a new work experience item to the resume.

        This tool formats the experience with impact-oriented language,
        ensuring achievements are presented professionally with proper
        structure and emphasis on results.

        Args:
            document: The ResumeDocument to update
            company: Company name
            role: Job role/title
            period: Time period (e.g., "2020-01 - 2022-06" or "2020 - Present")
            achievements: List of achievement descriptions
            location: Optional work location
            technologies: Optional list of technologies used

        Returns:
            ResumeDocument: Updated document with new experience added

        Requirements: 4.1, 4.3, 5.3, 5.5
        """
        # Parse the period to extract start and end dates
        start_date, end_date = self._parse_period(period)

        # Format achievements with impact-oriented language
        formatted_achievements = [
            Achievement(
                description=self._format_achievement(achievement),
                metrics=self._extract_metrics(achievement),
                impact_score=self._calculate_impact_score(achievement),
            )
            for achievement in achievements
        ]

        # Create the experience entry
        from agentic_resume_builder.models import Experience

        new_experience = Experience(
            company=company,
            role=role,
            start_date=start_date,
            end_date=end_date,
            location=location,
            achievements=formatted_achievements,
            technologies=technologies or [],
        )

        # Add to document's experiences list
        updated_doc = document.model_copy(deep=True)
        updated_doc.experiences.insert(0, new_experience)  # Add at the beginning (most recent)

        return updated_doc

    def _parse_period(self, period: str) -> tuple[str, Optional[str]]:
        """
        Parse a period string into start and end dates.

        Args:
            period: Period string (e.g., "2020-01 - 2022-06", "2020 - Present")

        Returns:
            Tuple of (start_date, end_date). end_date is None if "Present" or "Current"
        """
        # Handle various formats
        period = period.strip()

        # Check for "Present" or "Current"
        if "present" in period.lower() or "current" in period.lower():
            # Extract start date
            match = re.search(r"(\d{4}(?:-\d{2})?)", period)
            if match:
                return match.group(1), None
            return "2020", None  # Default fallback

        # Try to extract two dates
        dates = re.findall(r"(\d{4}(?:-\d{2})?)", period)
        if len(dates) >= 2:
            return dates[0], dates[1]
        elif len(dates) == 1:
            return dates[0], None

        # Fallback
        return "2020", None

    def _format_achievement(self, achievement: str) -> str:
        """
        Format an achievement with impact-oriented language.

        Ensures the achievement starts with an action verb and
        emphasizes results and impact.

        Args:
            achievement: Raw achievement description

        Returns:
            Formatted achievement string
        """
        achievement = achievement.strip()

        # Common action verbs for impact-oriented content
        action_verbs = [
            "achieved",
            "improved",
            "increased",
            "reduced",
            "developed",
            "implemented",
            "led",
            "managed",
            "created",
            "designed",
            "optimized",
            "delivered",
            "launched",
            "built",
            "established",
            "drove",
            "spearheaded",
            "executed",
            "streamlined",
            "enhanced",
        ]

        # Check if it already starts with an action verb
        first_word = achievement.split()[0].lower() if achievement else ""
        if first_word not in action_verbs:
            # If it doesn't start with an action verb, try to identify the verb
            # For now, just ensure it's properly capitalized
            achievement = achievement[0].upper() + achievement[1:] if achievement else achievement

        return achievement

    def _extract_metrics(self, achievement: str) -> Dict[str, Any]:
        """
        Extract quantifiable metrics from an achievement description.

        Args:
            achievement: Achievement description

        Returns:
            Dictionary of extracted metrics
        """
        metrics = {}

        # Extract percentages
        percentage_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", achievement)
        if percentage_matches:
            metrics["percentages"] = [float(p) for p in percentage_matches]

        # Extract numbers (with context)
        number_matches = re.findall(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(\w+)?", achievement)
        if number_matches:
            metrics["numbers"] = [
                {"value": num.replace(",", ""), "unit": unit} for num, unit in number_matches
            ]

        # Extract dollar amounts
        dollar_matches = re.findall(r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB])?", achievement)
        if dollar_matches:
            metrics["currency"] = [
                {"amount": amt.replace(",", ""), "scale": scale or ""}
                for amt, scale in dollar_matches
            ]

        return metrics

    def _calculate_impact_score(self, achievement: str) -> float:
        """
        Calculate an impact score for an achievement.

        The score is based on:
        - Presence of quantifiable metrics (numbers, percentages)
        - Use of action verbs
        - Length and detail level

        Args:
            achievement: Achievement description

        Returns:
            Impact score between 0.0 and 1.0
        """
        score = 0.0

        # Check for numbers/percentages (40% of score)
        has_numbers = bool(re.search(r"\d+", achievement))
        has_percentage = bool(re.search(r"\d+(?:\.\d+)?%", achievement))
        if has_percentage:
            score += 0.4
        elif has_numbers:
            score += 0.2

        # Check for action verbs (30% of score)
        action_verbs = [
            "achieved",
            "improved",
            "increased",
            "reduced",
            "developed",
            "implemented",
            "led",
            "managed",
            "created",
            "designed",
            "optimized",
            "delivered",
            "launched",
            "built",
        ]
        first_word = achievement.split()[0].lower() if achievement else ""
        if first_word in action_verbs:
            score += 0.3

        # Check for detail level (30% of score)
        word_count = len(achievement.split())
        if word_count >= 15:
            score += 0.3
        elif word_count >= 10:
            score += 0.2
        elif word_count >= 5:
            score += 0.1

        return min(score, 1.0)

    def enhance_with_metrics(
        self,
        text: str,
        metrics: Dict[str, Any],
    ) -> str:
        """
        Enhance text content by adding quantifiable metrics.

        This tool formats metrics prominently (bold numbers, percentages)
        and uses action verbs and impact-oriented structure to make
        achievements more compelling.

        Args:
            text: Original text to enhance
            metrics: Dictionary of metrics to add. Can include:
                    - 'percentage': percentage improvement (e.g., 30)
                    - 'number': numeric value (e.g., 10000)
                    - 'currency': dollar amount (e.g., "500K")
                    - 'timeframe': time period (e.g., "6 months")
                    - 'team_size': number of people (e.g., 5)
                    - 'custom': custom metric with value and unit

        Returns:
            Enhanced text with formatted metrics

        Requirements: 5.3, 5.5
        """
        enhanced_text = text.strip()

        # Ensure text starts with an action verb
        enhanced_text = self._ensure_action_verb(enhanced_text)

        # Add metrics in a prominent way
        metric_parts = []

        # Handle percentage improvements
        if "percentage" in metrics:
            percentage = metrics["percentage"]
            metric_parts.append(f"**{percentage}%**")

        # Handle numeric values
        if "number" in metrics:
            number = metrics["number"]
            # Format large numbers with commas
            if isinstance(number, (int, float)):
                if number >= 1000:
                    formatted_num = f"{number:,.0f}"
                else:
                    formatted_num = str(number)
            else:
                formatted_num = str(number)
            metric_parts.append(f"**{formatted_num}**")

        # Handle currency
        if "currency" in metrics:
            currency = metrics["currency"]
            metric_parts.append(f"**${currency}**")

        # Handle team size
        if "team_size" in metrics:
            team_size = metrics["team_size"]
            metric_parts.append(f"team of **{team_size}**")

        # Handle timeframe
        if "timeframe" in metrics:
            timeframe = metrics["timeframe"]
            metric_parts.append(f"in **{timeframe}**")

        # Handle custom metrics
        if "custom" in metrics:
            custom = metrics["custom"]
            if isinstance(custom, dict) and "value" in custom:
                value = custom["value"]
                unit = custom.get("unit", "")
                metric_parts.append(f"**{value}** {unit}".strip())
            else:
                metric_parts.append(f"**{custom}**")

        # Integrate metrics into the text
        if metric_parts:
            # Try to intelligently insert metrics
            # If text mentions "by" or "of", insert after that
            if " by " in enhanced_text.lower():
                parts = enhanced_text.split(" by ", 1)
                enhanced_text = f"{parts[0]} by {metric_parts[0]}"
                if len(parts) > 1:
                    enhanced_text += f" {parts[1]}"
                # Add remaining metrics at the end
                if len(metric_parts) > 1:
                    enhanced_text += f" ({', '.join(metric_parts[1:])})"
            elif " of " in enhanced_text.lower() and "number" in metrics:
                parts = enhanced_text.split(" of ", 1)
                enhanced_text = f"{parts[0]} of {metric_parts[0]}"
                if len(parts) > 1:
                    enhanced_text += f" {parts[1]}"
                # Add remaining metrics at the end
                if len(metric_parts) > 1:
                    enhanced_text += f" ({', '.join(metric_parts[1:])})"
            else:
                # Add metrics at the end in parentheses
                enhanced_text += f" ({', '.join(metric_parts)})"

        return enhanced_text

    def _ensure_action_verb(self, text: str) -> str:
        """
        Ensure text starts with an action verb.

        Args:
            text: Text to check

        Returns:
            Text starting with an action verb
        """
        if not text:
            return text

        action_verbs = [
            "achieved",
            "improved",
            "increased",
            "reduced",
            "developed",
            "implemented",
            "led",
            "managed",
            "created",
            "designed",
            "optimized",
            "delivered",
            "launched",
            "built",
            "established",
            "drove",
            "spearheaded",
            "executed",
            "streamlined",
            "enhanced",
            "accelerated",
            "automated",
            "collaborated",
            "coordinated",
            "directed",
            "engineered",
            "facilitated",
            "generated",
            "initiated",
            "maintained",
            "orchestrated",
            "pioneered",
            "resolved",
            "transformed",
        ]

        first_word = text.split()[0].lower() if text else ""

        # If already starts with action verb, just capitalize properly
        if first_word in action_verbs:
            return text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Otherwise, return as-is (agent should provide better input)
        return text[0].upper() + text[1:] if len(text) > 1 else text.upper()

    def analyze_impact_score(self, text: str) -> Dict[str, Any]:
        """
        Analyze how impact-oriented a text is and provide improvement suggestions.

        This tool detects generic content without quantifications and calculates
        a score based on the presence of metrics, action verbs, and quantifications.

        Args:
            text: Text to analyze (e.g., achievement description)

        Returns:
            Dictionary containing:
                - 'score': Impact score between 0.0 and 1.0
                - 'has_metrics': Boolean indicating presence of metrics
                - 'has_action_verb': Boolean indicating presence of action verb
                - 'has_quantification': Boolean indicating presence of numbers
                - 'suggestions': List of improvement suggestions
                - 'detected_metrics': Dictionary of detected metrics

        Requirements: 5.1
        """
        result = {
            "score": 0.0,
            "has_metrics": False,
            "has_action_verb": False,
            "has_quantification": False,
            "suggestions": [],
            "detected_metrics": {},
        }

        if not text or not text.strip():
            result["suggestions"].append("Text is empty. Please provide content to analyze.")
            return result

        text = text.strip()

        # Check for quantifications (numbers, percentages)
        has_numbers = bool(re.search(r"\d+", text))
        has_percentage = bool(re.search(r"\d+(?:\.\d+)?%", text))
        has_currency = bool(re.search(r"\$\s*\d+", text))

        result["has_quantification"] = has_numbers or has_percentage or has_currency

        if has_percentage:
            result["score"] += 0.4
            result["has_metrics"] = True
            percentages = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
            result["detected_metrics"]["percentages"] = [float(p) for p in percentages]
        elif has_numbers:
            result["score"] += 0.2
            result["has_metrics"] = True
            numbers = re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", text)
            result["detected_metrics"]["numbers"] = numbers

        if has_currency:
            result["has_metrics"] = True
            currency = re.findall(r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB])?", text)
            result["detected_metrics"]["currency"] = currency

        # Check for action verbs
        action_verbs = [
            "achieved",
            "improved",
            "increased",
            "reduced",
            "developed",
            "implemented",
            "led",
            "managed",
            "created",
            "designed",
            "optimized",
            "delivered",
            "launched",
            "built",
            "established",
            "drove",
            "spearheaded",
            "executed",
            "streamlined",
            "enhanced",
            "accelerated",
            "automated",
            "collaborated",
            "coordinated",
            "directed",
            "engineered",
            "facilitated",
            "generated",
            "initiated",
            "maintained",
            "orchestrated",
            "pioneered",
            "resolved",
            "transformed",
        ]

        first_word = text.split()[0].lower() if text else ""
        result["has_action_verb"] = first_word in action_verbs

        if result["has_action_verb"]:
            result["score"] += 0.3
        else:
            result["suggestions"].append(
                f"Consider starting with a strong action verb (e.g., {', '.join(action_verbs[:5])})."
            )

        # Check for detail level
        word_count = len(text.split())
        if word_count >= 15:
            result["score"] += 0.3
        elif word_count >= 10:
            result["score"] += 0.2
        elif word_count >= 5:
            result["score"] += 0.1
        else:
            result["suggestions"].append(
                "Text is very brief. Consider adding more detail about the context and impact."
            )

        # Provide suggestions based on what's missing
        if not result["has_quantification"]:
            result["suggestions"].append(
                "Add quantifiable metrics: How many? By what percentage? How much money? How much time?"
            )

        if not has_percentage and has_numbers:
            result["suggestions"].append(
                "Consider expressing impact as a percentage improvement (e.g., 'increased by 30%')."
            )

        # Check for generic/weak words
        weak_words = [
            "helped",
            "worked on",
            "responsible for",
            "assisted",
            "participated",
            "involved in",
        ]
        text_lower = text.lower()
        found_weak_words = [word for word in weak_words if word in text_lower]
        if found_weak_words:
            result["suggestions"].append(
                f"Replace weak phrases ({', '.join(found_weak_words)}) with stronger action verbs that emphasize your direct impact."
            )

        # Check for vague terms
        vague_terms = ["various", "several", "many", "some", "multiple", "numerous"]
        found_vague = [term for term in vague_terms if term in text_lower]
        if found_vague:
            result["suggestions"].append(
                f"Replace vague terms ({', '.join(found_vague)}) with specific numbers."
            )

        # Ensure score is between 0 and 1
        result["score"] = min(result["score"], 1.0)

        # Add overall assessment
        if result["score"] >= 0.8:
            result["assessment"] = "Excellent - Strong impact-oriented content"
        elif result["score"] >= 0.6:
            result["assessment"] = "Good - Has some quantification but could be stronger"
        elif result["score"] >= 0.4:
            result["assessment"] = "Fair - Needs more specific metrics and quantification"
        else:
            result["assessment"] = "Weak - Generic content lacking quantifiable impact"

        return result
