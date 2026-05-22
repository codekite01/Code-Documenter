import os
from crewai import Crew, Process
from agents.analyst import create_analyst_agent, create_analyse_task
from models.schemas import RepoMap, FileInfo

# Use the requests library (already cloned in phase 5 test)
repo_path = os.path.abspath('./tmp_repos/requests')

fake_map = RepoMap(
    repo_name='requests',
    repo_url='https://github.com/psf/requests',
    local_path=repo_path,
    languages=['Python'],
    directory_tree='requests/',
    key_files=[
        FileInfo(path='README.md', reason='Project overview', language='Markdown'),
        FileInfo(path='requests/__init__.py', reason='Entry point', language='Python'),
        FileInfo(path='requests/api.py', reason='Public API', language='Python'),
    ],
    entry_points=['requests/__init__.py'],
    has_tests=True,
    has_docker=False,
)

agent = create_analyst_agent()
task = create_analyse_task(agent, fake_map)
crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
result = crew.kickoff()

print('\n\n=== ANALYST OUTPUT ===')
r = result.pydantic
print('Project:', r.project_name)
print('Description:', r.one_line_description)
print('Tech stack:', r.tech_stack)
print('Features:', r.key_features)
