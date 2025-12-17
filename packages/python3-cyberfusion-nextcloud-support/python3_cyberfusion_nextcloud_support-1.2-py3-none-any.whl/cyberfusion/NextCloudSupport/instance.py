"""Instance."""

import json
import os
import re
import shutil
import subprocess
import zipfile
from enum import StrEnum
from functools import cached_property
from typing import List, Optional, Tuple, Union

from cyberfusion.Common import download_from_url
from cyberfusion.NextCloudSupport._occ import PHP_BIN, run_command
from cyberfusion.NextCloudSupport.app import App
from cyberfusion.NextCloudSupport.exceptions import (
    AppNotInstalledError,
    CommandFailedError,
    DirectoryNotEmptyError,
)
from cyberfusion.NextCloudSupport.user import User

URL_ZIP_NEXTCLOUD = "https://download.nextcloud.com/server/releases/latest.zip"


class SSLMode(StrEnum):
    """SSL modes."""

    NONE = "none"
    SSL = "ssl"
    TLS = "tls"


class MailAccountAuthMethod(StrEnum):
    """Auth methods for mail accounts."""

    PASSWORD = "password"
    XOAUTH2 = "xoauth2"


class DatabaseType(StrEnum):
    """Database types."""

    SQLITE = "sqlite"
    MYSQL = "mysql"
    PGSQL = "pgsql"
    OCI = "oci"


class Instance:
    """Represents NextCloud instance."""

    def __init__(self, path: str) -> None:
        """Set attributes."""
        self.path = path

    @staticmethod
    def download(destination_path: str, zip_path: Optional[str] = None) -> None:
        """Download NextCloud to path.

        If zip_path is not set, NextCloud is downloaded from their website.
        """
        if os.listdir(destination_path):
            raise DirectoryNotEmptyError

        # Downlaod ZIP from NextCloud if not specified

        if zip_path is None:
            zip_path = download_from_url(
                URL_ZIP_NEXTCLOUD,
                root_directory=destination_path,
            )

        # Extract ZIP

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(destination_path)

        # Move files from nextcloud/ to destination directory

        temp_directory = os.path.join(
            destination_path,
            "nextcloud",
        )

        for file_ in os.listdir(temp_directory):
            shutil.move(os.path.join(temp_directory, file_), destination_path)

        os.rmdir(temp_directory)

    @staticmethod
    def install(
        path: str,
        *,
        database_host: str,
        database_name: str,
        database_username: str,
        database_password: str,
        admin_user: str,
        admin_password: str,
        database_type: DatabaseType = DatabaseType.MYSQL,
    ) -> None:
        """Install downloaded NextCloud instance.

        NextCloud must be downloaded before calling this method.
        """
        run_command(
            [
                "maintenance:install",
                "--database",
                database_type,
                "--database-host",
                database_host,
                "--database-name",
                database_name,
                "--database-user",
                database_username,
                "--database-pass",
                database_password,
                "--admin-user",
                admin_user,
                "--admin-pass",
                admin_password,
                "--data-dir",
                os.path.join(path, "data"),
            ],
            path,
        )

    def get_app(self, name: str) -> App:
        """Get installed app by name."""
        for app in self.installed_apps:
            if name != app.name:
                continue

            return app

        raise AppNotInstalledError

    def get_system_config(
        self, name: str
    ) -> Union[
        str,
        int,
        float,
        bool,
    ]:
        """Get system config value by name."""
        output = run_command(
            [
                "config:system:get",
                name,
            ],
            self.path,
        )

        if output.isdigit():
            return int(output)

        if output == "true":
            return True

        if output == "false":
            return False

        try:
            return float(output)
        except ValueError:
            pass

        return output

    def set_system_config(
        self,
        name: str,
        value: Union[str, int, float, bool],
        index: Optional[int] = None,
    ) -> None:
        """Set system config value.

        Index must be set when manipulating arrays, as it corresponds to the
        array item.
        """

        # Set type

        type_ = "string"

        if isinstance(value, int):
            type_ = "integer"

        if isinstance(value, float):
            type_ = "float"

        if isinstance(value, bool):
            type_ = "boolean"

        # Set value

        _value = str(value)

        if isinstance(value, bool):
            _value = _value.lower()

        # Set command

        command = [
            "config:system:set",
            name,
        ]

        if index is not None:
            command.append(str(index))

        command.extend(["--value", _value, "--type", type_])

        # Run command

        run_command(command, self.path)

    def update(self) -> Tuple[str, str]:
        """Update NextCloud."""
        old_version = self.version

        command = [PHP_BIN, "updater/updater.phar", "--no-interaction"]

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.path,
            )
        except subprocess.CalledProcessError as e:
            raise CommandFailedError(
                return_code=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr,
                command=command,
            )

        new_version = self.version

        return old_version, new_version

    @property
    def available_version(self) -> Optional[str]:
        """Get version that instance can be updated to."""
        lines = run_command(
            [
                "update:check",
            ],
            self.path,
        ).splitlines()

        for line in lines:
            match = re.fullmatch(
                "^Nextcloud (.*) is available. Get more information on how to update at (.*).$",
                line,
            )

            if not match:
                continue

            return match.group(1)

        return None

    @property
    def version(self) -> str:
        """Get version."""
        return self.get_system_config("version")  # type: ignore[return-value]

    def create_mail_account(
        self,
        *,
        user_id: str,
        name: str,
        email_address: str,
        imap_hostname: str,
        imap_port: int,
        imap_ssl_mode: SSLMode,
        imap_username: str,
        imap_password: str,
        smtp_host: str,
        smtp_port: int,
        smtp_ssl_mode: SSLMode,
        smtp_username: str,
        smtp_password: str,
        auth_method: MailAccountAuthMethod,
    ) -> None:
        """Create mail account."""
        run_command(
            [
                "mail:account:create",
                user_id,
                name,
                email_address,
                imap_hostname,
                str(imap_port),
                imap_ssl_mode,
                imap_username,
                imap_password,
                smtp_host,
                str(smtp_port),
                smtp_ssl_mode,
                smtp_username,
                smtp_password,
                auth_method,
            ],
            self.path,
        )

    @property
    def users(self) -> List[User]:
        """Get users."""
        result = []

        output = json.loads(
            run_command(
                [
                    "user:list",
                    "--output",
                    "json",
                ],
                self.path,
            )
        )

        for id_, name in output.items():
            user = User(self, id_, name)

            result.append(user)

        return result

    def refresh_raw_app_list(self) -> None:
        """Clear the raw app list cache."""
        try:
            del self.raw_app_list
        except AttributeError:
            pass

    def refresh_raw_app_update_list(self) -> None:
        """Clear the raw app list cache."""
        try:
            del self.raw_app_update_list
        except AttributeError:
            pass

    @cached_property
    def raw_app_update_list(self) -> List[str]:
        """Get raw app list output."""
        return run_command(
            [
                "app:update",
                "--showonly",
            ],
            self.path,
        ).splitlines()

    @cached_property
    def raw_app_list(self) -> dict:
        """Get raw app list output."""
        return json.loads(
            run_command(
                [
                    "app:list",
                    "--output",
                    "json",
                ],
                self.path,
            )
        )

    @property
    def installed_apps(self) -> List[App]:
        """Get installed apps."""
        result = []

        for name, _ in (
            self.raw_app_list["enabled"] | self.raw_app_list["disabled"]
        ).items():
            app = App(
                self,
                name,
            )

            result.append(app)

        return result
