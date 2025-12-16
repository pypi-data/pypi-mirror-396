!start.

# log
+!start <-
    .my_name(N) ;
    .print("Hello from", N).

+!reset : spec(S) & req_list(L) <-
    .print("Erasing previous data.");
    -spec(S) ;
    -req_list(L).

+!reset <- .print("Nothing to reset.").

# error
+spec(S) : spec(X) & X \== S <-
    .print("Warning: specification ignored because already dealing with a specification.").

# input
+spec(S)[source(F)] <-
    +from(F) ;
    .print("I received the specification to manage:", S).

+ req_list(L) <-
    .print("List of requirements received").

# evaluate completeness
+!build : spec(S) & req_list(L) <-
    .print("Consulting LLM.") ;
    .prompt_generate(spec(S), req(L), RES) ;
    if(RES == failure) { !report_failure }
    else {
        !reply(RES)
    }.

# error
+!build : from(F) & not spec(_) <-
   .print ("Unexpected case : no specification received (report failure).") ;
   !reply_with_failure(F).

# error
+!build : from(F) <-
   .print ("Unexpected case (report failure).") ;
   !reply_with_failure(F).

# error
+!build[source(F)]: not spec(_) <-
    .print ("Unexpected case : no specification received before build request from", F).

# error
+!build <-
    .print ("Unexpected case.").

+!reply(R): from(F) <-
    .print("Generated requirement: ", R) ;
    .print("Sent to: ", F);
    .send(F, tell, reply(R)).

# log
+from(F) <-
    .print("Reply-to:", F).

# report failure
+!report_failure : from(F) <-
    .print("Reporting failure.");
    .send(F, tell, failure).
