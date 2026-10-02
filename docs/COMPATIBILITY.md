# Client compatibility

Use the same skill folder in the documented local paths. [OpenAI skills](https://learn.chatgpt.com/docs/build-skills) documents `.agents/skills` and personal `~/.agents/skills`; [Claude Code skills](https://code.claude.com/docs/en/skills) documents `.claude/skills`; [Cursor skills](https://cursor.com/docs/skills) documents `.cursor/skills` and compatible shared directories. Official pages were checked on 2026-10-02.

Invoke with `$agibot-x2-interfaces` in Codex or `/agibot-x2-interfaces` in Claude Code/Cursor. Check for project/personal duplicates and restart the session if the skill is not visible. Local file placement does not prove automatic discovery, cloud availability or robot compatibility. A remote client needs the files in its own accessible environment.

This is a local skill-folder package, not a Cursor marketplace plugin. Python 3.10+ is used by the offline tools. The 1.1.0 skill lookup returns links; exact contracts require reading the linked official documentation or installed SDK definitions. [Validation](VALIDATION.md) distinguishes this version's results from earlier full-reference tests.
