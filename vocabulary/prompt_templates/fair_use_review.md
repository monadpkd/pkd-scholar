# Fair Use Review Prompt

Review the following draft output for fair use compliance.

Check each item:

1. **Quote length:** Are any quotations longer than 2-3 sentences? Flag them.
2. **Quote necessity:** For each quote, is the specific wording analytically necessary, or could a paraphrase work? Flag unnecessary quotes.
3. **Paraphrase quality:** Are paraphrases genuine restatements or cosmetic word-swaps? Flag bad paraphrases.
4. **Plot reproduction:** Does any section narrate a scene beat-by-beat in a way that substitutes for reading the original? Flag it.
5. **Substitution test:** Could a reader skip the original work after reading this output? If yes, flag the section.
6. **Citation completeness:** Does every claim and every quote have a work + page/chapter reference? Flag missing citations.
7. **Multiple quotes from same source:** Are there more than 2 extended quotes from any single work? Flag for consolidation.
8. **Structural reproduction:** Does the output reproduce the structure (lists, tables, argument sequence) of any source? Flag it.

Output format:
```json
{
  "entry_id": "",
  "overall_status": "passed / flagged / needs_revision",
  "issues": [
    {
      "type": "quote_too_long / unnecessary_quote / bad_paraphrase / plot_reproduction / missing_citation / over_quotation / structural_copy",
      "location": "section name or paragraph number",
      "description": "",
      "suggestion": ""
    }
  ],
  "quote_count": 0,
  "max_quote_length_words": 0,
  "paraphrase_ratio": 0.0
}
```
