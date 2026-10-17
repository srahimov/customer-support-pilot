# Customer Support Pilot

A Python customer support copilot for **Fox Insurance Service**, built with LangChain, LangGraph, OpenAI, and Supabase Postgres.

The terminal application retrieves customer accounts, policies, invoices, and support tickets. One agent changes department through state and middleware. Ticket updates pause for human approval, editing, or rejection before reaching the database.

Fox Insurance Service serves residential and business customers across all 50 US states with car, truck, and home insurance.

- Address: 11111 Ash St, Los Angeles, CA 90001
- Phone: 877-977-8797

## Contents

- [Capabilities and current scope](#capabilities-and-current-scope)
- [LangChain topics covered](#langchain-topics-covered)
- [Project structure](#project-structure)
- [Setup](#setup)
- [Run and resume conversations](#run-and-resume-conversations)
- [How the LangChain pieces work](#how-the-langchain-pieces-work)
- [Human approval workflow](#human-approval-workflow)
- [Database consistency and error handling](#database-consistency-and-error-handling)
- [Manual verification](#manual-verification)
- [Optional LangSmith tracing](#optional-langsmith-tracing)
- [Topics still to implement](#topics-still-to-implement)

## Capabilities and current scope

| Capability | Current implementation |
| --- | --- |
| Customer, policy, and billing lookups | Python records in `records.py` |
| Ticket lookups and updates | Parameterized SQL through `TicketRepository` |
| Request classification | Pydantic `SupportResponse` |
| Department routing | Single agent, `active_department`, and dynamic middleware |
| Employee access checks | Role and assigned customer IDs checked inside tools |
| Conversation memory | LangGraph checkpoints in the `fox_insurance` Postgres schema |
| Human review | Per-call approve, edit, and reject for `update_ticket` |
| Pending review after restart | Resume the same conversation UUID and employee access scope |
| Concurrent ticket updates | Customer, ticket, and expected-version checks in one SQL statement |
| Interaction | Synchronous terminal application |

The current CLI supplies employee identity and permissions in code. It does not yet authenticate employees through an identity provider. An assigned `support_agent` or `supervisor` can review an update; a separate supervisor's approval is not required.

## LangChain topics covered

This table maps the topics practiced so far to the running application. The remaining documentation topics are listed in the [roadmap](#topics-still-to-implement).

| LangChain topic | What this project demonstrates | Code |
| --- | --- | --- |
| [Installation and quickstart](https://docs.langchain.com/oss/python/langchain/overview) | A packaged Python application managed with `uv`; provider integration installed separately | [pyproject.toml](pyproject.toml), [uv.lock](uv.lock) |
| [Models](https://docs.langchain.com/oss/python/langchain/models) | `init_chat_model`, environment-based model selection, Responses API configuration, timeout, and transport retries | [models.py](src/customer_support_pilot/models.py) |
| [Agents](https://docs.langchain.com/oss/python/langchain/agents) | `create_agent` composes a model, tools, prompt, response schema, state, context, middleware, and checkpointer | [agents.py](src/customer_support_pilot/agents.py) |
| [Messages](https://docs.langchain.com/oss/python/langchain/messages) | `HumanMessage`, model `AIMessage` tool calls, and `ToolMessage` results matched by tool-call ID | [main.py](src/customer_support_pilot/main.py), [tools.py](src/customer_support_pilot/tools.py), [middleware.py](src/customer_support_pilot/middleware.py) |
| [Tools](https://docs.langchain.com/oss/python/langchain/tools) | `@tool`, descriptive docstrings, typed arguments, model-selected calls, and typed update requests | [tools.py](src/customer_support_pilot/tools.py) |
| [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output) | `response_format=SupportResponse` produces a category, customer ID, and answer | [schemas.py](src/customer_support_pilot/schemas.py), [agents.py](src/customer_support_pilot/agents.py) |
| [Runtime context](https://docs.langchain.com/oss/python/langchain/runtime) | `context_schema`, `context=context`, `ToolRuntime`, employee permissions, and repository injection | [context.py](src/customer_support_pilot/context.py), [main.py](src/customer_support_pilot/main.py), [tools.py](src/customer_support_pilot/tools.py) |
| [Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory) | Messages and department state remain associated with a conversation thread | [state.py](src/customer_support_pilot/state.py), [persistence.py](src/customer_support_pilot/persistence.py) |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | `PostgresSaver`, thread configuration, state snapshots, serialization configuration, and restart recovery | [persistence.py](src/customer_support_pilot/persistence.py), [main.py](src/customer_support_pilot/main.py) |
| [Middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview) | Model and tool execution are controlled through an ordered middleware list | [middleware.py](src/customer_support_pilot/middleware.py) |
| [Prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in) | Model-call limits, tool-call limits, selected tool-error handling, and human review | [middleware.py](src/customer_support_pilot/middleware.py) |
| [Custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom) | `before_model`, `wrap_model_call`, and `wrap_tool_call` | [middleware.py](src/customer_support_pilot/middleware.py) |
| [Guardrails](https://docs.langchain.com/oss/python/langchain/guardrails) | In-tool authorization, department tool restrictions, Pydantic validation, and approval-gated writes | [tools.py](src/customer_support_pilot/tools.py), [schemas.py](src/customer_support_pilot/schemas.py), [middleware.py](src/customer_support_pilot/middleware.py) |
| [Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering) | The active department selects the prompt and available tools for each model call | [middleware.py](src/customer_support_pilot/middleware.py) |
| [Handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs) | One agent transitions between department configurations using state and `Command` | [state.py](src/customer_support_pilot/state.py), [tools.py](src/customer_support_pilot/tools.py), [middleware.py](src/customer_support_pilot/middleware.py) |
| [Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop) | `HumanInTheLoopMiddleware(interrupt_mode="per_call")`, pending interrupts, and approve/edit/reject decisions | [approvals.py](src/customer_support_pilot/approvals.py), [middleware.py](src/customer_support_pilot/middleware.py) |
| [Interrupts and resume](https://docs.langchain.com/oss/python/langgraph/interrupts) | `Command(resume={interrupt_id: decision})` resumes a specific paused action | [main.py](src/customer_support_pilot/main.py) |

Database version checks, SQL parameter binding, connection pooling, Python packaging, and Git complement these LangChain topics. They are application engineering concerns rather than additional LangChain agent patterns.

## Project structure

```text
customer-support-pilot/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── README.md
└── src/
    └── customer_support_pilot/
        ├── __init__.py
        ├── main.py              # Current terminal entry point
        ├── models.py            # Model factory
        ├── agents.py            # Agent assembly
        ├── schemas.py           # Final response and update request validation
        ├── state.py             # Department type and checkpointed agent state
        ├── context.py           # Employee scope and repository dependency
        ├── tools.py             # Lookups, handoff, and ticket update
        ├── middleware.py        # Routing, limits, tool restrictions, and HITL
        ├── approvals.py         # Terminal review interface
        ├── repositories.py      # Ticket SQL operations
        ├── persistence.py       # Checkpointer, pool, and thread configuration
        ├── records.py           # Customer, policy, invoice, and ticket seed records
        ├── seed_tickets.py      # Insert missing ticket records
        ├── main_no_handoff.py   # Earlier entry-point variant
        └── main_handoff.py      # Earlier entry-point variant
```

The console command uses `main.py`. The earlier entry-point variants are retained as references; they are not the command's configured entry point.

## Setup

### 1. Install dependencies

Requirements: Python 3.12 or newer, `uv`, an OpenAI API key with access to the configured model, and a Postgres database.

```bash
git clone https://github.com/srahimov/customer-support-pilot.git
cd customer-support-pilot
uv sync --locked
```

`pyproject.toml` declares dependencies and `uv.lock` records the resolved versions. The project currently declares LangChain `>=1.4.6`, which supports the per-call approval API used here.

### 2. Configure the environment

Create a local `.env` file at the project root:

```dotenv
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
OPENAI_MODEL=gpt-6-luna
DATABASE_URL="postgresql://postgres.YOUR_PROJECT_REF:YOUR_URL_ENCODED_PASSWORD@YOUR_SESSION_POOLER_HOST:5432/postgres"
```

Copy the actual Postgres connection string from the Supabase dashboard's **Connect** dialog. The example above illustrates a Session pooler connection; replace every placeholder, and URL-encode special characters in the password. This backend connects through Psycopg, so `DATABASE_URL` uses the database password rather than a Supabase Data API key. See [Supabase connection options](https://supabase.com/docs/guides/database/connecting-to-postgres).

Both Postgres connection helpers require SSL and disable prepared statements with `prepare_threshold=0`. The business-data pool has a minimum size of 1, a maximum size of 4, and a 10-second acquisition timeout.

The application calls `load_dotenv()` from its normal entry-point file. For a terminal heredoc such as `uv run python -`, use `load_dotenv(dotenv_path=".env")` to avoid automatic file-discovery problems.

### 3. Create the private schema and ticket table

Run this SQL using the database owner in the Supabase SQL Editor. The `fox_insurance` schema is dedicated to this application and should remain outside the exposed Data API schemas.

```sql
CREATE SCHEMA IF NOT EXISTS fox_insurance;

REVOKE ALL ON SCHEMA fox_insurance
FROM PUBLIC, anon, authenticated;

CREATE TABLE IF NOT EXISTS fox_insurance.tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    department TEXT NOT NULL CHECK (
        department IN (
            'customer_account',
            'billing',
            'document_delivery',
            'technical_support',
            'policy_service'
        )
    ),
    subject TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN (
            'open',
            'in_progress',
            'waiting_for_customer',
            'resolved'
        )
    ),
    latest_update TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0)
);

CREATE INDEX IF NOT EXISTS tickets_customer_updated_idx
ON fox_insurance.tickets (customer_id, updated_at DESC, ticket_id);

ALTER TABLE fox_insurance.tickets ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE fox_insurance.tickets
FROM PUBLIC, anon, authenticated;
```

There is no customer-table foreign key yet because customer profiles still live in `records.py`. `CREATE TABLE IF NOT EXISTS` creates a missing table; it does not migrate an incompatible existing table.

### 4. Initialize checkpoint tables

Run this bootstrap command from the project root for a new database. Re-run it when a checkpoint package upgrade requires its database migrations. Normal application startup does not call `.setup()`.

```bash
uv run python - <<'PY'
from dotenv import load_dotenv
from customer_support_pilot.persistence import open_checkpointer

load_dotenv(dotenv_path=".env")

with open_checkpointer() as checkpointer:
    checkpointer.setup()

print("Checkpoint tables initialized.")
PY
```

The checkpointer sets `search_path` to `fox_insurance, pg_catalog` before initialization. It creates `checkpoint_migrations`, `checkpoints`, `checkpoint_blobs`, and `checkpoint_writes` in that schema.

After initialization, run:

```sql
ALTER TABLE fox_insurance.checkpoint_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE fox_insurance.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE fox_insurance.checkpoint_blobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE fox_insurance.checkpoint_writes ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON ALL TABLES IN SCHEMA fox_insurance
FROM PUBLIC, anon, authenticated;
```

The backend connection must have the required privileges. A database owner can bypass RLS; enabling RLS does not turn the hardcoded CLI employee into a database-authenticated identity. Dedicated runtime database roles and employee authentication remain future work. See [Supabase RLS documentation](https://supabase.com/docs/guides/database/postgres/row-level-security).

### 5. Seed tickets

```bash
uv run python -m customer_support_pilot.seed_tickets
```

The command inserts missing tickets from `records.py`. `ON CONFLICT (ticket_id) DO NOTHING` preserves existing tickets, including changes made through human review.

## Run and resume conversations

```bash
uv run customer-support-pilot
```

The application prints a conversation UUID and the command to resume it:

```bash
uv run customer-support-pilot --resume YOUR_CONVERSATION_UUID
```

| Command or input | Behavior |
| --- | --- |
| A support question | Invoke the agent with the current employee context |
| `/new` | Create a new conversation UUID and begin in triage |
| `exit` or `/exit` | Exit the normal chat loop |
| `later` during review | Exit with the original proposal still pending |
| `--resume UUID` at startup | Load the saved conversation for the current employee and access scope |

`/new` starts a different thread. It does not delete earlier checkpoints, change customer records, or change employee permissions. A greeting such as `Hello` does not automatically reset the department.

The terminal supports one synchronous interaction at a time. It does not yet accept a follow-up-message queue while a run or approval is active.

### Current employee scope

`main.py` supplies employee `FOX-E1001`, role `support_agent`, and access to `FOX-C1001` and `FOX-C1002`. Records exist for six customers, but the current employee can access only those two.

The internal thread ID combines the employee ID, a hash of the role and allowed customer IDs, and the conversation UUID. Changing that scope changes the thread key. The hash separates histories by scope; it is not authentication or encryption.

## How the LangChain pieces work

### Models and agent assembly

`models.py` uses the standard model initializer:

```python
model = init_chat_model(
    model=os.getenv("OPENAI_MODEL") or "gpt-6-luna",
    model_provider="openai",
    use_responses_api=True,
    reasoning_effort="low",
    timeout=30,
    max_retries=2,
)
```

`os.getenv` reads environment configuration. The fallback model is used when `OPENAI_MODEL` is missing or empty. Model transport retries are separate from business-action approval and database retry handling.

`agents.py` assembles the application with the current `create_agent` API:

```python
return create_agent(
    model=create_chat_model(),
    tools=ALL_TOOLS,
    system_prompt=BASE_PROMPT,
    state_schema=SupportState,
    context_schema=SupportContext,
    response_format=SupportResponse,
    middleware=build_support_middleware(),
    checkpointer=checkpointer,
)
```

### Messages and tool selection

The CLI wraps each normal question in `HumanMessage`. The model can answer directly or return an `AIMessage` containing tool calls. Tool names, docstrings, and argument schemas describe which operations are available. Greetings, capability questions, and clarifying questions may not need a tool.

Tool results become `ToolMessage` objects. Each result references its originating `tool_call_id`, allowing the model to associate the response with the correct request. A denial result is still a tool result: access is enforced by Python before the model explains it to the employee.

| Tool | Purpose |
| --- | --- |
| `lookup_customer` | Read an exact customer profile |
| `lookup_policies` | Read a customer's policy summaries |
| `lookup_billing` | Read invoices, paid amounts, and calculated balances |
| `lookup_tickets` | Read all customer tickets or one exact ticket belonging to the customer |
| `handoff_to_department` | Update conversation department state |
| `update_ticket` | Apply a reviewed ticket-status and note update when permissions and version match |

IDs are normalized with `.strip().upper()`: `"  fox-c1002  "` becomes `"FOX-C1002"`. Billing balances are calculated from integer cents. Policy summaries do not determine coverage for a particular loss.

### Runtime context versus agent state

| Runtime context | Agent state |
| --- | --- |
| Supplied by the application through `context=context` | Maintained by the agent and checkpointer |
| Employee ID, role, allowed customer IDs, repository dependency | Messages, active department, and middleware state |
| Available inside a tool through `runtime.context` | Available through `runtime.state` or a middleware request |
| Recreated when the application starts | Restored from Postgres for the same thread |

`context_schema=SupportContext` declares the expected context type. The actual values are constructed in `main.py`; declaring the schema does not populate employee details. The repository object is an injected service dependency, not a message sent to the model or a checkpointed database connection.

The frozen dataclass prevents reassignment of its fields. Its annotations do not replace the explicit authorization checks inside tools.

### Structured responses and update validation

`SupportResponse` contains `category`, `customer_id`, and `answer`. The CLI reads these fields from `output.value["structured_response"]` after an uninterrupted final result.

`TicketUpdateRequest` validates the proposed `customer_id`, `ticket_id`, `expected_version`, `new_status`, and `note`. It rejects unexpected fields, strips surrounding string whitespace, requires a positive integer version, restricts the status values, and limits the note to 1,000 characters.

The allowed ticket statuses are:

```text
open
in_progress
waiting_for_customer
resolved
```

Response categories are model-generated classifications. The active department is a separate state field. `claims` and `quote` are possible classification labels, but dedicated claim-decision and quote-issuance tools are not implemented.

### Single-agent handoffs and ticket routing

The department states are `triage`, `customer_account`, `billing`, `document_delivery`, `technical_support`, and `policy_service`. This is one dynamically configured agent, not a supervisor spawning independent specialist agents.

`handoff_to_department` returns a `Command` that updates `active_department` and adds a matching `ToolMessage`. Before the next model call, `configure_department` selects that department's prompt and tools.

For ticket lookups, `route_ticket_results` inspects only the latest batch of tool messages. Successfully retrieved tickets from one department select that department. A mixed-department list selects `customer_account`. Missing records and permission denials do not infer a department or change the active one. Older ticket messages do not reroute a new turn.

The routing hook sets department state in code; prompt instructions guide the final response category to match the retrieved-ticket context.

### Middleware and guardrails

The middleware list combines custom hooks with prebuilt controls:

| Middleware | Responsibility |
| --- | --- |
| `route_ticket_results` / `before_model` | Set the department from the latest retrieved ticket records |
| `configure_department` / `wrap_model_call` | Set the system prompt and available tools |
| `ModelCallLimitMiddleware` | Limit model calls to 6 per run |
| `ToolCallLimitMiddleware` | Limit tool calls to 4 per run and 20 per thread |
| `enforce_department_tools` / `wrap_tool_call` | Reject unavailable tools and batches mixing an update or handoff with another call |
| `HumanInTheLoopMiddleware` | Pause every `update_ticket` call for review |
| `ToolErrorMiddleware` | Handle connection/time-out errors from the selected lookup tools |

Call limits count calls, not employee messages. One question can need several calls, and an answer may need none. A tool run limit must not exceed its thread limit. When a processing limit blocks the run, the CLI directs the employee to `/new` or `/exit`.

Role and customer-scope checks are code-enforced. Prompt instructions additionally require accurate reporting, fresh ticket lookups before proposed updates, and treating record contents as data rather than instructions. These prompt instructions are not a complete prompt-injection defense or a substitute for tool authorization.

## Human approval workflow

Example request:

```text
Update ticket FOX-T4002 for FOX-C1002 to waiting_for_customer.
Set the note to: Awaiting customer confirmation of the invoice payment allocation.
```

The model retrieves the ticket and submits an update proposal. Before the tool executes, per-call HITL raises an interrupt. The application prints the proposal for review.

| Review choice | Behavior |
| --- | --- |
| `approve` | Execute the proposal as displayed |
| `edit` | Edit the proposed status and/or note, then display it again |
| `reject` | Skip the tool execution and return rejection feedback |
| `later` | Exit and retain the original pending proposal in Postgres |

At `Status [waiting_for_customer]:`, Enter keeps the displayed status. Enter at the note prompt keeps the proposed note. After editing, choose `approve` to submit the revised action. Customer ID, ticket ID, and expected version remain fixed in the review interface. Local edits are not saved until submitted; choosing `later` retains the original checkpointed proposal.

The CLI resumes the particular interrupt using an application command:

```python
invocation = Command(resume={pending.id: decision})
output = agent.invoke(
    invocation,
    config=config,
    context=context,
    version="v2",
)
```

With `version="v2"`, the result exposes `.interrupts` and `.value`. The CLI checks interrupts before reading the final structured response. Approval is a separate terminal review operation; the model cannot approve its own tool call by writing an approval message.

Choosing `later` closes the application. Run the printed `--resume` command to recover the pending review. Ordinary completed conversations can also be resumed. A failed unfinished run without a review interrupt is blocked from accepting new messages; the CLI does not implement general recovery for every failed node yet.

## Database consistency and error handling

`TicketRepository.update_if_version_matches` compares ownership and version in the same statement that performs the update:

```sql
UPDATE fox_insurance.tickets
SET status = %s,
    latest_update = %s,
    updated_at = CURRENT_TIMESTAMP,
    version = version + 1
WHERE customer_id = %s
  AND ticket_id = %s
  AND version = %s
RETURNING ticket_id, customer_id, department, subject,
          status, latest_update, updated_at, version;
```

Values are bound separately through Psycopg. A matching update returns the new row. No match returns `None`: the ticket might be missing, belong to another customer, or have a newer version. The tool reports `conflict_or_not_found` rather than claiming every failure is a version conflict.

Every successful update increments `version`. Two attempts using the same reviewed version cannot both update the row. Writers added later must follow the same version-increment convention. The tool rechecks employee permissions when it executes after approval.

A database connection failure during a write produces `unknown_outcome`, because the transaction may already have committed. The prompt tells the agent not to automatically retry. There is not yet a durable action receipt that identifies an earlier successful execution after such a failure. Version checking protects against stale overwrites; it is not a complete exactly-once execution or audit system.

Checkpoint deserialization explicitly allows `customer_support_pilot.schemas.SupportResponse` through `JsonPlusSerializer`. Runtime context and the repository connection are reconstructed by the application rather than restored as arbitrary checkpoint objects.

## Manual verification

Run the CLI after setup. The repository currently has no committed automated test suite; these are manual acceptance scenarios. Approve, edit, and reject have been exercised through the terminal. Restart recovery and concurrency should also be verified against the configured database.

| Scenario | Input or action | Expected result |
| --- | --- | --- |
| Customer lookup | `Look up FOX-C1002.` | Pacific Route Logistics LLC account |
| Policy lookup | `Show policies for FOX-C1002.` | Policies belonging to that customer |
| Billing lookup | `How much does FOX-C1002 owe?` | Balance from invoice records; current records calculate $1,260.00 |
| Ticket routing | `Show FOX-T4002 for FOX-C1002.` | Billing department and recorded ticket details |
| Ownership mismatch | `Show FOX-T4002 for FOX-C1001.` | No matching ticket under that customer |
| Permission denial | `Show tickets for FOX-C1003.` | Access denied for the configured employee |
| New conversation | Enter `/new` on its own line | New UUID and triage state |
| Topic handoff | `Now I need help signing into the customer portal.` | Technical-support department |
| Reject update | Request a ticket update, then choose `reject` | No database update or version increment |
| Edit update | Choose `edit`, revise the note, then `approve` | Revised note saved and version increments once |
| Restart review | Choose `later`, run printed resume command | Pending proposal appears again |
| Stale review | Change the ticket through another versioned write while review is pending, then approve | No stale overwrite; conflict/no-match result |
| Call limits | Continue until a configured call limit is reached | Explanatory message and `/new` or `/exit` guidance |

To inspect ticket changes in the SQL Editor:

```sql
SELECT ticket_id, customer_id, status, latest_update, version, updated_at
FROM fox_insurance.tickets
WHERE customer_id = 'FOX-C1002'
  AND ticket_id = 'FOX-T4002';
```

## Optional LangSmith tracing

`langsmith` is installed, but tracing is not enabled by application code. To enable environment-based tracing for a run, add these local settings and restart the application:

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=YOUR_LANGSMITH_API_KEY
LANGSMITH_PROJECT=fox-insurance-support
```

Tracing helps inspect model calls, tool execution, and latency. This optional configuration does not create evaluation datasets, automated evaluators, or an application audit ledger. See the [LangSmith tracing quickstart](https://docs.langchain.com/langsmith/observability-quickstart).

## Topics still to implement

These items distinguish the current implementation from the broader LangChain documentation menu and the planned support application.

| Area | Planned practice |
| --- | --- |
| Action ledger and audit records | Persist proposals, reviewer identity/decisions, attempts, and execution receipts; recognize successful retries |
| Employee authentication | Derive trusted identity and permissions from authenticated sessions; provision appropriate database roles |
| Additional database repositories | Move customer, policy, and invoice records into Postgres with ownership constraints and migrations |
| Streaming and event streaming | Deliver model tokens, tool progress, and agent state updates |
| Frontend overview and patterns | Cloudflare-hosted UI, Markdown messages, tool cards, and human-review controls |
| Headless tools and client actions | Open customer/order panels and copy drafts through explicit client actions |
| Message queues and reconnect | Queue follow-up messages during active runs; join and rejoin streams |
| Branching chat and time travel | Inspect historical checkpoints and branch a conversation through an explicit interface |
| Reasoning-token UI | Display supported reasoning summaries/metadata appropriately; token accounting is not an implemented UI feature |
| Generative UI | Controlled components first; compare declarative and open-ended approaches separately |
| Frontend integrations | Compare AI Elements, assistant-ui, CopilotKit, and OpenUI when selecting the UI integration |
| Retrieval | Document loading, chunking, embeddings, vector search, and grounded document answers; SQL record lookup alone is not a RAG pipeline |
| Long-term memory | Cross-conversation memory using a store; persistent conversation checkpoints alone do not implement this |
| MCP | Tool discovery, connections, and authentication through MCP adapters |
| Other multi-agent patterns | Subagents, skills, routers, and custom workflows; current handoffs use one agent |
| Expanded guardrails and context engineering | Input/output policies, sensitive-data handling, history trimming/summarization, and context selection |
| Testing and agent evaluations | Unit tests, database integration tests, approval/restart tests, and quality/safety evaluation datasets |
| Agent development tools | LangSmith Studio and Agent Chat UI integration |
| Production deployment and observability | Backend API, hosting, deployment configuration, tracing verification, monitoring, and operational recovery |
| Documentation maintenance | Review LangChain changelogs and design guidance before dependency upgrades; update `uv.lock` and verification results |

The next implementation milestone is the action ledger and audit trail, followed by automated verification of approval persistence and retry handling.
