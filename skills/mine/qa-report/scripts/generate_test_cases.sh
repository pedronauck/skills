#!/bin/bash

# Real-User QA Test Case Generator
# Interactive workflow for creating user-centric test cases with persona,
# journey, and automation annotations.
# Usage: ./generate_test_cases.sh [qa-output-path/test-cases]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Real-User QA Test Case Generator            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Resolve output directory
OUTPUT_DIR="${1:-.}"
mkdir -p "$OUTPUT_DIR"

# Helper functions
prompt_input() {
    local prompt_text="$1"
    local var_name="$2"
    local required="$3"

    while true; do
        echo -e "${CYAN}${prompt_text}${NC}"
        read -r input

        if [ -n "$input" ]; then
            eval "$var_name=\"$input\""
            break
        elif [ "$required" != "true" ]; then
            eval "$var_name=\"\""
            break
        else
            echo -e "${RED}This field is required.${NC}"
        fi
    done
}

# Step 1: Basic Info
echo -e "${MAGENTA}━━━ Step 1: Test Case Basics ━━━${NC}"
echo ""

prompt_input "Test Case ID (e.g., TC-FUNC-001, TC-PERSONA-012, TC-JOURNEY-007):" TC_ID true
prompt_input "Test Case Title (state the surface + persona observation):" TC_TITLE true

echo ""
echo "Priority:"
echo "1) P0 - Critical (Blocks-Completion or Data-Loss on P0 journey)"
echo "2) P1 - High (Trust-Damage or repeated Friction)"
echo "3) P2 - Medium (Friction on lower-traffic surfaces)"
echo "4) P3 - Low (Cosmetic)"
echo ""

prompt_input "Select priority (1-4):" PRIORITY_NUM true

case $PRIORITY_NUM in
    1) PRIORITY="P0 (Critical)" ;;
    2) PRIORITY="P1 (High)" ;;
    3) PRIORITY="P2 (Medium)" ;;
    4) PRIORITY="P3 (Low)" ;;
    *) PRIORITY="P2 (Medium)" ;;
esac

echo ""
echo "Test Type (real-user QA only — TC-INT / TC-SEC / TC-PERF / TC-API are out of scope):"
echo "1) Functional (TC-FUNC-*)"
echo "2) UI/Visual (TC-UI-*)"
echo "3) Regression — journey-driven (TC-REG-*)"
echo "4) Smoke (SMOKE-*)"
echo "5) Persona-driven (TC-PERSONA-*)"
echo "6) Journey-driven (TC-JOURNEY-*)"
echo "7) Charter (TC-CHARTER-*)"
echo "8) Tour-driven (TC-TOUR-*)"
echo "9) CFR — usability/a11y/perf-perception/compat/recoverability (TC-CFR-*)"
echo ""

prompt_input "Select test type (1-9):" TYPE_NUM true

case $TYPE_NUM in
    1) TEST_TYPE="Functional" ;;
    2) TEST_TYPE="UI/Visual" ;;
    3) TEST_TYPE="Regression" ;;
    4) TEST_TYPE="Smoke" ;;
    5) TEST_TYPE="Persona" ;;
    6) TEST_TYPE="Journey" ;;
    7) TEST_TYPE="Charter" ;;
    8) TEST_TYPE="Tour" ;;
    9) TEST_TYPE="CFR" ;;
    *) TEST_TYPE="Functional" ;;
esac

prompt_input "Estimated test time (minutes):" EST_TIME false

# Step 2: Persona
echo ""
echo -e "${MAGENTA}━━━ Step 2: Persona ━━━${NC}"
echo ""

echo "Persona (the user role acting during this test):"
echo "1) New User (first-time visitor; zero familiarity; low patience)"
echo "2) Power User (returning expert; daily user; keyboard-driven)"
echo "3) Casual User (returning, infrequent; remembers goal, not steps)"
echo "4) Mobile User (touch-first; small viewport; often in transit)"
echo "5) Accessibility-Reliant (screen reader / keyboard-only / voice)"
echo "6) Recovering User (returning after a problem; trust fragile)"
echo ""

prompt_input "Select persona (1-6):" PERSONA_NUM true

case $PERSONA_NUM in
    1) PERSONA="New User" ;;
    2) PERSONA="Power User" ;;
    3) PERSONA="Casual User" ;;
    4) PERSONA="Mobile User" ;;
    5) PERSONA="Accessibility-Reliant" ;;
    6) PERSONA="Recovering User" ;;
    *) PERSONA="Casual User" ;;
