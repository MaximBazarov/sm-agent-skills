---
name: sm-refactor
description: Move a Combine codebase that passes shared instances around onto Structured State Management, staying green at every step.
disable-model-invocation: true
---

# Refactor Combine into Structured State Management

The starting codebase has observable classes holding `@Published` properties, single instances of them passed down as dependencies, and views observing whichever instance they were handed. The destination is one Environment, Containers, and Operations.

Two things make this work: the model is **redrawn** rather than translated, and the bridge lets both worlds hold the same fact so the app is green between every step.

Read [`reference/MODELLING.md`](../../reference/MODELLING.md) for the method and the markers, and [`reference/API-SURFACE.md`](../../reference/API-SURFACE.md) for signatures.

## 1. Survey the graph

Map what exists before proposing anything. Per observable class: its published properties, which plain properties sit beside them, who constructs it, who holds it, which views observe it, and who writes each property.

Two findings matter more than the rest, so look for them by name:

- **A fact with more than one writer**, which is the coupling the destination architecture removes.
- **A class two unrelated features both hold**, which is a boundary drawn by what needed injecting rather than by what the state is.

**Done when** every observable class has that entry and every published property has its writers listed.

## 2. Redraw the model, do not translate it

**The existing class boundaries are not the model.** They were drawn by what had to be injected where, so they record the shape of the old dependency graph, not the shape of the state. Carrying them over reproduces the coupling in a system whose whole point was to remove it. Expect facts to move between classes, and expect one class to become two Containers or two classes to become one.

Model with **`sm-state-map`**, then **`sm-state-modeling`** per area, and tell them the model is a redraw: group facts by what dies together, not by which class holds them today. Those two skills are typed by a human, so hand back here and stop.

Return to step 3 with the models in hand. If they already exist, start there.

**Done when** every fact from step 1 appears in an area model, and every fact whose Container differs from its current class is noted as a move.

## 3. Order the migration

The bridge is `@SMPublished`: it makes a legacy observable class a Container, so the Environment owns the fact while the old call sites keep reading and writing it unchanged. That is what buys a green app between steps.

Per fact, four moves in this order, each one shippable on its own:

1. **Bridge.** The class becomes a Container and the property swaps `@Published` for `@SMPublished`. The Environment now owns the fact; the old call sites still work. Keep the fact at its current address for now, even where the model says it moves — the move is step 4.
2. **Move the readers.** View by view, replace observing the instance with a Watch. Both paths read the same fact, so each view converts independently.
3. **Move the writers.** Replace each direct assignment with performing a named Operation from the model. Once a fact's writers are all Operations, its change path is one-way.
4. **Relocate and drop.** With no legacy call site left for that fact, move the Address to the Container the model gave it, and drop the observable conformance and the instance threading from the classes that no longer need them. Every call site is library-side by now, so this step is a mechanical rename.

Sequence the facts so that the ones with the fewest readers go first; they prove the loop cheaply. Where a class holds facts heading for different Containers, bridge the whole class at once and let each fact relocate on its own schedule.

**Done when** every fact has its four moves ordered, and each move names what proves the app still works.

## 4. One rule that will bite

**A legacy call site always reads and writes the shared Environment.** A property access on a bridged class uses the shared Environment whatever Environment surrounds it, and overriding that is unsupported. A Watch, a Computed, an Operation, and a Service all use the Environment they were given.

So while any fact still has a legacy call site:

- **Let the app run on the shared Environment.** Injecting a different one splits the fact in two — the old call sites write one Environment and the Watches read another, and the symptom is a view that will not update.
- **Own the Environment only after the last legacy call site for that Container is gone.** That is part of step 3's fourth move, not a separate decision.
- **Tests split by path.** A test that goes through a legacy call site uses the shared Environment and resets it. A test that Watches or performs an Operation gets a fresh Environment. Mixing the two in one test is the same split bug wearing a test's clothes.

Write this into the migration document, because it is the failure that costs an afternoon.

## 5. Write it down and hand back

Write `docs/state/MIGRATION.md`: the survey from step 1, the moves from step 2, the ordered per-fact steps from step 3, and the shared-Environment rule.

Then report the order and tell the human to run **`sm-implement`** for the modelled areas, and to work the migration steps in the order given. Name any `[SM-GAP]` and ask before filing a ticket.
