from backend.github.github_client import github_client

profile = github_client.get_user(
    "https://github.com/Krish-Puri"
)

print(profile)