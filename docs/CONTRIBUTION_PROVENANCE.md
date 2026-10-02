# Preserved 2022 contributions

Verified on 2026-10-02 using a clean, task-local checkout of
`xmutantson/Flipper-IRDB`, without changing any `.ir` file.

| Revision | Commit |
| --- | --- |
| Original three-file contribution | `7ee1a9f68f85a9da81bb2b3a21bdc58774061d9b` |
| Reviewed fork `main` | `e2175d56eef342e5eea2fa246a840d992b670973` |
| Reviewed `Lucaslhm/Flipper-IRDB` upstream `main` | `d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d` |

The reviewed fork head is an ancestor of the reviewed upstream head. The comparison
at these exact commits is **0 ahead / 4,379 behind**. The earlier review's 4,380
count is not reproduced by this fetch. No upstream merge or synchronization has
been made: thousands of unrelated commits are unnecessary to preserve these already
integrated contributions. Future synchronization remains a separate choice.

| File | Original records | Preserved in fork and upstream |
| --- | ---: | ---: |
| `Projectors/BenQ/BenQ_W1070.ir` | 35 | 35 |
| `TVs/Hitachi/Hitachi_LE46H508.ir` | 44 | 44 |
| `TVs/Toshiba/Toshiba_43LF421U21.ir` | 1 | 1 |
| Total | **80** | **80** |

Comparison includes signal type, protocol, address and command. It ignores button
labels and comments, normalizes hex case/whitespace, and retains duplicate payload
counts. Thus renaming a button does not count as data loss, but removing a duplicate
record does. The checked records all use the parsed NEC/NECext format; this is not
a claim to lint every capture or file format in the complete IR database.

Between the reviewed fork and upstream, the BenQ file has `On` renamed to `POWER`
and `Mute` to `MUTE`, plus comment spacing. Hitachi has button-label capitalization
and naming changes. Toshiba has a comment-only change. Signal payloads remain
identical. The Toshiba file's original limitation remains: one captured power
signal, with the source comment describing the other buttons as Bluetooth. No
additional captures are invented or inferred from that comment.

Primary evidence: [original contribution](https://github.com/xmutantson/Flipper-IRDB/commit/7ee1a9f68f85a9da81bb2b3a21bdc58774061d9b),
[reviewed fork](https://github.com/xmutantson/Flipper-IRDB/commit/e2175d56eef342e5eea2fa246a840d992b670973),
[reviewed upstream](https://github.com/Lucaslhm/Flipper-IRDB/commit/d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d).

## Repeat the checks offline

Python 3 and Git are sufficient; there are no Python dependencies or device APIs.
The required commits must already exist in the local Git object database.

```text
python -m unittest discover -s tests -v
python tools/verify_contributions.py --target e2175d56eef342e5eea2fa246a840d992b670973
python tools/verify_contributions.py --target d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d
git merge-base --is-ancestor e2175d56eef342e5eea2fa246a840d992b670973 d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d
git rev-list --left-right --count e2175d56eef342e5eea2fa246a840d992b670973...d126fb1b6f1e114c52b4a8c19839ea65e3a9c24d
```

If upstream objects are absent, an intentional read-only Git fetch is needed before
the offline check, for example:

```text
git fetch https://github.com/Lucaslhm/Flipper-IRDB.git main
```

The verifier itself never fetches or changes repository state. Its default target
is the exact pinned upstream commit above, not a moving remote-tracking branch.
An unavailable revision or any missing/added/changed payload causes a nonzero exit.

Validation results: **10/10 synthetic unit tests pass**, **80/80 payload records
match in each target**, ancestor check exits **0**, divergence output is **0 4379**.
Tests cover changed commands, duplicate multiplicity, label/hex normalization,
record order, required headers/fields, invalid byte widths and unknown fields.
No IR transmission, device testing, database-wide cleanup, fabricated capture,
GitHub workflow or paid CI was performed. Physical signal effectiveness is not
established by a byte-preservation comparison.
