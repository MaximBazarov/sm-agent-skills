---
name: sm-implement
description: Build one area from its state model, test-first, and commit.
disable-model-invocation: true
---

# Implement an area

Build one area from `docs/state/<area>-STATE-MODEL.md`. The model is the spec: it already settled the Containers, the shapes, and the reasons, so this pass writes code and does not re-decide.

Read [`reference/MODELLING.md`](../../reference/MODELLING.md) for the markers and the library-gap rule, and [`reference/API-SURFACE.md`](../../reference/API-SURFACE.md) for signatures — check its anchor against the project's `Package.resolved` before trusting one.

## 1. Take the model as the spec

Ask which area, if the human has not said. Read its model, and check the Open questions section.

**An unresolved `[?]` or `[BOUNDARY]` stops this pass.** Those marks exist because the answer needed a human, and building on a guess buries it in code where the next reader cannot tell it was ever a question. Report which ones are open and ask.

A `[SM-GAP]` does not stop the pass: the model already says which shape to build instead. Carry the marker into a comment at the site so it stays greppable in the code.

**Done when** the model is read, its build order is in hand, and no `[?]` or `[BOUNDARY]` is unresolved.

## 2. Build in the model's order

Follow the model's build order, one step at a time. Each step ends compiling and green before the next begins, which is what the order was written for.

Use **`sm-tdd`** for each step: fresh Environment, seed, perform, read, assert. Every Operation and every Computed the model names earns a test, because those are the two things the model asserts and the only two the Environment seam can prove.

When the code wants a shape the model does not have, the model is what changes: edit it, note what moved and why, then build. A silent divergence turns the model into fiction and the next area pass inherits the fiction.

**Done when** every Container, Value, Computed, Operation, and Service in the model exists, and every Operation and Computed has a test.

## 3. Check the whole thing

Typecheck and run the full suite, not just the files you touched. Then run **`sm-code-review`** over the diff and act on what it finds.

**Done when** the suite is green and every code-review finding is either fixed or recorded with a reason it stands.

## 4. Commit

Commit to the current branch. One commit per build step is fine; one for the area is fine. Say in the message which area was built.

Report what was built, which tests cover it, anything that moved in the model and why, and any `[SM-GAP]` you carried into the code. Ask before filing a ticket for a gap.
