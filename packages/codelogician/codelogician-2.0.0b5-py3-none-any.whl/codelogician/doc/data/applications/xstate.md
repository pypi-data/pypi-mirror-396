----
title: Formalizing XState applications
description: Tutorial and recommendations for formalizing XState library applications and reasoning about them.
order: 3
----

## Output Structure

```iml
(* ========================================= *)
(* [Machine Name] - IML Formalization *)
(* ========================================= *)

(* === Type Definitions === *)

(* States *)
type state =
  | State1
  | State2
  | End

(* Events *)
type event =
  | Event1
  | Event2 of payload_type
  | CompletionEvent  (* For invoke onDone *)

(* Context *)
type context = {
  field1: type1;
  field2: type2 option;
}
(* Or: type context = unit  if no context needed *)

(* Machine Configuration *)
type config = {
  state: state;
  ctx: context;
}

(* === Initial State === *)

let initial_context : context = (* ... *)

let init : config = {
  state = InitialState;
  ctx = initial_context;
}

(* === Transition Function === *)

let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (State1, Event1) -> { state = State2; ctx = c.ctx }
  (* ... more transitions ... *)
  | _ -> c  (* no valid transition *)

(* === Run Events === *)

let run (c: config) (evs: event list) : config =
  List.fold_left step c evs

(* === Properties === *)

let reaches_end (evs: event list) : bool =
  (run init evs).state = End

(* === Eval Examples === *)

eval (run init [Event1; Event2])
eval (reaches_end [Event1; Event2])
```

## Key Translation Rules

### 1. **Invoke/Async Operations → Explicit Completion Events**

XState `invoke` blocks with `onDone` become explicit events:

```typescript
// XState
HandleApprovedVisa: {
  invoke: {
    src: 'handleApprovedVisaWorkflowID',
    onDone: 'End'
  }
}
```

```iml
(* IML *)
type event =
  | VisaApprovedEvent
  | WorkflowComplete  (* Models onDone *)

let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (HandleApprovedVisa, WorkflowComplete) ->
      { state = End; ctx = c.ctx }
```

### 2. **After/Delays → Explicit Timeout Events**

```typescript
// XState
SleepTwoWeeks: {
  after: {
    PT2W: { target: 'GetBookStatus' }
  }
}
```

```iml
(* IML *)
type event =
  | TwoWeeksPassed  (* or TimerExpired *)

let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (SleepTwoWeeks, TwoWeeksPassed) ->
      { state = GetBookStatus; ctx = c.ctx }
```

### 3. **Always Transitions → Inline Decision Logic**

```typescript
// XState
'Book Status Decision': {
  always: [
    { guard: ({ context }) => context.book.status === 'onloan',
      target: 'ReportStatusToLender' },
    { guard: ({ context }) => context.book.status === 'available',
      target: 'CheckOutBook' }
  ]
}
```

```iml
(* IML - Inline in previous state's transition *)
let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (GetBookStatus, BookStatusFetched status) ->
      let updated_ctx = (* update context *) in
      (* Inline the "always" decision *)
      (match status with
       | OnLoan -> { state = ReportStatusToLender; ctx = updated_ctx }
       | Available -> { state = CheckOutBook; ctx = updated_ctx })
```

### 4. **Assign Actions → Record Update Syntax**

```typescript
// XState
actions: assign({
  retryCount: ({ context }) => context.retryCount + 1,
  errorMessage: (_, event) => event.message
})
```

```iml
(* IML *)
let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (Loading, Failure msg) ->
      { state = Error;
        ctx = { c.ctx with
                  retry_count = c.ctx.retry_count + 1;
                  error_message = Some msg } }
```

**CRITICAL: When to use 'with':**
```iml
(* ✅ Use 'with' when updating SOME fields *)
{ ctx with field1 = new_value }

(* ✅ DON'T use 'with' when defining ALL fields *)
{ field1 = v1; field2 = v2 }  (* Correct *)
{ ctx with field1 = v1; field2 = v2 }  (* ERROR: Redundant! *)

(* ❌ Single-field context: never use 'with' *)
type context = { bids: int list }
{ bids = new_bids }  (* Correct *)
{ ctx with bids = new_bids }  (* ERROR! *)
```

### 5. **Guards → When Clauses or If Conditions**

```typescript
// XState
RETRY: {
  target: 'loading',
  guard: ({ context }) => context.retryCount < 3
}
```

```iml
(* IML - Pattern 1: when clause *)
let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (Error, Retry) when c.ctx.retry_count < 3 ->
      { state = Loading; ctx = c.ctx }
  | (Error, Retry) -> c  (* Guard failed *)

(* Pattern 2: if condition *)
let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (Error, Retry) ->
      if c.ctx.retry_count < 3 then
        { state = Loading; ctx = c.ctx }
      else
        c
```

### 6. **Nested/Hierarchical States → Parametrized Constructors**

