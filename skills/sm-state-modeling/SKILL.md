---
name: sm-state-modeling
description: Model one area from the State Map into docs/state/<area>-STATE-MODEL.md, interviewing the forks along the way.
disable-model-invocation: true
---

# Area model

One area per invocation. This pass interviews, so it needs a human in the session, and it needs the State Map already agreed — the map settles the boundaries this pass works inside.

Read [`reference/MODELLING.md`](../../reference/MODELLING.md) first: the drop boundary, the forks worth interviewing, the decisions to derive with their reasons, and the markers. It is the method; this file is the sequence.

Ask the human which area, if they have not said. One area, never several.

## 1. Load the area

From the State Map, take this area's responsibility sentence, its `uses` lines, its facts and their owners, its outside boundaries, and its two order lines. Confirm the `model after` areas are already modelled; if one is not, say so and stop rather than guessing at its shape.

Then read the code behind those facts, so the proposal you bring to the interview comes from what exists. Arrive with answers, not questions.

**Done when** you can state this area's facts and which of the three owners each carries, what it needs from each area it uses, and what the code does with each fact today.

## 2. Draw the Containers

Group this area's facts by **what dies together**, which is the only thing Container granularity means. Unclear means coarse.

For each Container, write the drop boundary as a sentence: what event drops it, and what is gone when it does. A Container whose drop sentence you cannot write is not a Container yet — it is two Containers, or it belongs with another one.

A boundary the map drew that you would draw differently gets `[BOUNDARY]` and proceeds with the map's answer.

**Done when** every fact sits in exactly one Container and every Container has a drop sentence.

## 3. Name the Values

Every fact becomes a Value with an Address in one Container. Per Value, settle and record:

- **Atomic or Keyed**, derived from one-per-application versus one-per-id. When Keyed, say what the key is and where an entry comes from and goes.
- **Its starting Value**, which is what a dropped Container comes back as.
- **Whether anything writes it.** A fact nothing writes is not a Value at all; it goes to step 4.

Sourced facts stay Values here, held by the Environment as any other. The strategy that fills them is step 7.

**Done when** every stored fact has an Address, a shape, and a starting Value, with the reason for the shape written beside it.

## 4. Name the Computeds

Anything nothing writes. Per Computed, record what it derives and, exactly, **which Values it reads** — that read set is its invalidation, so a read that no branch uses is a defect worth catching here rather than in review.

Say whether it is Atomic or Keyed on the same one-per-application versus one-per-id test.

**Done when** every unwritten fact is a Computed with its read set listed, and no Computed reads a Value it does not use.

## 5. Name the Operations

Every change this area can undergo, as a named Operation. The name says what happened in the domain, not which Value it assigns.

Per Operation record what it writes, and derive **sync or async** from whether it has to await. An async Operation lands its result by performing a sync one; say which.

Include the changes that are easy to forget: entering and leaving, dropping the Container, and whatever the outside can trigger.

**Done when** every Value from step 3 has a named writer. For an owned fact the writer is an Operation here. For a sourced fact it is the strategy's inbound, named in step 7, and no Operation is owed — the outside changed, the application did not. A Value with neither is a Computed you missed or a fact another area owns; resolve it now, because it will not survive implementation.

## 6. Name the Services

Only where non-view logic must react to a Value. Per Service, record the Values it reads and the Operations it performs in response.

An area with no Service is a normal outcome. Reach for one only when something has to react with no view on screen; a reaction that only matters while a view is visible is a Watch.

**Done when** each Service names its inputs and the Operations it performs, and each one has a reason it cannot be a Watch.

## 7. Settle the outside

For each crossing the map recorded, name the AsyncStrategy that owns it and the Policy that says how each Address is backed. Say what happens on each of the three kicks — first read, write out, and drop — even where the answer is nothing.

A strategy that does not exist yet is a Satellite decision, which is a fork: ask it, do not assume it. Storage or network code written into this area instead is the failure this step exists to prevent.

**Only a fact sourced from outside belongs here.** A fact owned elsewhere in the app is read from that area's Values, and it needs no strategy, no Policy, and no entry in this section — the map's `uses` line already covers it. Where that fact is still a `@Published` on a legacy singleton, it is a migration note for `sm-refactor`, not a crossing. Reaching for a strategy is the pull to resist, because it looks like the only tool for a fact this area does not own.

**Done when** every crossing names its strategy and Policy, every strategy is either an existing Satellite or a recorded fork, and nothing this area merely uses has been given a strategy.

## 8. Close with a build order

Order the pieces so each step compiles and tests green on its own: Containers and Values, then Computeds, then Operations, then Services, then the strategy. Where this area's `build after` names another area, say what it needs from it.

**Done when** the order exists and each step names what proves it works.

## 9. Write the model

Write `docs/state/<area>-STATE-MODEL.md`, sections in the order of the steps above: Containers with drop sentences, Values, Computeds, Operations, Services, the outside, then the build order. Close with an Open questions section collecting every `[?]`, `[BOUNDARY]`, and `[SM-GAP]` in the document, so the redline is one scan.

**Done when** the file exists, every section is present, and every marker in the body also appears under Open questions.

## 10. Hand back

Report the Containers with their drop sentences, the counts of Values, Computeds, Operations, and Services, and every open question. Name any `[SM-GAP]` explicitly and ask before filing a ticket for it.

Then tell the human to run **`sm-implement`** on this area, and that other areas with an empty `model after` can be modelled in parallel.
