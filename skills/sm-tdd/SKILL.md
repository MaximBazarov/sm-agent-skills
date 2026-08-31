---
name: sm-tdd
description: App code against StateManagement, tested through the Environment. Use when writing or fixing a test for a Container, Value, Operation, Computed, or Service in an application that depends on the library.
---

# Testing app state

Your application's state has exactly one seam: **the Environment**. Seed it, run an Operation, then read the facts and Computeds and assert on what you read. That is every test, and there is no second seam to look for.

The seam is this narrow because the library already guarantees the parts either side of it. An Operation is the only way State changes, so nothing can change behind your test. Every read is a declared dependency, so a read that returns the right Value proves the wiring. What is left to test is your own logic: which Values an Operation writes, what a Computed derives, and when a Service reacts.

Signatures live in [`reference/API-SURFACE.md`](../../reference/API-SURFACE.md), generated from the library. Check its anchor against your `Package.resolved` before you trust one.

## The loop

Red before green, one slice at a time. Each cycle is four moves:

1. **A fresh Environment.** One per test, never the shared production one, so tests cannot leak into each other. Reach for the shared Environment only for a test that goes through leftover Combine, which has no other Environment.
2. **Seed the starting Values.** Seed is how a test arranges State. It is not a change, so it opens no observation round and needs no Operation of its own.
3. **Perform one Operation.** The thing under test. If arranging needs several, perform the real ones rather than reaching around them: an arrangement built from your own Operations is an arrangement that can actually occur.
4. **Read and assert.** Read the facts the Operation should have written, and the Computeds that derive from them. From outside the library, read through `StateReader` in the testing-support product; it is a Service, so its reads carry a known reader like any other.

Then the next slice, chosen by what this one taught you.

## What to assert

Assert the State an observer could see:

- **An Operation wrote this Value.** The fact at that Address holds what you expect afterwards.
- **An Operation left its neighbours alone.** Writing one Keyed value leaves the other keys as they were. This is the assertion that catches a too-coarse write.
- **A Computed equals this.** Derived from the Values you seeded, and recomputed after an Operation changes one of its inputs.
- **A Computed ignores what it does not read.** Change a Value the Computed never touches and it stays put. This is how you prove the dependency edges are the ones you meant.
- **An Operation threw.** A throwing Operation's failure is part of its contract.
- **A Service performed the Operation it owes.** Assert the State that Operation produced, which is the Service's only observable output.
- **A Container dropped.** After a reset, the facts in that Container are back to their declared starting Values.

## Where tests do not go

Each of these looks like a test of your state and is really a test of the library or of SwiftUI:

- **That a view's `body` ran, or that a Watch fired.** Watch re-reads in `body`, so a render count is a SwiftUI fact, not a state fact. Assert the Value the view would read instead.
- **That a read stayed subscribed.** Subscriptions are one-shot by design: a reader is notified once per change and re-subscribes by reading again. A test that reads once and waits for a second update is asserting a stream the library never promised.
- **A Computed's cache.** Whether a recompute happened is an implementation detail; whether the Value is right is the contract.
- **An AsyncStrategy against real storage or a real network.** The strategy belongs to a Satellite and is tested there. Your app's test asserts what the Environment holds once a Value has been applied, which you arrange by seeding it.

Tests that need more from the library's testing-support product than a fresh Environment, Seed, and `StateReader` are out of scope today. When you hit that wall, record it as a gap the way [`reference/MODELLING.md`](../../reference/MODELLING.md) describes rather than building a private probe to get around it.

## House style

- Swift Testing: `import Testing` and `@Test`.
- Every `@Test` carries a description string, a sentence in plain English, because that sentence is what a failure reads as: `@Test("Toggling one card's selection leaves the others alone")`.
- One description per test. Add a `///` comment only to say why the case matters, never to restate the description.
- Match the vocabulary in the project's `CONTEXT.md` if it has one, so a test name and the domain agree.
