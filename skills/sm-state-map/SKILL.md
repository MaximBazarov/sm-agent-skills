---
name: sm-state-map
description: Sketch an application's areas of state, confirm the sketch, then map the facts into docs/state/STATE-MAP.md. Takes a scope, which is usually one feature.
disable-model-invocation: true
---

# State Map

Two passes over one file. The first sketches the areas and gets them confirmed; the second fills in the facts underneath. Nothing here decides a Container or an Operation — that is the area model's job, and doing it now means doing it with the boundaries still unsettled.

Read [`reference/MODELLING.md`](../../reference/MODELLING.md) first. It carries the four levels and their gates, the three owners, the drop boundary, which decisions to interview and which to derive, and the markers this document uses.

**The gate between the two passes is the point of this skill.** A sketch is a dozen lines, so a misunderstanding costs a sentence. The same misunderstanding found after the fact tables exist is already in every row of them.

## 1. Sketch the areas, and confirm them

Ask the human for the scope if they have not given one. The whole application is the default; one feature is the usual answer, and the rest of this skill works the same either way.

Read enough code to name the areas — a skim for what the code is *about*, not the inventory, which is step 2. Then write, for each area:

- **A name**, in the application's own terms. The vocabulary a user of the product would recognise, not the folder layout.
- **One sentence** saying what it is responsible for knowing. A sentence needing an "and" is probably two areas.
- **`uses`**: which other areas it reads facts from, and what it needs from each.

Areas outside the scope get a name and a responsibility sentence and no more. They exist in the sketch so a `uses` line has something to point at, and so a fact they own can be recognised as theirs rather than mistaken for something external.

Group by what facts are about, letting the grouping cut across the view tree wherever the facts do — two screens sharing one fact is one area, not two. A good area is one a person can hold in their head at once, because areas are the units the human dispatches, one per invocation of the next skill.

Then **show the human the sketch and stop.** Every area, its sentence, and its `uses` lines, as a numbered list they can correct in place. Do not begin step 2 until they have confirmed it.

**Done when** the human has confirmed the area list, the responsibility sentences, and the `uses` lines.

## 2. Inventory every fact

A **fact** is one thing the application knows. Find all of them in scope, from the code.

Look in every place a fact hides, and name the place in your notes so the inventory is auditable:

- View-local storage: the `@State` and `@StateObject` properties, and every observed or environment object a view holds.
- Anything long-lived: singletons, shared instances, managers, controllers, view models, coordinators, caches.
- Anything already in an Environment, if the project has begun adopting the library.
- Anything outside the process: user defaults, the keychain, files, a database, a server, system permissions and settings, the clock.
- Anything derived: values recomputed in a `body`, in a getter, or cached in a property alongside the inputs it was computed from.

For each fact, record where it lives today and who writes it. A fact with two writers is the finding this step exists to surface; note it rather than resolving it.

**A fact that fits no confirmed area means the sketch was wrong.** Stop, propose the correction — a new area, or a split, or a widened responsibility — and get it confirmed before continuing. This is cheap now and expensive later, which is the whole reason the gate exists.

**Done when** every fact in scope has a line, every file that declares or mutates state has been opened, and every fact sits in a confirmed area. A fact you are unsure counts is listed with `[?]`, not dropped.

## 3. Mark who owns each fact

One of three owners per fact, from `reference/MODELLING.md`. Write the concrete spelling, not the category name: `Value here`, `Computed here`, `Value on <Area>`, `@SMPublished on <Area>` where that area is still a legacy class, or `outside: <what>`.

Derive it, do not ask it. The test is mechanical: **can application code write this fact?** If yes it is owned, and the sketch's `uses` lines already say by whom. If only the world beyond the process can change it, it is sourced.

Ask only where that test and the truth disagree — a cache, a mirror, a local copy the app writes freely while a server owns what it means. That is the genuine fork, because an owned fact and a sourced fact model completely differently, and the test alone answers it wrongly.

A fact owned elsewhere that is still a `@Published` on a legacy singleton stays *owned elsewhere*, with a note pointing at `sm-refactor`. How it is stored today is not who owns it.

**Done when** every fact carries one of the three owners, every *owned elsewhere* names its area, and any cache or mirror has been asked about rather than derived.

## 4. Draw the outside boundaries

Only facts sourced from outside make a crossing. Per area, name every one: what is read in, what is written out, and what the outside can change without being asked. Give each a direction, because a fact that only ever flows out is a much smaller problem than one that changes underneath you.

A crossing means an AsyncStrategy, and an AsyncStrategy that does not exist yet means a Satellite decision. Whether to create one is a fork; ask it and record the answer.

**An area named in a `uses` line is not a crossing.** It is application code either side, so reading it costs nothing and decides nothing. Putting a strategy there builds an adapter for the app to talk to itself.

**Done when** every sourced fact appears in exactly one crossing, every crossing has a direction and names either its Satellite or the fork asking for one, and no `uses` target appears among the crossings.

## 5. Order the work

Two schedules per area, on top of the `uses` relation already sketched. They genuinely differ, and merging them would over-serialise the human.

- **`model after`**: the areas whose model this one needs before it can be modelled at all. Largely it follows from `uses`, but an area can read another's facts and still be modelled first.
- **`build after`**: the areas that must already be built before this one can be built.

Either may be empty, and an empty `model after` is what makes an area available to model right now.

On a scoped run, expect these to chain: areas within one feature are usually layers of one concept, so little or nothing is parallel-safe. Report the chain as what it is, and do not present it as a property of the application.

**Done when** every area carries both lines, the `model after` lines contain no cycle, and the areas with an empty `model after` are listed together.

## 6. Write the map

Write `docs/state/STATE-MAP.md` for a whole application, or `docs/state/<scope>-STATE-MAP.md` for a scoped run.

```markdown
# State Map — <scope, or the application>

**Scope**: <what is in, and that areas outside it appear as neighbours without fact tables>

<one paragraph: what this knows, in the large>

## Areas

### <Area name>

<one sentence: what this area is responsible for knowing>

**uses**: <area, and what it needs from it>

| Fact | Owner | Lives today | Notes |
| --- | --- | --- | --- |
| ... | Value here / Computed here / Value on <Area> / @SMPublished on <Area> / outside: <what> | <where in the code> | |

**Outside boundaries**: <each crossing, with its direction, and the Satellite or the open fork>

**model after**: <areas, or nothing>
**build after**: <areas, or nothing>

## Neighbours

<areas outside the scope: name and responsibility sentence only>

## Ready to model now

<the areas with an empty `model after`>

## Open questions

<every `[?]` and `[BOUNDARY]` in one list, so the redline is one place>
```

Facts that turned out to be view-local belong in the map too, marked as such. Recording that a fact was considered and deliberately left out of the Environment is worth more than its absence, which reads as an oversight.

**Done when** the file exists, every confirmed area appears, every neighbour named in a `uses` line has an entry, and every `[?]` in the document is also collected under Open questions.

## 7. Hand back

Report the areas, which are ready to model now, and the count of open questions. Say plainly if the sketch moved during step 2 and what moved. Then tell the human to run **`sm-state-modeling`**, once per area, starting with any area that has an empty `model after`.

Do not model an area in this session. The area pass interviews, and it needs the map agreed before it starts.
