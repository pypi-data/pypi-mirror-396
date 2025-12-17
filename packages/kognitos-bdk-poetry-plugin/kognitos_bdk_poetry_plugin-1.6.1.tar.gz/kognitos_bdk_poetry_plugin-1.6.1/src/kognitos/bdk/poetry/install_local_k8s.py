import shutil
import subprocess
from pathlib import Path
from typing import Optional

import yaml
from cleo.helpers import option
from poetry.console.commands.command import Command
from rich.console import Console

console = Console()


class InstallLocalCommand(Command):
    name = "bdk install-local-k8s"
    description = "Install a local book into a kind cluster"

    options = [
        option(
            "cluster",
            "The name of the kind cluster",
            flag=False,
            value_required=False,
        ),
        option(
            "book-name",
            "The name of the book (overrides pyproject.toml [tool.poetry].name or [environment].repo_name)",
            flag=False,
            value_required=False,
        ),
        option(
            "book-version",
            "The version tag for the book (overrides pyproject.toml [tool.poetry].version, defaults to 0.0.1-local)",
            flag=False,
            value_required=False,
        ),
        option(
            "namespace",
            "The Kubernetes namespace (defaults to bdk)",
            flag=False,
            default="bdk",
            value_required=False,
        ),
    ]

    def _normalize_book_name(self, name: str) -> str:
        """Normalize book name by replacing underscores with hyphens for Kubernetes compatibility."""
        return name.replace("_", "-")

    def _get_book_name_from_pyproject(self) -> Optional[str]:
        """Get book name from pyproject.toml, preferring [tool.poetry].name over [environment].repo_name."""
        # First try [tool.poetry].name
        name = self.poetry.pyproject.data.get("tool", {}).get("poetry", {}).get("name")
        if name:
            return str(name)

        # Fall back to [environment].repo_name
        repo_name = self.poetry.pyproject.data.get("environment", {}).get("repo_name")
        if repo_name:
            return str(repo_name)
        return None

    def _get_version_from_pyproject(self) -> Optional[str]:
        """Get version from pyproject.toml [tool.poetry].version."""
        version = self.poetry.pyproject.data.get("tool", {}).get("poetry", {}).get("version")
        if version:
            return str(version)
        return None

    def _get_cluster_from_kubectl(self) -> Optional[str]:
        """Get the current cluster name from kubectl config current-context."""
        try:
            result = subprocess.run(
                ["kubectl", "config", "current-context"],
                capture_output=True,
                text=True,
                check=True,
            )
            context = result.stdout.strip()
            if context:
                # For kind clusters, the context is typically "kind-<cluster-name>"
                if context.startswith("kind-"):
                    return context[5:]  # Remove "kind-" prefix
                return context
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return None
        return None

    def handle(self) -> int:
        cluster_name = self.option("cluster")
        if not cluster_name:
            cluster_name = self._get_cluster_from_kubectl()
            if not cluster_name:
                console.log("[bold red]Error: Could not determine cluster name[/bold red]")
                console.log("")
                console.log("Unable to get cluster from 'kubectl config current-context'.")
                console.log("Please ensure kubectl is configured or provide --cluster explicitly.")
                console.log("")
                console.log("[bold yellow]Usage:[/bold yellow]")
                console.log("  poetry bdk install-local-k8s")
                console.log("  poetry bdk install-local-k8s --cluster <cluster-name>")
                return 1

        book_path = Path.cwd()

        # Get book name: CLI option > pyproject.toml > directory name
        book_name = self.option("book-name")
        if not book_name:
            book_name = self._get_book_name_from_pyproject()
        if not book_name:
            book_name = book_path.name

        # Normalize book name (replace underscores with hyphens for Kubernetes compatibility)
        book_name = self._normalize_book_name(book_name)

        # Get version: CLI option > pyproject.toml > default
        version = self.option("version")
        if not version:
            version = self._get_version_from_pyproject()
        if not version:
            version = "0.0.1-local"

        runtime_version = self.poetry.pyproject.data.get("environment", {}).get("bdk_runtime_version")
        if runtime_version:
            runtime_version = str(runtime_version)

        namespace = self.option("namespace")
        image_tag = f"{book_name}:{version}"

        console.log("[bold blue]=== Installing local book ===[/bold blue]")
        console.log(f"[bold blue]Cluster:[/bold blue] {cluster_name}")
        console.log(f"[bold blue]Namespace:[/bold blue] {namespace}")
        console.log(f"[bold blue]Book path:[/bold blue] {book_path}")
        console.log(f"[bold blue]Book name:[/bold blue] {book_name}")
        console.log(f"[bold blue]Version:[/bold blue] {version}")
        console.log(f"[bold blue]Image tag:[/bold blue] {image_tag}")

        # 2. Remove pre-existing dist
        console.log("\n[bold blue]=== Removing pre-existing dist ===[/bold blue]")
        dist_path = book_path / "dist"
        if dist_path.exists():
            shutil.rmtree(dist_path)
        console.log("Done!")

        # 3. Build Docker image
        console.log("\n[bold blue]=== Building Docker image ===[/bold blue]")
        try:
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    image_tag,
                    "--build-arg",
                    f"BDK_RUNTIME_IMAGE_URI=docker.io/kognitosinc/bdk:{runtime_version}",
                    ".",
                ],
                cwd=book_path,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            console.log(f"[bold red]Failed to build Docker image: {e}[/bold red]")
            return 1

        # 4. Load into kind
        console.log("\n[bold blue]=== Loading image into kind ===[/bold blue]")
        try:
            subprocess.run(
                ["kind", "load", "docker-image", image_tag, "--name", cluster_name],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            console.log(f"[bold red]Failed to load image into kind: {e}[/bold red]")
            return 1

        # 5. Generate custom resources using crgen
        console.log("\n[bold blue]=== Generating custom resources ===[/bold blue]")
        custom_resources_path = book_path / "custom_resources.yaml"
        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--entrypoint",
                    "/var/runtime/crgen",
                    image_tag,
                    image_tag,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            if not result.stdout.strip():
                console.log("[bold red]Error: crgen produced no output[/bold red]")
                console.log("")
                console.log("This usually indicates that the books failed to load properly.")
                console.log("Possible causes:")
                console.log("  - Incompatible BDK runtime and API versions")
                console.log("  - Import errors in the book code")
                console.log("  - Missing dependencies")
                return 1
            custom_resources_path.write_text(result.stdout)
        except subprocess.CalledProcessError as e:
            console.log(f"[bold red]Failed to generate custom resources: {e}[/bold red]")
            if e.stderr:
                console.log(f"[bold red]Error output: {e.stderr}[/bold red]")
            return 1

        # 6. Create helm directory structure
        console.log("\n[bold blue]=== Creating Helm chart ===[/bold blue]")
        helm_path = book_path / "helm"
        if helm_path.exists():
            shutil.rmtree(helm_path)
        templates_path = helm_path / "templates"
        templates_path.mkdir(parents=True)

        # 7. Create Chart.yaml
        chart_yaml = {
            "apiVersion": "v2",
            "name": f"book-{book_name}",
            "description": f"Local build of {book_name}",
            "type": "application",
            "version": version,
            "appVersion": version,
            "annotations": {"bdk.protocol/version": "1.0.0"},
        }
        (helm_path / "Chart.yaml").write_text(yaml.dump(chart_yaml, default_flow_style=False))

        # 8. Create values.yaml
        values_yaml = {
            "image": {
                "repository": book_name,
                "tag": version,
                "pullPolicy": "Never",
            }
        }
        (helm_path / "values.yaml").write_text(yaml.dump(values_yaml, default_flow_style=False))

        # 9. Process the custom resources and split into template files
        console.log("\n[bold blue]=== Processing custom resources ===[/bold blue]")
        file_count = self._process_custom_resources(custom_resources_path, image_tag, templates_path)
        custom_resources_path.unlink()

        if file_count == 0:
            console.log("[bold red]No custom resources were generated[/bold red]")
            return 1

        # 10. Show what was generated
        console.log("\n[bold blue]=== Generated templates ===[/bold blue]")
        for template_file in sorted(templates_path.iterdir()):
            console.log(f"  {template_file.name}")

        # 12. Uninstall any existing versions of this book
        console.log(f"\n[bold blue]=== Removing existing versions of book-{book_name} ===[/bold blue]")
        try:
            result = subprocess.run(
                ["helm", "list", "-n", namespace, "--short"],
                capture_output=True,
                text=True,
                check=True,
            )
            for release in result.stdout.strip().split("\n"):
                if release.startswith(f"book-{book_name}"):
                    console.log(f"Uninstalling: {release}")
                    subprocess.run(
                        ["helm", "uninstall", release, "-n", namespace],
                        check=False,
                    )
        except subprocess.CalledProcessError:
            pass  # Ignore errors if no releases exist

        # 13. Install with Helm
        console.log("\n[bold blue]=== Installing Helm chart ===[/bold blue]")
        try:
            subprocess.run(
                [
                    "helm",
                    "upgrade",
                    "--install",
                    f"book-{book_name}",
                    str(helm_path),
                    "-n",
                    namespace,
                    "--set",
                    "image.pullPolicy=Never",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            console.log(f"[bold red]Failed to install Helm chart: {e}[/bold red]")
            return 1

        # 14. Cleanup generated helm directory
        console.log("\n[bold blue]=== Cleaning up ===[/bold blue]")
        shutil.rmtree(helm_path)
        console.log("Done!")

        console.log("\n[bold green]=== Book installed successfully! ===[/bold green]")
        console.log(f"To check installed books use: kubectl get book -n {namespace}")

        return 0

    def _process_custom_resources(self, custom_resources_path: Path, image_tag: str, templates_path: Path) -> int:
        """Process custom resources YAML to add Helm templating and split into template files."""
        content = custom_resources_path.read_text()

        # Use yaml.safe_load_all to properly handle multi-document YAML
        file_count = 0
        try:
            for resource in yaml.safe_load_all(content):
                if resource and isinstance(resource, dict):
                    if "metadata" in resource:
                        resource["metadata"]["namespace"] = '{{ .Release.Namespace | default "default" }}'

                        original_name = resource["metadata"].get("name", "")
                        spec_name = ""
                        spec_version = ""

                        if "spec" in resource:
                            spec_name = resource["spec"].get("name", "")
                            spec_version = resource["spec"].get("version", "")

                        if spec_name:
                            if "labels" not in resource["metadata"] or not isinstance(
                                resource["metadata"].get("labels"), dict
                            ):
                                resource["metadata"]["labels"] = {}
                            resource["metadata"]["labels"]["kognitos.com/book-name"] = spec_name
                            if spec_version:
                                resource["metadata"]["labels"]["kognitos.com/book-version"] = spec_version

                        if spec_name and spec_version:
                            templated_name = "{{ .Release.Name }}-" + spec_name + "-" + spec_version
                        elif spec_name:
                            templated_name = "{{ .Release.Name }}-" + spec_name
                        else:
                            templated_name = "{{ .Release.Name }}-" + original_name

                        resource["metadata"]["name"] = templated_name

                    self._template_image(resource, image_tag)

                    # Write each resource to its own template file
                    file_count += 1
                    template_file = templates_path / f"resource-{file_count}.yaml"
                    template_file.write_text(yaml.dump(resource, default_flow_style=False))

        except yaml.YAMLError as e:
            console.log(f"[bold red]Error parsing custom resources YAML: {e}[/bold red]")
            return 0

        return file_count

    def _template_image(self, obj, image_tag: str) -> None:
        """Recursively replace image tags with Helm template values."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "image" and isinstance(value, str) and value == image_tag:
                    obj[key] = "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
                elif isinstance(value, (dict, list)):
                    self._template_image(value, image_tag)
        elif isinstance(obj, list):
            for item in obj:
                self._template_image(item, image_tag)
