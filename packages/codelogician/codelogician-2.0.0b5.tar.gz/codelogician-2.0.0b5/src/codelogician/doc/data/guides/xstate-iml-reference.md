----
title: XState-IML Pattern Reference
description: Comprehensive patterns for formalizing XState library applications.
order: 10
----

## Overview

This guide provides comprehensive patterns for translating XState TypeScript state machines into formal IML (Imandra Modeling Language) models for automated reasoning and verification.

---

## Core Translation Strategy

### The Three-Part Model Structure

Every IML translation consists of:

1. **Type Definitions** - States, Events, Context
2. **Step Function** - Pure state transition logic
3. **Verification** - Properties and test cases with `eval`

---

## Part 1: Type Definitions

### 1.1 State Types

**Simple States:**
```iml
type state =
  | CheckVisaStatus
  | HandleApprovedVisa
  | End
```

**States with Context (Config Pattern):**
```iml
type state =
  | Idle
  | Loading
  | Success

type config = {
  state: state;
  ctx: context;
}
```

**Hierarchical/Nested States:**
```iml
(* Substates as separate type *)
type checkout_substate =
  | CheckingOut
  | NotifyingLender

type state =
  | BookLendingRequest
  | CheckOutBook of checkout_substate  (* Parametrized constructor *)
  | End
```

**Pattern matching nested states:**
```iml
match current_state with
| CheckOutBook CheckingOut -> (* ... *)
| CheckOutBook NotifyingLender -> (* ... *)
```

### 1.2 Event Types

**Simple Events:**
```iml
type event =
  | VisaApprovedEvent
  | VisaRejectedEvent
  | NoEvent  (* Timeout modeled as explicit event *)
```

**Events with Payloads (Record Style):**
```iml
type event =
  | BookLendingRequest of {
      book_title: string;
      book_id: string;
      lender: lender_record;
    }
  | Success of int
```

**Events with Payloads (Tuple Style):**
```iml
type event =
  | BookLendingRequest of (string * string * lender_record)
  (* book_id, title, lender *)
```

**Both styles are valid!** Record style is more self-documenting; tuple style is more concise.

**Event Categories:**
```iml
type event =
  (* External/User Events *)
  | VisaApprovedEvent
  | HoldBook

  (* Invoke/Actor Completion Events *)
  | WorkflowComplete
  | BookStatusFetched of book_status

  (* Timer/Delay Events *)
  | TimerExpired
  | TwoWeeksPassed
```

### 1.3 Context Types

**Empty Context (when XState context is empty or unused):**
```iml
type context = unit
```

**Record Context:**
```iml
type context = {
  book: book_record option;      (* null -> option *)
  lender: lender_record option;
  retry_count: int;
  error_message: LString.t option;
}
```

**Type Mappings:**
- TypeScript `string` → IML `string` (native) or `LString.t` (logic mode)
- TypeScript `number` → IML `int` or `real`
- TypeScript `T | null` → IML `'a option`
- TypeScript `T[]` → IML `'a list`
- TypeScript object/interface → IML record type

### 1.4 Combined State + Context

**Pattern 1: Separate state and context in config:**
```iml
type config = {
  state: state;
  ctx: context;
}
```

**Pattern 2: Single machine_state type:**
```iml
type machine_state = {
  state: state;
  context: context;
}
```

**Pattern 3: State with embedded phase:**
```iml
type state = {
  book: book_record option;
  lender: lender_record option;
  phase: phase;  (* The actual state node *)
}

and phase =
  | Idle
  | BookStatusQueried
  | End
```

All patterns are valid! Choose based on preference.

---

## Part 2: State Transition Function

### 2.1 Basic Step Function Signatures

**Pure state transition (no context):**
```iml
let step (s: state) (e: event) : state =
  match (s, e) with
  | (State1, Event1) -> State2
  | _ -> s
```

**With context (config pattern):**
```iml
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (State1, Event1) -> { state = State2; ctx = c.ctx }
  | _ -> c
```

**With separate state and context:**
```iml
let step (st: state) (ctx: context) (ev: event) : (state * context) =
  match (st, ev) with
  | (State1, Event1) -> (State2, ctx)
  | _ -> (st, ctx)
```

