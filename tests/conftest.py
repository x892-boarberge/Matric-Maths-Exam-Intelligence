"""
Pytest configuration.

The tutor can use an LLM for phrasing. Tests must not. Force the LLM
off for the entire test session so tests are fast and deterministic.
"""
import os


def pytest_configure(config):
    os.environ["MATRICMATH_LLM_OFF"] = "1"
