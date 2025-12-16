import pytest

import hashlib
import itertools
import subprocess

from artefacts.cli.core.code_environment import CodeEnvironment


@pytest.fixture(scope="function")
def ce_in_git_repository(mocker):
    path = "/test/path"
    mocker.patch("artefacts.cli.core.code_environment.os.getcwd", return_value=path)
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0),
    )
    return CodeEnvironment(), path, spy


@pytest.fixture(scope="function")
def ce_no_git(mocker):
    path = "/test/path"
    mocker.patch("artefacts.cli.core.code_environment.os.getcwd", return_value=path)
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=1),
    )
    return CodeEnvironment(), path, spy


@pytest.fixture(scope="function")
def some_git_commit_hash(mocker):
    """
    Return fake Git commit hash on subprocess call
    """
    h = hashlib.new("sha1")
    h.update(b"Nobody inspects the spammish repetition")
    fake_hash = h.hexdigest()
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.check_output",
        return_value=fake_hash.encode("ascii"),
    )
    return fake_hash


@pytest.fixture(scope="function")
def some_git_branch(mocker):
    """
    Return fake Git branch on subprocess call
    """
    fake_branch = "test_branch"
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.check_output",
        return_value=bytes(fake_branch.encode("ascii")),
    )
    return fake_branch


def test_init_git(ce_in_git_repository):
    ce, path, _ = ce_in_git_repository
    assert ce._cwd == path
    assert ce._is_git_memo is True


def test_init_non_git(ce_no_git):
    ce, path, _ = ce_no_git
    assert ce._cwd == path
    assert ce._is_git_memo is False


def test_is_git_repository_with_git_and_same_dir(ce_in_git_repository):
    ce, path, spy = ce_in_git_repository
    assert ce.is_git_repository() is True
    assert spy.call_count == 1


def test_is_git_repository_no_git_and_same_dir(ce_no_git):
    ce, path, spy = ce_no_git
    assert ce.is_git_repository() is False
    assert spy.call_count == 2


def test_is_git_repository_with_git_and_changed_dir_under_git(
    mocker, ce_in_git_repository
):
    ce, path, spy = ce_in_git_repository
    # Before next CE command, let's change dir.
    mocker.patch(
        "artefacts.cli.core.code_environment.os.getcwd", return_value="/test/path/sub"
    )
    assert ce.is_git_repository() is True
    assert ce._cwd == "/test/path/sub"
    assert spy.call_count == 2


def test_is_git_repository_with_git_and_changed_dir_outside_git(
    mocker, ce_in_git_repository
):
    ce, path, spy = ce_in_git_repository

    assert ce._is_git_memo is True

    # Change to a dir not managed Git
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=1),
    )
    mocker.patch(
        "artefacts.cli.core.code_environment.os.getcwd", return_value="/just/different"
    )
    assert ce.is_git_repository() is False
    assert ce._cwd == "/just/different"


def test_is_git_repository_no_git_and_changed_dir_to_git(mocker, ce_no_git):
    ce, path, spy = ce_no_git
    assert ce._is_git_memo is False

    # Change to a Git-managed dir
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0),
    )
    mocker.patch(
        "artefacts.cli.core.code_environment.os.getcwd", return_value="/just/different"
    )
    assert ce.is_git_repository() is True
    assert ce._cwd == "/just/different"


def test_is_git_repository_no_git_and_changed_dir_to_no_git(mocker, ce_no_git):
    ce, path, spy = ce_no_git
    assert ce._is_git_memo is False

    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=1),
    )
    mocker.patch(
        "artefacts.cli.core.code_environment.os.getcwd", return_value="/just/different"
    )
    assert ce.is_git_repository() is False
    assert ce._cwd == "/just/different"


def test_is_git_repository_subprocess_error(mocker):
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    mocker.patch(
        "artefacts.cli.core.code_environment.os.getcwd", return_value="/test/path"
    )
    with pytest.raises(Exception, match="Unable to interact with Git"):
        CodeEnvironment()


def test_get_git_revision_hash(mocker, ce_in_git_repository, some_git_commit_hash):
    ce, _, _ = ce_in_git_repository
    assert ce.get_git_revision_hash(short=True) == some_git_commit_hash[:8]
    assert ce.get_git_revision_hash(short=False) == some_git_commit_hash


def test_get_no_git_revision_hash(mocker, ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.get_git_revision_hash(short=True) is None
    assert ce.get_git_revision_hash(short=False) is None


def test_get_git_revision_hash_suprocess_error(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    with pytest.raises(Exception, match="Unable to interact with Git"):
        ce.get_git_revision_hash(short=True)
    with pytest.raises(Exception, match="Unable to interact with Git"):
        ce.get_git_revision_hash(short=False)


def test_get_git_revision_branch_in_git(ce_in_git_repository, some_git_branch):
    ce, _, _ = ce_in_git_repository
    assert ce.get_git_revision_branch() == some_git_branch


def test_get_git_revision_branch_no_git(ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.get_git_revision_branch() is None


def test_get_git_revision_branch_subprocess_error(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    with pytest.raises(Exception, match="Unable to interact with Git"):
        ce.get_git_revision_branch()


def test_has_unstaged_changes_with_changes_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=1),
    )
    assert ce.has_unstaged_changes() is True
    spy.assert_called()


def test_has_unstaged_changes_without_change_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0),
    )
    assert ce.has_unstaged_changes() is False
    spy.assert_called()


