from backend.github.github_service import github_service

profile = github_service.analyze_candidate(
    "https://github.com/Krish-Puri"
)

print(profile)