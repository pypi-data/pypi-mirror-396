# Scenario with a repository agent, a selector agent, and various solution agents for generation of requirements

This example shows a selector/orchestrator agent that talks with a repository of running agents to find an agent capable of building a list of requirements from a short specification.

## Repository

The repository is an A2A/ACL agent. It stores information about running A2A/ACL agents.

Run the repository server :

```bash
  python3 ../../hot_repository/run_hot_repository_server.py
```

## Selector agent

The selector/orchestrator agent is an A2A/ACL agent programmed in AgentSpeak (files `agent_selector.asl` and `agent_selector.asi`).

Run the selector agent :

```bash
  python3 run_asp_agent.py agent_selector 9980
```

## Solution agents

Several solution agents are running and will be registered on the repository. 
All those agents are A2A/ACL agents and programmed in AgentSpeak but AgentSpeak is optional here.

Run any number of agents among the following ones:

* **Failing agent** 

    An agent that always fail. Used to illustrate how the orchestrator will give the task to another agent when facing a failure, and how the repository will degrade the reputation of the failing agent in order to avoid to recommend it. 

    ```bash
    python3 run_asp_agent.py ../../sample_agents/requirement_generators/bad_requirement_manager 9993
    ```

* **Too simple agent**

    An agent that gives a result which is of bad quality.

    ```bash
    python3 run_asp_agent.py ../../sample_agents/requirement_generators/naive_requirement_manager 9995
    ```

* **Agent based on Mistral LLM**

    (Needs the `mistralai` package and a MISTRAL_API_KEY set.)

    ```bash
    python3 run_requirement_manager_agent_on_mistral.py
    ```

* **Agent based on OpenAI LLM**

    (Needs the `openai` package and a OPENAI_API_KEY set.)

    ```bash
    python3 run_requirement_manager_agent_on_openai.py
    ```

* **Agent that does something not related to requirements**

    That agent declares skills that are not related to generation of requirements. The repository will not recommend it because it does not meet the requested criteria. 

    ```bash
    python3 run_asp_agent.py ../../sample_agents/robots/robot 9990
    ```

* **Stub agent**

    That agent always return the same list of requirement, whatever the specification is.

    ```bash
    python3 run_asp_agent.py ../../sample_agents/requirement_generators/stub_requirement_manager 9996
    ```

## Start the process

The client first registers the solution agents in the repository, then it initiates the request to the orchestrator agent.

Run the client :

```bash
  python3 run_test_client.py
```

### Parameters

* The specification is defined in `context.py` .
* A sleep time is defined in `agent_selector.asl` . It is used by agents dealing with a LLM. Change that duration to relax or stress the rate limit of the LLM provider. 