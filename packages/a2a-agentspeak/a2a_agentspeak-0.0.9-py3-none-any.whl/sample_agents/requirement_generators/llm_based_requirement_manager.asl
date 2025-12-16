!start.

# config
sleep_time(10). # milliseconds

# log
+!start <-
    .my_name(N) ;
    .print("Hello from", N).


# error
+spec(S) : spec(X) & X \== S <-
    .print("Warning: specification ignored because already dealing with a specification.").

# input
+spec(S)[source(F)] <-
    +from(F) ;
    .print("I received the specification to manage:", S).

# init
+!build : spec(S) & not req(_) <-
    .print("(Init) No list of requirements found, creating an empty list.");
    +req([]) ;
    !build.

# evaluate completeness
+!build : spec(S) & req(L) <-
    .print("Consulting LLM for evaluation.") ;
     .prompt_completeness(spec(S), req(L), RES) ;
    .print("Received", RES);
    if(RES == failure) { !reply_with_failure }
    else {
        ?sleep_time(T) ;
        .print("Sleeping" , T, "ms.") ;
        .wait(T) ;
        +completeness(RES)
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

# stop
+completeness(complete) : req(L) & from(F) <-
    .print("List of requirements complete:", L) ;
    .print("Sent to", F);
    .send(F, tell, reply(L)).

# continue
+completeness(incomplete) : spec(S) & req(L) <-
    .print("Consulting LLM for generation.") ;
    .prompt_generate(spec(S), req(L), RES) ;
    if(RES == failure) { !reply_with_failure }
    else {
        -req(L) ;
        +req([RES|L]) ;
         ?sleep_time(T) ;
        .print("Sleeping" , T, "ms.") ;
        .wait(T) ;
        !build
    }.

# error
+completeness(Other) <-
    .print ("other:", Other).

# log
+req(L) <-
    .print("Status of requirements:", L).

# log
+from(F) <-
    .print("Reply-to:", F).

# report failure
+!reply_with_failure : from(F) <-
    .print("Reporting failure.");
    .send(F, tell, failure).
