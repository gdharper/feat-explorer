
open String

let consume i s = sub s i ((length s) - i)

let rev_join sl = List.rev sl |> concat ""


type t = string list list
exception Malformed_csv of string

type parseState = U | Q | QQ | E
let parse row =
    let rec parse state toks acc l =
        match l,state with
        | "",U ->  acc
        | "",Q -> raise (Malformed_csv "Missing quote to close quoted column")
        | "",QQ -> ((rev_join toks) :: acc)
        | "",E -> ("" :: acc)
        | _,U ->
            if get l 0 = '"'
                then parse Q [] acc (consume 1 l)
            else
                (match index_opt l ',' with
                | None -> parse U [] (l::acc) "" (* == return l::acc *)
                | Some i -> parse
                                (if i = (length l) -1 then E else U)
                                [] ((sub l 0 i) :: acc) (consume (i+1) l))
        | _,Q ->
            (match index_opt l '"' with
            | None -> raise (Malformed_csv "Missing quote to end column")
            | Some i -> parse QQ ((sub l 0 i)::toks) acc (consume (i+1) l))
        | _,QQ ->
            (match get l 0 with
            | ',' -> parse U [] ((rev_join toks) :: acc) (consume 1 l)
            | '"' -> parse Q ("\"" :: toks) acc (consume 1 l)
            | _ -> raise (Malformed_csv "Invalid character after quote"))
        | _,E -> failwith l (* We don't expect any input to generate this case *)
    in parse U [] [] row |> List.rev

let of_strings strings = 
    strings
    |> List.rev_map trim
    |> List.filter (fun s -> s <> "")
    |> List.rev_map parse

let of_string s = s |> split_on_char '\n' |> of_strings

let of_in_channel ic = 
    let rec rl acc =
        match input_line ic with
        | l -> rl (l :: acc)
        | exception End_of_file -> acc
    in [] |> rl |> List.rev |> of_strings

let of_path path = 
    let ic = open_in path in
    let c = of_in_channel ic in
    close_in ic; c

