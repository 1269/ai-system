# Lead time zones with Jev (n8n template)

Your CRM is full of leads with no time zone. You want your follow-up to land at 9am their time, not 3am. Asking a chat model "what time zone is this person in?" works, but you're paying a PhD to answer a multiple choice question, and it hands you a confident-sounding paragraph whether it knows or not.

This workflow asks [Jev](https://docs.typesafe.ai) instead. Jev is TypeSafe AI's System One model. It doesn't write text. You hand it what you know about a lead and a typed question, and it hands back an answer with a probability. That probability is what makes this safe to run across a whole database: confident answers get written back, unsure ones go to a person.

## What it does

```
Sample leads ─▶ Time zone already known? ─ yes ─▶ Keep existing time zone
                          │
                          no
                          ▼
              Jev: time zone, decision-maker, fit
                          ▼
                   Flatten answers
                          ▼
                  Confident enough? ─ yes ─▶ 9am their time, on my clock ─▶ Write back to CRM
                          │
                          no ──────────────▶ Needs human review
```

Each lead goes to Jev together with `me`: a short profile of who's doing the outreach (your business, your ideal customer, who isn't a fit, your time zone). One Jev request per lead asks three questions at once, one of each type Jev supports:

| Question | Type | What comes back |
| --- | --- | --- |
| `timezone` | **Choice**: pick one from a list | One of 51 time zones, or `unknown`, plus a confidence |
| `is_decision_maker` | **Noul**: true or false | The probability of yes, 0 to 1 |
| `lead_fit` | **Score**: a position on levels you define | 0 (not a fit) to 3 (ideal fit), judged against `me`, plus a confidence |

Leads that already have a time zone skip Jev entirely. Known facts stay in plain logic; Jev only handles the judgment calls. The last step isn't AI at all: for each confident lead it finds the next 9am in their time zone and shows it on your clock (`me.timezone`), so you know when to send.

## What the sample leads show

The sample data has eleven leads, picked to show where this beats a lookup table. The first seven:

| Lead | Signal | Jev's answer |
| --- | --- | --- |
| Tom, accounting firm | LinkedIn says "Greater Boston", phone is a 617 number | `America/New_York` |
| Priya, joinery | Only a `.co.uk` email and "Manchester" as company HQ | `Europe/London` |
| Jordan, home services | Company HQ is San Francisco, but the notes say remote, lives outside Denver | `America/Denver` (the person beats the HQ) |
| Sam, landscaping | Scottsdale, 480 phone | `America/Phoenix` (Arizona skips daylight saving) |
| Aroha, physio clinic | `.co.nz` email, +64 phone | `Pacific/Auckland` |
| Chris, intern | A gmail address and nothing else | `unknown`, sent to review |

These are real results from `jev-1.13.0` with the questions in this workflow, every one at 0.98 confidence or higher. The seventh lead (Maria) already has a time zone, so it never reaches Jev.

The last four are the leads from the video's live run:

| Lead | Signal | Jev's answer |
| --- | --- | --- |
| Ray, roofing | A 602 number, and his notes say "we never change our clocks out here" | `America/Phoenix` (no daylight saving, so a lookup table that says Mountain time is wrong half the year), 1.00 |
| Lena, legal staffing | Company HQ is Chicago, but a +49 30 phone and notes that say she moved to Berlin | `Europe/Paris`, the zone in the list that shares Berlin's clock (the person beats the HQ), 0.84 |
| Mia, physio clinic | A `.com.au` email, a +61 8 phone, and the Fremantle Doctor in her notes | `Asia/Singapore`, the zone in the list that shares Perth's clock, 0.90; not the decision maker (0.05: her notes say the owner signs off) |
| A gmail address | Nothing else | `unknown`, sent to review |

## Set it up

No n8n yet? [`SETUP-PROMPT.md`](./SETUP-PROMPT.md) is a prompt you hand to Claude Code: it runs n8n on your machine in Docker, installs the TypeSafe AI node, and connects n8n's MCP server so Claude Code can build workflows in it. Then come back here.

1. **Install the TypeSafe AI node.** It's a verified community node. On n8n Cloud, search for "TypeSafe AI" in the nodes panel. Self-hosted: **Settings → Community Nodes → Install**, package `@typesafe-ai/n8n-nodes-typesafe-ai`.
2. **Import the workflow.** Download [`lead-timezones-jev.json`](./lead-timezones-jev.json), then in n8n open a new workflow and choose **Import from File** (or copy the file's contents and paste onto the canvas).
3. **Add your API key.** Open the Jev node, create a **TypeSafe AI API** credential, and paste a key from [typesafe.ai](https://typesafe.ai).
4. **Run it** with the sample leads to see the three answers on each item.
5. **Make `me` yours.** In the sample leads node, edit `me`: your business, your ideal customer, who isn't a fit, your time zone and working hours. The fit and decision-maker questions are judged against it, and the 9am step uses your time zone.
6. **Swap in your real leads.** Replace the sample leads with your Google Sheets, HubSpot, Airtable, or CRM node, and send each lead on as `{ me, lead }`. Map your columns to the lead fields in [`sample-leads.json`](./sample-leads.json): `name`, `title`, `company`, `email`, `phone`, `city`, `region`, `country`, `linkedin_location`, `company_hq`, `notes`, `timezone`. Missing fields are fine; Jev uses whatever is there.
7. **Replace the two end nodes.** "Write back to CRM" becomes your CRM's update node, writing `timezone_inferred`, `timezone_confidence`, `decision_maker_probability`, `lead_fit_score`, and the send times (`send_at_their_time`, `send_at_my_time`, `send_at_utc`). "Needs human review" can be a Slack message, a sheet, or a task.

## Things worth knowing

- **Why 51 time zones and not 400?** A Choice question takes up to 255 options, and the official time zone database has about 400 zones. For scheduling, what matters is the UTC offset and the daylight saving rule, and there are only about 57 distinct patterns worldwide. Each option is one real zone that stands for its pattern, with a description of the places it covers. So a lead in Perth comes back as `Asia/Singapore`, which shares Perth's clock all year. Edit the list in the Jev node if you want city-level zones for your own markets.
- **Jev writes to new fields.** `timezone_inferred` sits next to your `timezone` field instead of overwriting it. A guess should never silently replace something a person entered.
- **Tune the threshold.** The flatten step uses 0.8. Run it on a sample of your own leads, check the review pile, and move the number up or down.
- **Make the fit question yours.** The `lead_fit` levels are written against `me`, so editing `me` is usually enough. Rewrite the four levels in the Jev node if your idea of fit is more specific.
- **Cost.** Each lead is a few thousand input tokens (mostly the time zone list) and comes back in a fraction of a second.
- **No community nodes?** Use an **HTTP Request** node instead: `POST https://api.typesafe.ai/v1/systemone` with an `Authorization: Bearer <key>` header and a JSON body of `{"model": "jev-latest", "state": {"me": <me>, "lead": <the lead>}, "questions": <the questions JSON from the Jev node>}`. The answers come back under `answers`, same as the node with Simplify turned off.

## Part of the AI System

This sits under component 9, [Automation](../../README.md): work that runs in the background without you asking. The judgment layer here is one small model making one kind of call, wired into a workflow you already run.
