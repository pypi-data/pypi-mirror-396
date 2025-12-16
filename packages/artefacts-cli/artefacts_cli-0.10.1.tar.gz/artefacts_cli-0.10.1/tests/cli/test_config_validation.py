from artefacts.cli.app import (
    run,
)


class TestConfigValidation:
    def test_accept_valid_configuration(self, cli_runner, authorised_project_with_conf):
        result = cli_runner.invoke(
            run,
            ["simple_job", "--config", authorised_project_with_conf, "--dryrun"],
        )
        assert result.exit_code == 0

    def test_invalid_job_section(
        self, cli_runner, authorised_project_with_editable_conf
    ):
        authorised_project_with_editable_conf.update({"jobs": None})
        with authorised_project_with_editable_conf as config_path:
            result = cli_runner.invoke(
                run,
                ["simple_job", "--config", config_path, "--dryrun"],
            )
            assert result.exit_code == 2
            assert "Missing jobs definition" in result.output