**With action logging (useful for debugging):**
```iml
let step (st: state) (ev: event) : (state * string list) =
  match (st, ev) with
  | (State1, Event1) -> (State2, ["action1"; "action2"])
  | _ -> (st, [])
```

### 2.2 Handling XState "invoke" - Critical Pattern!

XState's `invoke` represents async operations. Model completion as explicit events:

**Pattern 1: Explicit completion event**
```iml
(* XState *)
HandleApprovedVisa: {
  invoke: {
    src: 'handleApprovedVisaWorkflowID',
    onDone: 'End'
  }
}

(* IML - Completion as explicit event *)
type event =
  | VisaApprovedEvent
  | WorkflowComplete  (* Models onDone *)

let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (CheckVisaStatus, VisaApprovedEvent) ->
      { state = HandleApprovedVisa; ctx = c.ctx }
  | (HandleApprovedVisa, WorkflowComplete) ->  (* onDone *)
      { state = End; ctx = c.ctx }
```

**Pattern 2: Wildcard (any event completes invoke)**
```iml
let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (HandleApprovedVisa, _) ->  (* Any event completes *)
      let ctx' = handleApprovedVisaWorkflowID c.ctx in
      { state = End; ctx = ctx' }
```

**Pattern 3: Invoke with result/payload**
```iml
(* XState *)
'Get Book Status': {
  invoke: {
    src: 'Get status for book',
    onDone: {
      target: 'Book Status Decision',
      actions: assign({
        book: ({ event }) => ({ ...event.output.status })
      })
    }
  }
}

(* IML - Model result as event payload *)
type event =
  | BookStatusFetched of book_status  (* onDone with result *)

let step (s: state) (e: event) : state =
  match (s.state, e) with
  | (GetBookStatus, BookStatusFetched status) ->
      let updated_book = { s.book with status = status } in
      { s with book = Some updated_book; state = BookStatusDecision }
```

**Opaque Functions for Invoke Actions:**
```iml
(* Abstract representation of async workflow *)
let handleApprovedVisaWorkflowID (ctx: context) : context =
  ctx  (* Pure function, no actual work *)

(* Or fully opaque: *)
let handleRejectedVisaWorkflow : context -> context = () [@@opaque]
```

### 2.3 Handling XState "after" (Delays/Timeouts)

Model timeouts as explicit events:

```iml
(* XState *)
SleepTwoWeeks: {
  after: {
    PT2W: { target: 'Get Book Status' }
  }
}

(* IML - Timeout as explicit event *)
type event =
  | TwoWeeksPassed  (* or TimerExpired, EvTimerTwoWeeksExpired *)

let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (SleepTwoWeeks, TwoWeeksPassed) ->
      { state = GetBookStatus; ctx = c.ctx }
```

**Root-level timeout:**
```iml
(* XState: Timeout at machine level *)
after: {
  PT30D: { target: '.CancelOrder' }
}

(* IML: Check from any state *)
let step (c: config) (e: event) : config =
  match (c.state, e) with
  (* Regular transitions... *)
  | (_, TimeoutEvent) -> { state = CancelOrder; ctx = c.ctx }
  (* Or explicitly from specific states *)
  | (StartNewOrder, TimeoutEvent) -> { state = CancelOrder; ctx = c.ctx }
  | (WaitForConfirmation, TimeoutEvent) -> { state = CancelOrder; ctx = c.ctx }
```

### 2.4 Handling XState "always" Transitions

XState's `always` transitions are eventless. Two approaches:

**Approach 1: Inline Decision Logic**
Fold the `always` logic into the transition leading to it:

```iml
(* XState *)
'Book Status Decision': {
  always: [
    { guard: ({ context }) => context.book.status === 'onloan',
      target: 'Report Status To Lender' },
    { guard: ({ context }) => context.book.status === 'available',
      target: 'Check Out Book' },
    { target: 'End' }
  ]
}

(* IML - Inline in previous state *)
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (GetBookStatus, BookStatusFetched status) ->
      let updated_context = (* update context *) in
      (* Inline the "always" decision here *)
      (match status with
       | OnLoan -> { state = ReportStatusToLender; ctx = updated_context }
       | Available -> { state = CheckOutBook; ctx = updated_context }
       | Unknown -> { state = End; ctx = updated_context })
```

