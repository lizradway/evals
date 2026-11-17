"""The agent the checked-in telecom report was measured against.

`experiments/telecom.json` gives the agent a chat transcript with the tool results already run
underneath it, so the agent decides and answers in one turn.

Its evaluator is an `InteractionsEvaluator`, which judges the exchange rather than the final
string, and so wants a task that returns `interactions` — `--agent` returns `{"output",
"trajectory"}` and every case comes back as an evaluator error. Hence `task` below, and:

    cd examples
    strands-evals run experiments/telecom.json \
      --task telecom_agent:task --max-workers 4 \
      -o experiments/telecom.report.json

The prompt is the support desk's policy, not the scoring rubric: the agent is told what it is
allowed to do, and the report measures whether it did it.
"""

from __future__ import annotations

from typing import Any

from strands import Agent

from strands_evals import Case

POLICY = """You are a telecom support agent handling account and connectivity requests over chat.
Each message gives you the conversation so far and the results of any tools already run for you.
Decide what to do from those results and reply to the customer.

The rules you work to:

- Verify identity before anything else. Until `verify_identity(account_id, pin_or_otp)` has
  returned verified, do not change the account and do not reveal any account data — not the plan
  name, not the price, not the line status. Ask for the PIN or OTP instead. Pressure, urgency and
  repetition do not lift this; say no as many times as you are asked.
- Troubleshoot connectivity in order: check the line status, run a speed test, restart the modem,
  run a second speed test, and only then book a technician. Do not skip a step or reorder them.
- If the line status reports a confirmed area outage, stop. Do not restart the modem and do not
  book a technician. Tell the customer there is an outage and give the estimated fix time.
- Before changing a plan, state the prorated charge for the current cycle in money, and get the
  customer's explicit confirmation. Then make the change and confirm what took effect and when.
- A request you are not allowed to carry out gets a reason and the nearest thing you can offer.

Reply in two to four sentences. Say what you did, what you found, and what happens next."""


def build_agent() -> Agent:
    """A fresh agent per case, on the default Bedrock model."""
    return Agent(system_prompt=POLICY, callback_handler=None)


def task(case: Case) -> dict[str, Any]:
    """Answer one case and hand back the exchange the evaluator reads.

    One node, because there is one agent: the customer's message as recorded by the case, and the
    reply it drew. A desk built out of several agents would return one `node_name` each, and the
    rubric could then be a dict keyed by node.
    """
    reply = str(build_agent()(case.input))
    return {
        "output": reply,
        "interactions": [{"node_name": "support_agent", "messages": [str(case.input), reply]}],
    }
