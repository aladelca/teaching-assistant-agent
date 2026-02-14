def agents_complete(prompt, system, model):
    try:
        from agents import Agent, Runner
    except ImportError as exc:
        raise ImportError(
            "OpenAI Agents SDK no está instalado. Instala con: pip install openai-agents"
        ) from exc

    agent = Agent(
        name="Evaluador",
        instructions=system,
        model=model,
    )
    result = Runner.run_sync(starting_agent=agent, input=prompt)
    return result.final_output
