---
name: sm-code-review
description: App code against StateManagement, reviewed against the library's grain. Use when reviewing a diff, a branch, or a file that declares Containers, Values, Operations, Computeds, Services, or Watches in an application that depends on the library.
---

# Reviewing app state code

One axis only: does this code go with the library's grain, or against it? General Swift review, the project's own standards, and whether the change matches its spec are all separate jobs; this skill is the state-shaped read of the diff.

Apply every rule below to every changed file that touches state, and report each finding with the file, the line, and which rule it breaks. A rule you checked and found clean does not need reporting. Finish only when every changed state file has been through the whole list.

Signatures live in [`reference/API-SURFACE.md`](../../reference/API-SURFACE.md), generated from the library at a known anchor. **It is the authority on what exists**, not your memory: the library is pre-1.0 and the set of reads each Restricted Environment offers has moved between releases. Check its anchor against the project's `Package.resolved` first. When the surface says the read you want is not there, that is a design signal about the shape, not an invitation to reach around it.

## One way in

- **Change flows through an Operation.** A view, a Service, or a plain function assigning State is the break this whole architecture exists to prevent. The fix is an Operation with a name that says what it does.
- **A Service causes change only by performing an Operation.** Data flows out of a Service, never in. A Service that writes State directly has made itself a second writer.
- **An Async operation writes nothing itself.** It awaits, then performs a Sync operation to land the result. An async body that writes has escaped the one-way rule at the only point where the rule is hard to enforce.
- **Seed is for previews and tests.** Production State arrives through an Operation. Seeding, or the debug write helpers, appearing on a production path is a real defect.

## The one-shot read

Subscriptions are one-shot: a reader is notified once per change and stays subscribed by reading again. Every rule here is the same bug wearing a different hat, so look for all three shapes:

- **A Value copied into `@State`.** The copy gets exactly one update and then drifts. A view depends on a Value by Watching it, in `body`, every render.
- **A Service that reads only in its setup.** It reacts once, then never again. A Service re-reads its inputs on each run, which is how it stays subscribed.
- **A snapshot read from a view body.** It returns the right Value now and never updates. Watch is the view-side read.

## Addressing

- **A Container is a drop boundary**, not a namespace and not a feature folder. One Container per set of facts that die together, because dropping one Container type drops all of it. Facts with different lifetimes sharing a Container means you cannot drop either without the other.
- **Multi-instance is Keyed inside one Container**, never a Container per instance. An Environment owns exactly one instance of each Container type, so a Container per document or per user cannot exist.
- **Splitting a Container never sharpens updates.** An Address is a key path plus a key, so notification is already per Value. A split justified as "so views get fewer updates" is doing nothing, and the review should say so: judge the split on the drop boundary alone.
- **Containers do not nest.** Types may nest inside a Value; Containers may not contain Containers, and there is never a second Environment.
- **The strategy seam takes the `$` Address.** Kicks and inbound verbs name the wrapper; Watch and Operations name the Value. A mix-up here compiles in some shapes and silently addresses the wrong thing.

## Derived versus stored

- **A fact nothing writes is a Computed.** Stored and recalculated by hand is two sources of truth for one fact, and they will disagree.
- **A Computed does not cause anything.** It derives a Value from Values it reads. Side effects, performs, and writes inside a derivation break the single source of truth in the direction that is hardest to debug.
- **A Computed's dependencies are whatever it last read.** A derivation that reads a Value it does not need has widened its own invalidation. Look for reads that no branch uses.

## Views

- **A fact two surfaces need belongs in the Environment; a fact one view owns alone does not.** A sheet toggle, a text-field draft mid-edit, a scroll position: view-local. Promoting those to the Environment adds an Address nothing else reads, and it costs the drop semantics.
- **A child that needs a Value takes its identity and Watches inside.** A parent that Watches a Value and passes it down has made itself dependent on the child's fact, so the parent re-renders for a change it does not care about.
- **Keyed reads differ in optionality.** A keyed stored Value can be absent, so reading one hands back an optional; a keyed Computed always runs, so it does not. The call shapes look alike, so check which one a keyed read is actually against.

## Boundaries

- **Persistence, sync, HTTP, and platform stores belong to a Satellite**, behind an AsyncStrategy that ships with it. Storage code inside a Container, an Operation, or a Service has put an external boundary in the middle of your state.
- **Leftover Combine always runs on the shared Environment.** A leftover property access on such a class reads and writes the shared Environment whatever Environment surrounds it, and overriding that is unsupported. A test or a preview that expects isolation through leftover Combine is wrong in a way that passes locally and fails in a suite.
- **One observation round per outermost Operation.** A nested Operation joins the round in flight, so there is no notification between the two. Logic that depends on an intermediate update is depending on something the library does not do.

## Reporting a library gap

When the review finds that the right shape is unreachable because the library does not offer it, that is a gap, not a finding against the author. Record it the way [`reference/MODELLING.md`](../../reference/MODELLING.md) describes: the greppable marker in the artifact, the upstream repo named, and no workaround written into app code.