esac

prompt_input "Journey (J-NN journey name from journey-maps.md, or 'n/a'):" JOURNEY false

# Step 3: Real-User Conditions
echo ""
echo -e "${MAGENTA}━━━ Step 3: Real-User Conditions ━━━${NC}"
echo ""

prompt_input "Device (desktop | laptop | tablet | phone-small | phone-large):" DEVICE false
prompt_input "Network (wifi-fast | wifi-slow | 4g | 3g | flaky):" NETWORK false
prompt_input "Browser (Chrome | Safari | Firefox | iOS Safari | Android Chrome):" BROWSER false
prompt_input "Locale (en-US | pt-BR | de-DE | ar-EG | ...):" LOCALE false
prompt_input "Modality (mouse-keyboard | touch | screen-reader | keyboard-only | voice):" MODALITY false

# Step 4: Automation Strategy
echo ""
echo -e "${MAGENTA}━━━ Step 4: Automation Strategy ━━━${NC}"
echo ""

echo "Automation Target:"
echo "1) E2E (public flow; user-observable behavior)"
echo "2) Manual-only (exploratory / usability / visual / a11y-via-real-AT)"
echo "3) N/A"
echo ""

prompt_input "Select automation target (1-3):" AUTOMATION_TARGET_NUM true

case $AUTOMATION_TARGET_NUM in
    1) AUTOMATION_TARGET="E2E" ;;
    2) AUTOMATION_TARGET="Manual-only" ;;
    3) AUTOMATION_TARGET="N/A" ;;
    *) AUTOMATION_TARGET="N/A" ;;
esac

if [ "$AUTOMATION_TARGET" = "Manual-only" ] || [ "$AUTOMATION_TARGET" = "N/A" ]; then
    AUTOMATION_STATUS="N/A"
    AUTOMATION_COMMAND="N/A"
else
    echo ""
    echo "Automation Status:"
    echo "1) Existing - matching coverage already exists"
    echo "2) Missing - repository supports it but coverage is absent"
    echo "3) Blocked - harness exists but prerequisites are missing"
    echo "4) N/A"
    echo ""

    prompt_input "Select automation status (1-4):" AUTOMATION_STATUS_NUM true

    case $AUTOMATION_STATUS_NUM in
        1) AUTOMATION_STATUS="Existing" ;;
        2) AUTOMATION_STATUS="Missing" ;;
        3) AUTOMATION_STATUS="Blocked" ;;
        4) AUTOMATION_STATUS="N/A" ;;
        *) AUTOMATION_STATUS="Missing" ;;
    esac

    prompt_input "Existing spec path or command (if known):" AUTOMATION_COMMAND false
fi

prompt_input "Automation notes or blocker:" AUTOMATION_NOTES false

# Step 5: Objective
echo ""
echo -e "${MAGENTA}━━━ Step 5: Test Objective ━━━${NC}"
echo ""

prompt_input "Objective (state from the persona's perspective):" OBJECTIVE true
prompt_input "Why this matters to the user (optional):" WHY_IMPORTANT false

# Step 6: Preconditions
echo ""
echo -e "${MAGENTA}━━━ Step 6: Preconditions ━━━${NC}"
echo ""

echo "Enter preconditions (one per line, press Enter twice when done):"
PRECONDITIONS=""
while true; do
    read -r line
    if [ -z "$line" ]; then
        break
    fi
    PRECONDITIONS="${PRECONDITIONS}- ${line}"$'\n'
done

# Step 7: Test Steps
echo ""
echo -e "${MAGENTA}━━━ Step 7: Test Steps (user-language actions) ━━━${NC}"
echo ""

echo "Enter test steps (action in user-language | expected user-side observable)"
echo "Type 'done' when finished"
echo ""

TEST_STEPS=""
STEP_NUM=1

while true; do
    echo -e "${YELLOW}Step $STEP_NUM:${NC}"
    prompt_input "User-language action:" ACTION false

    if [ "$ACTION" = "done" ] || [ -z "$ACTION" ]; then
        break
    fi

    prompt_input "Expected user-side observable:" EXPECTED true

    TEST_STEPS="${TEST_STEPS}${STEP_NUM}. ${ACTION}"$'\n'"   **Expected:** ${EXPECTED}"$'\n'$'\n'
    ((STEP_NUM++))
done

