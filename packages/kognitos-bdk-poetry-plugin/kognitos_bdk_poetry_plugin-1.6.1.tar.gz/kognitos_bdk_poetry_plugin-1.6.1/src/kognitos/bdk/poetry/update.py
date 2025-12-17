import requests
import semver
from poetry.console.commands.command import Command
from poetry.utils.env import EnvManager
from rich.console import Console

console = Console()


def sort_semver_tags(image_tags):
    return sorted(image_tags, key=semver.VersionInfo.parse, reverse=True)


def is_valid_semver_tag(tag):
    try:
        semver.VersionInfo.parse(tag)
        return True
    except ValueError:
        return False


def get_latest_bdk_runtime_version(image_repository):
    url = f"https://hub.docker.com/v2/repositories/{image_repository}/tags/?page_size=10&ordering=last_updated"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        return None
    image_tags = [result["name"] for result in data["results"]]
    semver_tags = filter(is_valid_semver_tag, image_tags)
    sorted_tags = sort_semver_tags(semver_tags)

    if sorted_tags:
        latest_tag = sorted_tags[0]
        return latest_tag
    return None


def get_tag_without_prerelease(tag):
    return tag.split("-")[0]


class UpdateCommand(Command):
    name = "bdk update"
    description = "Update BDK runtime from the current active virtual environment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._container = None

    def handle(self) -> int:
        console.log("[bold blue]Loading up virtual environment...[/bold blue]")
        env = EnvManager(self.poetry).get()
        console.log(f"[bold blue]Virtual Environment: [/bold blue][bold green]{env.path}[/bold green]")

        console.log("[bold blue]Fetching latest BDK runtime version from DockerHub...[/bold blue]")

        latest_tag = get_latest_bdk_runtime_version(image_repository="kognitosinc/bdk")

        if not latest_tag:
            console.log("[bold red]Failed to fetch BDK runtime latest version[/bold red]")
            return 1

        current_bdk_runtime_version = self.poetry.pyproject.data.get("environment", {}).get("bdk_runtime_version")

        console.log(f"[bold blue]Current BDK runtime version: {current_bdk_runtime_version}[/bold blue]")

        tag_without_prerelease = get_tag_without_prerelease(latest_tag)

        if current_bdk_runtime_version == tag_without_prerelease:
            console.log("[bold blue]Current BDK runtime version is up-to-date[/bold blue]")
            return 0

        console.log("[bold blue]Updating pyproject.toml with latest BDK runtime version...[/bold blue]")

        if "environment" not in self.poetry.pyproject.data:
            console.log("[bold blue]Environment section not found in pyproject.toml, creating it...[/bold blue]")
            self.poetry.pyproject.data["environment"] = {}

        self.poetry.pyproject.data["environment"]["bdk_runtime_version"] = tag_without_prerelease  # type: ignore
        self.poetry.pyproject.file.write(self.poetry.pyproject.data)

        console.log(
            f"[bold blue]pyproject.toml updated successfully with BDK runtime version {tag_without_prerelease}[/bold blue]"
        )
        return 0
