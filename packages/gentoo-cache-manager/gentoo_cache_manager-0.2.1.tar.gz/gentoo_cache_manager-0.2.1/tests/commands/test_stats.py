import subprocess
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gcm.commands.base import ccache_dir_env
from gcm.commands.exit_codes import CCACHE_BINARY_NOT_FOUND
from gcm.commands.stats import Stats

MODERN_STATS = """Cacheable calls:   101 / 235 (42.98%)
  Hits:              8 / 101 ( 7.92%)
    Direct:          6 /   8 (75.00%)
    Preprocessed:    2 /   8 (25.00%)
  Misses:           93 / 101 (92.08%)
Uncacheable calls: 134 / 235 (57.02%)
Local storage:
  Cache size (GiB): 0.1 / 2.0 ( 0.00%)
  Cleanups:         16
  Hits:              8 / 101 ( 7.92%)
  Misses:           93 / 101 (92.08%)"""

LEGACY_STATS = """Summary:
  Hits:               8 /  101 (7.92 %)
    Direct:           6 /  135 (4.44 %)
    Preprocessed:     2 /  119 (1.68 %)
  Misses:            93
    Direct:         129
    Preprocessed:   117
  Uncacheable:      134
Primary storage:
  Hits:              37 /  260 (14.23 %)
  Misses:           223
  Cache size (GB): 0.10 / 2.00 (0.00 %)
  Cleanups:          16

Use the -v/--verbose option for more details."""

MODERN_OUTPUT = """Showing ccache stats for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m
  \x1b[33mCacheable calls\x1b[0m:   \x1b[33m101\x1b[0m / \x1b[35m235\x1b[0m (\x1b[33m42.98%\x1b[0m)
    \x1b[32mHits\x1b[0m:              \x1b[32m8\x1b[0m / \x1b[33m101\x1b[0m (\x1b[32m 7.92%\x1b[0m)
      \x1b[92mDirect\x1b[0m:          \x1b[92m6\x1b[0m / \x1b[32m  8\x1b[0m (\x1b[92m75.00%\x1b[0m)
      \x1b[92mPreprocessed\x1b[0m:    \x1b[92m2\x1b[0m / \x1b[32m  8\x1b[0m (\x1b[92m25.00%\x1b[0m)
    \x1b[34mMisses\x1b[0m:           \x1b[34m93\x1b[0m / \x1b[33m101\x1b[0m (\x1b[34m92.08%\x1b[0m)
  \x1b[31mUncacheable calls\x1b[0m: \x1b[31m134\x1b[0m / \x1b[35m235\x1b[0m (\x1b[31m57.02%\x1b[0m)
  \x1b[37mLocal storage\x1b[0m:
    \x1b[36mCache size (GiB)\x1b[0m: \x1b[36m0.1\x1b[0m / \x1b[35m2.0\x1b[0m (\x1b[36m 0.00%\x1b[0m)
    \x1b[90mCleanups\x1b[0m:\x1b[90m         16\x1b[0m
    \x1b[32mHits\x1b[0m:              \x1b[32m8\x1b[0m / \x1b[33m101\x1b[0m (\x1b[32m 7.92%\x1b[0m)
    \x1b[34mMisses\x1b[0m:           \x1b[34m93\x1b[0m / \x1b[33m101\x1b[0m (\x1b[34m92.08%\x1b[0m)
\x1b[32mDone :-)\x1b[0m
"""  # noqa: E501

LEGACY_OUTPUT = """Showing ccache stats for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m
  Summary:
    \x1b[32mHits\x1b[0m:               \x1b[32m8\x1b[0m / \x1b[33m 101\x1b[0m (\x1b[32m7.92 %\x1b[0m)
      \x1b[92mDirect\x1b[0m:           \x1b[92m6\x1b[0m / \x1b[32m 135\x1b[0m (\x1b[92m4.44 %\x1b[0m)
      \x1b[92mPreprocessed\x1b[0m:     \x1b[92m2\x1b[0m / \x1b[32m 119\x1b[0m (\x1b[92m1.68 %\x1b[0m)
    \x1b[34mMisses\x1b[0m:\x1b[34m            93\x1b[0m
      \x1b[92mDirect\x1b[0m:\x1b[92m         129\x1b[0m
      \x1b[92mPreprocessed\x1b[0m:\x1b[92m   117\x1b[0m
    Uncacheable:      134
  Primary storage:
    \x1b[32mHits\x1b[0m:              \x1b[32m37\x1b[0m / \x1b[33m 260\x1b[0m (\x1b[32m14.23 %\x1b[0m)
    \x1b[34mMisses\x1b[0m:\x1b[34m           223\x1b[0m
    \x1b[36mCache size (GB)\x1b[0m: \x1b[36m0.10\x1b[0m / \x1b[35m2.00\x1b[0m (\x1b[36m0.00 %\x1b[0m)
    \x1b[90mCleanups\x1b[0m:\x1b[90m          16\x1b[0m
  
  Use the -v/--verbose option for more details.
\x1b[32mDone :-)\x1b[0m
"""  # noqa: E501


@pytest.mark.parametrize(
    'stats,output',
    (
        (MODERN_STATS, MODERN_OUTPUT),
        (LEGACY_STATS, LEGACY_OUTPUT),
    ),
)
@patch('subprocess.Popen')
def test_stats_ok(popen, stats, output):
    popen.return_value.stdout.readlines.return_value = [
        f'{line}\n' for line in stats.split('\n')
    ]

    result = CliRunner().invoke(Stats(), ['foo'], color=True)

    popen.assert_called_once_with(
        ['ccache', '-s'],
        env=ccache_dir_env('app-misc/foo'),
        stdout=subprocess.PIPE,
        text=True,
    )
    assert result.exit_code == 0
    assert result.output == output


NO_CCACHE_OUTPUT = """Showing ccache stats for \x1b[32m\x1b[1mapp-misc/foo\x1b[0m
\x1b[33mUnable to show stats due to missing ccache binary\x1b[0m
\x1b[31mAborted!\x1b[0m
"""  # noqa: E501


@patch('subprocess.Popen', side_effect=FileNotFoundError)
def test_stats_no_ccache(popen):
    result = CliRunner().invoke(Stats(), ['foo'], color=True)

    popen.assert_called_once()
    assert result.exit_code == CCACHE_BINARY_NOT_FOUND
    assert result.output == NO_CCACHE_OUTPUT
