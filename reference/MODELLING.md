# The modelling method

Shared by `sm-state-map`, `sm-state-modeling`, `sm-implement`, and `sm-refactor`. Each of those is user-invoked, so none can reach another; this file is where the method they share actually lives.

## Four levels

Modelling state has four levels of zoom. Naming which one you are on prevents the most common failure, which is arguing about one Operation while the boundary it sits inside is still undecided.

| Level | Question it answers | Artifact |
| --- | --- | --- |
| **Sketch** | What areas of state are there, what is each responsible for, and which area uses which? | `docs/state/STATE-MAP.md`, first pass |
| **Facts** | Per area: what does it know, who owns each fact, and where does the outside genuinely touch it? | the same file, second pass |
| **Area model** | Inside one area: which Containers, which Values, which derivations, which changes? | `docs/state/<area>-STATE-MODEL.md` |
| **Behaviour** | What does this one Operation, Computed, or Service actually do? | the code, and its tests |

Work down, never up, and stop at each gate:

- **The sketch is confirmed by the human before any fact is inventoried.** It is a dozen lines, so a misunderstanding costs a sentence to fix. The same misunderstanding found after the fact tables are written is already baked into every row of them, and that is the expensive version.
- **A fact that fits no confirmed area means the sketch was wrong.** Stop, propose the correction, and get it confirmed before the inventory continues.
- **The map is agreed before any area is modelled**, and an area is modelled before its behaviour is built.

The top two levels share one file because the sketch is that file's skeleton: each area's responsibility sentence is written first and the fact table is filled in underneath it once the skeleton is agreed.

The shape is borrowed from context-and-container diagramming, the vocabulary is not. In particular a **Container** here is the library's Container, a named slice of state that drops as a unit. It has nothing to do with a deployable unit.

## Propose from the code, interview the forks

Read the code first and arrive with a proposal. An interview that starts from nothing spends the human's attention on questions the codebase already answers, and they will answer them worse than the code does.

Then interview **only the genuine forks** — the decisions where two answers are both defensible and the code cannot settle it:

1. **A Container boundary that could plausibly split two ways.** Two sets of facts that might die together or might not.
2. **A fact owned by the application versus sourced from outside.** Is this fact the application's own, or a copy of something a server, a store, or the system owns?
3. **Navigation in state versus SwiftUI's own.** Selection, the current tab, and what is presented can live either way, and the answer changes the whole area.
4. **Whether a new Satellite gets created.** A new external boundary is a package decision, not a modelling one.
5. **Whether a fact belongs in the Environment at all**, rather than staying view-local. The Environment is for facts more than one surface needs.

Ask a fork as a numbered question with your recommended answer attached, so answering is a yes or a correction rather than an essay.

## Derive the rest, and record why

Everything else follows from a property of the fact itself. Derive it, write the reason in the artifact next to it, and do not spend a question on it. The reason is what makes the model reviewable: a reader can disagree with the reason without re-deriving the answer.

| Decision | Derived from | Reads as |
| --- | --- | --- |
| Atomic or Keyed | One per application, or one per id | "Keyed by document id: one per open document" |
| Computed or stored | Whether anything writes it | "Computed: nothing writes it, it follows from the selection" |
| Sync or Async operation | Whether it has to await | "Sync: no await on this path" |
| A Service exists | Whether non-view logic must react to a Value | "Service: the exporter has to react when the queue changes, and no view is on screen" |
| Who owns a fact | Whether application code writes it, and whether it is this area's | "Owned elsewhere in the app: the Checker writes the current language" |
| An AsyncStrategy is involved | Whether the fact comes from or goes to somewhere outside the application | "AsyncStrategy: the draft persists between launches" |

## Three owners, and one word that must not slip

Every fact has exactly one of three owners, and the third exists because it is the one that gets lost:

| Owner | Means | What follows |
| --- | --- | --- |
| **Owned here** | This area is the source of truth | An Operation in this area writes it |
| **Owned elsewhere in the app** | Another area is the source of truth. Name it | Read that area's Values. No crossing, no strategy, nothing to decide |
| **Sourced from outside** | Something beyond the process owns it — a store, a server, the system | An AsyncStrategy, and possibly a Satellite |

**Outside the application never means outside this area.** That sentence is the whole point of the middle row. When a modelling pass is scoped to one feature, every neighbouring area is out of view, and the pull is to file it as an outside boundary because that looks like the only column for a thing you are not modelling. It is not: a fact that application code writes is owned by the application, and an AsyncStrategy wrapping it is the app building an adapter to talk to itself.

The test is mechanical, so derive it rather than asking: **can application code write this fact?** If yes it is owned, here or elsewhere. If only the world outside can change it, it is sourced.

A fact owned elsewhere may still be a `@Published` on a legacy singleton rather than a Value. That is a property of the code today, not of who owns the fact, so it stays *owned elsewhere* and picks up a note pointing at `sm-refactor`, whose `@SMPublished` bridge is the tool for it.

## Container granularity is the drop boundary

