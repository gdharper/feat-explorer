
type t = string list list
exception Malformed_csv of string

val of_strings : string list -> t

val of_string : string -> t

val of_in_channel : in_channel -> t

val of_path : string -> t

