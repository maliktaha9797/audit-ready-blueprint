<!-- What it is: a prompt that asks Claude to generate a setup from your answered questionnaire. -->
<!-- When to create it: after you have answered the questionnaire. Copy the prompt block, fill in the two slots, and paste it into a session. -->
<!-- Where it goes: it is not a project file. Run it in a new, empty directory so that nothing else is read by mistake. -->

# Generation prompt

Replace the two slots, then paste the block into Claude Code.

```
I need to create a Claude Code setup for <<FILL: purpose>>.

Here are my answers to the setup questionnaire:

<<FILL: paste your answers>>

Please create the following, using the templates in the Claude Code Setup Blueprint
and the file formats in docs/conventions.md:

1. CLAUDE.md: project rules, with a governing sentence, an authority order, and a
   DO NOT list in which each line ends with the id of the invariant that checks it.
2. Workflow files in .claude/workflow-docs/: one per repeatable process.
3. Agent files in .claude/agents/: one per agent, with name and description in the
   frontmatter and only the tools that agent needs. Any agent that audits other work
   has no edit or write tool.
4. Skill files in .claude/skills/<name>/SKILL.md: one folder per skill needed.
5. Command files in .claude/skills/<command>/SKILL.md with disable-model-invocation: true.
6. Context files in .claude/context/: summary.md, decisions.md, and any others the
   answers call for.
7. If the answers describe work that must be auditable: an invariants skill, a
   scenario register, a phase log template, and settings.json with deny rules and hooks.

Do not use real personal data or real names of organisations anywhere in the output.
Label every verification you report as executed, read or not-verifiable.

For each file, explain:
- what it does
- how it connects to the other files
- when it gets used

After creating the files, give me the folder structure and a checklist for setup.
Stop and ask if a decision is mine to make.
```
