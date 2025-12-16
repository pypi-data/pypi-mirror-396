# Scenario with a validator agent (interactive), a generator agent (with a LLM), and a manager agent.

This example shows a manager agent that talks with a LLM agent and 
to a validator interactive agent
to build a list of requirements from a short specification.

## Validator agent

The interactive validator agent is shipped in the a2a-acl package (programmed in python, not in AgentSpeak).

```bash
  python3 PATH/TO/hot_repository/run_validator_agent.py
```
The validator agent runs on port 9999.


## Generator agent

The generator agent is an A2A/ACL agent programmed in AgentSpeak that uses an LLM to generate atomic requirements.
Each request to that agent generates exactly one requirement.

Run the generator agent :

```bash
  python3 run_requirement_generator.py 
```

The generator agent runs on port 9990.

## Manager agent

The manager agents send requests to the generator agent, then submits the result to the validator agent.
After reply from the validator agent, according to the answer, the manager will either stop, or ask new inputs to the generator.

Run the manager agent:

```bash
    python3 run_manager.py 
```

The manager agent runs on port 9981.

### Parameters

* The specification is defined in `manager.asl` .
