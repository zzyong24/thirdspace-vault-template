---
name: lifeos
description: Use when handling ThirdSpace interpersonal events, relationship analysis, people profiles, LifeOS records, event retrospectives, or decisions involving people and context.
triggers:
  - "人际事件"
  - "记录关系"
  - "人物档案"
  - "人际"
  - "生活记录"
  - "LifeOS"
---

# LifeOS Skill

## Scope

LifeOS is a domain Skill loaded after the current workspace Skill. It handles people profiles, interpersonal events, relationship context, event analysis, retrospectives, and decision preparation.

## Current Paths

- Events: `{VAULT}/02-日记/人际事件/事件`
- Raw event records: `{VAULT}/02-日记/人际事件/原始记录`
- Reflections: `{VAULT}/02-日记/反思`
- People profiles: `{VAULT}/05-资源/人物档案/people.json`
- Machine copy: `{VAULT}/.thirdspace/data/lifeos/people.json`

## Load Order

1. Load `thirdspace-vault`.
2. Load `workspace-journal` for event/reflection work, or `workspace-resources` for people profile work.
3. Load this Skill only when the task mentions people, relationship, interpersonal events, LifeOS, event analysis, retrospective, or decision simulation.

## Rules

- Do not put new LifeOS files under `space/crafted/lifeos` or `flux/lifeos`.
- New event files go to `02-日记/人际事件/事件/YYYYMMDD_主题.md`.
- Raw records go to `02-日记/人际事件/原始记录/YYYYMMDD_主题.md`.
- People profile updates must keep `05-资源/人物档案/people.json` and `.thirdspace/data/lifeos/people.json` consistent.
- Event analysis should record facts, stakeholders, constraints, emotions, decisions, and follow-up actions.
- Do not flatten sensitive interpersonal context into generic knowledge notes unless the user explicitly asks for reusable lessons.

## Frontmatter

Event documents use:

```yaml
type: "event"
topic: "lifeos"
workspace: "02-日记"
source: "lifeos"
status: "active"
tags: ["lifeos", "event", "relationship"]
```

Raw records use `type: "event-raw"` and tags `["lifeos", "raw", "event"]`.

## Maintenance

- If old paths contain files, add them to `.thirdspace/queues/normalization-queue.yaml`.
- If people profiles are changed, update both JSON copies.
- If an event produces a reusable principle, create a separate knowledge note in `03-知识` and link back to the event.
