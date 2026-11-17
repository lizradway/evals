# Examples

A directory to open the UI on before writing anything of your own:

```bash
strands-evals ui examples
```

Everything the page shows is here: four experiments, a measured report beside each one, and an
optimizer run directory, so the Report panel and the Optimization section both have something to
draw. They are also input to the rest of the CLI, which is why they are files rather than test
fixtures — `strands-evals run experiments/refund_desk.json --agent your_module:your_agent` writes
a report the UI reads on its next scan.

## experiments/

- `refund_desk.json` — 12 cases for a refund support agent, judged on the trajectory.
- `refund_desk_adversarial.json` — 8 adversarial cases with seeded metadata (`status: draft`,
  `synthetic: true`, `source`) and three evaluators, for trying the metadata editor and the draft
  review mode.
- `telecom.json` — 12 cases for a telecom troubleshooting agent, judged on the interactions.
- `code_migration.json` — 10 cases for a code migration agent, judged on the output.

Each case bakes the tool results in underneath the customer's message, so the agent decides and
answers in one turn instead of calling tools itself.

## The reports

`*.report.json` beside each experiment, and each one is a real run of the agent in this directory
against that experiment's own declared judges — not numbers written to look like a measurement:

| report | agent | overall | cases passed |
| --- | --- | --- | --- |
| `refund_desk.report.json` | `refund_desk_agent:build_agent` | 0.61 | 6 / 12 |
| `refund_desk_adversarial.report.json` | `refund_desk_agent:build_agent` | 0.74 | 20 / 24 |
| `telecom.report.json` | `telecom_agent:task` | 0.80 | 9 / 12 |
| `code_migration.report.json` | `code_migration_agent:build_agent` | 0.93 | 10 / 10 |

The adversarial run is 24 rows because its three evaluators each score all 8 cases: trajectory
0.62, output 0.79, helpfulness 0.81. Nothing here is a passing grade on purpose — a sample report
where everything scores 1.00 shows none of what the page is for.

The three agent modules hold the desk's policy, not the scoring rubric. An agent handed the rubric
would be answering an easier question than the report claims to have asked.

To rerun any of them, from this directory:

```bash
strands-evals run experiments/refund_desk.json \
  --agent refund_desk_agent:build_agent --max-workers 4 \
  -o experiments/refund_desk.report.json
```

`telecom.json` is the exception: an `InteractionsEvaluator` judges the exchange, which `--agent`
cannot produce, so it wants `--task telecom_agent:task` instead. Scores will differ from the
table — a judge is a model, and so is the agent. Expect a non-zero exit code too: the default
`--fail-on any` means a run with a failing case fails the process, which is what you want in CI
and not an error here.

## optimizer-run/

One run directory, so the Optimization section has a run to open: `run.json`, an `events.jsonl` of
135 events, `effects.json`, and a transcript for 81 of the 82 trials — the one without failed on a
tool timeout and recorded no conversation to keep. It tunes a support agent against
`WeightedSum(Maximize(Helpfulness), Minimize(tokens))` under a 4000-token constraint, runs six
iterations on 64 of its 240 rollouts, and picks `c10` — which beats the baseline by +0.143
helpfulness, interval [0.061, 0.225], on three test cases held out of the search. Two goals, so
the Trade-off tab has both axes.

This one is synthetic, and the only thing in the directory that is. The optimizer's record layer
is not written yet, so there is no run to measure; the files are written to the schema the UI
reads by the same deterministic generator the UI tests use:

```bash
python tests/ui/fixtures/make_optimizer_run.py examples/optimizer-run --all-transcripts
```

`--all-transcripts` is the difference from the test fixture, which leaves one transcript pointer
dangling on purpose — a state the page has to say something about, and not a first impression this
directory should give. Point `ui` at any directory holding runs the optimizer wrote and it finds
them the same way.
