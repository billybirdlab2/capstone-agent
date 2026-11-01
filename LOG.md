# Chunk structure note — Lab 5 Checkpoint B

Document: Learning programs by learning from failures  
Edition: 2020; arXiv v1  
Chunk: `popper_learning_from_failures:p020:03`  
Stored section: 4 Popper  
Stored starting page: 20  
Stored ending page: 21

## Stored text

```text
Popper is an implementation of our learning from failures id ea9. Popper works in three separate stages: generate, test, and constrain, as describ ed in Section 1. Algorithm 1 sketches the Popper algorithm which combines the three stag es. T o learn optimal so- lutions (Deﬁnition 14), Popper searches for programs of inc reasing size. We describe the generate, test, and constrain stages in detail, how we us e ASP’s multi-shot solving (Gebser et al., 2019) to maintain state between the three sta ges, and then prove the soundness and completeness of Popper . 9 Popper is only one implementation of our idea. The ﬂexibilit y of our three staged approach allows for a variety of algorithms, which we intend to explore in future work. Learning programs by learning from failures 21 Algorithm 1 Popper 1 def popper(e+, e−, bk, declarations, constraints, max_literals): 2 num_literals = 1 3 while num_literals ≤ max_literals: 4 program = generate(declarations, constraints, num_lite rals) 5 if program == /quotesingle.Varspace_exhausted/quotesingle.Var: 6 num_literals += 1 7 continue 8 outcome = test(e +, e−, bk, program) 9 if outcome == (/quotesingle.Varall_positive/quotesingle.Var, /quotesingle.Varnone_negative/quotesingle.Var) 10 return program 11 constraints += learn_constraints(program, outcome) 12 return {} Answer set programming. Popper uses ASP to generate logic programs. We brieﬂy intro- duce some ASP speciﬁc syntax and refer the reader to the excel lent book by Gebser et al. (2012) for more information about ASP . A literal is either an atom a or its default nega- tion not a . An ASP rule is of the form h:- b 1, . . ., b n. where h is an atom, each bi is a literal, h is the head, and b1, . . ., b n, is the body. A constraint is a rule without a head. A choice rule is of the form l{h1, . . ., h m}u :- b 1, . . ., b n. where l and u are integers denoting lower and upper bounds. For instance, 2{ a,b,c }3 asserts that at least two of a,b,c need to be true.
```

## Structural assessment
The chunk retains the generate–test–constrain description and document/edition/section/page metadata, but contains PDF extraction artifacts such as split words. It is a prose chunk, not evidence that numerical tables were preserved. The evaluation retained the text-parser index; no layout-parser comparison is claimed. The successful citation-checking test matched the stored extraction, which alone does not validate its semantic interpretation.

This note was prepared from the uploaded index. The student must inspect the cited original PDF page before recording personal confirmation in LOG.md.
