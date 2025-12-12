import os
import tomllib


class ConfigProfile:
    def __init__(self, profile_name: str, data: dict) -> None:
        self.profile_name = profile_name
        self._data = data

    @property
    def domain(self) -> str:
        return self._data.get("domain", "")

    @property
    def username(self) -> str:
        return self._data.get("username", "")

    @property
    def password(self) -> str:
        return self._data.get("password", "")

    def __str__(self) -> str:
        return (
            f"Profile Name: {self.profile_name}\n"
            f"\tDomain: {self.domain}\n"
            f"\tUsername: {self.username}\n"
            f"\tPassword: {'*' * len(self.password) if self.password else ''}"
        )


class Config:
    def __init__(self, file_loc: str, profiles: list[ConfigProfile]) -> None:
        self.file = file_loc
        self.profiles = profiles

    def find_profile_by_name(self, profile_name: str) -> ConfigProfile:
        for profile in self.profiles:
            if profile.profile_name == profile_name:
                return profile
        return ConfigProfile(profile_name="", data={})


def read_config(config_file: str) -> Config:
    if not os.path.isfile(path=config_file):
        return Config(file_loc="", profiles=[ConfigProfile(profile_name="", data={})])

    try:
        with open(file=config_file, mode="rb") as _file:
            data = tomllib.load(_file)
    except ValueError as error:
        data = {}
        print(f"invalid toml: {error}")
    return Config(
        file_loc=config_file,
        profiles=[
            ConfigProfile(profile_name=profile_name, data=data[profile_name])
            for profile_name in data.keys()
        ],
    )
