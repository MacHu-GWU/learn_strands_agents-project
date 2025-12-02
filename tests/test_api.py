# -*- coding: utf-8 -*-

from learn_strands_agents import api


def test():
    _ = api


if __name__ == "__main__":
    from learn_strands_agents.tests import run_cov_test

    run_cov_test(
        __file__,
        "learn_strands_agents.api",
        preview=False,
    )
