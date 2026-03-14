# Dictionary Entry Structure

## Minimum Schema (per Ted's spec)

Every psychology or AI topic entry must include:

| Field | Required | Description |
|-------|----------|-------------|
| Entry ID | Yes | `ENTRY_{slug}` |
| Canonical Topic | Yes | Display name |
| Aliases / variant labels | Yes | All variant forms |
| Topic Family | Yes | psychology, ai_automation, capitalism, metaphysics, epistemology |
| Definition | Yes | Scholarly definition (plain English, 1-2 sentences) |
| PKD Relevance | Yes | Why this matters for Dick studies (2-3 sentences) |
| Primary Evidence (fiction) | Yes | Lane A: novels, stories, essays |
| Exegesis Evidence | If applicable | Lane A: Exegesis passages with folder/date |
| Secondary Scholarship | Yes | Lane C: critics, biographers, scholars |
| Dick's Apparent Uses | Yes | How Dick deploys this concept (dramatizes, theorizes, self-applies) |
| Competing Interpretations | If applicable | Where scholars disagree |
| Chronology | If applicable | How Dick's engagement shifted over time |
| Related Works | Yes | Works where this topic appears |
| Related Persons | If applicable | Thinkers, characters, biographers |
| Related Schools / Thinkers | If applicable | Intellectual traditions |
| Key Quotations | If applicable | Brief, cited, analytically necessary only |
| Editorial Notes | Yes | Confidence level, known gaps, open questions |
| Confidence Rating | Yes | high / medium / low |
| Open Questions | If applicable | What we don't know, what would strengthen the entry |

## Prose Formulas

### Opening Pattern
Open with a compact scholarly definition, then immediately state PKD relevance.
Do NOT start with biography, fan-lore, or "Philip K. Dick was..."

### Evidentiary Layer Separation
Every entry must keep these lanes visibly distinct in the prose:

```
"In the fiction, [concept] appears as..."
"In the Exegesis, Dick [theorizes/self-applies/questions]..."
"In biographical criticism, [scholar] argues..."
"In later scholarship, [concept] has been read as..."
```

### Contradiction Requirement
Every entry MUST include contradictions if they exist.
Dick regularly cycles through incompatible explanations.
If one Exegesis passage treats a phenomenon as divine anamnesis and another as pathological disintegration, the entry preserves that tension.

### Do Not Diagnose
Describe represented mental states, self-descriptions, biographical events, and the interpretive debate.
Do NOT flatten that into a clinical verdict.

### See Also Links (three directions)
1. Neighboring psychological/thematic concepts
2. Major related works
3. Relevant scholars

## Machine Role Entry (AI Study)

For the AI/robot study, entries should additionally include:

| Field | Description |
|-------|-------------|
| Machine Role | economic_gatekeeper, diagnostic_authority, etc. |
| Human Response | compliance, circumvention, sabotage, etc. |
| System Type | What kind of system structures the society |
| Turnstile Motif | Whether the 5-step narrative structure applies |
| Political Economy | How the technology reflects economic/power relations |
