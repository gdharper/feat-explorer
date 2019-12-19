# Schema Validation

This library is used to validate whether a given string * string association list
matches a given schema. The schema defines four categories of constraints for
the association list: required terms, optional terms, term values, and
value separators.

## Schema Definition.

Each constraint is defined by a string of the format defined by the context-free
grammar enumerated [here](constraint_definition.enbf).

All whitespace within a constraint definition is ignored, and individual constraint
definitions are separated by whitespace. When mutiple constraint definitions
provide a definition for the same keyword, only the final definition applies.

## Schema Constraints

A given schema is defined by four sets of constraints:

### Required Terms

Denoted by definitions which define the 'required' keyword.

All terms of this constraint MUST be present in the association list as the key
to a non-empty, non-whtespace value.

### Optional Terms

Denoted by definitions which define the 'optional' keyword.

All keys in the association list MUST be present as a term in either the optional
terms constraint or the required terms constraint.

Only terms present in the optional terms constraint MAY be keys to empty or
purely-whitespace values

### Term Values

Denoted by defnitions which define the keywords containing the string literal
'values'.

Term value constraints take two forms: general and specific.

#### General Term Values

Denoted by definitions which define the 'values' keyword.

All values in the association list MUST be present as a term in this constraint.

#### Specific Term Values

Denoted by definitions which define keywords containing the string literal 'values.'

All values in the association list pointed to by the key formed from the latter
component of the keyword MUST be present as a term in this constraint

### Value Separators

Denoted by definitions which define keywords containing the string literal 'separator'.

Value separator constraints can be either general or specifc.

#### General Value Separators

Denoted by definitions which define the 'separator' keyword.

If defined, all values in the association list MAY take the form of collections of
values concatenated by the character literal given in the definition.

#### Specific Value Separators

Denoted by definitions which define keywords containing the string literal 'separator.'

All values in the association list pointed to by he key formed from the latter
component of the keyword MAY take the form of collections of values concatenated
by the character literal given in the definition.


