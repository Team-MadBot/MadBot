import discord
import logging

from fluent.runtime import FluentLocalization, FluentResourceLoader

log = logging.getLogger("discord")

class PermissionsParser:
    @staticmethod
    async def parse_permissions(perms: discord.Permissions) -> tuple[str, bool]:
        loader = FluentResourceLoader("locales/{locale}")
        l10n = FluentLocalization(["ru"], ["permissions.ftl"], loader)  # FIXME: move it out to config?

        for name, value in perms:
            log.debug(f"PERMS: {l10n.format_value(name)} {str(value).upper()}")
            