def test_has_unstaged_changes_subprocess_error_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    with pytest.raises(
        Exception, match="Unable to detect unstaged changes by interacting with Git"
    ):
        ce.has_unstaged_changes()


def test_has_unstaged_changes_no_git(ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.has_unstaged_changes() is None


def test_has_staged_changes_with_changes_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=1),
    )
    assert ce.has_staged_changes() is True
    spy.assert_called()


def test_has_staged_changes_without_change_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0),
    )
    assert ce.has_staged_changes() is False
    spy.assert_called()


def test_has_staged_changes_subprocess_error_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    with pytest.raises(
        Exception, match="Unable to detect staged changes by interacting with Git"
    ):
        ce.has_staged_changes()


def test_has_staged_changes_no_git(ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.has_staged_changes() is None


def test_has_untracked_changes_with_changes_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout="afile\n"),
    )
    assert ce.has_untracked_changes() is True
    spy.assert_called()


def test_has_untracked_changes_without_change_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout=""),
    )
    assert ce.has_untracked_changes() is False
    spy.assert_called()


def test_has_untracked_changes_subprocess_error_in_git(mocker, ce_in_git_repository):
    ce, _, _ = ce_in_git_repository
    mocker.patch(
        "artefacts.cli.core.code_environment.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "some_cmd"),
    )
    with pytest.raises(
        Exception, match="Unable to detect untracked changes by interacting with Git"
    ):
        ce.has_untracked_changes()


def test_has_untracked_changes_no_git(mocker, ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.has_untracked_changes() is None


def test_get_state_without_change_in_git(
    mocker, ce_in_git_repository, some_git_commit_hash
):
    ce, _, _ = ce_in_git_repository
    # Set Git change detection to find no change.
    spy1 = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_untracked_changes",
        return_value=False,
    )
    spy2 = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_unstaged_changes",
        return_value=False,
    )
    spy3 = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_staged_changes",
        return_value=False,
    )
    spy4 = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.get_git_revision_hash",
        return_value=some_git_commit_hash[:8],
    )
    assert ce.get_state() == some_git_commit_hash[:8]
    spy1.assert_called_once()
    spy2.assert_called_once()
    spy3.assert_called_once()
    spy4.assert_called_once()


def test_get_state_with_change_in_git(
    mocker, ce_in_git_repository, some_git_commit_hash
):
    ce, _, _ = ce_in_git_repository
    hash_finder = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.get_git_revision_hash"
    )
    untracked = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_untracked_changes"
    )
    unstaged = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_unstaged_changes"
    )
    staged = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.has_staged_changes"
    )

    # Cover all possible configurations of the SUT code: Git change
    # can be either untracked, unstaged or staged, but we don't know if order
    # matters, and we don't want the test to assume an order, so we test all
    # (only 6 permutations).
    for setter, unset1, unset2 in itertools.permutations([untracked, unstaged, staged]):
        # Set change detection on 1 of the checks, not the others.
        setter.return_value = True
        unset1.return_value = False
        unset2.return_value = False
        hash_finder.return_value = some_git_commit_hash[:8]

        # Conduct expected condition checking
        assert ce.get_state() == some_git_commit_hash[:8] + "~"
        setter.assert_called_once()
        hash_finder.assert_called_once()

        # Reset the code spy counts.
        for mock in [untracked, unstaged, staged, hash_finder]:
            mock.reset_mock(return_value=True)


def test_get_state_no_git(ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.get_state() is None


def test_get_state_no_git_with_override(mocker, ce_no_git, some_git_commit_hash):
    ce, _, _ = ce_no_git
    mocker.patch.dict(
        "artefacts.cli.core.code_environment.os.environ",
        {"ARTEFACTS_CODE_STATE": some_git_commit_hash},
    )
    assert ce.get_state() == some_git_commit_hash


def test_get_reference_in_git(mocker, ce_in_git_repository, some_git_branch):
    ce, _, _ = ce_in_git_repository
    spy = mocker.patch(
        "artefacts.cli.core.code_environment.CodeEnvironment.get_git_revision_branch",
        return_value=some_git_branch,
    )
    assert f"{some_git_branch}~" in ce.get_reference()
    spy.assert_called_once()


def test_get_reference_no_git(mocker, ce_no_git):
    ce, _, _ = ce_no_git
    assert ce.get_reference() is None


def test_get_reference_no_git_with_override(mocker, ce_no_git, some_git_branch):
    ce, _, _ = ce_no_git
    mocker.patch.dict(
        "artefacts.cli.core.code_environment.os.environ",
        {"ARTEFACTS_CODE_REFERENCE": some_git_branch},
    )
    assert ce.get_reference() == some_git_branch