# Step 8: Figma (only for UI/Visual)
echo ""
if [ "$TEST_TYPE" = "UI/Visual" ]; then
    echo -e "${MAGENTA}━━━ Step 8: Figma Design Validation ━━━${NC}"
    echo ""

    prompt_input "Figma design URL (if applicable):" FIGMA_URL false
    prompt_input "Visual elements to validate:" VISUAL_CHECKS false
fi

# Step 9: Edge Cases + Related
echo ""
echo -e "${MAGENTA}━━━ Step 9: Additional Info ━━━${NC}"
echo ""

prompt_input "User edge cases or variations to try (from user-edge-cases.md, e.g. 'refresh mid-submit', 'back after success'):" EDGE_CASES false
prompt_input "Related test cases (IDs):" RELATED_TCS false
prompt_input "Charter (CH-NN if this was surfaced via a charter, else blank):" CHARTER_ID false
prompt_input "Notes or comments:" NOTES false

if [ -z "$PRECONDITIONS" ]; then
    PRECONDITIONS="- [No special preconditions documented]"
fi

if [ -z "$TEST_STEPS" ]; then
    echo -e "${RED}At least one test step is required.${NC}" >&2
    exit 1
fi

if [ -z "$AUTOMATION_COMMAND" ]; then
    AUTOMATION_COMMAND="N/A"
fi

# Generate filename
FILENAME="${TC_ID}.md"
FILENAME="${FILENAME//[^a-zA-Z0-9._-]/}"

OUTPUT_FILE="$OUTPUT_DIR/$FILENAME"

# Generate test case
echo ""
echo -e "${BLUE}Generating test case...${NC}"
echo ""

cat > "$OUTPUT_FILE" << EOF
# ${TC_ID}: ${TC_TITLE}

**Priority:** ${PRIORITY}
**Type:** ${TEST_TYPE}
**Status:** Not Run
**Estimated Time:** ${EST_TIME:-TBD} minutes
**Created:** $(date +%Y-%m-%d)
**Last Updated:** $(date +%Y-%m-%d)
**Persona:** ${PERSONA}
**Journey:** ${JOURNEY:-n/a}
**Charter:** ${CHARTER_ID:-n/a}
**Automation Target:** ${AUTOMATION_TARGET}
**Automation Status:** ${AUTOMATION_STATUS}
**Automation Command/Spec:** ${AUTOMATION_COMMAND}
**Automation Notes:** ${AUTOMATION_NOTES:-None}

---

## Objective

${OBJECTIVE}

${WHY_IMPORTANT:+**Why this matters to the user:** ${WHY_IMPORTANT}}

---

## Preconditions

${PRECONDITIONS}

---

## Real-User Conditions

| Dimension | Value |
|---|---|
| Device | ${DEVICE:-(not specified)} |
| Network | ${NETWORK:-(not specified)} |
| Browser | ${BROWSER:-(not specified)} |
| Locale | ${LOCALE:-en-US} |
| Modality | ${MODALITY:-(not specified)} |

---

## Test Steps

${TEST_STEPS}

---

EOF

# Add Figma section if UI test
if [ "$TEST_TYPE" = "UI/Visual" ] && [ -n "$FIGMA_URL" ]; then
    cat >> "$OUTPUT_FILE" << EOF
## Visual Validation (Figma)

**Design Reference:** ${FIGMA_URL}

**Elements to validate:**
${VISUAL_CHECKS}

**Verification checklist (viewports: 375px, 768px, 1280px):**
- [ ] Layout matches Figma design
- [ ] Spacing (padding/margins) accurate
- [ ] Typography (font, size, weight, color) correct
- [ ] Colors match design system
- [ ] Component states (hover, active, focus, disabled) implemented
- [ ] Responsive behavior as designed

---

EOF
fi

cat >> "$OUTPUT_FILE" << EOF
## Post-conditions

- [Describe user-side state after test execution]
- [Any cleanup required]

---

## Edge Cases & Variations

${EDGE_CASES:-Pick relevant entries from ../qa-execution/references/user-edge-cases.md (refresh-during-submit, double-click, autofill, back-after-error, multi-tab, session-expiry, slow-network, locale switch, etc.)}

---

## Related Test Cases

${RELATED_TCS:-None documented}

---

## Execution History

| Date | Tester | Build | Result | Bug ID | Notes |
|------|--------|-------|--------|--------|-------|
| | | | Not Run | | |

---

## Notes

${NOTES:-None}

EOF

echo -e "${GREEN}Test case generated: ${BLUE}$OUTPUT_FILE${NC}" >&2
echo "$OUTPUT_FILE"
