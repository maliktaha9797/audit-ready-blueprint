# Reason codes

A short taxonomy for classifying why the system and a human reviewer disagreed. When a reviewer overrides the system, or the system flags something the reviewer judges fine, record one code. The codes show where the setup needs work.

Codes have the form `RSN-nn`. They are appended and never renumbered or reused, because past records cite them. (Rule-change proposals use a different prefix, `RC-nnn`, defined in `rule-changes.md`.)

| Code | Name | Meaning | Usual follow-up |
|---|---|---|---|
| RSN-01 | Extraction error | The system read a value wrongly from a document or message | Add a scenario and a fixture for that input |
| RSN-02 | Rule ambiguity | The rule gave an answer, but its wording allows more than one reading | Clarify the policy through `/policy-change` |
| RSN-03 | Judgment difference | The evidence was ambiguous and the reviewer decided differently from the draft | Record it. No change unless a pattern emerges |
| RSN-04 | Fixture defect | The test data did not represent the real situation | Fix the fixture and re-run |
| RSN-05 | Missing scenario | The case was not in the register | Add it through `/new-scenario` |

Add new codes below this line, with the next number.