**Approach 2: Automatic Advancement Function**
Separate function that automatically advances through transient states:

```iml
let rec advance_auto (st: state) (ctx: context) : (state * context) =
  match st with
  | BookStatusDecision ->
      (match ctx.book_opt with
       | Some { status = OnLoan; _ } ->
           advance_auto ReportStatusToLender ctx
       | Some { status = Available; _ } ->
           advance_auto (CheckOutBook CheckingOut) ctx
       | _ -> advance_auto End ctx)
  | CheckOutBook CheckoutEnd ->
      advance_auto End ctx
  | _ -> (st, ctx)  (* No automatic transition *)

let step (st: state) (ctx: context) (ev: event) : (state * context) =
  let (st', ctx') = step_once st ctx ev in
  advance_auto st' ctx'  (* Automatically advance through transient states *)
```

### 2.5 Context Updates (XState "assign" Actions)

**Record Update Syntax:**
```iml
(* Single field update - use 'with' *)
{ ctx with retry_count = ctx.retry_count + 1 }

(* Multiple field updates - use 'with' *)
{ ctx with
    retry_count = ctx.retry_count + 1;
    error_message = Some {l|Error occurred|l} }

(* Nested update *)
let updated_book = match ctx.book with
  | Some b -> Some { b with status = Available }
  | None -> None
in
{ ctx with book = updated_book }
```

**IMPORTANT: When to use 'with' vs not:**
```iml
type context = { field1: int; field2: string }

(* ✅ Updating SOME fields → use 'with' *)
{ ctx with field1 = 42 }

(* ✅ Updating ALL fields → DON'T use 'with' *)
{ field1 = 42; field2 = "hello" }

(* ❌ ERROR: Redundant 'with' when all fields defined *)
{ ctx with field1 = 42; field2 = "hello" }  (* Error! *)

(* Special case: Single-field context *)
type context = { bids: int list }

(* ✅ Correct - no 'with' needed *)
{ bids = new_bids }

(* ❌ ERROR: 'with' is redundant for single-field record *)
{ ctx with bids = new_bids }  (* Error: All fields defined! *)
```

**Helper Functions for Complex Updates:**
```iml
let increment_attempts (ctx: context) : context =
  { ctx with attempts = ctx.attempts + 1 }

let set_error (ctx: context) (msg: LString.t) : context =
  { ctx with error_msg = Some msg }

(* Chain updates *)
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (Loading, Failure msg) ->
      let ctx' = c.ctx |> increment_attempts |> set_error msg in
      { state = Error; ctx = ctx' }
```

### 2.6 Guards (Conditional Transitions)

**Inline Guards:**
```iml
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (Error, Retry) ->
      if c.ctx.retry_count < 3 then
        { state = Loading; ctx = reset_context c.ctx }
      else
        c  (* Stay in error state *)
```

**Guard Functions:**
```iml
let can_retry (ctx: context) : bool =
  ctx.retry_count < 5

let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (Error, Retry) when can_retry c.ctx ->
      { state = Loading; ctx = c.ctx }
  | (Error, Retry) ->
      c  (* Guard failed *)
```

**Multiple Guards (XState array of transitions):**
```iml
(* XState *)
FAILURE: [
  {
    target: 'error',
    guard: ({ context }) => context.retryCount >= 3,
    actions: assign({ errorMessage: (_, event) => event.message })
  },
  {
    target: 'loading',
    actions: assign({ retryCount: ({ context }) => context.retryCount + 1 })
  }
]

(* IML - Order matters! First match wins *)
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (Loading, Failure msg) when c.ctx.retry_count >= 3 ->
      { state = Error; ctx = set_error c.ctx msg }
  | (Loading, Failure msg) ->  (* Default case *)
      { state = Loading; ctx = increment_retry c.ctx msg }
```

### 2.7 Final States

```iml
type state =
  | Active
  | Done      (* final *)
  | Failed    (* final *)

let is_final (s: state) : bool =
  match s with
  | Done -> true
  | Failed -> true
  | _ -> false

(* Final states are terminal - no transitions out *)
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (Done, _) -> c  (* Stay in Done *)
  | (Failed, _) -> c  (* Stay in Failed *)
  | (* other transitions *)
```

