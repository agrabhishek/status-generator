# AI Judge Implementation Guide

## Overview

The AI Judge feature provides **automatic validation** of generated Jira reports with **auto-regeneration** capabilities to ensure all report content is **fully grounded** in actual ticket data.

---

## Key Features

### 1. **Automatic Validation**
- AI Judge automatically validates reports after generation
- Checks for completeness, accuracy, and data grounding
- Verifies no hallucinated or fabricated content

### 2. **Auto-Regeneration Loop**
- If validation fails, report is automatically regenerated with feedback
- **Maximum 2 regeneration attempts** (fail-safe to prevent infinite loops)
- Each regeneration includes specific instructions from judge

### 3. **Strict Grounding Policy**
- Reports can ONLY contain information from actual Jira tickets
- No inference or assumption of missing data
- Insufficient data sections marked as "[Insufficient ticket detail - not specified]"

### 4. **Persona-Specific Validation**
- Different validation criteria for Team Lead, Manager, Group Manager, CTO
- Tailored checks for technical depth vs business focus

---

## Files Modified

### 1. **config.py**
**Added:**
- `AI_JUDGE_CONFIG`: Configuration for judge behavior
- `AI_JUDGE_PROMPTS`: Persona-specific validation prompts with strict verification protocols
- `NO_HALLUCINATION_INSTRUCTIONS`: Instructions enforcing no fabrication policy
- `REGENERATION_MESSAGES`: User-facing status messages

**Key Configuration:**
```python
AI_JUDGE_CONFIG = {
    "enabled": False,
    "auto_validate": True,
    "auto_regenerate": True,
    "max_regeneration_attempts": 2,  # FAIL-SAFE
    "temperature": 0.3,
    "max_tokens": 1200,
    "strict_mode": True
}
```

### 2. **jira_core.py**
**Added Functions:**

#### `extract_ticket_data_for_judge(issues, persona)`
- Extracts structured ticket data for judge comparison
- Returns formatted ticket inventory with counts
- Includes descriptions for detailed verification (Team Lead persona)

#### `parse_judge_evaluation(judge_response)`
- Parses judge LLM response
- Extracts: validation_status, trustworthiness_score, regeneration_required, regeneration_instructions
- Returns structured dict for decision-making

#### `generate_report_with_validation(...)`
- **Main function** implementing auto-validation loop
- Calls `generate_report()` → validates → regenerates if needed
- **Maximum 2 attempts** enforced
- Returns: report, df, next_df, judge_evaluation, validation_passed

### 3. **app.py**
**Added UI Sections:**

#### AI Judge Configuration (before "Generate Report")
- Enable/disable AI Judge checkbox
- Judge LLM provider selection (can differ from report LLM)
- Editable judge validation prompt
- Auto-validation info message

#### Report Generation Logic
- Detects if judge enabled
- Calls `generate_report_with_validation()` instead of regular `generate_report()`
- Displays validation results with trust score

#### Judge Evaluation Display
- Shows trustworthiness score (1-10) with color coding
- Displays validation status (PASS/FAIL/INSUFFICIENT_DATA)
- Shows recommendation (APPROVE/REGENERATE/MANUAL_REVIEW)
- Expandable full judge evaluation report

---

## How It Works

### Workflow

```
1. User clicks "Generate Report"
   ↓
2. [If Judge Enabled]
   ↓
3. ATTEMPT 1: Generate report with no-hallucination instructions
   ↓
4. AI Judge validates:
   - Completeness: All tickets accounted for?
   - Accuracy: No fabricated IDs or data?
   - Grounding: All claims backed by tickets?
   - Metrics: Counts correct?
   ↓
5. [If PASS] → Display report ✅
   ↓
6. [If FAIL & attempt < 2]
   ↓
7. ATTEMPT 2: Regenerate with judge feedback
   - Add "PREVIOUS ISSUES TO FIX" to prompt
   - Include specific regeneration instructions
   ↓
8. AI Judge validates again
   ↓
9. [If PASS] → Display report ✅
   ↓
10. [If FAIL or INSUFFICIENT_DATA]
    → Display report with warning ⚠️
    → Show judge evaluation details
    → Recommend manual review
```

### Fail-Safe Mechanism

**Maximum 2 Regeneration Attempts:**
- Attempt 1: Initial generation
- Attempt 2: Regeneration with feedback (if validation fails)
- If still fails after 2 attempts → stop and display warning

**Why 2 attempts?**
- Prevents infinite regeneration loops
- Catches LLM limitations (if judge always fails)
- Surfaces insufficient data issues (tickets lack detail)

