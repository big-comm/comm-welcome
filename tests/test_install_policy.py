from copy import deepcopy

import pytest
from comm_welcome.install_policy import browser_reference, validate_plan

REFERENCE = "alpm:extra/firefox"


@pytest.fixture
def plan():
    return {
        "sections": [
            {
                "planned_packages": [
                    {"ref": REFERENCE, "action": "install"},
                    {"ref": "alpm:extra/dependency", "action": "install"},
                ],
                "removes": [],
            }
        ]
    }


def test_native_install_with_dependency(plan):
    assert validate_plan(plan, REFERENCE)


@pytest.mark.parametrize(
    "reference",
    ["aur:firefox", "alpm:extra/bash", "firefox", "alpm:/firefox", "alpm:extra/firefox;rm"],
)
def test_unknown_reference_rejected(reference):
    assert not browser_reference(reference)


@pytest.mark.parametrize("action", ["remove", "downgrade", "build", "unknown"])
def test_disallowed_actions_rejected(plan, action):
    plan["sections"][0]["planned_packages"][1]["action"] = action
    assert not validate_plan(plan, REFERENCE)


def test_no_silent_removals_or_interactions(plan):
    changed = deepcopy(plan)
    changed["sections"][0]["removes"] = ["brave-browser"]
    assert not validate_plan(changed, REFERENCE)
    plan["preparation_interactions"] = [{"kind": "cascade-removal"}]
    assert not validate_plan(plan, REFERENCE)


@pytest.mark.parametrize(
    "plan", [{}, {"sections": []}, {"sections": {}}, {"sections": [{}]}, {"sections": [None]}]
)
def test_unknown_plan_shape_fails_closed(plan):
    assert not validate_plan(plan, REFERENCE)


def test_requested_browser_must_be_in_plan(plan):
    assert not validate_plan(plan, "alpm:extra/vivaldi")


def test_foreign_source_cannot_be_hidden_in_dependencies(plan):
    plan["sections"][0]["planned_packages"][1]["ref"] = "aur:dependency"
    assert not validate_plan(plan, REFERENCE)
