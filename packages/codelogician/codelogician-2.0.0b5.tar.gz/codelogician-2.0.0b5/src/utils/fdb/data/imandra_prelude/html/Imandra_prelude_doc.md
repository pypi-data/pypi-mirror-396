

==================================================
Content from: Root
==================================================

[Up](../index.html) – [imandra-base](../index.html) » Imandra_prelude

# Module `Imandra_prelude`

  * Bare minimum needed for ordinals and validation
  * Ordinals
  * Other builtin types
  * Sets
  * Logic-mode strings



`type 'a printer = Stdlib.Format.formatter -> 'a -> unit`

`module [Caml](Caml/index.html) : sig ... end`

`module Imandra_caml = [Caml](Caml/index.html)`

`module Caml_unix = Unix`

`module Caml_sys = Stdlib.Sys`

`module [Unix](Unix/index.html) : sig ... end`

`module [Sys](Sys/index.html) : sig ... end`

### Bare minimum needed for ordinals and validation

`type nonrec int = Z.t`

Builtin integer type, using arbitrary precision integers.

This type is an alias to `Z`.t (using [Zarith](https://github.com/ocaml/Zarith)).

**NOTE** : here Imandra diverges from normal OCaml, where integers width is bounded by native machine integers. "Normal" OCaml integers have type [`Caml.Int.t`](Caml/Int/index.html#type-t) and can be entered using the 'i' suffix: `0i`

`val (=) : 'a -> 'a -> bool`

Equality. Must be applied to non-function types.

`val (<>) : 'a -> 'a -> bool`

`val not : bool -> bool`

`val implies : bool -> bool -> bool`

`val explies : bool -> bool -> bool`

`val iff : bool -> bool -> bool`

`val (+) : Z.t -> Z.t -> Z.t`

`val const : 'a -> 'b -> 'a`

`const x y` returns `x`. In other words, `const x` is the constant function that always returns `x`.

`val (>=) : int -> int -> bool`

`type nonrec nativeint = nativeint`

`val mk_nat : int -> int`

`type nonrec 'a option = 'a option = ``| None`  
---  
`| Some of 'a`  
  
`type 'a list = 'a [Caml.list](Caml/index.html#type-list) = ``| []`  
---  
`| :: of 'a * 'a list`  
  
`type nonrec float = float`

`type nonrec real = Q.t`

`type nonrec string = string`

`val (<) : int -> int -> bool`

`val (<=) : int -> int -> bool`

`val (>) : int -> int -> bool`

`val min : int -> int -> int`

`val max : int -> int -> int`

`val (<.) : real -> real -> bool`

`val (<=.) : real -> real -> bool`

`val (>.) : real -> real -> bool`

`val (>=.) : real -> real -> bool`

`val min_r : real -> real -> real`

`val max_r : real -> real -> real`

`val (~-) : Z.t -> Z.t`

`val abs : int -> int`

`val (-) : Z.t -> Z.t -> Z.t`

`val (~+) : Z.t -> Z.t`

`val (*) : Z.t -> Z.t -> Z.t`

`val (/) : Z.t -> Z.t -> Z.t`

Euclidian division on integers, see <http://smtlib.cs.uiowa.edu/theories-Ints.shtml>

`val (mod) : Z.t -> Z.t -> Z.t`

Euclidian remainder on integers

`val compare : int -> int -> Z.t`

Total order

### Ordinals

`module [Ordinal](Ordinal/index.html) : sig ... end`

We need to define ordinals before any recursive function is defined, because ordinals are used for termination proofs.

`module [Peano_nat](Peano_nat/index.html) : sig ... end`

### Other builtin types

`type nonrec unit = unit = ``| ()`  
---  
  
`type ('a, 'b) result = ( 'a, 'b ) Stdlib.result = ``| Ok of 'a`  
---  
`| Error of 'b`  
  
Result type, representing either a successul result `Ok x` or an error `Error x`.

`module [Result](Result/index.html) : sig ... end`

`type ('a, 'b) either = ``| Left of 'a`  
---  
`| Right of 'b`  
  
A familiar type for Haskellers

`val (|>) : 'a -> ( 'a -> 'b ) -> 'b`

Pipeline operator.

`x |> f` is the same as `f x`, but it composes nicely: ` x |> f |> g |> h` can be more readable than `h(g(f x))`.

`val (@@) : ( 'a -> 'b ) -> 'a -> 'b`

Right-associative application operator.

`f @@ x` is the same as `f x`, but it binds to the right: `f @@ g @@ h @@ x` is the same as `f (g (h x))` but with fewer parentheses.

`val id : 'a -> 'a`

Identity function. `id x = x` always holds.

`val (%>) : ( 'a -> 'b ) -> ( 'b -> 'c ) -> 'a -> 'c`

Mathematical composition operator.

`f %> g` is `fun x -> g (f x)`

`val (==) : 'a -> 'b -> [Caml.use_normal_equality](Caml/index.html#type-use_normal_equality)`

`val (!=) : 'a -> 'b -> [Caml.use_normal_equality](Caml/index.html#type-use_normal_equality)`

`val (+.) : real -> real -> real`

`val (-.) : real -> real -> real`

`val (~-.) : Q.t -> Q.t`

`val (*.) : real -> real -> real`

`val (/.) : real -> real -> real`

`module [List](List/index.html) : sig ... end`

`val (@) : 'a list -> 'a list -> 'a list`

Infix alias to [`List.append`](List/index.html#val-append)

`val (--) : int -> int -> int list`

Alias to [`List.(--)`](List/index.html#val-\(--\))

`module [Int](Int/index.html) : sig ... end`

`module [Bool](Bool/index.html) : sig ... end`

`module [Array](Array/index.html) : sig ... end`

`module [Option](Option/index.html) : sig ... end`

`module [Real](Real/index.html) : sig ... end`

`module [Map](Map/index.html) : sig ... end`

`module [Multiset](Multiset/index.html) : sig ... end`

### Sets

`module [Set](Set/index.html) : sig ... end`

`module [String](String/index.html) : sig ... end`

`val (^) : [String.t](String/index.html#type-t) -> [String.t](String/index.html#type-t) -> [String.t](String/index.html#type-t)`

Alias to [`String.append`](String/index.html#val-append)

`val succ : Z.t -> Z.t`

Next integer

`val pred : Z.t -> Z.t`

Previous integer

`val fst : ('a * 'b) -> 'a`

`val snd : ('a * 'b) -> 'b`

`module [Float](Float/index.html) : sig ... end`

`module [LChar](LChar/index.html) : sig ... end`

### Logic-mode strings

Strings purely in Imandra.

`module [LString](LString/index.html) : sig ... end`

`module [Pervasives](Pervasives/index.html) : sig ... end`

`module [Stdlib](Stdlib/index.html) : sig ... end`


==================================================
Content from: Array
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Array

# Module `Imandra_prelude.Array`

  * Arrays



### Arrays

Program mode only

A program-mode imperative array, that can be mutated

`include module type of struct include [Caml.Array](../Caml/Array/index.html) end`

`type !'a t = 'a array`

`val create : int -> 'a -> 'a array`

`val create_float : int -> float array`

`val make_float : int -> float array`

`val make_matrix : int -> int -> 'a -> 'a array array`

`val create_matrix : int -> int -> 'a -> 'a array array`

`val append : 'a array -> 'a array -> 'a array`

`val concat : 'a array list -> 'a array`

`val copy : 'a array -> 'a array`

`val to_list : 'a array -> 'a list`

`val of_list : 'a list -> 'a array`

`val iter : ( 'a -> unit ) -> 'a array -> unit`

`val map : ( 'a -> 'b ) -> 'a array -> 'b array`

`val fold_left : ( 'a -> 'b -> 'a ) -> 'a -> 'b array -> 'a`

`val fold_right : ( 'b -> 'a -> 'a ) -> 'b array -> 'a -> 'a`

`val iter2 : ( 'a -> 'b -> unit ) -> 'a array -> 'b array -> unit`

`val map2 : ( 'a -> 'b -> 'c ) -> 'a array -> 'b array -> 'c array`

`val for_all : ( 'a -> bool ) -> 'a array -> bool`

`val exists : ( 'a -> bool ) -> 'a array -> bool`

`val for_all2 : ( 'a -> 'b -> bool ) -> 'a array -> 'b array -> bool`

`val exists2 : ( 'a -> 'b -> bool ) -> 'a array -> 'b array -> bool`

`val mem : 'a -> 'a array -> bool`

`val memq : 'a -> 'a array -> bool`

`val sort : ( 'a -> 'a -> int ) -> 'a array -> unit`

`val stable_sort : ( 'a -> 'a -> int ) -> 'a array -> unit`

`val fast_sort : ( 'a -> 'a -> int ) -> 'a array -> unit`

`val to_seq : 'a array -> 'a Stdlib.Seq.t`

`val to_seqi : 'a array -> (int * 'a) Stdlib.Seq.t`

`val of_seq : 'a Stdlib.Seq.t -> 'a array`

`val unsafe_get : 'a array -> int -> 'a`

`val unsafe_set : 'a array -> int -> 'a -> unit`

`module Floatarray = Stdlib__array.Floatarray`

`val get : 'a array -> Z.t -> 'a`

`val set : 'a array -> Z.t -> 'a -> unit`

`val make : Z.t -> 'a -> 'a array`

`val init : Z.t -> ( Z.t -> 'a ) -> 'a array`

`val sub : 'a array -> Z.t -> Z.t -> 'a array`

`val length : 'a array -> Z.t`

`val mapi : ( Z.t -> 'a -> 'b ) -> 'a array -> 'b array`

`val iteri : ( Z.t -> 'a -> unit ) -> 'a array -> unit`

`val fill : 'a array -> Z.t -> Z.t -> 'a -> unit`

`val blit : 'a array -> Z.t -> 'a array -> Z.t -> Z.t -> unit`


==================================================
Content from: Bool
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Bool

# Module `Imandra_prelude.Bool`

`type t = bool`


==================================================
Content from: Caml
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Caml

# Module `Imandra_prelude.Caml`

`include module type of struct include Stdlib end`

`val raise : exn -> 'a`

`val raise_notrace : exn -> 'a`

`val invalid_arg : string -> 'a`

`val failwith : string -> 'a`

`exception Exit`

`exception Match_failure of string * int * int`

`exception Assert_failure of string * int * int`

`exception Invalid_argument of string`

`exception Failure of string`

`exception Not_found`

`exception Out_of_memory`

`exception Stack_overflow`

`exception Sys_error of string`

`exception End_of_file`

`exception Division_by_zero`

`exception Sys_blocked_io`

`exception Undefined_recursive_module of string * int * int`

`val (=) : 'a -> 'a -> bool`

`val (<>) : 'a -> 'a -> bool`

`val (<) : 'a -> 'a -> bool`

`val (>) : 'a -> 'a -> bool`

`val (<=) : 'a -> 'a -> bool`

`val (>=) : 'a -> 'a -> bool`

`val compare : 'a -> 'a -> int`

`val min : 'a -> 'a -> 'a`

`val max : 'a -> 'a -> 'a`

`val not : bool -> bool`

`val (&&) : bool -> bool -> bool`

`val (&) : bool -> bool -> bool`

`val (||) : bool -> bool -> bool`

`val or : bool -> bool -> bool`

`val __LOC__ : string`

`val __FILE__ : string`

`val __LINE__ : int`

`val __MODULE__ : string`

`val __POS__ : string * int * int * int`

`val __FUNCTION__ : string`

`val __LOC_OF__ : 'a -> string * 'a`

`val __LINE_OF__ : 'a -> int * 'a`

`val __POS_OF__ : 'a -> (string * int * int * int) * 'a`

`val (|>) : 'a -> ( 'a -> 'b ) -> 'b`

`val (@@) : ( 'a -> 'b ) -> 'a -> 'b`

`val (~-) : int -> int`

`val (~+) : int -> int`

`val succ : int -> int`

`val pred : int -> int`

`val (+) : int -> int -> int`

`val (-) : int -> int -> int`

`val (*) : int -> int -> int`

`val (/) : int -> int -> int`

`val (mod) : int -> int -> int`

`val abs : int -> int`

`val max_int : int`

`val min_int : int`

`val (land) : int -> int -> int`

`val (lor) : int -> int -> int`

`val (lxor) : int -> int -> int`

`val lnot : int -> int`

`val (lsl) : int -> int -> int`

`val (lsr) : int -> int -> int`

`val (asr) : int -> int -> int`

`val (~-.) : float -> float`

`val (~+.) : float -> float`

`val (+.) : float -> float -> float`

`val (-.) : float -> float -> float`

`val (*.) : float -> float -> float`

`val (/.) : float -> float -> float`

`val (**) : float -> float -> float`

`val sqrt : float -> float`

`val exp : float -> float`

`val log : float -> float`

`val log10 : float -> float`

`val expm1 : float -> float`

`val log1p : float -> float`

`val cos : float -> float`

`val sin : float -> float`

`val tan : float -> float`

`val acos : float -> float`

`val asin : float -> float`

`val atan : float -> float`

`val atan2 : float -> float -> float`

`val hypot : float -> float -> float`

`val cosh : float -> float`

`val sinh : float -> float`

`val tanh : float -> float`

`val ceil : float -> float`

`val floor : float -> float`

`val abs_float : float -> float`

`val copysign : float -> float -> float`

`val mod_float : float -> float -> float`

`val frexp : float -> float * int`

`val ldexp : float -> int -> float`

`val modf : float -> float * float`

`val float : int -> float`

`val float_of_int : int -> float`

`val truncate : float -> int`

`val int_of_float : float -> int`

`val infinity : float`

`val neg_infinity : float`

`val nan : float`

`val max_float : float`

`val min_float : float`

`val epsilon_float : float`

`type fpclass = Stdlib.fpclass = ``| FP_normal`  
---  
`| FP_subnormal`  
`| FP_zero`  
`| FP_infinite`  
`| FP_nan`  
  
`val classify_float : float -> fpclass`

`val (^) : string -> string -> string`

`val int_of_char : char -> int`

`val char_of_int : int -> char`

`val ignore : 'a -> unit`

`val string_of_bool : bool -> string`

`val bool_of_string_opt : string -> bool option`

`val bool_of_string : string -> bool`

`val string_of_int : int -> string`

`val int_of_string_opt : string -> int option`

`val int_of_string : string -> int`

`val string_of_float : float -> string`

`val float_of_string_opt : string -> float option`

`val fst : ('a * 'b) -> 'a`

`val snd : ('a * 'b) -> 'b`

`val (@) : 'a list -> 'a list -> 'a list`

`type in_channel = Stdlib.in_channel`

`type out_channel = Stdlib.out_channel`

`val stdin : in_channel`

`val stdout : out_channel`

`val stderr : out_channel`

`val print_char : char -> unit`

`val print_string : string -> unit`

`val print_bytes : bytes -> unit`

`val print_int : int -> unit`

`val print_float : float -> unit`

`val print_endline : string -> unit`

`val print_newline : unit -> unit`

`val prerr_char : char -> unit`

`val prerr_string : string -> unit`

`val prerr_bytes : bytes -> unit`

`val prerr_int : int -> unit`

`val prerr_float : float -> unit`

`val prerr_endline : string -> unit`

`val prerr_newline : unit -> unit`

`val read_line : unit -> string`

`val read_int_opt : unit -> int option`

`val read_int : unit -> int`

`val read_float_opt : unit -> float option`

`val read_float : unit -> float`

`type open_flag = Stdlib.open_flag = ``| Open_rdonly`  
---  
`| Open_wronly`  
`| Open_append`  
`| Open_creat`  
`| Open_trunc`  
`| Open_excl`  
`| Open_binary`  
`| Open_text`  
`| Open_nonblock`  
  
`val open_out : string -> out_channel`

`val open_out_bin : string -> out_channel`

`val open_out_gen : open_flag list -> int -> string -> out_channel`

`val flush : out_channel -> unit`

`val flush_all : unit -> unit`

`val output_char : out_channel -> char -> unit`

`val output_string : out_channel -> string -> unit`

`val output_bytes : out_channel -> bytes -> unit`

`val output : out_channel -> bytes -> int -> int -> unit`

`val output_substring : out_channel -> string -> int -> int -> unit`

`val output_byte : out_channel -> int -> unit`

`val output_binary_int : out_channel -> int -> unit`

`val output_value : out_channel -> 'a -> unit`

`val seek_out : out_channel -> int -> unit`

`val pos_out : out_channel -> int`

`val out_channel_length : out_channel -> int`

`val close_out : out_channel -> unit`

`val close_out_noerr : out_channel -> unit`

`val set_binary_mode_out : out_channel -> bool -> unit`

`val open_in : string -> in_channel`

`val open_in_bin : string -> in_channel`

`val open_in_gen : open_flag list -> int -> string -> in_channel`

`val input_char : in_channel -> char`

`val input_line : in_channel -> string`

`val input : in_channel -> bytes -> int -> int -> int`

`val really_input : in_channel -> bytes -> int -> int -> unit`

`val really_input_string : in_channel -> int -> string`

`val input_byte : in_channel -> int`

`val input_binary_int : in_channel -> int`

`val input_value : in_channel -> 'a`

`val seek_in : in_channel -> int -> unit`

`val pos_in : in_channel -> int`

`val in_channel_length : in_channel -> int`

`val close_in : in_channel -> unit`

`val close_in_noerr : in_channel -> unit`

`val set_binary_mode_in : in_channel -> bool -> unit`

`module LargeFile = Stdlib.LargeFile`

`type !'a ref = 'a Stdlib.ref = {``mutable contents : 'a;`  
---  
`}`

`val ref : 'a -> 'a ref`

`val (!) : 'a ref -> 'a`

`val (:=) : 'a ref -> 'a -> unit`

`val incr : int ref -> unit`

`val decr : int ref -> unit`

`type (!'a, !'b) result = ( 'a, 'b ) Stdlib.result = ``| Ok of 'a`  
---  
`| Error of 'b`  
  
`type (!'a, !'b, !'c, !'d, !'e, !'f) format6 = ( 'a, 'b, 'c, 'd, 'e, 'f ) CamlinternalFormatBasics.format6`

`type (!'a, !'b, !'c, !'d) format4 = ( 'a, 'b, 'c, 'c, 'c, 'd ) format6`

`type (!'a, !'b, !'c) format = ( 'a, 'b, 'c, 'c ) format4`

`val string_of_format : ( 'a, 'b, 'c, 'd, 'e, 'f ) format6 -> string`

`val format_of_string : ( 'a, 'b, 'c, 'd, 'e, 'f ) format6 -> ( 'a, 'b, 'c, 'd, 'e, 'f ) format6`

`val (^^) : ( 'a, 'b, 'c, 'd, 'e, 'f ) format6 -> ( 'f, 'b, 'c, 'e, 'g, 'h ) format6 -> ( 'a, 'b, 'c, 'd, 'g, 'h ) format6`

`val exit : int -> 'a`

`val at_exit : ( unit -> unit ) -> unit`

`val valid_float_lexem : string -> string`

`val unsafe_really_input : in_channel -> bytes -> int -> int -> unit`

`val do_at_exit : unit -> unit`

`module Arg = Stdlib__arg`

`module ArrayLabels = Stdlib__arrayLabels`

`module Atomic = Stdlib__atomic`

`module Bigarray = Stdlib__bigarray`

`module Bool = Stdlib__bool`

`module Buffer = Stdlib__buffer`

`module Bytes = Stdlib__bytes`

`module BytesLabels = Stdlib__bytesLabels`

`module Callback = Stdlib__callback`

`module Complex = Stdlib__complex`

`module Digest = Stdlib__digest`

`module Either = Stdlib__either`

`module Ephemeron = Stdlib__ephemeron`

`module Filename = Stdlib__filename`

`module Float = Stdlib__float`

`module Fun = Stdlib__fun`

`module Gc = Stdlib__gc`

`module Genlex = Stdlib__genlex`

`module Hashtbl = Stdlib__hashtbl`

`module Int32 = Stdlib__int32`

`module Int64 = Stdlib__int64`

`module Lazy = Stdlib__lazy`

`module Lexing = Stdlib__lexing`

`module ListLabels = Stdlib__listLabels`

`module Marshal = Stdlib__marshal`

`module MoreLabels = Stdlib__moreLabels`

`module Nativeint = Stdlib__nativeint`

`module Obj = Stdlib__obj`

`module Oo = Stdlib__oo`

`module Option = Stdlib__option`

`module Parsing = Stdlib__parsing`

`module Pervasives = Stdlib__pervasives`

`module Printexc = Stdlib__printexc`

`module Queue = Stdlib__queue`

`module Random = Stdlib__random`

`module Result = Stdlib__result`

`module Scanf = Stdlib__scanf`

`module Seq = Stdlib__seq`

`module Stack = Stdlib__stack`

`module StdLabels = Stdlib__stdLabels`

`module Stream = Stdlib__stream`

`module StringLabels = Stdlib__stringLabels`

`module Sys = Stdlib__sys`

`module Uchar = Stdlib__uchar`

`module Unit = Stdlib__unit`

`module Weak = Stdlib__weak`

`type use_normal_equality`

`type nonrec 'a list = 'a list = ``| []`  
---  
`| :: of 'a * 'a list`  
  
`val (==) : 'a -> 'b -> use_normal_equality`

`val (!=) : 'a -> 'b -> use_normal_equality`

`module [String](String/index.html) : sig ... end`

`module Char : sig ... end`

`module List : sig ... end`

`module Array : sig ... end`

`module Set : sig ... end`

`module Map : sig ... end`

`module Printf : sig ... end`

`module Format = CCFormat`

`val float_of_string : string -> float`

`val count_function_actual_implem : 'a -> 'b`

`val sleep : int -> unit`

`module [Int](Int/index.html) : sig ... end`


==================================================
Content from: Float
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Float

# Module `Imandra_prelude.Float`

`type t = [float](../index.html#type-float)`

`module [Round](Round/index.html) : sig ... end`

`val of_int : Z.t -> float`

`val of_string : string -> float`

`val (~-) : t -> t`

`val (+) : t -> t -> t`

`val (-) : t -> t -> t`

`val (*) : t -> t -> t`

`val (/) : t -> t -> t`

`val nan : t`

`val infinity : t`

`val (<) : t -> t -> bool`

`val (<=) : t -> t -> bool`

`val (>) : t -> t -> bool`

`val (>=) : t -> t -> bool`

`val (=) : t -> t -> bool`

`val (<>) : t -> t -> bool`

`val neg : t -> t`

`val abs : t -> t`

`val is_zero : t -> bool`

`val is_nan : t -> bool`

`val is_infinite : t -> bool`

`val is_normal : t -> bool`

`val is_subnormal : t -> bool`

`val is_positive : t -> bool`

`val is_negative : t -> bool`

`val min : t -> t -> t`

`val max : t -> t -> t`

`val rem : t -> t -> t`

`val sqrt : t -> t`


==================================================
Content from: Int
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Int

# Module `Imandra_prelude.Int`

`type t = [int](../index.html#type-int)`

`val (+) : Z.t -> Z.t -> Z.t`

`val (-) : Z.t -> Z.t -> Z.t`

`val (~-) : Z.t -> Z.t`

`val (*) : Z.t -> Z.t -> Z.t`

`val (/) : Z.t -> Z.t -> Z.t`

`val (mod) : Z.t -> Z.t -> Z.t`

`val (<) : [int](../index.html#type-int) -> [int](../index.html#type-int) -> bool`

`val (<=) : [int](../index.html#type-int) -> [int](../index.html#type-int) -> bool`

`val (>) : [int](../index.html#type-int) -> [int](../index.html#type-int) -> bool`

`val (>=) : [int](../index.html#type-int) -> [int](../index.html#type-int) -> bool`

`val min : [int](../index.html#type-int) -> [int](../index.html#type-int) -> [int](../index.html#type-int)`

`val max : [int](../index.html#type-int) -> [int](../index.html#type-int) -> [int](../index.html#type-int)`

`val abs : [int](../index.html#type-int) -> [int](../index.html#type-int)`

`val to_string : t -> [string](../index.html#type-string)`

Conversion to a string. Only works for nonnegative numbers

`val equal : 'a -> 'a -> bool`

`val compare : 'a -> 'a -> int`

`val pp : Stdlib.Format.formatter -> Z.t -> unit`

`val of_caml_int : int -> Z.t`

`val for_ : [int](../index.html#type-int) -> [int](../index.html#type-int) -> ( [int](../index.html#type-int) -> unit ) -> [unit](../index.html#type-unit)`

`val for_down_to : [int](../index.html#type-int) -> [int](../index.html#type-int) -> ( [int](../index.html#type-int) -> unit ) -> [unit](../index.html#type-unit)`


==================================================
Content from: LChar
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » LChar

# Module `Imandra_prelude.LChar`

  * Logic mode char



## Logic mode char

An 8-bit char.

`type t = ``| Char of bool * bool * bool * bool * bool * bool * bool * bool`  
---  
  
`val zero : t`

`val to_int : t -> [Caml.Int.t](../Caml/Int/index.html#type-t)`

`val of_int : [Caml.Int.t](../Caml/Int/index.html#type-t) -> t`

`val of_char : char -> t`

`val to_char : t -> char`

`val pp : Stdlib.Format.formatter -> t -> unit`

`val explode : [string](../index.html#type-string) -> t [list](../index.html#type-list)`

`val is_printable : t -> bool`


==================================================
Content from: LString
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » LString

# Module `Imandra_prelude.LString`

`type t = [LChar.t](../LChar/index.html#type-t) [list](../index.html#type-list)`

`val empty : t`

`val of_list : 'a -> 'a`

`val to_string : t -> string`

`val of_string : [string](../index.html#type-string) -> [LChar.t](../LChar/index.html#type-t) [list](../index.html#type-list)`

`val length : t -> Z.t`

`val pp : Stdlib.Format.formatter -> [LChar.t](../LChar/index.html#type-t) [list](../index.html#type-list) -> unit`

`val len_pos : t -> bool`

`val len_zero_inversion : t -> bool`

`val append : t -> t -> t`

`val (^^) : t -> t -> t`

`val for_all : ( [LChar.t](../LChar/index.html#type-t) -> bool ) -> t -> bool`

`val exists : ( [LChar.t](../LChar/index.html#type-t) -> bool ) -> t -> bool`

`val concat : t -> [LChar.t](../LChar/index.html#type-t) [list](../index.html#type-list) [list](../index.html#type-list) -> [LChar.t](../LChar/index.html#type-t) [list](../index.html#type-list)`

`val is_printable : t -> bool`

`val sub : t -> [int](../index.html#type-int) -> [int](../index.html#type-int) -> t`

`val prefix : t -> t -> bool`

`val suffix : t -> t -> bool`

`val contains : sub:t -> t -> bool`

`val take : [int](../index.html#type-int) -> t -> t`

`val drop : [int](../index.html#type-int) -> t -> t`


==================================================
Content from: List
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » List

# Module `Imandra_prelude.List`

  * List module



### List module

This module contains many safe functions for manipulating lists.

`type 'a t = 'a [list](../index.html#type-list)`

`val empty : 'a [list](../index.html#type-list)`

`val is_empty : 'a [list](../index.html#type-list) -> bool`

Test whether a list is empty

`val cons : 'a -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

`cons x l` prepends `x` to the beginning of `l`, returning a new list

`val return : 'a -> 'a [list](../index.html#type-list)`

Singleton list

`val hd : 'a list -> 'a`

Partial function to access the head of the list. This function will fail when applied to the empty list. **NOTE** it is recommended to rely on pattern matching instead

`val tl : 'a list -> 'a list`

Partial function to access the tail of the list. This function will fail when applied to the empty list **NOTE** it is recommended to rely on pattern matching instead

`val append : 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

List append / concatenation. `append l1 l2` returns a list composed of all elements of `l1`, followed by all elements of `l2`

`val append_to_nil : 'a [list](../index.html#type-list) -> bool`

`val append_single : 'a -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list) -> bool`

`val rev : 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

Reverse a list

`val length : 'a [list](../index.html#type-list) -> Z.t`

Compute the length of a list. Linear time.

`val len_nonnegative : 'a [list](../index.html#type-list) -> bool`

`val len_zero_is_empty : 'a [list](../index.html#type-list) -> bool`

`val split : ('a * 'b) [list](../index.html#type-list) -> 'a [list](../index.html#type-list) * 'b [list](../index.html#type-list)`

Split a list of pairs into a pair of lists

`val map : ( 'a -> 'b ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list)`

Map a function over a list.

  * `map f [] = []`
  * `map f [x] = [f x]`
  * `map f (x :: tail) = f x :: map f tail`



`val map2 : ( 'a -> 'b -> 'c ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list) -> ( 'c [list](../index.html#type-list), string ) [result](../index.html#type-result)`

`val for_all : ( 'a -> bool ) -> 'a [list](../index.html#type-list) -> bool`

`for_all f l` tests whether all elements of `l` satisfy the predicate `f`

`val exists : ( 'a -> bool ) -> 'a [list](../index.html#type-list) -> bool`

`exists f l` tests whether there is an element of `l` that satisfies the predicate `f`

`val fold_left : ( 'a -> 'b -> 'a ) -> 'a -> 'b [list](../index.html#type-list) -> 'a`

Fold-left, with an accumulator that makes induction more challenging

`val fold_right : ( 'a -> 'b -> 'b ) -> base:'b -> 'a [list](../index.html#type-list) -> 'b`

Fold-right, without accumulator. This is generally more friendly for induction than `fold_left`.

`val mapi_with : base:Z.t -> ( Z.t -> 'a -> 'b ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list)`

`val mapi : ( Z.t -> 'a -> 'b ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list)`

`val filter : ( 'a -> bool ) -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

`filter f l` keeps only the elements of `l` that satisfy `f`.

`val filter_map : ( 'a -> 'b [option](../index.html#type-option) ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list)`

`val flat_map : ( 'a -> 'b [list](../index.html#type-list) ) -> 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list)`

`val find : ( 'a -> bool ) -> 'a [list](../index.html#type-list) -> 'a [option](../index.html#type-option)`

`find f l` returns `Some x` if `x` is the first element of `l` such that `f x` is true. Otherwise it returns `None`

`val mem : 'a -> 'a [list](../index.html#type-list) -> bool`

`mem x l` returns `true` iff `x` is an element of `l`

`val mem_assoc : 'a -> ('a * 'b) [list](../index.html#type-list) -> bool`

`val nth : Z.t -> 'a [list](../index.html#type-list) -> 'a [option](../index.html#type-option)`

`val assoc : 'a -> ('a * 'b) [list](../index.html#type-list) -> 'b [option](../index.html#type-option)`

`val take : [int](../index.html#type-int) -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

`take n l` returns a list composed of the first (at most) `n` elements of `l`. If `length l <= n` then it returns `l`

`val drop : [int](../index.html#type-int) -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

`drop n l` returns `l` where the first (at most) `n` elements have been removed. If `length l <= n` then it returns `[]`

`val (--) : [int](../index.html#type-int) -> [int](../index.html#type-int) -> [int](../index.html#type-int) [list](../index.html#type-list)`

Integer range. `i -- j` is the list `[i; i+1; i+2; …; j-1]`. Returns the empty list if `i >= j`.

`val insert_sorted : leq:( 'a -> 'a -> bool ) -> 'a -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

Insert `x` in `l`, keeping `l` sorted.

`val sort : leq:( 'a -> 'a -> bool ) -> 'a [list](../index.html#type-list) -> 'a [list](../index.html#type-list)`

Basic sorting function

`val is_sorted : leq:( 'a -> 'a -> bool ) -> 'a [list](../index.html#type-list) -> bool`

Check whether a list is sorted, using the `leq` small-or-equal-than predicatet

`val monoid_product : 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list) -> ('a * 'b) [list](../index.html#type-list)`

`val (>|=) : 'a [list](../index.html#type-list) -> ( 'a -> 'b ) -> 'b [list](../index.html#type-list)`

`val (>>=) : 'a [list](../index.html#type-list) -> ( 'a -> 'b [list](../index.html#type-list) ) -> 'b [list](../index.html#type-list)`

`val let+ : 'a [list](../index.html#type-list) -> ( 'a -> 'b ) -> 'b [list](../index.html#type-list)`

`val and+ : 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list) -> ('a * 'b) [list](../index.html#type-list)`

`val let* : 'a [list](../index.html#type-list) -> ( 'a -> 'b [list](../index.html#type-list) ) -> 'b [list](../index.html#type-list)`

`val and* : 'a [list](../index.html#type-list) -> 'b [list](../index.html#type-list) -> ('a * 'b) [list](../index.html#type-list)`


==================================================
Content from: Map
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Map

# Module `Imandra_prelude.Map`

`type (+'a, 'b) t`

`val const : 'b -> ( _, 'b ) t`

`val add : 'a -> 'b -> ( 'a, 'b ) t -> ( 'a, 'b ) t`

`val add' : ( 'a, 'b ) t -> 'a -> 'b -> ( 'a, 'b ) t`

`val get : 'a -> ( 'a, 'b ) t -> 'b`

`val get' : ( 'a, 'b ) t -> 'a -> 'b`

`val get_default : ( _, 'b ) t -> 'b`

`val of_list : default:'b -> ('a * 'b) [list](../index.html#type-list) -> ( 'a, 'b ) t`

`val filter_map : default:( 'b -> 'c ) -> f:( 'a -> 'b -> 'c [option](../index.html#type-option) ) -> ( 'a, 'b ) t -> ( 'a, 'c ) t`

`val for_all : default:( 'b -> bool ) -> f:( 'a -> 'b -> bool ) -> ( 'a, 'b ) t -> bool`

`val merge : default:( 'b -> 'c -> 'd ) -> f_both:( 'a -> 'b -> 'c -> 'd [option](../index.html#type-option) ) -> f1:( 'a -> 'b -> 'd [option](../index.html#type-option) ) -> f2:( 'a -> 'c -> 'd [option](../index.html#type-option) ) -> ( 'a, 'b ) t -> ( 'a, 'c ) t -> ( 'a, 'd ) t`

`val extract : ( 'a, 'b ) t -> ('a * 'b) [list](../index.html#type-list) * 'b`

`val pp : 'a [printer](../index.html#type-printer) -> 'b [printer](../index.html#type-printer) -> ( 'a, 'b ) t [printer](../index.html#type-printer)`


==================================================
Content from: Multiset
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Multiset

# Module `Imandra_prelude.Multiset`

  * Multiset



### Multiset

A multiset is a collection of elements that don't have any particular order, but can occur several times (unlike a regular set).

`type +'a t = ( 'a, [int](../index.html#type-int) ) [Map.t](../Map/index.html#type-t)`

`val empty : 'a t`

`val add : 'a -> 'a t -> 'a t`

`val remove : 'a -> 'a t -> 'a t`

`val mem : 'a -> 'a t -> bool`

`val find : 'a -> 'a t -> [int](../index.html#type-int)`

`val of_list : 'a [list](../index.html#type-list) -> 'a t`


==================================================
Content from: Option
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Option

# Module `Imandra_prelude.Option`

  * Option module



### Option module

The option type `type 'a option = None | Some of 'a` is useful for representing partial functions and optional values.

`type 'a t = 'a [option](../index.html#type-option)`

`val map : ( 'a -> 'b ) -> 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option)`

Map over the option.

  * `map f None = None`
  * `map f (Some x) = Some (f x)`



`val map_or : default:'a -> ( 'b -> 'a ) -> 'b [option](../index.html#type-option) -> 'a`

`val is_some : 'a [option](../index.html#type-option) -> bool`

Returns `true` iff the argument is of the form `Some x`

`val is_none : 'a [option](../index.html#type-option) -> bool`

Returns `true` iff the argument is `None`

`val return : 'a -> 'a [option](../index.html#type-option)`

Wrap a value into an option. `return x = Some x`

`val (>|=) : 'a [option](../index.html#type-option) -> ( 'a -> 'b ) -> 'b [option](../index.html#type-option)`

Infix alias to `map`

`val flat_map : ( 'a -> 'b [option](../index.html#type-option) ) -> 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option)`

Monadic operator, useful for chaining multiple optional computations

`val (>>=) : 'a [option](../index.html#type-option) -> ( 'a -> 'b [option](../index.html#type-option) ) -> 'b [option](../index.html#type-option)`

Infix monadic operator, useful for chaining multiple optional computations together. It holds that `(return x >>= f) = f x`

`val or_ : else_:'a [option](../index.html#type-option) -> 'a [option](../index.html#type-option) -> 'a [option](../index.html#type-option)`

Choice of a value

  * `or_ ~else_:x None = x`
  * `or_ ~else_:x (Some y) = Some y`



`val (<+>) : 'a [option](../index.html#type-option) -> 'a [option](../index.html#type-option) -> 'a [option](../index.html#type-option)`

`val exists : ( 'a -> bool ) -> 'a [option](../index.html#type-option) -> bool`

`val for_all : ( 'a -> bool ) -> 'a [option](../index.html#type-option) -> bool`

`val get_or : default:'a -> 'a [option](../index.html#type-option) -> 'a`

`val fold : ( 'a -> 'b -> 'a ) -> 'a -> 'b [option](../index.html#type-option) -> 'a`

`val (<$>) : ( 'a -> 'b ) -> 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option)`

`f <$> x = map f x`

`val monoid_product : 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option) -> ('a * 'b) [option](../index.html#type-option)`

`val let+ : 'a [option](../index.html#type-option) -> ( 'a -> 'b ) -> 'b [option](../index.html#type-option)`

`val and+ : 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option) -> ('a * 'b) [option](../index.html#type-option)`

`val let* : 'a [option](../index.html#type-option) -> ( 'a -> 'b [option](../index.html#type-option) ) -> 'b [option](../index.html#type-option)`

`val and* : 'a [option](../index.html#type-option) -> 'b [option](../index.html#type-option) -> ('a * 'b) [option](../index.html#type-option)`


==================================================
Content from: Ordinal
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Ordinal

# Module `Imandra_prelude.Ordinal`

We need to define ordinals before any recursive function is defined, because ordinals are used for termination proofs.

`type t = ``| Int of [int](../index.html#type-int)`  
---  
`| Cons of t * [int](../index.html#type-int) * t`  
  
`val pp : Stdlib.Format.formatter -> t -> unit`

`val of_int : [int](../index.html#type-int) -> t`

`val (~$) : [int](../index.html#type-int) -> t`

`val (<<) : t -> t -> bool`

`val plus : t -> t -> t`

`val simple_plus : t -> t -> t`

`val (+) : t -> t -> t`

`val of_list : t [list](../index.html#type-list) -> t`

`val pair : t -> t -> t`

`val triple : t -> t -> t -> t`

`val quad : t -> t -> t -> t -> t`

`val shift : t -> by:t -> t`

`val is_valid : t -> bool`

`val is_valid_rec : t -> bool`

`val zero : t`

`val one : t`

`val omega : t`

`val omega_omega : t`


==================================================
Content from: Peano_nat
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Peano_nat

# Module `Imandra_prelude.Peano_nat`

  * Natural numbers



### Natural numbers

`type t = ``| Z`  
---  
`| S of t`  
  
`val zero : t`

`val succ : t -> t`

`val of_int : [int](../index.html#type-int) -> t`

Turn this integer into a natural number. Negative integers map to zero.

`val to_int : t -> [int](../index.html#type-int)`

Turn this natural number into a native integer.

`val plus : t -> t -> t`

Peano addition

`val leq : t -> t -> bool`

Comparison

`val (=) : 'a -> 'a -> bool`

`val (<=) : t -> t -> bool`

`val (+) : t -> t -> t`


==================================================
Content from: Pervasives
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Pervasives

# Module `Imandra_prelude.Pervasives`


==================================================
Content from: Real
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Real

# Module `Imandra_prelude.Real`

`type t = [real](../index.html#type-real)`

`val of_int : [int](../index.html#type-int) -> t`

`val to_int : t -> [int](../index.html#type-int)`

`val (+) : t -> t -> t`

`val (-) : t -> t -> t`

`val (~-) : t -> t`

`val (*) : t -> t -> t`

`val (/) : t -> t -> t`

`val (<) : t -> t -> bool`

`val (<=) : t -> t -> bool`

`val (>) : t -> t -> bool`

`val (>=) : t -> t -> bool`

`val abs : t -> t`

`val min : t -> t -> t`

`val max : t -> t -> t`

`val mk_of_float : [float](../index.html#type-float) -> t`

`val mk_of_q : t -> t`

`val mk_of_string : [string](../index.html#type-string) -> t`

`val to_float : t -> [float](../index.html#type-float)`

`val of_float : [float](../index.html#type-float) -> t`

`val compare : t -> t -> [Caml.Int.t](../Caml/Int/index.html#type-t)`

`val pp : Stdlib.Format.formatter -> t -> [unit](../index.html#type-unit)`

`val to_string : t -> [string](../index.html#type-string)`

`val to_string_approx : t -> [string](../index.html#type-string)`


==================================================
Content from: Reflect
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Reflect

# Module `Imandra_prelude.Reflect`

### Reflection

`module [Uid](Uid/index.html) : sig ... end`

`module [Type](Type/index.html) : sig ... end`

`module [Var](Var/index.html) : sig ... end`

`module [Term](Term/index.html) : sig ... end`


==================================================
Content from: Result
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Result

# Module `Imandra_prelude.Result`

`type ('a, 'b) t = ( 'a, 'b ) [result](../index.html#type-result)`

`val return : 'a -> ( 'a, 'b ) [result](../index.html#type-result)`

`val fail : 'a -> ( 'b, 'a ) [result](../index.html#type-result)`

`val map : ( 'a -> 'b ) -> ( 'a, 'c ) [result](../index.html#type-result) -> ( 'b, 'c ) [result](../index.html#type-result)`

`val map_err : ( 'a -> 'b ) -> ( 'c, 'a ) [result](../index.html#type-result) -> ( 'c, 'b ) [result](../index.html#type-result)`

`val get_or : ( 'a, 'b ) [result](../index.html#type-result) -> default:'a -> 'a`

`val map_or : ( 'a -> 'b ) -> ( 'a, 'c ) [result](../index.html#type-result) -> default:'b -> 'b`

`val (>|=) : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'a -> 'c ) -> ( 'c, 'b ) [result](../index.html#type-result)`

`val flat_map : ( 'a -> ( 'b, 'c ) [result](../index.html#type-result) ) -> ( 'a, 'c ) [result](../index.html#type-result) -> ( 'b, 'c ) [result](../index.html#type-result)`

`val (>>=) : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'a -> ( 'c, 'b ) [result](../index.html#type-result) ) -> ( 'c, 'b ) [result](../index.html#type-result)`

`val fold : ok:( 'a -> 'b ) -> error:( 'c -> 'b ) -> ( 'a, 'c ) [result](../index.html#type-result) -> 'b`

`val is_ok : ( 'a, 'b ) [result](../index.html#type-result) -> bool`

`val is_error : ( 'a, 'b ) [result](../index.html#type-result) -> bool`

`val monoid_product : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'c, 'b ) [result](../index.html#type-result) -> ( 'a * 'c, 'b ) [result](../index.html#type-result)`

`val let+ : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'a -> 'c ) -> ( 'c, 'b ) [result](../index.html#type-result)`

`val and+ : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'c, 'b ) [result](../index.html#type-result) -> ( 'a * 'c, 'b ) [result](../index.html#type-result)`

`val let* : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'a -> ( 'c, 'b ) [result](../index.html#type-result) ) -> ( 'c, 'b ) [result](../index.html#type-result)`

`val and* : ( 'a, 'b ) [result](../index.html#type-result) -> ( 'c, 'b ) [result](../index.html#type-result) -> ( 'a * 'c, 'b ) [result](../index.html#type-result)`


==================================================
Content from: Set
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Set

# Module `Imandra_prelude.Set`

`type +'a t = ( 'a, bool ) [Map.t](../Map/index.html#type-t)`

`val empty : 'a t`

`val is_valid : _ t -> bool`

`val is_empty : _ t -> bool`

`val mem : 'a -> 'a t -> bool`

`val add : 'a -> 'a t -> 'a t`

`val remove : 'a -> 'a t -> 'a t`

`val subset : 'a t -> 'a t -> bool`

`val union : 'a t -> 'a t -> 'a t`

`val complement : 'a t -> 'a t`

`val inter : 'a t -> 'a t -> 'a t`

`val diff : 'a t -> 'a t -> 'a t`

`val (++) : 'a t -> 'a t -> 'a t`

`val (--) : 'a t -> 'a t -> 'a t`

`val of_list : 'a [list](../index.html#type-list) -> 'a t`

`val to_list : 'a t -> 'a [list](../index.html#type-list)`

`val pp : 'a [printer](../index.html#type-printer) -> 'a t [printer](../index.html#type-printer)`


==================================================
Content from: Stdlib
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Stdlib

# Module `Imandra_prelude.Stdlib`


==================================================
Content from: String
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » String

# Module `Imandra_prelude.String`

  * Byte strings



### Byte strings

These strings correspond to OCaml native strings, and do not have a particular unicode encoding.

Rather, they should be seen as sequences of bytes, and it is also this way that Imandra considers them.

`type t = [string](../index.html#type-string)`

`val empty : t`

`val length : t -> [int](../index.html#type-int)`

`val make : [Caml.Int.t](../Caml/Int/index.html#type-t) -> char -> t`

`val append : t -> t -> t`

`val get : t -> [Caml.Int.t](../Caml/Int/index.html#type-t) -> char`

`val concat : t -> t [list](../index.html#type-list) -> t`

`val prefix : t -> t -> bool`

`val suffix : t -> t -> bool`

`val contains : t -> sub:t -> bool`

`val unsafe_sub : t -> [int](../index.html#type-int) -> [int](../index.html#type-int) -> t`

`val sub : t -> [int](../index.html#type-int) -> [int](../index.html#type-int) -> t [option](../index.html#type-option)`

`val of_int : [int](../index.html#type-int) -> t`

`val to_int : t -> [int](../index.html#type-int) [option](../index.html#type-option)`

`val is_int : t -> bool`

`val is_nat : t -> bool`

`val to_nat : t -> [int](../index.html#type-int) [option](../index.html#type-option)`


==================================================
Content from: Sys
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Sys

# Module `Imandra_prelude.Sys`

`val ocaml_version : string`


==================================================
Content from: Unix
==================================================

[Up](../index.html) – [imandra-base](../../index.html) » [Imandra_prelude](../index.html) » Unix

# Module `Imandra_prelude.Unix`
