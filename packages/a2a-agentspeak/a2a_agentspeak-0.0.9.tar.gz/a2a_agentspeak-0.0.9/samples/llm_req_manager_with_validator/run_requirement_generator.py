import context
from a2a_agentspeak import build_server
from sample_agents.requirement_generators import mistral_requirement_actions

if __name__ == "__main__":

    host = "127.0.0.1"
    name = "../../sample_agents/requirement_generators/atomic/llm_requirement_generator"

    build_server.build_and_run(
        name,
        host,
        context.generator_port,
        [
            mistral_requirement_actions.action_prompt_completeness,
            mistral_requirement_actions.action_prompt_generate,
        ],
    )
