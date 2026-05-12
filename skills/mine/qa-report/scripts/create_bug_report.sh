#!/bin/bash

# Real-User QA Bug Report Generator
# Create structured, reproducible bug reports keyed by user impact
# (Blocks-Completion / Data-Loss / Trust-Damage / Friction / Cosmetic).
# Usage: ./create_bug_report.sh [qa-output-path/issues]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║     Real-User QA Bug Report Generator            ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Resolve output directory
OUTPUT_DIR="${1:-.}"
mkdir -p "$OUTPUT_DIR"

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

# Bug ID
BUG_ID="BUG-$(date +%Y%m%d%H%M%S)"
echo -e "${YELLOW}Auto-generated Bug ID: $BUG_ID${NC}"
echo ""

# Basic Info
prompt_input "Bug title (state surface + persona observation — e.g., '[Signup] Email cleared on verify error — mobile New User'):" BUG_TITLE true

# Impact (user-side) — drives Severity/Priority defaults
echo ""
echo -e "${MAGENTA}━━━ Impact (user-side) ━━━${NC}"
echo "(See ../qa-execution/references/bug-severity-by-user-impact.md for the full rubric.)"
echo ""
echo "1) Blocks-Completion (user cannot complete journey; gives up or breaks state)"
echo "2) Data-Loss (user's data destroyed / corrupted / inaccessible without consent)"
echo "3) Trust-Damage (nothing broken, but user's confidence eroded)"
echo "4) Friction (user can complete but with extra effort / confusion / repetition)"
echo "5) Cosmetic (visual / wording issue that doesn't affect completion or trust)"
echo ""

prompt_input "Select impact (1-5):" IMPACT_NUM true

case $IMPACT_NUM in
    1) IMPACT="Blocks-Completion"; SEVERITY="Critical"; PRIORITY="P0" ;;
    2) IMPACT="Data-Loss";         SEVERITY="Critical"; PRIORITY="P0" ;;
    3) IMPACT="Trust-Damage";      SEVERITY="High";     PRIORITY="P1" ;;
    4) IMPACT="Friction";          SEVERITY="Medium";   PRIORITY="P2" ;;
    5) IMPACT="Cosmetic";          SEVERITY="Low";      PRIORITY="P3" ;;
    *) IMPACT="Friction";          SEVERITY="Medium";   PRIORITY="P2" ;;
esac

echo ""
echo -e "${YELLOW}Default Severity: ${SEVERITY}, Priority: ${PRIORITY} (per impact rubric).${NC}"
prompt_input "Override Severity? (leave blank to keep ${SEVERITY}):" SEVERITY_OVERRIDE false
prompt_input "Override Priority? (leave blank to keep ${PRIORITY}):" PRIORITY_OVERRIDE false

if [ -n "$SEVERITY_OVERRIDE" ]; then
    SEVERITY="$SEVERITY_OVERRIDE"
fi
if [ -n "$PRIORITY_OVERRIDE" ]; then
    PRIORITY="$PRIORITY_OVERRIDE"
fi

echo ""
echo "Bug type:"
echo "1) Functional"
echo "2) UI"
echo "3) Accessibility"
echo "4) Usability"
echo "5) Data"
echo "6) Crash"
echo ""

prompt_input "Select type (1-6):" TYPE_NUM true

case $TYPE_NUM in
    1) BUG_TYPE="Functional" ;;
    2) BUG_TYPE="UI" ;;
    3) BUG_TYPE="Accessibility" ;;
    4) BUG_TYPE="Usability" ;;
    5) BUG_TYPE="Data" ;;
    6) BUG_TYPE="Crash" ;;
    *) BUG_TYPE="Functional" ;;
esac

# Persona Affected
echo ""
echo -e "${MAGENTA}━━━ Persona Affected ━━━${NC}"
echo ""
echo "1) New User"
echo "2) Power User"
echo "3) Casual User"
echo "4) Mobile User"
echo "5) Accessibility-Reliant"
echo "6) Recovering User"
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

prompt_input "Journey step (e.g., 'J-01 Complete first purchase, Step 4 (payment)'):" JOURNEY_STEP false

# Environment
echo ""
echo -e "${MAGENTA}━━━ Environment Details ━━━${NC}"
echo ""

prompt_input "Build/Version (e.g., v2.5.0 or commit hash):" BUILD true
prompt_input "Operating System (e.g., macOS 14, iOS 17):" OS false
prompt_input "Browser & Version (e.g., Chrome 120, iOS Safari 17):" BROWSER false
prompt_input "Viewport (e.g., 1280 × 800, 375 × 812):" VIEWPORT false
prompt_input "Network (wifi-fast | wifi-slow | 4g | 3g | flaky):" NETWORK false
prompt_input "Locale (en-US | pt-BR | ...):" LOCALE false
prompt_input "URL where bug occurs:" URL false

# Bug Description
echo ""
echo -e "${MAGENTA}━━━ Bug Description ━━━${NC}"
echo ""