**One Container per set of facts that die together.** This is the whole rule, and it comes from the library: dropping state drops one Container type at a time, so a Container is exactly the granularity at which you can throw state away.

Three consequences worth stating, because each is a mistake people make:

- **Multi-instance is Keyed inside a Container**, never a Container per instance. An Environment owns exactly one instance of each Container type, so "a Container per open document" is not a shape that exists.
- **Feature-tree depth is view decomposition.** A screen with four nested subviews is not four Containers. The model does not mirror the view tree.
- **Splitting for update precision achieves nothing.** An Address is a key path plus a key, so notification is already per Value. The drop boundary is the only reason to split.

**Unclear means coarse.** A Container that turns out to be too big splits later with the facts intact. Facts scattered across Containers that should have been one have to be gathered, and every Address that named them changes. When you cannot tell, keep them together and mark it.

## Never model everything at once

The map is agreed first. Then the human invokes the area skill once per area, one at a time or several in parallel, scheduling against the map's own lines:

- **`uses`** names the areas this one reads facts from, and what it needs from each. This is a relation between areas, not a schedule, and it is written at sketch time because it is what makes *owned elsewhere in the app* visible before a single fact table exists.
- **`model after`** names the areas whose model this one needs in order to be modelled at all. Largely it follows from `uses`, but not always: an area can read another's facts and still be modelled first.
- **`build after`** names the areas that must already be built before this one can be. These two orders are different, and collapsing them into one "depends on" over-serialises the work for no reason.

Any of the three can be empty, and an empty `model after` is what makes an area parallel-safe to model right now.

Keep `uses` and outside boundaries apart. `uses` is in-app and costs nothing to satisfy; a boundary is external and costs a strategy. Collapsing them is the same slip as the middle owner row, arriving from the other direction.

## A scoped pass is the normal pass

Mapping an entire existing application in one go is rare. Usually the scope is one feature, and the method holds — but three things change, and each has bitten:

- **Neighbours belong in the sketch.** An area outside the scope is named, given its responsibility sentence, and left without a fact table. That is what a `uses` line points at, and it is how a scoped pass keeps *owned elsewhere in the app* available as an answer.
- **A lifetime decided outside the scope is a `[?]`.** When a fact might die with something you cannot see, you cannot write its drop sentence, and guessing quietly produces a Container boundary that a later app-wide view contradicts. `[BOUNDARY]` is for disagreeing with a boundary you can see; this is not that.
- **Ordering inside one feature says little.** Areas within a feature are usually layers of one concept, so `model after` chains and almost nothing is parallel-safe. Report the chain, and do not present it as a property of the application.

An area agent works inside one area. When it decides a fact really belongs on the other side of a boundary the map drew, it **flags and proceeds with the map's answer** rather than redrawing unilaterally. The main session reconciles the flags once the areas report.

## Markers

Three markers, so a reviewer scans instead of reading, and so a later session can grep. Use exactly these spellings.

| Marker | Means | Who resolves it |
| --- | --- | --- |
| `[?]` | A guess. Everything the code could not settle and no fork was asked about, including anything a scoped pass cannot see far enough to answer. | The human, on the redline pass |
| `[BOUNDARY]` | This area would draw a boundary differently from the map. Proceeding with the map's answer. | The main session, after the areas report |
| `[SM-GAP]` | The library cannot express the right shape here. | An upstream ticket |

Mark every guess. An unmarked guess is indistinguishable from a derived answer, which turns the redline pass from a scan into a re-read of the whole document.

## A library gap is never worked around

When the right shape is unreachable because the library does not offer it, the app code does not get a workaround. A workaround is permanent, invisible, and it teaches the next reader that the shape was a choice.

Instead:

1. **Mark it** in the artifact with `[SM-GAP]`, stating what shape you wanted and what stopped you.
2. **Name the upstream repository** that owns the gap, so the marker points somewhere.
3. **Model the shape you can express**, and say in the artifact that it is the fallback.
4. **Ask the human before filing anything.** A confirmed gap becomes two tickets, one on the library and one on this skills project. Do not file either without being asked to in that session.

## Check the API surface anchor before trusting a signature

[`API-SURFACE.md`](API-SURFACE.md) is generated from the library by `swift symbolgraph-extract` and carries in its header the release and commit it was generated against. The library is pre-1.0, and the surface has moved between releases.

Before relying on it, compare its anchor with the version in the consuming project's `Package.resolved`. On a mismatch, regenerate against the resolved version into a git-ignored path in that project and prefer that copy:

```shell
scripts/generate-api-surface.sh <path-to-library-checkout> <resolved-version> .sm/API-SURFACE.md
```

The skills themselves name no signatures at all, so this file is the only place one appears. That is deliberate: judgement that quotes a signature goes stale silently, while judgement anchored to nothing stays true across releases.

## Terminology belongs to the project

Use the library's own words for library concepts, and the project's own words for its domain. When a domain term is genuinely unsettled and the model keeps tripping over it, that is glossary work: invoke the `domain-modeling` skill and settle the term there rather than coining one inside a state model.