### 2.8 Wildcard/Default Transitions

```iml
let step (c: config) (e: event) : config =
  match (c.state, e) with
  | (State1, Event1) -> { state = State2; ctx = c.ctx }
  | (State2, Event2) -> { state = State3; ctx = c.ctx }
  (* ... *)
  | _ -> c  (* No valid transition - stay in current state *)
```

---

## Part 3: Initial State and Running Workflows

### 3.1 Initial State

```iml
let initial_context : context = {
  book = None;
  lender = None;
  retry_count = 0;
}

let initial_state : config = {
  state = BookLendingRequest;
  ctx = initial_context;
}

(* Or with unit context *)
let init : config = { state = CheckVisaStatus; ctx = () }
```

### 3.2 Running Event Sequences

**Recommended: List.fold_left (implicit recursion)**
```iml
let run (c: config) (evs: event list) : config =
  List.fold_left step c evs
```

**With accumulated logs (using fold_left with tuple):**
```iml
let run_with_logs (c: config) (evs: event list) : (config * string list) =
  List.fold_left
    (fun (cfg, logs) ev ->
      let (cfg', acts) = step cfg ev in
      (cfg', List.append logs acts))
    (c, [])
    evs
```

**NOT Recommended: Explicit recursion**
```iml
(* Avoid this pattern - use fold_left instead *)
let rec run (c: config) (evs: event list) : config =
  match evs with
  | [] -> c
  | e :: rest -> run (step c e) rest
```

---

## Part 4: Verification Properties

### 4.1 Bounded Verification (Recommended Approach)

**For most state machines, use bounded verification with explicit event parameters.**

Instead of quantifying over all possible event sequences, enumerate events equal to the number of event types. This approach finds counterexamples quickly and is sufficient for most verification needs.

```iml
(* Count your event type variants - if you have 10, use 10 parameters *)
type event =
  | Event1
  | Event2
  (* ... *)
  | Event10  (* 10 total variants *)

(* ✅ RECOMMENDED: Bounded verification *)
verify (fun ev1 ev2 ev3 ev4 ev5 ev6 ev7 ev8 ev9 ev10 ->
  let final = run init [ev1; ev2; ev3; ev4; ev5; ev6; ev7; ev8; ev9; ev10] in
  safety_property final)

(* ❌ AVOID: Unbounded verification *)
verify (fun (events : event list) ->
  let final = run init events in
  safety_property final)
```

**Rule:** Number of explicit parameters = number of variants in your `event` type.

**When bounded verification fails:**
1. Add helper lemma with `[@@disable]` and `[@@rewrite]`:
   ```iml
   theorem safety_preserved c events =
     safety_property c ==> safety_property (run c events)
   [@@by auto] [@@disable step, safety_property]

   verify (fun events -> safety_property (run init events))
   [@@by [%use safety_preserved init events] @> auto]
   ```

2. Define and prove invariants separately:
   ```iml
   let invariant (c: config) : bool =
     inv_1 c && inv_2 c && inv_3 c

   theorem invariant_holds_initially () =
     invariant init

   theorem invariant_implies_safety c =
     invariant c ==> safety_property c
   ```

### 4.2 Property Patterns

**Reachability:**
```iml
let reaches_end (evs: event list) : bool =
  let final = run_events initial_state evs in
  final.state = End
```

**State Invariants:**
```iml
let count_non_negative (c: config) : bool =
  c.ctx.count >= 0

let book_implies_lender (c: config) : bool =
  match c.ctx.book with
  | Some _ -> Option.is_some c.ctx.lender
  | None -> true
```

**Transition Properties:**
```iml
let available_book_leads_to_checkout (c: config) : bool =
  match c.state with
  | GetBookStatus ->
      let c' = step c (BookStatusFetched Available) in
      (match c'.state with
       | CheckOutBook _ -> true
       | _ -> false)
  | _ -> true  (* Property only applies to GetBookStatus *)
```