prompt_input "Summary from the persona's perspective (what did the user try, see, expect?):" DESCRIPTION true
prompt_input "Charter (CH-NN if this surfaced via a charter, or 'off-script' / 'CFR pass' / 'journey execution'):" CHARTER false
prompt_input "Tour (if surfaced inside a tour, name it — else leave blank):" TOUR false

# Reproduction Steps
echo ""
echo -e "${MAGENTA}━━━ Steps to Reproduce (user-language) ━━━${NC}"
echo ""

echo "Enter reproduction steps (one per line, press Enter twice when done):"
REPRO_STEPS=""
STEP_NUM=1
while true; do
    read -r line
    if [ -z "$line" ]; then
        break
    fi
    REPRO_STEPS="${REPRO_STEPS}${STEP_NUM}. ${line}"$'\n'
    ((STEP_NUM++))
done

# Expected vs Actual
echo ""
prompt_input "Expected user-side behavior:" EXPECTED true
prompt_input "Observed user-side behavior:" ACTUAL true
prompt_input "Screenshot path (optional):" SCREENSHOT false

# Impact
echo ""
echo -e "${MAGENTA}━━━ Impact details ━━━${NC}"
echo ""

prompt_input "Frequency (always / sometimes / rare):" FREQUENCY false
prompt_input "Users affected (all of <persona> | subset | specific role):" USER_IMPACT false
prompt_input "Workaround available? (describe if yes):" WORKAROUND false
prompt_input "Trust cost (one sentence — what does this signal to the user?):" TRUST_COST false

# Related
echo ""
echo -e "${MAGENTA}━━━ Related Items ━━━${NC}"
echo ""

prompt_input "Related test case ID (e.g., TC-PERSONA-012):" TEST_CASE false
prompt_input "Figma design link (if UI bug):" FIGMA_LINK false
prompt_input "Related journeys (e.g., J-01, J-02):" RELATED_JOURNEYS false
prompt_input "Related charters (e.g., CH-01, CH-02):" RELATED_CHARTERS false

RELATED_ITEMS=""
if [ -n "$TEST_CASE" ]; then
    RELATED_ITEMS="${RELATED_ITEMS}- Test Case: ${TEST_CASE}"$'\n'
fi
if [ -n "$FIGMA_LINK" ]; then
    RELATED_ITEMS="${RELATED_ITEMS}- Figma Design: ${FIGMA_LINK}"$'\n'
fi
if [ -n "$RELATED_JOURNEYS" ]; then
    RELATED_ITEMS="${RELATED_ITEMS}- Related journeys: ${RELATED_JOURNEYS}"$'\n'
fi
if [ -n "$RELATED_CHARTERS" ]; then
    RELATED_ITEMS="${RELATED_ITEMS}- Related charters: ${RELATED_CHARTERS}"$'\n'
fi
if [ -z "$RELATED_ITEMS" ]; then
    RELATED_ITEMS="- None"
fi

FILENAME="${BUG_ID}.md"
OUTPUT_FILE="$OUTPUT_DIR/$FILENAME"

echo ""
echo -e "${BLUE}Generating bug report...${NC}"
echo ""

cat > "$OUTPUT_FILE" << EOF
# ${BUG_ID}: ${BUG_TITLE}

**Impact (user-side):** ${IMPACT}
**Severity:** ${SEVERITY}
**Priority:** ${PRIORITY}
**Type:** ${BUG_TYPE}
**Status:** pending
**Persona Affected:** ${PERSONA}
**Journey Step:** ${JOURNEY_STEP:-n/a}

## Environment

- **Build:** ${BUILD}
- **OS:** ${OS:-N/A}
- **Browser:** ${BROWSER:-N/A}
- **Viewport:** ${VIEWPORT:-N/A}
- **Network:** ${NETWORK:-N/A}
- **Locale:** ${LOCALE:-en-US}
- **URL:** ${URL:-N/A}

## Summary

${DESCRIPTION}

## Reproduction

Charter: ${CHARTER:-n/a}
Tour: ${TOUR:-n/a}

Steps:

${REPRO_STEPS}

Observed:

- ${ACTUAL}
${SCREENSHOT:+- Screenshot: ${SCREENSHOT}}

## Expected

${EXPECTED}

## Root cause

[Engineering fills this in during fix.]

## Fix

[Engineering fills this in.]

## Verification

- [ ] Narrow reproduction rerun
- [ ] Re-run of the affected journey
- [ ] CFR pass on the affected category (if applicable)

## Impact

- **Users Affected:** ${USER_IMPACT:-Unknown}
- **Frequency:** ${FREQUENCY:-Unknown}
- **Workaround:** ${WORKAROUND:-None}
- **Trust cost:** ${TRUST_COST:-(not stated)}

## Related

${RELATED_ITEMS}
EOF

echo -e "${GREEN}Bug report generated: ${BLUE}$OUTPUT_FILE${NC}" >&2
echo "$OUTPUT_FILE"
