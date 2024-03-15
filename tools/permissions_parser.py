import discord
import logging

from fluent.runtime import FluentLocalization, FluentResourceLoader

log = logging.getLogger("discord")


class PermissionsParser:
    @staticmethod
    def parse_permissions(perms: discord.Permissions) -> dict[str, bool]:
        loader = FluentResourceLoader("locales/{locale}")
        l10n = FluentLocalization(
            ["ru"], ["permissions.ftl"], loader
        )  # FIXME: move it out to config?
        parsed = {}

        for name, value in perms:
            log.debug(f"PERMS: {l10n.format_value(name)} {str(value).upper()}")
            parsed[l10n.format_value(name)] = value

        return parsed
