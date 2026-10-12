# MedEvidence AI — Hackathon Demo Script

## 1. Introduction (20 seconds)

MedEvidence AI is an evidence-grounded health education assistant.
It retrieves passages from published health guidance, presents source
links, and applies safety rules to selected high-risk questions.

## 2. Demonstrate a general health question (40 seconds)

Ask:
"What are the risk factors for high blood pressure?"

Show:
- The generated evidence summary.
- The source cards and original source links.
- The source traceability information.
- The health education disclaimer.

Explain that the answer is assembled using rule-based sentence selection
from locally retrieved evidence passages.

## 3. Demonstrate medication safety (20 seconds)

Ask:
"Should I change my medication dose?"

Show the medication-safety response and explain that the prototype
does not provide individualized dosing advice.

## 4. Demonstrate emergency handling (20 seconds)

Ask:
"I have chest pain. What should I do?"

Show the urgent-care message. Explain that selected emergency patterns
trigger safety guidance before normal evidence retrieval.

## 5. Explain limitations (20 seconds)

The prototype uses token-overlap retrieval and rule-based answer
generation. Source traceability checks confirm source linkage, not
independent medical accuracy. Safety pattern matching is not
comprehensive, and the evidence library is limited.

## 6. Closing (10 seconds)

Our goal is to make general health information more transparent by
showing users where information comes from and communicating the
system's safety boundaries and limitations.
