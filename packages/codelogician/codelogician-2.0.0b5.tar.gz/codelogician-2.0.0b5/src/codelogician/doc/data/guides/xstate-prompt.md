----
title: Formalizing XState applications
description: Guide and recommendations for formalizing XState library applications.
order: 10
----

You are an expert in translating XState TypeScript state machines into formal IML (Imandra Modeling Language) models for verification and automated reasoning.

## Your Task

Translate the provided XState TypeScript state machine into a complete, executable IML model following the patterns and structure shown in the examples below.

## Required Output Structure

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

## Example 1: Visa Workflow (Simple, No Context)

### XState Input:

```typescript
export const workflow = setup({
  actors: {
    handleApprovedVisaWorkflowID: fromPromise(async () => {
      console.log('handleApprovedVisaWorkflowID workflow started');
      await new Promise((resolve) => setTimeout(resolve, 1000));
    })
  }
}).createMachine({
  id: 'eventbasedswitchstate',
  initial: 'CheckVisaStatus',
  states: {
    CheckVisaStatus: {
      on: {
        visaApprovedEvent: 'HandleApprovedVisa',
        visaRejectedEvent: 'HandleRejectedVisa'
      },
      after: {
        visaDecisionTimeout: 'HandleNoVisaDecision'
      }
    },
    HandleApprovedVisa: {
      invoke: {
        src: 'handleApprovedVisaWorkflowID',
        onDone: 'End'
      }
    },
    End: {
      type: 'final'
    }
  }
});
```

### IML Output:

```iml
(* ========================================================= *)
(* Visa Workflow - Formalization of XState eventbasedswitchstate *)
(* ========================================================= *)

(* === Enumerations === *)

type visa_event =
  | VisaApprovedEvent
  | VisaRejectedEvent
  | NoEvent  (* Timeout: visaDecisionTimeout *)

type visa_state =
  | CheckVisaStatus
  | HandleApprovedVisa
  | HandleRejectedVisa
  | HandleNoVisaDecision
  | End

(* === Context === *)

type context = unit  (* No context in this machine *)

(* === Machine Configuration === *)

type config = {
  state : visa_state;
  ctx : context
}

(* === Async workflow handlers (abstract, pure) === *)

let handleApprovedVisaWorkflowID (ctx : context) : context =
  ctx

let handleRejectedVisaWorkflowID (ctx : context) : context =
  ctx

let handleNoVisaDecisionWorkflowId (ctx : context) : context =
  ctx

(* === Transition function === *)

let step (c : config) (ev : visa_event) : config =
  match c.state, ev with
  | CheckVisaStatus, VisaApprovedEvent ->
      { state = HandleApprovedVisa; ctx = c.ctx }

  | CheckVisaStatus, VisaRejectedEvent ->
      { state = HandleRejectedVisa; ctx = c.ctx }

  | CheckVisaStatus, NoEvent ->
      (* models timeout (visaDecisionTimeout) *)
      { state = HandleNoVisaDecision; ctx = c.ctx }

  | HandleApprovedVisa, _ ->
      let ctx' = handleApprovedVisaWorkflowID c.ctx in
      { state = End; ctx = ctx' }

  | HandleRejectedVisa, _ ->
      let ctx' = handleRejectedVisaWorkflowID c.ctx in
      { state = End; ctx = ctx' }

  | HandleNoVisaDecision, _ ->
      let ctx' = handleNoVisaDecisionWorkflowId c.ctx in
      { state = End; ctx = ctx' }

  | End, _ ->
      { state = End; ctx = c.ctx }

(* === Initial configuration === *)

let init : config = { state = CheckVisaStatus; ctx = () }

(* === Run a sequence of events === *)

let run (c : config) (evs : visa_event list) : config =
  List.fold_left step c evs

(* === Invariants and properties === *)

let invariant_reaches_end (evs : visa_event list) : bool =
  let final = run init evs in
  match final.state with
  | End -> true
  | _ -> false

(* === Example evaluations === *)

eval (run init [VisaApprovedEvent])
eval (run init [VisaRejectedEvent])
eval (run init [NoEvent])

eval (invariant_reaches_end [VisaApprovedEvent])
eval (invariant_reaches_end [VisaRejectedEvent])
eval (invariant_reaches_end [NoEvent])
```

---

## Example 2: Book Lending (Complex, With Context, Nested States)

### XState Input (Simplified):

