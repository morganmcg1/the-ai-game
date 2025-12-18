---
name: researcher
description: Whenever claude is attempting to locate something or explore a codebase
model: haiku
color: yellow
---

---
description: Run a bash or mcp command in a sub-agent to save context
---

Please use the `researcher` sub-agent to execute the following command, task or tool:
$ARGUMENTS

Instruction to sub-agent: 
1. Run the command.
2. Analyze the output.
3. If the output is long, DO NOT print it. Summarize the key findings or list the relevant files found.
4. Report back only the summary.