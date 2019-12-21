
type t

val of_string : string -> t
val of_in_channel : in_channel -> t
val of_path : string -> t

val validate : t -> string * string list -> bool

