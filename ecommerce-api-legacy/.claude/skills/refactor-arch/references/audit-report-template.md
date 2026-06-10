# Audit Report Template

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project:       {{project-name}}
Stack:         {{language}} + {{framework}} ({{persistence}})
Architecture:  {{summary of current architecture}}
Files:         {{N}} analyzed | ~{{LOC}} lines
Date:          {{YYYY-MM-DD}}

## Summary
CRITICAL: {{n}} | HIGH: {{n}} | MEDIUM: {{n}} | LOW: {{n}} | DEPRECATED: {{n}}
Total: {{N}} findings

## Findings

### [CRITICAL] 1. <Anti-pattern name>
- **File:** <path:line>
- **Description:** <what was found>
- **Impact:** <consequence>
- **Recommendation:** <fix direction>

### [HIGH] 2. <Anti-pattern name>
- **File:** <path:line>
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [MEDIUM] 3. <Anti-pattern name>
- **File:** <path:line>
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [LOW] 4. <Anti-pattern name>
- **File:** <path:line>
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

## Deprecated APIs
- **<obsolete API>** at <path:line> → use **<modern equivalent>**

================================
Total: {{N}} findings
================================

Read-only report — no file was modified.
```