```typescript
// XState
'Check Out Book': {
  initial: 'CheckingOutBook',
  states: {
    'CheckingOutBook': { /* ... */ },
    'NotifyingLender': { /* ... */ }
  }
}
```

```iml
(* IML *)
type checkout_substate =
  | CheckingOut
  | NotifyingLender

type state =
  | BookLendingRequest
  | CheckOutBook of checkout_substate
  | End

let step (c: config) (ev: event) : config =
  match (c.state, ev) with
  | (CheckOutBook CheckingOut, CheckoutDone) ->
      { state = CheckOutBook NotifyingLender; ctx = c.ctx }
  | (CheckOutBook NotifyingLender, NotifyDone) ->
      { state = End; ctx = c.ctx }
```

### 7. **Type Conversions**

| TypeScript | IML |
|------------|-----|
| `string` | `string` or `LString.t` |
| `number` | `int` or `real` |
| `T \| null` | `'a option` |
| `T[]` | `'a list` |
| `boolean` | `bool` |
| Object/Interface | Record type |

### 8. **Context Patterns**

- **Empty context**: Use `type context = unit`
- **With data**: Use record type with `option` for nullable fields
- **Never use functions** in context (IML restriction)

---

## Important Notes

1. **Invoke = Explicit Events**: Always model `invoke` with `onDone` as explicit completion events
2. **After = Timeout Events**: Model delays/timers as explicit events (e.g., `TimeoutEvent`, `TwoWeeksPassed`)
3. **Always = Inline Logic**: Fold `always` transitions into the previous state's transition
4. **Run Function**: Use `List.fold_left step init events` (implicit recursion) instead of explicit recursion
5. **Empty Context**: Use `type context = unit` when XState has no context or it's unused
6. **Nested States**: Use parametrized constructors for hierarchical states
7. **Guards**: Use `when` clauses or `if` conditions within match cases
8. **Final States**: Mark as terminal by returning same state for any event
9. **Properties**: Write at least one reachability property and workflow test
10. **Eval**: Include multiple `eval` statements testing different paths (they act as smoke tests)

---

## Translation Process:

### Step 1: Write the IML Translation
Write the complete IML model following all patterns and rules above.

### Step 2: Self-Verification Checklist
**CRITICAL: Before returning your output, review it against this checklist:**

#### Type Definitions
- [ ] All XState states → IML state variants
- [ ] All XState events → IML event variants
- [ ] All invoke.onDone → Explicit completion events
- [ ] All after delays → Explicit timeout events
- [ ] TypeScript `T | null` → IML `'a option` (never use null!)
- [ ] Context uses records with option for nullable fields

#### Record Updates (Common Error!)
- [ ] **Single-field context**: Use `{ field = value }` (NO 'with')
- [ ] **Multi-field partial update**: Use `{ ctx with field = value }`
- [ ] **Multi-field full update**: Use `{ f1 = v1; f2 = v2 }` (NO 'with')
- [ ] Check EVERY context update follows this rule!

#### Step Function
- [ ] Pattern matches on (state, event) or state.node
- [ ] Always transitions are inlined (no transient state)
- [ ] Guards use `when` or `if` conditions
- [ ] Final states return same state: `| End, _ -> state`
- [ ] Wildcard case included: `| _ -> current_state`

#### Completeness
- [ ] Initial state and initial context defined
- [ ] Run function uses `List.fold_left` (preferred over explicit recursion)
- [ ] At least 2-3 workflow examples with `eval` (to act as smoke tests)
- [ ] At least 1 verification property
- [ ] Comments explain non-obvious mappings


## Property Categories

**Note:** These categories are XState-specific patterns for state machine verification.

### 1. Reachability - States can be reached
```iml
theorem reaches_end_from_valid_event event =
  List.mem event [Event1; Event2; Event3] ==> (run init [event]).state = End
[@@by auto]

instance (fun events -> (run init events).state = End && List.length events <= 3)
```

### 2. Safety - Bad states never occur
```iml
(* Final states are stable *)
theorem final_state_stable event =
  (step {state = End; ctx = init.ctx} event).state = End
[@@by auto]

(* Context invariants - bounded verification (RECOMMENDED) *)
verify (fun ev1 ev2 ev3 ev4 ev5 ev6 ev7 ev8 ev9 ev10 ->
  let final = run init [ev1; ev2; ev3; ev4; ev5; ev6; ev7; ev8; ev9; ev10] in
  safety_property final)

(* Alternative: Helper lemma for unbounded verification *)
theorem safety_preserved c events =
  safety_property c ==> safety_property (run c events)
[@@by auto] [@@disable step, safety_property]

verify (fun events -> safety_property (run init events))
[@@by [%use safety_preserved init events] @> auto]
```

### 3. Determinism - Consistent behavior
```iml
theorem deterministic events =
  (run init events).state = (run init events).state
[@@by auto]
```

### 4. Completeness - No deadlocks
```iml
theorem all_valid_paths_complete event =
  List.mem event [Event1; Event2; Event3] ==>
  is_final (run init [event]).state
[@@by auto]
```

