# Nuclei Reporter

A Python script to parse [Nuclei](https://github.com/projectdiscovery/nuclei) JSON reports, generate markdown reports, and optionally refine them using OpenAI's `gpt-3.5-turbo` model. Compatible with Nuclei’s JSON schema.

## Features
- Parses Nuclei JSON reports to extract details (name, severity, description, host, type, timestamp, etc.).
- Generates a markdown report with dynamic executive summary, issues, and remediation recommendations.
- Creates severity-based remediation suggestions with references from the schema.
- Supports command-line arguments for input/output paths and OpenAI usage.
- Includes logging for debugging and execution tracking.
- Enhances reports with OpenAI’s `gpt-3.5-turbo` (optional, requires an API key).
- Validates input JSON for required fields.
- Licensed under BSD.

## Requirements
- Python 3.6+
- `openai` package (`pip install openai`)
- A valid OpenAI API key (stored in `OPENAI_API_KEY` environment variable, optional)
- A Nuclei JSON report file (see [schema](https://github.com/projectdiscovery/nuclei/blob/dev/nuclei-jsonschema.json))

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd nuclei-reporter
   ```
2. Install dependencies:
   ```bash
   pip install openai
   ```
3. Optionally, set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## Usage
Run the script with a Nuclei JSON report:
```bash
python nuclei_reporter.py path/to/nuclei_report.json
```
### Options
- `-o, --output <path>`: Specify output report file (default: `nuclei_report_YYYYMMDD_HHMMSS.md`).
- `--no-openai`: Skip OpenAI refinement for faster execution or if no API key is available.

### Examples
- Generate a report with default output:
  ```bash
  python nuclei_reporter.py nuclei_report.json
  ```
- Specify output file and skip OpenAI:
  ```bash
  python nuclei_reporter.py nuclei_report.json -o custom_report.md --no-openai
  ```

## Example Input
A sample `nuclei_report.json` (per the schema):
```json
[
  {
    "template-id": "CVE-2023-1234",
    "info": {
      "name": "Vulnerable Component",
      "severity": "high",
      "description": "Detected a vulnerable component.",
      "reference": ["https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-1234"]
    },
    "host": "example.com",
    "matched-at": "example.com/vuln",
    "type": "http",
    "timestamp": "2025-04-12T10:00:00Z"
  }
]
```

## Output
The script produces a markdown file (e.g., `nuclei_report_20250412_143022.md`) with:
- A dynamic executive summary (issue count, critical issues).
- Issues section with severity, type, description, host, matched-at, timestamp, and references.
- Remediation recommendations tailored to severity.
- Refined by `gpt-3.5-turbo` if enabled.

## Notes
- The Nuclei schema lacks a `"recommendation"` field; the script generates suggestions based on severity and references.
- Logs are saved to `nuclei_reporter.log` for troubleshooting.
- Consider adding external remediation sources (e.g., CVE databases) for richer recommendations.

## Author
- **encrypter15** (encrypter15@gmail.com)

## Version
- **2.2**

## License
- BSD

## Contributing
Submit issues or pull requests for improvements, especially for remediation logic or schema updates.

## Changelog
See [CHANGELOG.md](#changelog) for version history.

## [2.2] - 2025-04-12
- **Added**: Command-line arguments for input/output paths and OpenAI toggle.
- **Added**: Logging to `nuclei_reporter.log` for debugging.
- **Added**: Dynamic remediation recommendations based on severity and references.
- **Added**: Support for `type` and `timestamp` schema fields in reports.
- **Added**: Option to skip OpenAI refinement with `--no-openai`.
- **Added**: Input validation for required schema fields.
- **Changed**: Replaced deprecated `text-davinci-003` with `gpt-3.5-turbo` using `ChatCompletion` API.
- **Improved**: Output filename includes timestamp to avoid overwrites.
- **Improved**: Executive summary with issue counts and critical issue highlights.

## [2.1] - 2025-01-10
- **Added**: Support for Nuclei schema’s `reference` field in reports.
- **Fixed**: Corrected JSON parsing to match schema (root array, not `results`).
- **Improved**: Added error handling for file I/O and OpenAI API calls.
- **Changed**: Save report to `nuclei_formal_report.md` instead of printing.

## [2.0] - 2024-07-15
- **Added**: OpenAI integration for formal report generation.
- **Improved**: Adopted markdown format for reports.
- **Changed**: Modularized parsing and reporting functions.

## [1.1] - 2024-02-20
- **Added**: Basic remediation recommendations section (placeholder due to schema).
- **Fixed**: Handling of missing `info` fields.
- **Improved**: Report structure with severity and host details.

## [1.0] - 2023-10-05
- **Initial Release**: Parsed Nuclei JSON reports to generate simple text output.
```

**Changes**:
- Added new features under v2.2 (CLI args, logging, recommendations, etc.).
- Kept the `gpt-3.5-turbo` change as part of v2.2.
- Maintained existing entries for continuity.

---

### Step 5: Verification

- **Features Added**:
  - CLI args: `python nuclei_reporter.py input.json -o report.md --no-openai`.
  - Logging: Writes to `nuclei_reporter.log`.
  - Recommendations: Severity-based with references (e.g., “Review vendor documentation” for high severity).
  - Schema fields: `type` and `timestamp` included.
  - OpenAI toggle: Skips refinement if `--no-openai` or no API key.
  - Validation: Skips invalid results.
  - Output: Timestamped filename (e.g., `nuclei_report_20250412_143022.md`).
- **Version**: Preserved as 2.2, with all enhancements listed in the changelog.
- **Schema**: Still compliant with Nuclei’s JSON schema.
- **Testing**: Without a JSON file or API key, I rely on the schema and code review. The script should handle the example input correctly and produce a detailed report.

**Sample Output (Simulated)**:
For the example input:
```json
[
  {
    "template-id": "CVE-2023-1234",
    "info": {
      "name": "Vulnerable Component",
      "severity": "high",
      "description": "Detected a vulnerable component.",
      "reference": ["https://cve.mitre.org"]
    },
    "host": "example.com",
    "matched-at": "example.com/vuln",
    "type": "http",
    "timestamp": "2025-04-12T10:00:00Z"
  }
]
```
The report (`nuclei_report_20250412_143022.md`) might look like:
```markdown
This report summarizes findings from a Nuclei security scan conducted on 2025-04-12. Found 1 issue, including 0 critical. Prioritize remediation for high-severity issues.

## Issues

### Vulnerable Component
- **Severity**: High
- **Type**: http
- **Description**: Detected a vulnerable component.
- **Host**: example.com
- **Matched At**: example.com/vuln
- **Timestamp**: 2025-04-12T10:00:00Z
- **Recommendation**: Review vendor documentation and apply patches. See references: https://cve.mitre.org
- **References**: https://cve.mitre.org

## Remediation Recommendations

### Vulnerable Component (High)
- Review vendor documentation and apply patches. See references: https://cve.mitre.org