---

## Judge Validation Criteria

### For All Personas

#### 1. **COMPLETENESS (Critical)**
- All tickets in data accounted for in summary
- No missing ticket IDs
- Status: PASS/FAIL

#### 2. **ACCURACY (Critical - Zero Tolerance)**
- Every mentioned ticket ID exists in data
- Statuses match actual data
- Assignees match actual data
- No invented metrics
- List any fabricated content
- Status: PASS/FAIL

#### 3. **GROUNDING CHECK (Critical)**
- Every claim grounded in ticket summary/description
- Flag any inferred or assumed information
- List ungrounded claims
- Status: PASS/FAIL

#### 4. **METRIC VERIFICATION (Critical)**
- Total tickets count matches
- Completion count accurate
- Percentages correctly calculated
- List any metric errors
- Status: PASS/FAIL

#### 5. **INSUFFICIENT DATA (Warning)**
- Identify tickets lacking detail
- Flag sections that can't be completed
- Status: OK/INSUFFICIENT_DATA

### Persona-Specific Checks

**Team Lead:**
- Technical depth appropriate
- Specific components/APIs mentioned from tickets
- Architectural decisions captured

**Manager:**
- Business impact claims match ticket priorities
- No exaggerated outcomes
- Performance claims have evidence

**Group Manager:**
- Portfolio statistics accurate
- Cross-team work captured
- Velocity claims match completion

**CTO:**
- Strategic claims defensible
- ROI/efficiency claims calculable
- Innovation claims grounded in actual work

---

## Judge Output Format

```
TRUSTWORTHINESS_SCORE: 8
VALIDATION_STATUS: PASS

COMPLETENESS: PASS
Missing_Tickets: None

ACCURACY: PASS
Fabricated_Content: None
Hallucinated_IDs: None

GROUNDING: PASS
Ungrounded_Claims: None

METRICS: PASS
Metric_Errors: None

INSUFFICIENT_DATA_SECTIONS: None

REGENERATION_REQUIRED: NO
REGENERATION_INSTRUCTIONS: None

RECOMMENDATION: APPROVE
```

---

## Usage Instructions

### For Users

#### 1. **Enable AI Judge**
- Expand "AI as Judge (Optional)" section
- Check "Enable AI as Judge"
- Note: Auto-validation with max 2 regeneration attempts

#### 2. **Configure Judge LLM**
- Select LLM provider (can be different from report generation)
- Choose model (Groq users: select from available models)
- Enter API key if needed

#### 3. **Customize Validation Criteria (Optional)**
- Edit "Judge Validation Prompt" text area
- Modify verification checklist as needed
- Keep placeholders: {ticket_data}, {summary_text}, {ticket_count}

#### 4. **Generate Report**
- Click "Generate Report"
- System will:
  - Generate report with no-hallucination instructions
  - Automatically run AI Judge validation
  - Regenerate if issues found (max 1 retry)
  - Display results with trust score

#### 5. **Review Judge Results**
- Check **Trustworthiness Score** (1-10)
  - 8-10: High confidence ✅
  - 6-7: Medium confidence ⚠️
  - 1-5: Low confidence ❌ (review required)
- View **Validation Status**: PASS/FAIL/INSUFFICIENT_DATA
- See **Recommendation**: APPROVE/REGENERATE/MANUAL_REVIEW
- Expand "View Full Judge Evaluation" for details

---

## Handling Insufficient Data

### What It Means
When Jira tickets lack sufficient detail (e.g., no description, generic summaries), the report generator **cannot** and **will not** fabricate information.

### How It's Handled

#### In Report Generation:
- Sections with insufficient data marked: `[Insufficient ticket detail - not specified]`
- No assumptions made about technologies, approaches, or details

#### In Judge Validation:
- Judge flags `INSUFFICIENT_DATA_SECTIONS`
- Validation status may be `INSUFFICIENT_DATA`
- Recommendation typically: `MANUAL_REVIEW`

#### User Action Required:
1. **Improve Jira ticket quality:**
   - Add descriptions
   - Document technical details
   - Specify technologies used
   
2. **Accept limitations:**
   - Manually fill in known details after generation
   - Add context from external sources
   - Use report as starting point

---

## Example Scenarios

### Scenario 1: Perfect Pass ✅

**Tickets:** Well-documented with descriptions, clear statuses
**Judge Result:**
- Trustworthiness: 9/10
- Status: PASS
- Recommendation: APPROVE
**Outcome:** Report displayed with high confidence badge

### Scenario 2: Auto-Regeneration Success 🔄