### 5. Guards - Conditionals work correctly
```iml
theorem guard_blocks_when_limit_reached ctx =
  ctx.retry_count >= 3 ==>
  (step {state = ErrorState; ctx = ctx} RetryEvent).state = ErrorState
[@@by auto]

theorem guard_allows_when_under_limit ctx =
  ctx.retry_count < 3 ==>
  (step {state = ErrorState; ctx = ctx} RetryEvent).state = LoadingState
[@@by auto]
```

### 6. Invoke - Async operations complete
```iml
theorem invoke_completes event =
  (step {state = HandleApproved_Invoke; ctx = init.ctx} event).state = End
[@@by auto]
```

---

## How to Write Properties

### Step 1: Identify which properties apply to your machine

- Has final states? → Safety properties (#2)
- Has invoke states? → Invoke properties (#6)
- Has context? → Context invariants (#2)
- Has guards? → Guard properties (#5)
- Multiple paths? → Completeness (#4)

### Step 2: Always include these core properties

```iml
(* Import your model first *)
[@@@import "machine.iml"]
open Machine

(* Reachability *)
theorem valid_path_exists () =
  (run init [Event1; Event2]).state = End
[@@by auto]

(* Safety - bounded verification *)
theorem final_state_stable event =
  (step {state = End; ctx = init.ctx} event).state = End
[@@by auto]

verify (fun ev1 ev2 ev3 ->
  safety_property (run init [ev1; ev2; ev3]))
```

### Step 3: Test with `eval` before formal verification

```iml
eval (run init [Event1; Event2])
eval ((run init [Event1; Event2]).state = End)
eval (step {state = End; ctx = ()} Event1)
```

### Step 4: Choose verification approach

- **Start with bounded verification** - Use explicit event parameters equal to event type count
- **If bounded fails** - Add helper lemmas with `[@@disable]` and `[@@rewrite]`
- **For theorems** - Use `[@@by auto]` as default strategy
- **For complex properties** - Define and prove invariants separately

---

## Template

```iml
(* ========================================= *)
(* Verification Goals for [Machine Name]    *)
(* ========================================= *)

(* === IMPORT MODEL === *)
[@@@import "machine_name.iml"]
open Machine_name

(* === REACHABILITY === *)
theorem happy_path_reaches_end () =
  (run init [Event1; Event2]).state = End
[@@by auto]

instance (fun events ->
  (run init events).state = End && List.length events <= 5)

(* === SAFETY === *)
theorem final_states_stable event =
  (step {state = End; ctx = init.ctx} event).state = End
[@@by auto]

(* Bounded verification - adjust number of events to match your event type count *)
verify (fun ev1 ev2 ev3 ev4 ev5 ->
  (run init [ev1; ev2; ev3; ev4; ev5]).ctx.counter >= 0)

(* === DETERMINISM === *)
theorem deterministic events =
  (run init events).state = (run init events).state
[@@by auto]

(* === COMPLETENESS === *)
theorem all_valid_events_complete event =
  List.mem event [Event1; Event2] ==> is_final (run init [event]).state
[@@by auto]

(* === GUARDS (if applicable) === *)
theorem guard_blocks ctx =
  ctx.retry_count >= 5 ==>
  (step {state = ErrorState; ctx = ctx} RetryEvent).state = ErrorState
[@@by auto]

(* === INVOKE (if applicable) === *)
theorem invoke_completes event =
  (step {state = InvokeState; ctx = init.ctx} event).state = NextState
[@@by auto]

(* === DOMAIN-SPECIFIC === *)
theorem book_available_leads_to_checkout () =
  match (run init [RequestBook; StatusFetched Available]).state with
  | CheckOutBook _ -> true
  | _ -> false
[@@by auto]

(* === HELPER LEMMAS (if needed) === *)
(* Use [@@rewrite] to install as rewrite rules for main theorems *)
lemma context_increments_correctly ctx event =
  (step {state = ProcessingState; ctx = ctx} event).ctx.counter =
  ctx.counter + 1
[@@by auto] [@@rewrite]

(* === TEST EVALUATIONS === *)
eval (run init [Event1; Event2])
eval ((run init [Event1]).state = End)
```

---

## Tips

1. **Use bounded verification** - Match number of parameters to event type count
2. **Import your model** - Use `[@@@import "file.iml"]` at the top of your verification file
3. **Use `eval` first** - Test properties before attempting formal proofs
4. **Start with `[@@by auto]`** for theorems - It's the most common proof strategy
5. **Use helper predicates** - `let is_final (s : state) = ...`
6. **Name descriptively** - `theorem retry_limit_works` not `theorem prop1`
7. **Handle options carefully** - Pattern match on `Some`/`None`
8. **Use implication** - `precondition ==> postcondition`
9. **When bounded fails** - Try helper lemmas with `[@@disable]` and `[@@rewrite]`
10. **Check proof output** - When auto fails, look at checkpoints to find needed lemmas
