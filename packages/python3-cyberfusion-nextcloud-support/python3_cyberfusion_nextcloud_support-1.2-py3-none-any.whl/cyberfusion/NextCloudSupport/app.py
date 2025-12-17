"""App."""

import os
import re
import tarfile
from typing import TYPE_CHECKING, Optional, Tuple

from cyberfusion.Common import download_from_url
from cyberfusion.NextCloudSupport._occ import run_command
from cyberfusion.NextCloudSupport.exceptions import AppNotInstalledError

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.NextCloudSupport.instance import Instance


class App:
    """Represents app."""

    def __init__(
        self,
        instance: "Instance",
        name: str,
    ) -> None:
        """Set attributes."""
        self.instance = instance
        self.name = name

    @staticmethod
    def install(
        instance: "Instance",
        name: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """Install app by name or URL.

        For custom versions: NextCloud does not natively support installing
        specific versions of apps (default is latest). To work around this,
        install the app by URL, pointing to the archive containing the
        needed version.

        Note that installing apps from a specific URL is not officially
        supported, and the way we do it is undocumented, and therefore
        a hack.
        """
        if name and url:
            raise ValueError("Specify either name or URL")

        if name:
            run_command(["app:install", name], instance.path)

            return

        with tarfile.open(download_from_url(url)) as f:
            name = os.path.commonpath(f.getnames())

            f.extractall(path=os.path.join(instance.path, "apps"))

        run_command(
            ["app:enable", name],
            instance.path,
        )

    @property
    def is_enabled(self) -> bool:
        """Get if app is enabled."""
        return self.name in self.instance.raw_app_list["enabled"]

    def enable(self) -> None:
        """Enable app."""
        run_command(
            ["app:enable", self.name],
            self.instance.path,
        )

        self.instance.refresh_raw_app_list()

    def disable(self) -> None:
        """Disable app."""
        run_command(
            ["app:disable", self.name],
            self.instance.path,
        )

        self.instance.refresh_raw_app_list()

    @property
    def version(self) -> str:
        """Get version."""
        for app_name, version in (
            self.instance.raw_app_list["enabled"]
            | self.instance.raw_app_list["disabled"]
        ).items():
            if app_name != self.name:
                continue

            # Sometimes, NextCloud suffixes the version by another version number.
            # It's unclear why or when, but we don't want it.
            # Code: https://github.com/nextcloud/server/blob/72b6db40435ce0407d0aafa626945d4f2380460f/core/Command/App/ListApps.php#L91

            return version.split(" ")[0]

        raise AppNotInstalledError

    def remove(self) -> None:
        """Remove app."""
        run_command(
            ["app:remove", self.name],
            self.instance.path,
        )

        self.instance.refresh_raw_app_list()

    def update(self) -> Tuple[str, str]:
        """Update app."""
        old_version = self.version

        run_command(
            ["app:update", self.name],
            self.instance.path,
        )

        self.instance.refresh_raw_app_list()
        self.instance.refresh_raw_app_update_list()

        new_version = self.version

        return old_version, new_version

    @property
    def available_version(self) -> Optional[str]:
        """Get version that app can be updated to."""
        for line in self.instance.raw_app_update_list:
            match = re.fullmatch("^(.*) new version available: (.*)$", line)

            if not match:
                continue

            if match.group(1) != self.name:
                continue

            return match.group(2)

        return None

    def __str__(self) -> str:
        """Get string representation."""
        return (
            self.name
            + " ("
            + self.version
            + ", available: "
            + str(self.available_version)
            + ", enabled: "
            + str(self.is_enabled)
            + ")"
        )
