# sm-skills

Agent skills for building Swift applications with [Structured State Management](https://github.com/MaximBazarov/StateManagement).

Six skills that model an application's state into an artifact, build from that artifact, and refactor an existing Combine codebase into it. No Swift ships here: this is a toolkit of documents an agent reads.

## Install

### Claude Code

```shell
/plugin marketplace add MaximBazarov/sm-agent-skills
/plugin install sm-skills@sm
```

Then `/reload-plugins` if the installer asks for it. Skills arrive namespaced, so `sm-state-map` is `/sm-skills:sm-state-map`.

Third-party marketplaces have auto-update **off** by default. Either enable it on the Marketplaces tab or run `/plugin update sm-skills` by hand. The plugin's `version` is the cache key, so a release you have not bumped past will report "already at the latest version".

### Cursor

Cursor reads no Claude Code marketplace. It does read `.claude/skills/`, so vendor the repo and point one entry inside that directory at it:

```shell
git submodule add https://github.com/MaximBazarov/sm-agent-skills vendor/sm-agent-skills
mkdir -p .claude/skills
ln -s ../../vendor/sm-agent-skills/skills .claude/skills/sm
```

Cursor walks the skills root recursively, so all six load from that one link. Update with `git submodule update --remote vendor/sm-agent-skills`.

Keep `.claude/skills` itself a **real directory**. Claude Code reports an error and scans nothing when the `skills` directory or its parent `.claude` is a symlink, so the link has to be an entry inside it — which is why the recipe above symlinks `.claude/skills/sm` and not `.claude/skills`. Both hosts then read the same checkout.

`.cursor/skills/` and `.agents/skills/` work the same way if you would rather not touch `.claude/`.

## The skills

Three you type, two the agent reaches on its own, one for review.

| Skill | Invoked by | What it does |
| --- | --- | --- |
| `sm-state-map` | you | Maps the whole application's state into `docs/state/STATE-MAP.md`: the areas, who owns each fact, the boundaries with the outside, and the order to work in |
| `sm-state-modeling` | you | One area per run, because it interviews you. Produces `docs/state/<area>-STATE-MODEL.md` |
| `sm-implement` | you | Builds one area from its model |
| `sm-refactor` | you | Turns a Combine codebase into Structured State Management, one green step at a time |
| `sm-tdd` | the agent | Tests through the Environment |
| `sm-code-review` | the agent | Reviews app code against the library's grain |

Start with `sm-state-map`. Each skill names the next one where you need it, so there is nothing else to remember.

## Which library release this matches

`reference/API-SURFACE.md` is generated from the library by `swift symbolgraph-extract`, never written by hand, and carries the release and commit it was generated against in its header. The plugin's version mirrors that release.

A skill that needs the surface checks that anchor against your `Package.resolved` first. On a mismatch it regenerates with `scripts/generate-api-surface.sh` into a git-ignored path in your own repo and prefers that copy, so a newer library does not get described by an older document.

## License

MIT. See [LICENSE](LICENSE).
