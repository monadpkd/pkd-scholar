# Psychology Analysis Prompt

Analyze the following text for psychological content relevant to Philip K. Dick studies.

Answer these questions:

1. Is this passage using a psychological term literally, metaphorically, diagnostically, narratologically, or polemically?
2. Is the speaker Dick (in Exegesis/letters), a character, a narrator, or a critic?
3. Is the concept endorsed, dramatized, merely mentioned, questioned, or contradicted?

Classify the passage:
- source_mode: fiction / exegesis / letter / interview / criticism
- psych_mode: clinical / psychoanalytic / jungian / existential / neuropsychological / anti_psychiatric / mystical_psychological / popular_psychology / metaphorical
- claim_type: definition / symptom_description / causal_theory / treatment_model / allegorical_use / self_report / critique / comparison / unresolved
- confidence: high / medium / low

Identify:
- Which psychology topics from the controlled vocabulary are present
- Whether this is a direct engagement with psychological theory or an indirect/literary use
- Whether Dick is self-theorizing, dramatizing through character, or deploying psychology as narrative structure

Output format:
```json
{
  "work_id": "",
  "seg_id": "",
  "topics_detected": [],
  "source_mode": "",
  "psych_mode": "",
  "claim_type": "",
  "speaker_type": "",
  "stance": "",
  "schools_referenced": [],
  "persons_referenced": [],
  "confidence": "",
  "brief_analysis": "",
  "contradicts": []
}
```

Constraints:
- Do not diagnose Dick. Describe represented states and self-descriptions.
- Keep evidentiary lanes separate: what the fiction shows vs. what Dick theorizes vs. what critics argue.
- Paraphrase; quote only key phrases when analytically necessary.
- If the passage is ambiguous between psychological schools, note all plausible readings.
