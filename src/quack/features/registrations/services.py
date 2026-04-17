from collections.abc import Iterable

from quack.storage.registrations import check_alias_existence, persist_users


def persist_users_tags(users_tags: Iterable[str]) -> str | None:
    persist_users([tag for tag in users_tags if tag.startswith("@")])
    for alias in users_tags:
        if alias.startswith("@"):
            continue
        found = check_alias_existence(alias)
        if found:
            return alias
    return None