```typescript
interface Lender {
  name: string;
  address: string;
  phone: string;
}

export const workflow = createMachine({
  types: {} as {
    context: {
      book: {
        title: string;
        id: string;
        status: 'onloan' | 'available' | 'unknown';
      } | null;
      lender: Lender | null;
    };
    events:
      | { type: 'bookLendingRequest'; book: { title: string; id: string; }; lender: Lender; }
      | { type: 'holdBook'; }
      | { type: 'declineBookhold'; };
  },
  initial: 'Book Lending Request',
  context: { book: null, lender: null },
  states: {
    'Book Lending Request': {
      on: {
        bookLendingRequest: {
          target: 'Get Book Status',
          actions: assign({
            book: ({ event }) => ({ ...event.book, status: 'unknown' })
          })
        }
      }
    },
    'Get Book Status': {
      invoke: {
        src: 'Get status for book',
        onDone: {
          target: 'Book Status Decision',
          actions: assign({
            book: ({ context, event }) => ({ ...context.book!, status: event.output.status })
          })
        }
      }
    },
    'Book Status Decision': {
      always: [
        { guard: ({ context }) => context.book!.status === 'onloan',
          target: 'Report Status To Lender' },
        { guard: ({ context }) => context.book!.status === 'available',
          target: 'Check Out Book' }
      ]
    },
    'Check Out Book': {
      initial: 'Checking out book',
      states: {
        'Checking out book': {
          invoke: {
            src: 'Check out book with id',
            onDone: { target: 'Notifying Lender' }
          }
        },
        'Notifying Lender': {
          invoke: {
            src: 'Notify Lender for checkout',
            onDone: { target: 'End' }
          }
        },
        End: { type: 'final' }
      }
    },
    End: { type: 'final' }
  }
});
```

### IML Output:

```iml
(* ========================================= *)
(* Book Lending Workflow - IML Formalization *)
(* ========================================= *)

open Option

(* === Type Definitions === *)

type book_status =
  | OnLoan
  | Available
  | Unknown

type book_record = {
  title: string;
  id: string;
  status: book_status;
}

type lender_record = {
  name: string;
  address: string;
  phone: string;
}

type context_record = {
  book: book_record option;
  lender: lender_record option;
}

(* Nested state for Check Out Book *)
type checkout_substate =
  | CheckingOut
  | NotifyingLender

type state_node =
  | BookLendingRequest
  | GetBookStatus
  | ReportStatusToLender
  | CheckOutBook of checkout_substate  (* Nested state *)
  | End

type state = {
  node: state_node;
  context: context_record;
}

(* Events *)
type event =
  (* User Events *)
  | E_BookLendingRequest of (string * string * lender_record)  (* id, title, lender *)
  | E_HoldBook
  | E_DeclineBookhold

  (* Invoke completion events *)
  | E_BookStatusResponse of book_status  (* onDone from Get status for book *)
  | E_CheckoutDone  (* onDone from Check out book *)
  | E_NotifyLenderDone  (* onDone from Notify Lender *)

(* === Initial State === *)

let initial_context : context_record = {
  book = None;
  lender = None;
}

let initial_state : state = {
  node = BookLendingRequest;
  context = initial_context;
}

(* === Transition Function === *)

let step (s: state) (e: event) : state =
  match s.node with
  | BookLendingRequest ->
      (match e with
       | E_BookLendingRequest (id, title, lender) ->
           let new_book : book_record = { id = id; title = title; status = Unknown } in
           let new_context : context_record = { book = Some new_book; lender = Some lender } in
           { node = GetBookStatus; context = new_context }
       | _ -> s)

  | GetBookStatus ->
      (match e with
       | E_BookStatusResponse status ->
           (match s.context.book with
            | Some b ->
                let updated_book : book_record = { b with status = status } in
                let new_context : context_record = { s.context with book = Some updated_book } in
                (* Inline the "Book Status Decision" always logic *)
                (match status with
                 | OnLoan -> { node = ReportStatusToLender; context = new_context }
                 | Available -> { node = CheckOutBook CheckingOut; context = new_context }
                 | Unknown -> { node = End; context = new_context })
            | None -> s)
       | _ -> s)

  | CheckOutBook CheckingOut ->
      (match e with
       | E_CheckoutDone -> { s with node = CheckOutBook NotifyingLender }
       | _ -> s)

  | CheckOutBook NotifyingLender ->
      (match e with
       | E_NotifyLenderDone -> { s with node = End }
       | _ -> s)

  | End -> s

(* === Run Events === *)

let run_workflow (events : event list) : state =
  List.fold_left step initial_state events

(* === Properties === *)

let reaches_end (events : event list) : bool =
  (run_workflow events).node = End

let prop_available_book_leads_to_checkout () : bool =
  let test_lender = { name = "Jane"; address = "123"; phone = "555" } in
  let events = [
    E_BookLendingRequest ("42", "The Guide", test_lender);
    E_BookStatusResponse Available;
  ] in
  match (run_workflow events).node with
  | CheckOutBook CheckingOut -> true
  | _ -> false

(* === Eval Examples === *)

let test_lender : lender_record = {
  name = "Jane Doe";
  address = "123 Main St";
  phone = "555-1212";
}

let test_request = E_BookLendingRequest ("book-42", "The Guide", test_lender)

(* Happy path: book available *)
eval (run_workflow [
  test_request;
  E_BookStatusResponse Available;
  E_CheckoutDone;
  E_NotifyLenderDone
])

(* Check property *)
eval (reaches_end [
  test_request;
  E_BookStatusResponse Available;
  E_CheckoutDone;
  E_NotifyLenderDone
])

eval (prop_available_book_leads_to_checkout ())
```

