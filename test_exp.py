
from crewai import Crew, Process
from agents.explorer import create_explorer_agent, create_explore_task

agent = create_explorer_agent()
task = create_explore_task(agent, 'https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning')

crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
result = crew.kickoff()

print('\n\n=== EXPLORER OUTPUT ===')
print(result.pydantic)
print('repo_name:', result.pydantic.repo_name)
print('languages:', result.pydantic.languages)
print('key_files:', len(result.pydantic.key_files), 'files identified')


