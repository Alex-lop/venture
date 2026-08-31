# source: https://api.github.com/repos/guardrails-ai/guardrails/readme
# fetched: 2026-08-30


---

cR9QvYE)](https://discord.gg/U9RKkZSBgx)
[![Static Badge](https://img.shields.io/badge/Docs-blue?link=https%3A%2F%2Fwww.guardrailsai.com%2Fdocs)](https://guardrailsai.com/guardrails/docs)
[![Static Badge](https://img.shields.io/badge/Blog-blue?link=https%3A%2F%2Fwww.guardrailsai.com%2Fblog)](https://www.guardrailsai.com/blog)
[![Gurubase](https://img.shields.io/badge/Gurubase-Ask%20Guardrails%20Guru-006BFF)](https://gurubase.io/g/guardrails)

</div>

## News and Updates
- [July 6, 2026] Guardrails validators are moving to standard PyPI packages you install directly with pip, and Guardrails is discontinuing its hosted remote inferencing. See [How to Migrate](https://github.com/guardrails-ai/guardrails/issues/1560) for what to do. Planned cutoff: August 25, 2026.
- [Feb 12, 2025] We just launched Guardrails Index -- the first of its kind benchmark comparing the performance and latency of 24 guardrails across 6 most common categories! Check out the index at index.guardrailsai.com

## What is Guardrails?

Guardrails is a Python framework that helps build reliable AI applications by performing two key functions:
1. Guardrails runs Input/Output Guards in your application that detect, qua

---

e the presence of specific types of risks. To look at the full suite of risks, check out [Guardrails Hub](https://guardrailsai.com/hub/).
2. Guardrails help you generate structured data from LLMs.


<div align="center">
<img src="https://raw.githubusercontent.com/guardrails-ai/guardrails/main/docs/assets/withandwithoutguardrails.svg" alt="Guardrails in your application" width="1500px">
</div>


### Guardrails Hub

Guardrails Hub is a collection of pre-built measures of specific types of risks (called 'validators'). Multiple validators can be combined together into Input and Output Guards that intercept the inputs and outputs of LLMs. Visit [Guardrails Hub](https://guardrailsai.com/hub/) to see the full list of validators and their documentation.

<div align="center">
<img src="https://raw.githubusercontent.com/guardrails-ai/guardrails/main/docs/assets/guardrailshub.gif" alt="Guardrails Hub gif" width="600px">
</div>


## Installation

python
pip install guardrails-ai



## Getting Started


### Create Input and Output Guards for LLM Validation

1. Download and configure the Guardrails Hub CLI.

 bash
 pip install guardrails-ai
 guardrails configure
 
2. Install a guardrail from Guardrails Hub.

 bash
 pip install guardrails-ai-regex-match
 
3. Create a Guard from the installed guardrail.

 python
 from guardrails import Guard, OnFailAction
 from guardrailsai.regexmatch import RegexMatch

 guard = Guard().use(
 RegexMatch, regex="\(?\d{3}\)?-? \d{3}-? -?\d{4}", onfail=OnFailAction.EXCEPTION
 )

 guard.validate("123-456-7890") # Guardrail passes

 try:
 guard.validate("1234-789-0000") # Guardrail fails
 except Exception as e:
 print(e)
 
 Output:
 console
 Validation failed for field with errors: Result must match \(?\d{3}\)?-? \d{3}-? -?\d{4}
 
4. Run multiple guardrails within a Guard.
 First, install the necessary guardrails from Guardrails Hub.

 bash
 pip install guardrails-ai-competitor-check guardrails-ai-toxic-language
 

 Then, create a Guard from the installed guardrails.

 python
 from guardrails import Guard, OnFailAction
 from guardrailsai.compe
