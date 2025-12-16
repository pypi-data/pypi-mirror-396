----
title: XState Verification
description: Tutorial and recommendations for writing verificaiton goals for XState library applications.
order: 5
----

## Overview

After translating an XState machine to IML, write verification goals to formally prove properties using Imandra.

## Imandra Commands

- **`verify (fun args -> property) [@@upto n]? [@@upto_bound n]? [@@by auto]? ...`** - Proves a property always holds (returns counterexample if it fails)
- **`instance (fun args -> property) [@@upto n]? [@@upto_bound n]? ...`** - Finds a concrete example satisfying a property
- **`theorem <name> <vars> = <body> [@@by auto]? [@@rewrite]? ...`** - Proves and names a theorem for reuse in subsequent proofs
- **`lemma <name> <vars> = <body> [@@by auto]? [@@rewrite]? ...`** - Synonym of theorem, idiomatically used for subsidiary results

```iml
verify (fun x -> x + 1 > x)
verify (fun x -> x + 1 > x) [@@upto 50]
instance (fun events -> (run init events).state = End)
theorem final_stable event = (step {state = End; ctx = ()} event).state = End
```

---

## Bounded Verification (Recommended)

**For most XState machines, use bounded verification with explicit event parameters.**

Instead of quantifying over all possible event sequences, enumerate events equal to the number of event types in your machine. This is sufficient because counterexamples are typically found within a small number of steps.

```iml
(* ❌ DON'T: Unbounded over event lists *)
verify (fun (events : event list) ->
  safety_property (run init events))

(* ✅ DO: Bounded with explicit events *)
(* If you have 10 event types, use 10 parameters *)
verify (fun ev1 ev2 ev3 ev4 ev5 ev6 ev7 ev8 ev9 ev10 ->
  safety_property (run init [ev1; ev2; ev3; ev4; ev5; ev6; ev7; ev8; ev9; ev10]))
```

**Rule of thumb:** Number of parameters = number of variants in your `event` type.

**When bounded verification isn't enough:**
- Use helper lemmas with `[@@disable]` and `[@@rewrite]` (see Safety section)
- Define invariants and prove them separately (manual induction)

---

## Importing Your Model

Before writing verification goals, you need to import the IML model file you want to verify.

### Import Syntax

```iml
(* Import with implicit module name (derived from filename) *)
[@@@import "traffic_light.iml"]

(* Import with explicit module name *)
[@@@import Traffic_light, "traffic_light.iml"]

(* Then open the module to use its definitions *)
open Traffic_light
```

### Common Patterns

```iml
(* Pattern 1: Import and open in one go *)
[@@@import "state_machine.iml"]
open State_machine

(* Pattern 2: Import with custom name *)
[@@@import MyMachine, "path/to/machine.iml"]
open MyMachine

(* Pattern 3: Import from OCamlFind/Dune packages *)
[@@@import Lib, "findlib:package.module"]
[@@@import Lib, "dune:package.module"]
```

### Complete Example

```iml
(* verification.iml *)

(* Import the state machine model *)
[@@@import "traffic_light.iml"]
open Traffic_light

(* Now you can use types and functions from the model *)
theorem safety_property events =
  let final = run init events in
  safety_no_both_green final
[@@by auto]

eval (run init [NS_TIMER_EXPIRED])
```

---

## Verification Attributes

Attributes guide Imandra's proof strategy and install theorems as rules for automatic application.

### Common Proof Strategies

- **`[@@by auto]`** - Apply Imandra's inductive waterfall (simplification + optional induction)
  - **This is the most common way to prove a theorem in Imandra**

- **`[@@by induct ~on_fun:[%id <func_name>] ()]`** - Control induction strategy:
  - Follow function's recursive structure using functional induction

- **`[@@by induct ~on_struct:[<args>] ()]`** - Structural induction on algebraic datatypes

- **`[@@by simp]`** or **`[@@by simplify]`** - Apply simplification before unrolling

- **`[@@by blast]`** - Use SAT-based bit-blasting for combinatorial problems

### Rule Classes (for installing theorems)

- **`[@@rw]`** or **`[@@rewrite]`** - Install as rewrite rule for automatic simplification
- **`[@@fc]`** or **`[@@forward-chaining]`** - Install as forward-chaining rule
- **`[@@elim]`** or **`[@@elimination]`** - Install as elimination rule
- **`[@@gen]`** or **`[@@generalization]`** - Install as generalization rule

### Examples

```iml
(* Most common: auto strategy *)
theorem len_append x y =
  List.length (x @ y) = List.length x + List.length y
[@@by auto]

(* Functional induction with rewrite rule *)
theorem merge_sorts x y =
  is_sorted x && is_sorted y ==> is_sorted (merge x y)
[@@by induct ~on_fun:[%id merge] ()] [@@rewrite]

(* With blast for combinatorial problems *)
theorem adder_correct a b cin =
  List.length a = List.length b ==>
  int_of_bits (ripple_carry_adder a b cin) =
  int_of_bits a + int_of_bits b + int_of_bit cin
[@@by blast]
```

---

## Property Categories

**Note:** These categories are XState-specific patterns for state machine verification, not standard Imandra terminology.

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

## Common Mistakes

- ❌ Using unbounded `verify (fun events -> ...)` instead of bounded explicit parameters
- ❌ Wrong bound: use number of event types, not arbitrary number
- ❌ Forgetting to import: add `[@@@import "model.iml"]` at the top
- ❌ Properties too weak: `verify (fun () -> true)`
- ❌ Ignoring context invariants
- ❌ Not testing with `eval` first

## Proof Strategy Workflow

```
1. Write bounded verify with explicit events (count = number of event types)
2. If proof succeeds → Done!
3. If proof fails:
   a. Write helper lemma with [@@disable] and [@@rewrite]
   b. Use [%use lemma] in main verify
4. If still stuck, try:
   - Define invariants and prove them separately
   - Use `[@@by blast]` for combinatorial problems
```

## Property Count Guide

- **Simple** (like visa workflow): 3-5 properties
- **Medium** (with context/guards): 6-10 properties
- **Complex** (nested states, multiple invokes): 10-15+ properties

## References

Based on Imandra verification documentation:
- Use `[@@by auto]` as the primary proof strategy
- Apply functional induction with `[@@by induct ~on_fun:[%id <func>] ()]`
- Install helper lemmas as rewrite rules with `[@@rewrite]`
- See Imandra docs for advanced strategies like `[@@by blast]`, `[@@forward-chaining]`, etc.
