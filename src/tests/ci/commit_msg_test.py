"""Test commit msg validation."""

import unittest
import re

from . import cfg


class Constants(cfg.Constants):
    """Module specific constant values."""

    ValidMsgPattern = re.compile(
        r'^([mM]erge .*)$'
        '|'
        '(^'
        r'((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)!?: .+)'
        '('
        r'(\n\n(.+)\n\n)'
        r'((BREAKING CHANGE|DEPRECATED)(: )(.+)\n\n(.+)\n\n\n)?'
        r'(resolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+)'
        r'((, )(resolve[ds]? \#[A-Z0-9\-]+|fix(ed|es)? \#[A-Z0-9\-]+|close[ds]? \#[A-Z0-9\-]+))?'
        ')?'
        '$)'
        '|'
        '(^'
        r'revert: ((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)!?: .+)'
        r'(\n\n(This reverts commit [a-z0-9]{40}\..*)\n\n)'
        r'(fix(ed|es)? \#[A-Z0-9\-]+)'
        r'((, )(fix(ed|es)? \#[A-Z0-9\-]+))?'
        '$)'
        )


class TestMessageValidation(unittest.TestCase):
    """Tests for commit msg validation."""

    def test_01_simple_msg(self):
        """Test short version works."""

        self.assertTrue(
            bool(
                Constants
                .ValidMsgPattern
                .match(
                    'test: __short_valid_example__'
                    )
                )
            )

    def test_02_regular_msg(self):
        """Test normal version works."""

        self.assertTrue(
            bool(
                Constants
                .ValidMsgPattern
                .match(
                    'feat: __valid_example__'
                    '\n\n'
                    'optional body text'
                    '\n\n'
                    'closes #1, resolve #2'
                    )
                )
            )

    def test_03_breaking_changes_msg(self):
        """Test breaking changes version works."""

        self.assertTrue(
            bool(
                Constants
                .ValidMsgPattern
                .match(
                    'feat!: __new_stuff__'
                    '\n\n'
                    'body text.'
                    '\n\n'
                    'BREAKING CHANGE: Breaks stuff.'
                    '\n\n'
                    'Details on how stuff breaks and what to do.'
                    '\n\n\n'
                    'resolves #1'
                    )
                )
            )

    def test_04_revert_msg(self):
        """Test revert version works."""

        self.assertTrue(
            bool(
                Constants
                .ValidMsgPattern
                .match(
                    'revert: feat!: __new_stuff__'
                    '\n\n'
                    'This reverts commit'
                    ' 2c4ed28b069267f39974b5da50795c5210040e33. Because'
                    ' reasons.'
                    '\n\n'
                    'fixes #TKT-123'
                    )
                )
            )