**Workflow Properties:**
```iml
let prop_happy_path () : bool =
  let workflow = [
    BookLendingRequest ("id", "title", test_lender);
    BookStatusFetched Available;
    CheckoutDone;
    NotifyDone;
  ] in
  (run_events initial_state workflow).state = End
```

### 4.3 Using `eval` for Testing

```iml
(* Test individual transitions *)
let s1 = step initial_state (BookLendingRequest ("42", "Title", lender))
eval (s1.state = GetBookStatus)

(* Test workflow paths *)
let happy_path = run_events initial_state [
  BookLendingRequest ("42", "Title", lender);
  BookStatusFetched Available;
  CheckoutDone;
  NotifyDone;
]
eval (happy_path.state = End)

(* Test properties *)
eval (prop_happy_path ())
eval (reaches_end [Event1; Event2; Event3])
eval (count_non_negative happy_path)
```

---

## Translation Checklist

- [ ] **States**: Define `type state` with all state nodes
- [ ] **Events**: Define `type event` with all events and payloads
  - [ ] User events
  - [ ] Invoke completion events (`onDone` → explicit events)
  - [ ] Timer/delay events (`after` → explicit events)
- [ ] **Context**: Define `type context` (use `unit` if empty)
- [ ] **Config/Machine State**: Combine state + context
- [ ] **Initial State**: Define `initial_state` with initial context
- [ ] **Step Function**: Implement pure transition logic
  - [ ] Pattern match on (state, event)
  - [ ] Handle invoke completions
  - [ ] Handle timeouts
  - [ ] Inline or separately handle `always` transitions
  - [ ] Apply guards with `if` or `when`
  - [ ] Update context with record syntax
  - [ ] Wildcard case: `| _ -> current_state`
- [ ] **Helper Functions**: Guards, actions, opaque functions
- [ ] **Run Function**: Fold over event list
- [ ] **Properties**: Define verification properties
- [ ] **Eval Statements**: Test workflows and properties
- [ ] **Documentation**: Comment any omitted XState features

---

## Common Patterns Reference

### Invoke Patterns
| XState | IML |
|--------|-----|
| `invoke: { src: 'foo', onDone: 'Next' }` | Explicit event: `FooDone` |
| `invoke: { src: 'foo', onError: 'Error' }` | Explicit event: `FooError of LString.t` |
| `invoke` with output | Event payload: `FooResult of result_type` |

### After/Delay Patterns
| XState | IML |
|--------|-----|
| `after: { DELAY: 'Next' }` | Event: `TimerExpired` or `DelayPassed` |
| Root-level `after` | Match from multiple states or use wildcard |

### Always Patterns
| XState | IML |
|--------|-----|
| `always: [{ guard, target }]` | Inline decision in previous state OR `advance_auto` function |

### Context Update Patterns
| XState | IML |
|--------|-----|
| `assign({ field: value })` | `{ ctx with field = value }` |
| `assign({ field: (ctx) => ctx.field + 1 })` | `{ ctx with field = ctx.field + 1 }` |
| Multiple assigns | Chain with `|>` or helper functions |

---

## What to Omit

1. **Side Effects**: `console.log`, API calls, DOM manipulation
2. **XState Internal Metadata**: `.id`, `.meta`, `.tags`
3. **Development-Only Features**: `devTools`, logging actions
4. **Spawn/Actors**: Dynamic actor creation (unless modeled abstractly)
5. **History States**: Model explicitly in context if needed
6. **Entry/Exit Actions**: Fold into transition or model as events

---

## Best Practices

1. **Use List.fold_left for Run Functions**: Required for bounded verification, better for automated reasoning
2. **Use Bounded Verification**: Match number of explicit parameters to event type count
3. **Prefer Simple Patterns**: Use record events over tuples for clarity
4. **Model Invoke Explicitly**: Always use explicit completion events
5. **Unit Context for Stateless Machines**: Don't create unnecessary fields
6. **Guards as Functions**: Extract complex conditions
7. **Comment Mappings**: Note which IML construct maps to which XState feature
8. **Test Extensively**: Use `eval` for multiple workflow paths before formal verification
9. **Properties First**: Define key correctness properties with bounded verification first
10. **Opaque for External**: Use `[@@opaque]` for external/unavailable operations
