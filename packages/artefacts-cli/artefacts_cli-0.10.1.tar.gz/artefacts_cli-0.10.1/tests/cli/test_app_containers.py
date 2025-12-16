import pytest

from artefacts.cli.app_containers import containers


@pytest.mark.skip(
    reason="Change from Click 8.2.0. This now shows a help menu and returns status 2"
)
def test_container_package_exists(cli_runner):
    result = cli_runner.invoke(containers, [])
    assert result.exit_code == 0


def test_container_package_build_specific_dockerfile(
    cli_runner, dockerfile_available, docker_mocker
):
    dockerfile = "non_standard_dockerfile"
    result = cli_runner.invoke(containers, ["build", "--dockerfile", dockerfile])
    dockerfile_available.assert_any_call(dockerfile)
    assert result.exit_code == 0


def test_container_package_build(
    cli_runner, dockerfile_available, docker_mocker, sample_artefacts_config
):
    before = len(docker_mocker.images())
    result = cli_runner.invoke(containers, ["build"])
    assert result.exit_code == 0
    assert len(docker_mocker.images()) == before + len(sample_artefacts_config["jobs"])
    for job_name in sample_artefacts_config["jobs"]:
        # Check the images exist, with name following our naming convention project/job_name
        assert (
            docker_mocker.get_image(
                f"{sample_artefacts_config['project'].lower()}/{job_name}"
            )
            is not None
        )
