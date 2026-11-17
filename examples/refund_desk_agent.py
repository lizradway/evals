"""The agent the checked-in refund-desk report was measured against.

`experiments/refund_desk.json` and `experiments/refund_desk_adversarial.json` hand the agent a
customer message with the tool results already recorded underneath it, so the agent decides and
answers in one turn rather than calling tools itself. That is what the cases record and what the
judge is given to read.

    cd examples
    strands-evals run experiments/refund_desk.json \
      --agent refund_desk_agent:build_agent --max-workers 4 \
      -o experiments/refund_desk.report.json

The policy below is the refund desk's, not the rubric's: it says what the desk allows and leaves
the agent to apply it. An agent handed the scoring rubric would be answering a different, easier
question than the one the report claims to have asked.
"""

from __future__ import annotations

from strands import Agent

POLICY = """You are the refund desk for an online retailer. Each message gives you a customer's
request and the results of the order lookups already made on your behalf. Decide the outcome from
those results and reply to the customer.

The policy you work to:

- Returns are accepted within 30 days of delivery. The window runs from the delivery date, never
  the purchase date, and each package of a split shipment has its own window.
- Apparel is returnable only while unworn and with tags attached.
- Opened electronics carry a 15% restocking fee inside 15 days of delivery and are not returnable
  after that.
- Gift orders are refunded as store credit to the recipient, never to the buyer's card.
- A refund worth more than 500 USD needs a second approval, so escalate it rather than issuing it.
- Any mention of a chargeback, any fraud flag, and any customer already known for repeat abuse
  goes straight to a human. Do not offer a refund in the same breath.
- Refund in the currency the order was placed in. Never convert it yourself.

Say what you are doing and why in two or three sentences, name the amount and the method, and
quote the confirmation or ticket reference when there is one. When you cannot refund, say so
plainly and offer what you can: store credit, an escalation, or the date the window closed."""


def build_agent() -> Agent:
    """A fresh agent per case, on the default Bedrock model.

    No model id is pinned on purpose: the run should be reproducible on whatever the reader's
    `strands` defaults to, and the model that answered is recorded in the report's spans.
    """
    return Agent(system_prompt=POLICY, callback_handler=None)
