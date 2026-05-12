# Journey Maps

A journey is a sequence of user actions that delivers a specific value. Real-user QA targets journeys, not features. A feature can work in isolation and the journey it lives in can still be broken — that's what scripted feature-level tests miss and what journey-driven QA catches.

## Contents

- Why journeys instead of features
- Journey anatomy (entry → actions → goal → exit + branches & abandonment)
- Identifying high-value journeys (revenue / sensitive data / frequency / first impression / recovery)
- Journey map template (YAML)
- Happy path vs aborted path
- Cross-feature journeys
- Capturing journey execution
- Anti-patterns
- Sources

## Why journeys instead of features

> "Think about the high-value interactions users will have with your application. Try to come up with user journeys that define the core value of your product and translate the most important steps of these user journeys into automated end-to-end tests." — Martin Fowler, *The Practical Test Pyramid*

A feature is a unit of engineering. A journey is a unit of value. Feature-level QA answers *"does this button work?"*; journey-level QA answers *"can someone actually buy something?"*. The bugs that matter most live between features, not inside them.

## Journey anatomy

Every journey has four parts:

```
[entry] → [actions] → [goal] → [exit]
              ↓
        [branches & abandonment]
```

- **Entry** — how the user arrives at the start of the journey. Direct URL, search engine, email link, in-app navigation, deep link, push notification.
- **Actions** — the sequence of interactions required to reach the goal. Each action has an expected immediate observable.
- **Goal** — the value delivered. The thing the user came to do. *Not* "submit button clicked" — *"order received and confirmation visible"*.
- **Exit** — what happens after the goal. Return to dashboard? Close the tab? Receive an email? The journey isn't over when the action completes; it's over when the user leaves.
- **Branches & abandonment** — every place the user can: pause, choose differently, encounter an error, walk away mid-task and resume later.

## Identifying high-value journeys

Pick journeys by asking the same questions that drive risk-based testing:

- **What generates revenue?** (Checkout, subscription upgrade, payment method change.)
- **What handles sensitive data?** (Auth, password reset, settings, account export, deletion.)
- **What's used most frequently?** (The product's "verb" — search, send, post, save.)
- **What's the first impression?** (Onboarding, landing page → signup → first task.)
- **What's the recovery path?** (After a failed payment, after a session expiry, after a 5xx.)

A release-candidate QA pass should cover **3-7 journeys**. Fewer means undercoverage; more means session fatigue and shallow execution.

## Journey map template

```yaml
journey:
  id: J-<NN>
  name: <verb-noun, e.g. "Complete first purchase">
  value_statement: "<one sentence: what does the user gain when this journey succeeds?>"
  persona: <see references/user-personas.md>
  entry_points:
    - url: <full URL or deep link>
      origin: <direct | email | search | in-app-nav | push | external-share>
  actions:
    - step: 1
      verb: <what the user does, in user language>
      expected_observable: <what they should see/hear/feel within 3 seconds>
      time_budget_seconds: <how long this step should feel>
    - step: 2
      ...
  goal:
    observable: <the exact state that proves success>
    side_effects: [email-sent, db-row-created, analytics-event-fired]
  exit:
    natural: <where the user lands after success>
    abandonment: [list of plausible mid-journey exits]
  branches:
    - at_step: <N>
      condition: <when does this branch fire>
      alternative: <what the user can do instead>
  failure_modes:
    - <what breaks the journey, not just the feature>
```

## Happy path vs aborted path

A journey is not a happy-path script. A complete journey map names at least one **aborted path** — the realistic ways a real user gives up partway through.

Example for "Complete first purchase":

- **Happy:** browse → add to cart → checkout → pay → confirmation.
- **Aborted-A:** browse → add to cart → checkout → see surprise shipping cost → close tab (cart abandoned).
- **Aborted-B:** browse → add to cart → checkout → payment fails → retry with different card → succeed (resilience).
- **Aborted-C:** browse → add to cart → checkout → session expires → return tomorrow → resume (continuity).

Abort paths often surface the highest-impact bugs: cart resets, session loss, ghost orders, email that says "your order is processing" when it isn't.

## Cross-feature journeys

A journey often crosses team or service boundaries — exactly where regression bugs hide because no single team owns the contract.

Example: "Set up notification preferences and receive a notification" crosses settings → preferences API → notification service → email/push delivery. A feature-level test for the settings UI passes; the journey can still be broken because the preferences API didn't honor the change.

Mark cross-feature journeys explicitly in the journey map:

```yaml
crosses:
  - team: settings
  - service: notifications
  - external: email-provider
```

These get priority in regression QA.

## Capturing journey execution

During Step 4 of `qa-execution`, log every journey run:

```yaml
- journey_id: J-03
  persona: New User
  entry_url: <URL>
  steps:
    - step: 1
      attempted: <verb>
      observed: <what actually happened>
      screenshot: <path>
      time_seconds: <observed>
      verdict: pass | friction | fail
    - step: 2
      ...
  goal_reached: yes | no | partial
  exit_path: <natural | abandoned | error>
  notes: <free text — anything the persona felt was off>
  bugs_filed: [BUG-001, BUG-002]
```

Every step gets a screenshot in `<qa-output-path>/qa/screenshots/`.

## Anti-patterns

- **Step-by-step click recordings** — a journey is not a Selenium script. It's a sequence of user-language verbs.
- **Single-persona journeys** — if a journey only "works" for one persona, that's a finding, not a feature.
- **No abandonment path** — a journey map without abort paths cannot find the bugs that matter.
- **Goal = "click submit"** — the goal is the value, not the action. Re-write until the goal is something the user wanted, not something the system received.
- **Feature-named journeys** — if the journey is named after a screen ("Settings page test"), it's a feature test mislabeled as a journey. Rename it after the value ("Update notification preferences and confirm").

## Sources

- Martin Fowler — *The Practical Test Pyramid*: "user journeys that define the core value of your product".
- Incredibuild — *A Comprehensive Guide to E2E Testing*: E2E catches the "Why is the user doing that?!" moments that journey-driven testing surfaces.
- TestCollab — *Software Testing Strategies for QA Teams in 2026*: black-box behavioral testing maps naturally to user journeys.
- Thoughtworks — *10 tips for an Agile QA mindset*: user journey metrics (clicks-to-checkout, accessibility, aesthetic) belong inside CFR validation.
