
type r = string list
type t = r list
exception Malformed_csv of string

type parseState = Init | UnQ | Q | QQ

let parse_line line = 
    let rec parse state tok acc line =
        match line with
        | h::t ->
            (match h,state with
            (* Init state *)
            | ',',Init -> parse Init [] ("" :: acc) t
            | '"',Init -> parse Q [] acc t
            | _,Init -> parse UnQ [h;] acc t
            (* Unquoted State *)
            | ',',UnQ -> parse Init []
                ((String.init (List.length tok) (List.nth (List.rev tok))) :: acc) t
            | '"',UnQ -> raise (Malformed_csv "Unexpected quote")
            | _,UnQ -> parse UnQ (h :: tok) acc t
            (* Quoted State *)
            | '"',Q -> parse QQ tok acc t
            | _,Q -> parse Q (h :: tok) acc t
            (* Double Quote State *)
            | ',',QQ -> parse Init []
                ((String.init (List.length tok) (List.nth (List.rev tok))) :: acc) t
            | '"',QQ -> parse Q ('"' :: tok) acc t
            | _,QQ -> raise (Malformed_csv "Unexpected character after quote"))
        | [] ->
            match state with
            | Init -> ("" :: acc)
            | UnQ
            | QQ -> ((String.init (List.length tok) (List.nth (List.rev tok))) :: acc)
            | Q -> raise (Malformed_csv "Missing quote to end line")
    in parse Init [] [] line
    |> List.rev

let of_strings strings =
    List.rev_map (fun s -> List.init (String.length s) (String.get s)) strings
    |> List.rev_map parse_line

let of_string s = 
    String.split_on_char '\n' s
    |> List.filter (fun s -> (String.trim s) <> "")
    |> of_strings

let of_in_channel ic = 
    let rec rl acc =
        match input_line ic with
        | l -> rl (l :: acc)
        | exception End_of_file -> acc
    in rl []
    |> List.filter (fun s -> (String.trim s) <> "")
    |> List.rev
    |> of_strings

let of_path path = 
    let ic = open_in path in
    let c = of_in_channel ic in
    close_in ic; c

