---
name: sm-state-map
description: Map an application's whole state into docs/state/STATE-MAP.md before modelling any of it.
disable-model-invocation: true
---

# State Map

One pass over the whole application to answer three questions: what areas of state exist, who owns each fact, and where the outside world touches them. Nothing here decides a Container or an Operation — that is the area model's job, and doing it now means doing it with the boundaries still unsettled.

Read [`reference/MODELLING.md`](../../reference/MODELLING.md) first. It carries the three levels, the drop boundary, which decisions to interview and which to derive, and the markers this document uses.

## 1. Inventory every fact

A **fact** is one thing the application knows. Find all of them, from the code, before grouping anything.

Look in every place a fact hides, and name the place in your notes so the inventory is auditable:

- View-local storage: the `@State` and `@StateObject` properties, and every observed or environment object a view holds.
- Anything long-lived: singletons, shared instances, managers, controllers, view models, coordinators, caches.
- Anything already in an Environment, if the project has begun adopting the library.
- Anything outside the process: user defaults, the keychain, files, a database, a server, system permissions and settings, the clock.
- Anything derived: values recomputed in a `body`, in a getter, or cached in a property alongside the inputs it was computed from.

For each fact, record where it lives today and who writes it. A fact with two writers is the finding this step exists to surface; note it rather than resolving it.

**Done when** every fact you can find has a line, and every file that declares or mutates state has been opened. A fact you are unsure counts is listed with `[?]`, not dropped.

## 2. Group facts into areas

An **area** is a region of state that hangs together in the application's own terms — the vocabulary a user of the product would recognise, not the folder layout. Areas are the units the human will dispatch, one per invocation of the next skill, so a good area is one a person can hold in their head at once.

Group by what the facts are about, and let the grouping cut across the view tree wherever the facts do. Two screens sharing one fact means one area, not two.

Give each area a name and one sentence saying what it is responsible for knowing. An area whose sentence needs an "and" is probably two areas.

**Done when** every fact from step 1 belongs to exactly one area, and no area's responsibility sentence needs an "and".

## 3. Mark ownership and the outside boundaries

Per area, settle two things:

- **Who owns each fact.** Either this application owns it, or it is a copy of something outside that owns it. This is a genuine fork, so ask it rather than guessing — an owned fact and a sourced fact model completely differently.
- **Where the outside touches the area.** Every crossing: what is read in, what is written out, and what the outside can change without being asked. Name the direction, because a fact that only ever flows out is a much smaller problem than one that changes underneath you.

A crossing means an AsyncStrategy, and an AsyncStrategy that does not exist yet means a Satellite decision. Whether to create one is a fork; ask it and record the answer.

**Done when** each fact is marked owned or sourced, every crossing has a direction, and each crossing names either the Satellite it goes through or the fork asking whether one gets created.

## 4. Order the work

Two independent orders per area, because they genuinely differ and merging them would over-serialise the human.

- **`model after`**: the areas whose model this one needs before it can be modelled at all. Usually because this area's facts are defined in terms of theirs.
- **`build after`**: the areas that must already be built before this one can be built.

Either line may be empty. An empty `model after` is what makes an area available to model right now, and the map says so explicitly so the human can dispatch several in parallel without working it out again.

**Done when** every area carries both lines, the `model after` lines contain no cycle, and the areas with an empty `model after` are listed together as the ones ready now.

## 5. Write the map

Write `docs/state/STATE-MAP.md`:

```markdown
# State Map

<one paragraph: what this application knows, in the large>

## Areas

### <Area name>

<one sentence: what this area is responsible for knowing>

| Fact | Owner | Lives today | Notes |
| --- | --- | --- | --- |
| ... | owned / sourced from <what> | <where in the code> | |

**Outside boundaries**: <each crossing, with its direction, and the Satellite or the open fork>

**model after**: <areas, or nothing>
**build after**: <areas, or nothing>

## Ready to model now

<the areas with an empty `model after`>

## Open questions

<every `[?]` and `[BOUNDARY]` in one list, so the redline is one place>
```

Facts that turned out to be view-local belong in the map too, marked as such. Recording that a fact was considered and deliberately left out of the Environment is worth more than its absence, which reads as an oversight.

**Done when** the file exists, every area from step 2 appears, and every `[?]` in the document is also collected under Open questions.

## 6. Hand back

Report the areas, which are ready to model now, and the count of open questions. Then tell the human to run **`sm-state-modeling`**, once per area, starting with any area that has an empty `model after`.

Do not model an area in this session. The area pass interviews, and it needs the map agreed before it starts.
