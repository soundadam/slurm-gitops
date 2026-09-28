#!/usr/bin/env python3
"""Mirror docs/ref/ into a Feishu wiki space as native Markdown.

The repo is where a fact lives (.claude/rules/scope.md: one fact, one place);
Feishu is where colleagues read it and argue about the purchase. docs/ref/ is
the part written for them, and it has to read on its own: a link from it to
anything outside docs/ref/ opens nothing in Feishu, so every command refuses
to run while one exists.

A second copy in Feishu is only safe if nobody edits it there. So the mirror
is one-way and machine-written, and it is tracked in both directions: every
page carries a header naming the commit it came from, and `check` fetches each
page back and reports any page whose content is not what was last pushed.

docs/ref/README.md is not a page of its own: it is written into the docx the
wiki root node already is, so the space opens on it. A docx fetched back comes
out re-serialised, not byte for byte, so `check` watches its revision id
instead of its content.

Native .md is the only shape that survives a periodic push. `markdown
+overwrite` keeps the file token, so the wiki node and its URL stay put and
Feishu keeps one version per push. Importing as docx renders nicer but
`drive +import` has no in-place replace outside bitable, so every sync would
mint a new document at a new URL and orphan whatever comments were on the old
one.

    tools/feishu_docs.py init --space-id <id> --base-url <url>   once
    tools/feishu_docs.py push                           after docs change
    tools/feishu_docs.py status                         what push would do, no network
    tools/feishu_docs.py check                          did anyone edit in Feishu

State lives in tools/feishu_docs.json: repo path -> file token and the hash
last pushed. That map is what makes push idempotent rather than duplicating,
so it is committed.

Identity: wiki writes need a member of the space, and a user refresh token
dies in a week. For anything unattended, add the app to the space once as the
user --

    lark-cli wiki +member-add --space-id <id> --member-type appid \
        --member-id <app id> --member-role admin --as user

-- and set "as": "bot" in the state file. The CLI grants the calling user
full_access on whatever the bot creates, so the pages stay manageable by hand.

lark-cli's envelope has a trap: success carries no top-level `code`, so the
OpenAPI habit of testing `code == 0` calls every successful write a failure.
`run_cli` reads `ok` instead.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parent.parent
STATE_PATH = REPO / "tools" / "feishu_docs.json"
DOC_ROOT = "docs/ref"
INDEX = f"{DOC_ROOT}/README.md"

# Inline links only, and not images: [text](target). Anchors are split off
# below -- a .md preview in Feishu has no heading anchors to jump to.
LINK_RE = re.compile(r"(?<!!)\[([^\]\[]+)\]\(([^)\s]+)\)")
REF_USE_RE = re.compile(r"(?<!!)\[([^\]\[]+)\]\[([^\]\[]+)\]")
REF_DEF_RE = re.compile(r"^\[([^\]\[]+)\]:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)



class LarkError(RuntimeError):
    pass


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=True
    )
    return proc.stdout.strip()


def run_cli(args: list[str], identity: str, stdin: str | None = None) -> dict:
    """Call lark-cli and return `data`, per the shared JSON output contract.

    Progress chatter ("Found 3 node(s)") goes to stderr, so stdout is parsed
    whole rather than scanned for the first brace.
    """
    cmd = ["lark-cli", *args, "--as", identity, "--format", "json"]
    proc = subprocess.run(
        cmd, cwd=REPO, input=stdin, capture_output=True, text=True
    )
    if proc.returncode == 10:
        raise LarkError(
            "lark-cli asked for high-risk confirmation (exit 10) on "
            f"`{' '.join(args)}`. These scripts only issue plain writes, so "
            "treat that as a sign the command changed; confirm by hand first."
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise LarkError(
            f"lark-cli `{' '.join(args)}` printed no JSON "
            f"(exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        ) from None
    if not payload.get("ok"):
        err = payload.get("error", {})
        raise LarkError(
            f"lark-cli `{' '.join(args)}` failed: "
            f"{err.get('code', '?')} {err.get('message', payload)}"
        )
    return payload.get("data", {})


def load_state() -> dict:
    if not STATE_PATH.exists():
        sys.exit(
            f"{STATE_PATH.relative_to(REPO)} is missing. Run "
            "`tools/feishu_docs.py init --under <wiki page URL>` first."
        )
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def tracked_docs() -> list[str]:
    """Tracked pages under DOC_ROOT, the index excluded; scratch files are not."""
    listed = git(["ls-files", DOC_ROOT]).splitlines()
    return sorted(p for p in listed if p.endswith(".md") and p != INDEX)


def link_targets(text: str) -> list[str]:
    refs = {m.group(1).lower(): m.group(2) for m in REF_DEF_RE.finditer(text)}
    inline = [m.group(2) for m in LINK_RE.finditer(text)]
    used = [refs[m.group(2).lower()] for m in REF_USE_RE.finditer(text)
            if m.group(2).lower() in refs]
    return inline + used


def require_closed() -> None:
    """Refuse to go on while a doc in DOC_ROOT links anywhere outside it.

    docs/work/ may cite docs/ref/, never the other way: a reader in Feishu
    cannot open a repo path, and a sentence that leans on one does not read.
    """
    bad = []
    for rel in [INDEX, *tracked_docs()]:
        for target in link_targets((REPO / rel).read_text(encoding="utf-8")):
            path = target.partition("#")[0]
            if SCHEME_RE.match(target) or not path:
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
            if not resolved.startswith(DOC_ROOT + "/") or not (REPO / resolved).is_file():
                bad.append(f"  {rel}: ({target})")
    if bad:
        sys.exit(
            f"{DOC_ROOT}/ 里的文档只能链到 {DOC_ROOT}/ 里的文档，"
            "飞书上的读者打不开别的路径：\n" + "\n".join(bad)
        )


def stamp(rel: str) -> str:
    """Name the commit the content came from, not HEAD.

    Using HEAD would rewrite every page on every commit and defeat the
    unchanged-skip. The last commit to touch this file is also the honest
    answer to "how old is what I am reading".
    """
    line = git(["log", "-1", "--format=%h %cs", "--", rel])
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", rel], cwd=REPO
    ).returncode
    origin = f"`{line.split(' ')[0]}`（{line.split(' ')[1]}）" if line else "未提交"
    if dirty:
        origin += "，**本地有未提交改动**"
    return (
        f"> 本页是 slurm-gitops 仓库 `{rel}` 的只读镜像，由 `tools/feishu_docs.py` "
        f"生成自 {origin}。\n"
        "> **不要在飞书上改这一页**：下次同步整页覆盖。有意见请在采购讨论文档里提，"
        "结论由仓库改完再同步过来。\n\n"
        "---\n\n"
    )


def resolve(label: str, target: str, src_dir: str, urls: dict[str, str]) -> str:
    """One link's replacement: the wiki URL of the page it names.

    require_closed has already refused anything outside DOC_ROOT, so the only
    miss left is a page not created yet (status, dry-run), which keeps its label.
    """
    if SCHEME_RE.match(target) or target.startswith("#"):
        return f"[{label}]({target})"
    path, _, _anchor = target.partition("#")
    if not path:
        return f"[{label}]({target})"
    url = urls.get(posixpath.normpath(posixpath.join(src_dir, path)))
    return f"[{label}]({url})" if url else label


def rewrite_links(text: str, rel: str, urls: dict[str, str]) -> str:
    """Point cross-doc links at wiki nodes, reference-style ones included.

    A relative path means nothing in Feishu, and a .md preview there has no
    heading anchors to jump to, so a link keeps its page and loses its anchor.
    """
    src_dir = posixpath.dirname(rel)
    refs = {m.group(1).lower(): m.group(2) for m in REF_DEF_RE.finditer(text)}
    text = REF_DEF_RE.sub("", text).rstrip() + "\n"

    def inline(match: re.Match[str]) -> str:
        return resolve(match.group(1), match.group(2), src_dir, urls)

    def reference(match: re.Match[str]) -> str:
        target = refs.get(match.group(2).lower())
        if target is None:
            return match.group(0)
        return resolve(match.group(1), target, src_dir, urls)

    return LINK_RE.sub(inline, REF_USE_RE.sub(reference, text))


def render(rel: str, urls: dict[str, str]) -> str:
    body = (REPO / rel).read_text(encoding="utf-8")
    return stamp(rel) + rewrite_links(body, rel, urls)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def url_map(state: dict) -> dict[str, str]:
    base = state["base_url"].rstrip("/")
    urls = {
        rel: f"{base}/wiki/{entry['node_token']}"
        for rel, entry in state["files"].items()
        if entry.get("node_token")
    }
    urls[INDEX] = f"{base}/wiki/{state['root_node_token']}"
    return urls


def index_doc(state: dict, identity: str) -> str:
    """The docx token behind the root node, looked up once and kept."""
    index = state.setdefault("index", {})
    if not index.get("doc_token"):
        node = run_cli(["wiki", "+node-get", "--node-token", state["root_node_token"]], identity)
        index["doc_token"] = node["obj_token"]
    return index["doc_token"]


def push_index(state: dict, urls: dict[str, str], identity: str, args) -> bool:
    index = state.setdefault("index", {})
    content = render(INDEX, urls)
    sha = digest(content)
    if sha == index.get("sha256") and not args.force:
        return False
    if args.dry_run:
        print(f"  ~ 会覆盖首页 {INDEX}")
        return True
    data = run_cli(
        ["docs", "+update", "--doc", index_doc(state, identity),
         "--command", "overwrite", "--doc-format", "markdown", "--content", "-"],
        identity,
        stdin=content,
    )
    index["sha256"] = sha
    index["revision_id"] = data.get("document", data).get("revision_id")
    save_state(state)
    print(f"  ~ {INDEX}  ->  {urls[INDEX]}")
    return True


def ensure_dir_node(state: dict, reldir: str, identity: str) -> str:
    """One wiki node per docs/ subdirectory, so the tree keeps its shape."""
    if reldir == DOC_ROOT:
        return state["root_node_token"]
    if reldir in state["dirs"]:
        return state["dirs"][reldir]
    parent = ensure_dir_node(state, posixpath.dirname(reldir), identity)
    data = run_cli(
        [
            "wiki", "+node-create",
            "--space-id", state["space_id"],
            "--parent-node-token", parent,
            "--obj-type", "docx",
            "--title", posixpath.basename(reldir),
        ],
        identity,
    )
    state["dirs"][reldir] = data["node_token"]
    print(f"  + 目录节点 {reldir}")
    return data["node_token"]


def create_file(state: dict, rel: str, identity: str) -> None:
    """Create the file empty-ish; pass two writes the real content.

    Two passes because a page can link to a page that does not exist yet. The
    placeholder only ever reaches Feishu if pass two dies in between.
    """
    parent = ensure_dir_node(state, posixpath.dirname(rel), identity)
    data = run_cli(
        [
            "markdown", "+create",
            "--wiki-token", parent,
            "--name", posixpath.basename(rel),
            "--content", "-",
        ],
        identity,
        stdin=f"（`{rel}` 的镜像正在首次同步。）\n",
    )
    file_token = data["file_token"]
    # A file under a wiki node has no stable /file/ URL, so resolve the node
    # it became; that node_token is what every rewritten link points at.
    node = run_cli(
        [
            "wiki", "+node-get",
            "--node-token", file_token,
            "--obj-type", "file",
            "--space-id", state["space_id"],
        ],
        identity,
    )
    state["files"][rel] = {
        "file_token": file_token,
        "node_token": node["node_token"],
        "sha256": "",
    }
    print(f"  + 新页 {rel}")


def report_orphans(state: dict, docs: list[str]) -> None:
    orphans = sorted(set(state["files"]) - set(docs))
    if orphans:
        print(
            "\n孤儿页（仓库里已经没有对应文档，本脚本不会自动删除，"
            "删是 `wiki +node-delete`，高风险，手动确认）:"
        )
        for rel in orphans:
            print(f"  ? {rel}")


def select(docs: list[str], only: list[str] | None) -> list[str]:
    if not only:
        return docs
    missing = [p for p in only if p not in docs]
    if missing:
        sys.exit(f"--only names files that are not tracked docs: {missing}")
    return [p for p in docs if p in only]


def cmd_init(args: argparse.Namespace) -> None:
    if STATE_PATH.exists() and not args.force:
        sys.exit(
            f"{STATE_PATH.relative_to(REPO)} already exists. Re-running init "
            "would strand the pages it points at; pass --force if that is "
            "really what you want."
        )
    identity = args.identity
    if args.under:
        split = urlsplit(args.under)
        if not split.scheme or not split.netloc:
            sys.exit("--under wants a full wiki page URL, not a bare token.")
        base_url = f"{split.scheme}://{split.netloc}"
        node = run_cli(
            ["wiki", "+node-get", "--node-token", args.under], identity
        )
        space_id, parent = node["space_id"], node["node_token"]
    else:
        if not args.space_id or not args.base_url:
            sys.exit("Pass --under <wiki page URL>, or --space-id with --base-url.")
        base_url, space_id, parent = args.base_url, args.space_id, None
    create = [
        "wiki", "+node-create",
        "--space-id", space_id,
        "--obj-type", "docx",
        "--title", args.title,
    ]
    if parent:
        create += ["--parent-node-token", parent]
    root = run_cli(create, identity)
    state = {
        "as": identity,
        "base_url": base_url,
        "space_id": root.get("resolved_space_id", space_id),
        "root_node_token": root["node_token"],
        "dirs": {},
        "files": {},
    }
    save_state(state)
    print(
        f"根节点「{args.title}」已建：{base_url}/wiki/{root['node_token']}\n"
        f"状态写入 {STATE_PATH.relative_to(REPO)}。下一步 `tools/feishu_docs.py push`。"
    )


def cmd_push(args: argparse.Namespace) -> None:
    require_closed()
    state = load_state()
    identity = args.identity or state.get("as", "bot")
    docs = select(tracked_docs(), args.only)

    for rel in docs:
        if rel not in state["files"]:
            if args.dry_run:
                print(f"  + 会新建 {rel}")
                continue
            create_file(state, rel, identity)
            save_state(state)

    urls = url_map(state)
    pushed = skipped = 0
    for rel in docs:
        entry = state["files"].get(rel)
        if entry is None:  # dry-run, never created
            continue
        content = render(rel, urls)
        sha = digest(content)
        if sha == entry.get("sha256") and not args.force:
            skipped += 1
            continue
        if args.dry_run:
            print(f"  ~ 会覆盖 {rel}")
            pushed += 1
            continue
        data = run_cli(
            ["markdown", "+overwrite", "--file-token", entry["file_token"],
             "--content", "-"],
            identity,
            stdin=content,
        )
        entry["sha256"] = sha
        entry["version"] = data.get("version", "")
        save_state(state)
        print(f"  ~ {rel}  ->  {urls.get(rel, entry['file_token'])}")
        pushed += 1

    if not args.only:
        if push_index(state, urls, identity, args):
            pushed += 1
        else:
            skipped += 1
    print(f"\n推了 {pushed} 篇，跳过 {skipped} 篇未变的。")
    report_orphans(state, tracked_docs())


def cmd_status(args: argparse.Namespace) -> None:
    require_closed()
    state = load_state()
    docs = select(tracked_docs(), args.only)
    urls = url_map(state)
    for rel in docs:
        entry = state["files"].get(rel)
        if entry is None:
            print(f"  + {rel}  新页")
            continue
        if digest(render(rel, urls)) != entry.get("sha256"):
            print(f"  ~ {rel}  待推送")
        else:
            print(f"  = {rel}")
    if not args.only:
        index = state.get("index", {})
        mark = "=" if digest(render(INDEX, urls)) == index.get("sha256") else "~"
        print(f"  {mark} {INDEX}  首页")
    report_orphans(state, tracked_docs())


def cmd_check(args: argparse.Namespace) -> None:
    """Fetch each page back and diff it against what we last pushed.

    This is the one guard on the mirror being one-way, and it is also what
    arms the repair. `push` skips a page whose rendered content still hashes
    to the stored sha, so on its own it would leave an edit made in Feishu
    standing forever. Clearing that sha here is what makes the next push
    rewrite the page. The diff is printed first, so anything worth keeping
    can be moved back into the repo before that happens.
    """
    require_closed()
    state = load_state()
    identity = args.identity or state.get("as", "bot")
    docs = select(tracked_docs(), args.only)
    urls = url_map(state)
    drifted = 0
    index = state.get("index", {})
    if not args.only and index.get("revision_id") is not None:
        doc = run_cli(
            ["docs", "+fetch", "--doc", index_doc(state, identity),
             "--scope", "outline", "--max-depth", "1"],
            identity,
        )["document"]
        if doc["revision_id"] == index["revision_id"]:
            print(f"  = {INDEX}  首页")
        else:
            drifted += 1
            if not args.keep:
                index["sha256"] = ""
                save_state(state)
            print(
                f"  ! {INDEX}  首页在飞书上被改过（版本 {index['revision_id']} → "
                f"{doc['revision_id']}），docx 取回来不是原文，没法逐行比，去飞书的版本历史看"
            )
    for rel in docs:
        entry = state["files"].get(rel)
        if entry is None:
            print(f"  + {rel}  还没同步过")
            continue
        remote = run_cli(
            ["markdown", "+fetch", "--file-token", entry["file_token"]],
            identity,
        )["content"]
        local = render(rel, urls)
        if digest(remote) == entry.get("sha256"):
            print(f"  = {rel}")
            continue
        drifted += 1
        if not args.keep:
            entry["sha256"] = ""
            save_state(state)
        print(f"  ! {rel}  飞书上的内容不是上次推的那一份")
        for line in difflib.unified_diff(
            remote.splitlines(),
            local.splitlines(),
            fromfile=f"feishu:{rel}",
            tofile=f"local:{rel}",
            lineterm="",
            n=2,
        ):
            print(f"      {line}")
    if drifted:
        if args.keep:
            print(f"\n{drifted} 篇在飞书上被改过，没有标记（--keep）。")
        else:
            print(
                f"\n{drifted} 篇在飞书上被改过，已标记为待推——"
                "下一次 push 会用仓库那一份整页覆盖它们。"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mirror docs/ into a Feishu wiki space.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="create the root node, write the state")
    init.add_argument("--under", help="wiki page URL to hang the mirror under")
    init.add_argument("--space-id", help="space to put the root node in")
    init.add_argument("--base-url", help="e.g. https://xxx.feishu.cn")
    init.add_argument("--title", default="slurm-gitops docs")
    init.add_argument("--identity", "--as", default="user", dest="identity")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    push = sub.add_parser("push", help="create what is missing, overwrite what changed")
    push.add_argument("--only", nargs="+", help="repo-relative doc paths")
    push.add_argument("--force", action="store_true", help="push unchanged pages too")
    push.add_argument("--dry-run", action="store_true")
    push.add_argument("--identity", "--as", dest="identity")
    push.set_defaults(func=cmd_push)

    status = sub.add_parser("status", help="what push would do, no network")
    status.add_argument("--only", nargs="+")
    status.set_defaults(func=cmd_status)

    check = sub.add_parser("check", help="diff Feishu against the last push")
    check.add_argument("--only", nargs="+")
    check.add_argument("--identity", "--as", dest="identity")
    check.add_argument(
        "--keep", action="store_true", help="report drift without arming the repair"
    )
    check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    try:
        args.func(args)
    except LarkError as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