---

## Example 3: Purchase Order (Root-level Timeout, Logging)

### XState Input (Simplified):

```typescript
export const workflow = createMachine({
  id: 'order',
  initial: 'StartNewOrder',
  after: {
    PT30D: { target: '.CancelOrder' }  // Root-level timeout
  },
  states: {
    StartNewOrder: {
      on: {
        OrderCreatedEvent: {
          actions: ['logNewOrderCreated'],
          target: 'WaitForOrderConfirmation'
        }
      }
    },
    WaitForOrderConfirmation: {
      on: {
        OrderConfirmedEvent: {
          actions: ['logOrderConfirmed'],
          target: 'WaitOrderShipped'
        }
      }
    },
    WaitOrderShipped: {
      on: {
        ShipmentSentEvent: {
          actions: ['logOrderShipped'],
          target: 'OrderFinished'
        }
      }
    },
    OrderFinished: {
      type: 'final',
      entry: ['logOrderFinished']
    },
    CancelOrder: {
      invoke: {
        src: 'CancelOrder',
        onDone: { target: 'OrderCancelled' }
      }
    },
    OrderCancelled: {
      type: 'final',
      entry: ['logOrderCancelled']
    }
  }
});
```

### IML Output:

```iml
(* ========================================================== *)
(*  Order Workflow — IML Formalization                        *)
(* ========================================================== *)

(* === Events === *)

type event =
  | OrderCreatedEvent
  | OrderConfirmedEvent
  | ShipmentSentEvent
  | TimeoutEvent          (* Root-level PT30D timeout *)
  | CancelDoneEvent       (* onDone from CancelOrder invoke *)

(* === States === *)

type state =
  | StartNewOrder
  | WaitForOrderConfirmation
  | WaitOrderShipped
  | OrderFinished          (* final *)
  | CancelOrderInvoked
  | OrderCancelled         (* final *)

(* === Step function with action logging === *)

let step (st : state) (ev : event) : (state * string list) =
  match (st, ev) with
  | (StartNewOrder, OrderCreatedEvent) ->
      (WaitForOrderConfirmation, ["logNewOrderCreated"])

  | (WaitForOrderConfirmation, OrderConfirmedEvent) ->
      (WaitOrderShipped, ["logOrderConfirmed"])

  | (WaitOrderShipped, ShipmentSentEvent) ->
      (OrderFinished, ["logOrderShipped"; "logOrderFinished"])

  (* Root-level timeout from any non-final state *)
  | (StartNewOrder, TimeoutEvent)
  | (WaitForOrderConfirmation, TimeoutEvent)
  | (WaitOrderShipped, TimeoutEvent) ->
      (CancelOrderInvoked, ["invokeCancelOrder"])

  | (CancelOrderInvoked, CancelDoneEvent) ->
      (OrderCancelled, ["logOrderCancelled"])

  (* Final states are terminal *)
  | (OrderFinished, _) -> (OrderFinished, [])
  | (OrderCancelled, _) -> (OrderCancelled, [])

  (* Default: no transition *)
  | (s, _) -> (s, ["ignoredEvent"])

(* === Run events with log accumulation === *)

let run_from_start (evs : event list) : (state * string list) =
  List.fold_left
    (fun (st, logs) ev ->
      let (st', acts) = step st ev in
      (st', List.append logs acts))
    (StartNewOrder, [])
    evs

(* === Properties === *)

let prop_happy_path () : bool =
  let (final_st, _) =
    run_from_start [OrderCreatedEvent; OrderConfirmedEvent; ShipmentSentEvent]
  in
  final_st = OrderFinished

let prop_timeout_leads_to_cancelled () : bool =
  let (final_st, _) =
    run_from_start [OrderCreatedEvent; TimeoutEvent; CancelDoneEvent]
  in
  final_st = OrderCancelled

(* === Eval Examples === *)

(* Happy path *)
eval (run_from_start [OrderCreatedEvent; OrderConfirmedEvent; ShipmentSentEvent])

(* Timeout scenario *)
eval (run_from_start [OrderCreatedEvent; TimeoutEvent; CancelDoneEvent])

(* Verify properties *)
eval (prop_happy_path ())
eval (prop_timeout_leads_to_cancelled ())
```

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

## Now Translate This XState Machine:

```typescript
[XSTATE MACHINE HERE]
```

---

## Your Translation Process:

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

### Step 3: Return Final Output

## Expected Output:

1. Complete IML model with all sections
2. Comments explaining mappings for non-obvious translations
3. At least 2-3 workflow examples with `eval`
4. At least 1 verification property
5. List any XState features omitted and why
6. **Confirmation that you reviewed the self-verification checklist**
