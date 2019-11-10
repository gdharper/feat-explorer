
type op = And | Or

type 'a filter = Leaf of 'a * bool | Clause of op * 'a filter * 'a filter

let apply filt f value = 
    let rec apply filt f value k =
        match filt with
        | Leaf (term,b) -> k ((f value term) = b)
        | Clause (o,l,r) -> apply l f value (fun l' ->
                apply r f value (fun r' -> match o with
                | And -> k (l' && r')
                | Or -> k (l' || r')))
    in apply filt r value (fun x -> x)

