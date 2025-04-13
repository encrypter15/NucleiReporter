# nuclei_reporter.py
# Author: encrypter15 (encrypter15@gmail.com)
# Version: 2.2
# License: BSD
# Description: Processes Nuclei JSON reports based on the official schema,
# generates a markdown report with dynamic recommendations, and refines it using
# OpenAI's gpt-3.5-turbo. Enhanced with CLI args, logging, and schema fields (v2.2, 2025-04-12).

import json
import openai
import os
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='nuclei_reporter.log'
)

def parse_nuclei_report(nuclei_json_path):
    """
    Parse a Nuclei JSON report based on the official schema.
    Validates required fields and extracts details for reporting.
    """
    logging.info(f"Parsing JSON file: {nuclei_json_path}")
    try:
        # Open and read the JSON file
        with open(nuclei_json_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error(f"File {nuclei_json_path} not found.")
        print(f"Error: File {nuclei_json_path} not found.")
        return []
    except json.JSONDecodeError:
        logging.error("Invalid JSON format.")
        print("Error: Invalid JSON format.")
        return []

    issues = []
    # Schema: Root is an array of results
    for result in data:
        # Validate required fields
        if not result.get('info') or not result.get('info').get('name'):
            logging.warning(f"Skipping result with missing 'info.name': {result}")
            continue
        
        # Generate dynamic recommendation based on severity and references
        severity = result.get('info', {}).get('severity', 'unknown').lower()
        references = result.get('info', {}).get('reference', [])
        recommendation = (
            "Review vendor documentation and apply patches."
            if severity in ['critical', 'high'] else
            "Assess impact and update configurations."
            if severity in ['medium'] else
            "Monitor and consider mitigation."
        )
        if references:
            recommendation += f" See references: {', '.join(references)}"

        # Extract fields, including new ones (timestamp, type)
        issue = {
            'name': result.get('info', {}).get('name', 'N/A'),
            'severity': severity.capitalize(),
            'description': result.get('info', {}).get('description', 'N/A'),
            'recommendation': recommendation,
            'host': result.get('host', 'N/A'),
            'matched_at': result.get('matched-at', 'N/A'),
            'references': references,
            'type': result.get('type', 'N/A'),
            'timestamp': result.get('timestamp', 'N/A')
        }
        issues.append(issue)
    
    logging.info(f"Parsed {len(issues)} issues.")
    return issues

def generate_report(issues):
    """Generate a markdown report from parsed issues."""
    logging.info("Generating markdown report.")
    # Dynamic executive summary
    issue_count = len(issues)
    critical_count = sum(1 for i in issues if i['severity'].lower() == 'critical')
    executive_summary = (
        f"This report summarizes findings from a Nuclei security scan conducted on {datetime.now().strftime('%Y-%m-%d')}. "
        f"Found {issue_count} issue{'s' if issue_count != 1 else ''}, including {critical_count} critical. "
        "Prioritize remediation for high-severity issues."
    )
    
    # Build issues section with new fields
    issues_section = "\n\n## Issues\n"
    for issue in issues:
        issues_section += f"\n### {issue['name']}\n"
        issues_section += f"- **Severity**: {issue['severity']}\n"
        issues_section += f"- **Type**: {issue['type']}\n"
        issues_section += f"- **Description**: {issue['description']}\n"
        issues_section += f"- **Host**: {issue['host']}\n"
        issues_section += f"- **Matched At**: {issue['matched_at']}\n"
        issues_section += f"- **Timestamp**: {issue['timestamp']}\n"
        issues_section += f"- **Recommendation**: {issue['recommendation']}\n"
        if issue['references']:
            issues_section += f"- **References**: {', '.join(issue['references'])}\n"
    
    # Build remediation recommendations section
    remediation_recommendations = "\n\n## Remediation Recommendations\n"
    for issue in issues:
        remediation_recommendations += f"\n### {issue['name']} ({issue['severity']})\n"
        remediation_recommendations += f"- {issue['recommendation']}\n"
    
    # Combine sections
    report = f"{executive_summary}\n{issues_section}\n{remediation_recommendations}"
    return report

def generate_formal_report(report, use_openai=True):
    """
    Enhance the report using OpenAI's gpt-3.5-turbo model via ChatCompletion API.
    Updated from deprecated text-davinci-003 (v2.2, 2025-04-12).
    Skips OpenAI if use_openai=False or API key is missing.
    """
    if not use_openai:
        logging.info("Skipping OpenAI refinement as requested.")
        return report

    # Check for API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        logging.warning("OpenAI API key not set; skipping refinement.")
        print("Warning: OpenAI API key not set; using original report.")
        return report

    logging.info("Refining report with OpenAI gpt-3.5-turbo.")
    try:
        # Call OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Refine this security report to be more formal, concise, and professional:\n{report}"
                }
            ],
            max_tokens=1500
        )
        refined_report = response.choices[0].message.content.strip()
        logging.info("Report refined successfully.")
        return refined_report
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        print(f"OpenAI API error: {e}; using original report.")
        return report

def main():
    """Main function to orchestrate report generation with CLI args."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Nuclei Report Generator")
    parser.add_argument("json_path", help="Path to Nuclei JSON report")
    parser.add_argument("--output", "-o", default=None, help="Output report file path (default: nuclei_report_YYYYMMDD_HHMMSS.md)")
    parser.add_argument("--no-openai", action="store_true", help="Skip OpenAI report refinement")
    args = parser.parse_args()

    # Set up paths
    nuclei_json_path = args.json_path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output or f"nuclei_report_{timestamp}.md"

    logging.info(f"Starting report generation for {nuclei_json_path}.")

    # Parse the report
    issues = parse_nuclei_report(nuclei_json_path)
    if not issues:
        print("No issues to report.")
        logging.info("No issues found; exiting.")
        return

    # Generate markdown report
    report = generate_report(issues)
    
    # Generate formal report (with OpenAI option)
    formal_report = generate_formal_report(report, use_openai=not args.no_openai)

    # Save to file
    try:
        with open(output_path, 'w') as f:
            f.write(formal_report)
        print(f"Report saved to {output_path}")
        logging.info(f"Report saved to {output_path}")
    except IOError as e:
        logging.error(f"Failed to save report: {e}")
        print(f"Error: Failed to save report to {output_path}")

if __name__ == "__main__":
    main()