**Attempt 1:**
- Missing 2 tickets in summary
- Judge detects: COMPLETENESS: FAIL
- Regeneration triggered with instructions

**Attempt 2:**
- All tickets now included
- Judge validates: PASS
- Trustworthiness: 8/10
**Outcome:** Report approved after 1 regeneration

### Scenario 3: Insufficient Data ⚠️

**Tickets:** Minimal descriptions, no technical details
**Judge Result:**
- Trustworthiness: 6/10
- Status: INSUFFICIENT_DATA
- Recommendation: MANUAL_REVIEW
**Outcome:** Report shown with warning; sections marked as insufficient

### Scenario 4: Max Attempts Reached ❌

**Attempt 1:**
- Hallucinated ticket IDs
- Judge: ACCURACY: FAIL

**Attempt 2:**
- Still contains ungrounded claims
- Judge: GROUNDING: FAIL

**Outcome:** Max attempts (2) reached. Report displayed with low trust score. Manual review required.

---

## Configuration Options

### In config.py

```python
# Adjust judge behavior
AI_JUDGE_CONFIG = {
    "max_regeneration_attempts": 2,  # Change to 1 or 3 if needed
    "temperature": 0.3,              # Lower = more consistent
    "strict_mode": True              # Enforce zero-tolerance policy
}
```

### In UI

**Judge LLM Selection:**
- Can use same or different LLM as report generation
- Separate model allows experimentation (e.g., fast model for report, thorough model for judging)

**Judge Prompt Editing:**
- Modify validation checklist
- Add custom criteria
- Adjust strictness level

---

## Best Practices

### 1. **Use Judge for High-Stakes Reports**
- Board presentations
- Executive summaries
- External stakeholder reports

### 2. **Improve Source Data Quality**
- Encourage team to write detailed ticket descriptions
- Document technical approaches in tickets
- Keep ticket statuses updated

### 3. **Review Judge Feedback**
- Read full judge evaluation for improvement insights
- Use feedback to enhance ticket documentation practices

### 4. **Trust But Verify**
- Even with APPROVE recommendation, spot-check critical claims
- Use judge as first-line defense, not replacement for human review

### 5. **Iterate on Prompts**
- Customize judge prompts for your organization's standards
- Add company-specific validation criteria

---

## Troubleshooting

### Judge Always Fails Validation

**Possible Causes:**
- Judge prompt too strict
- Ticket data genuinely insufficient
- LLM model not following instructions

**Solutions:**
1. Review judge evaluation details
2. Check if tickets have adequate descriptions
3. Try different judge LLM model
4. Adjust judge prompt strictness

### Regeneration Loop Not Improving

**Cause:** Report generator LLM unable to meet judge criteria

**Solution:**
- Review specific judge feedback
- Try different report generation model
- Manually improve ticket data quality

### Judge Evaluation Parsing Fails

**Cause:** Judge LLM output doesn't match expected format

**Solution:**
- Check judge prompt includes OUTPUT FORMAT section
- Try higher-capability LLM for judge
- Review `parse_judge_evaluation()` regex patterns

---

## API Usage & Costs

### Token Consumption

**With Judge Enabled:**
- Report generation: ~300-400 tokens
- Judge validation: ~1,200 tokens
- If regeneration: additional 300-400 tokens (report) + 1,200 tokens (judge)

**Maximum tokens per report:**
- 1 attempt (pass): ~1,500 tokens
- 2 attempts: ~2,600 tokens

**Cost Estimate (using Groq Free Tier):**
- Free tier typically sufficient for testing
- Production use: consider OpenAI API costs

---

## Future Enhancements

### Potential Additions

1. **Configurable Max Attempts**
   - UI control for max regeneration loops

2. **Judge Consensus**
   - Multiple judges vote on validation

3. **Learning from Feedback**
   - Store judge evaluations to improve prompts

4. **Automated Ticket Enhancement Suggestions**
   - Judge recommends which tickets need better descriptions

5. **Custom Validation Rules**
   - Company-specific compliance checks
   - Industry-specific validation criteria

---

## Summary

The AI Judge feature provides **audit-level confidence** in generated reports by:

✅ **Verifying completeness** - All tickets accounted for
✅ **Ensuring accuracy** - No hallucinated data
✅ **Enforcing grounding** - All claims backed by tickets
✅ **Auto-correcting** - Regenerates with feedback (max 2 attempts)
✅ **Handling insufficient data** - Never fabricates missing information
✅ **Providing transparency** - Detailed validation reports

This ensures reports are **trustworthy** and **defensible** for stakeholder presentations.
