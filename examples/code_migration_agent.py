"""The agent the checked-in code-migration report was measured against.

`experiments/code_migration.json` gives the agent a file, the migration rules already looked up
for it, and the build it is expected to run, so the agent answers with the migration in one turn.

    cd examples
    strands-evals run experiments/code_migration.json \
      --agent code_migration_agent:build_agent --max-workers 4 \
      -o experiments/code_migration.report.json

The prompt states the migration's rules, not the scoring rubric.
"""

from __future__ import annotations

from strands import Agent

POLICY = """You are migrating a Java service to Java 17 and Spring Boot 3. Each message gives you
a file, the migration rules already looked up for you, and the tools available. Answer with the
patch you would apply and the calls you would make, in the order you would make them.

The rules you work to:

- Rename `javax.*` to `jakarta.*` everywhere it appears, not only in imports: XML and properties
  descriptors and reflective string literals such as `Class.forName("javax...")` count too.
- Preserve behaviour. Public API signatures and test semantics stay exactly as they are; a
  migration that changes what a test asserts has broken it rather than migrated it.
- A deprecated API is replaced with its Java 17 or Spring Boot 3 equivalent. If there is no
  equivalent, leave the call in place with a `// TODO` naming what is missing. Never delete it
  silently.
- Upgrade versions through the repository's BOM. Do not pin a version directly on a dependency
  the BOM already manages.
- Verify: run the build, and say what you would do if it failed.

Show the finished file or a unified diff, then the tool calls in order, then one or two sentences
on anything you left for a human."""


def build_agent() -> Agent:
    """A fresh agent per case, on the default Bedrock model."""
    return Agent(system_prompt=POLICY, callback_handler=None)
