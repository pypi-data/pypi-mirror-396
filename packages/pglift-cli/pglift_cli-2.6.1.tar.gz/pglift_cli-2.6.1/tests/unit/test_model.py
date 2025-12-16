# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from datetime import date
from typing import Any

import click
import pytest
from click.testing import CliRunner
from pydantic.fields import FieldInfo

from pglift.models import testing as models
from pglift_cli import model

from . import click_result_traceback


def test_paramspec() -> None:
    foospec = model.ArgumentSpec(("foo",), FieldInfo(), {"type": int}, ())
    barspec = model.OptionSpec(("--bar",), FieldInfo(description="bar"), {}, ())

    @click.command()
    @foospec.decorator
    @barspec.decorator
    def cmd(foo: int, bar: str) -> None:
        assert isinstance(foo, int)
        assert isinstance(bar, str)
        click.echo(f"foo: {foo}, bar: {bar}")

    runner = CliRunner()
    result = runner.invoke(cmd, ["1", "--bar=baz"])
    assert result.stdout == "foo: 1, bar: baz\n"


def test_as_parameters_typeerror() -> None:
    with pytest.raises(TypeError, match="expecting a 'person: Person' parameter"):

        @click.command("add-person")
        @model.as_parameters(models.Person, "create")
        @click.pass_context
        def cb1(ctx: click.core.Context, x: models.Person) -> None:
            pass

    with pytest.raises(TypeError, match="expecting a 'person: Person' parameter"):

        @click.command("add-person")
        @model.as_parameters(models.Person, "create")
        @click.pass_context
        def cb2(ctx: click.core.Context, person: str) -> None:
            pass


def test_as_parameters(runner: CliRunner) -> None:
    @click.command("add-person")
    @click.option("--exclude-none", is_flag=True, default=False)
    @model.as_parameters(models.Person, "create")
    @click.option("--indent", type=int)
    def add_person(exclude_none: bool, person: models.Person, indent: int) -> None:
        """Add a new person."""
        click.echo(
            person.model_dump_json(
                by_alias=True, indent=indent, exclude_none=exclude_none
            ),
            err=True,
        )

    result = runner.invoke(add_person, ["--help"])
    assert result.exit_code == 0, click_result_traceback(result)
    assert result.stdout == (
        "Usage: add-person [OPTIONS] NAME {friend|family|other}\n"
        "\n"
        "  Add a new person.\n"
        "\n"
        "Options:\n"
        "  --exclude-none\n"
        "  --nickname TEXT                 Your secret nickname.  [required]\n"
        "  --age AGE                       Age.\n"
        "  --address-street STREET         Street lines. (Can be used multiple times.)\n"
        "  --address-zip-code ZIP_CODE     ZIP code.\n"
        "  --address-town CITY             City.\n"
        "  --address-country [fr|be]\n"
        "  --address-primary / --no-address-primary\n"
        "                                  Is this person's primary address?\n"
        "  --address-coords-long LONG      Longitude.\n"
        "  --address-coords-lat LAT        Latitude.\n"
        "  --birth-date DATE               Date of birth.  [required]\n"
        "  --birth-place PLACE             Place of birth.\n"
        "  --is-dead / --no-is-dead        Is dead.\n"
        "  --phone-numbers PHONE_NUMBERS   Phone numbers. (Can be used multiple times.)\n"
        "  --pet PET                       Owned pets. (Can be used multiple times.)\n"
        "  --member-of GROUP               Groups the person is a member of. (Can be used\n"
        "                                  multiple times.)\n"
        "  --indent INTEGER\n"
        "  --help                          Show this message and exit.\n"
    )

    result = runner.invoke(
        add_person,
        [
            "alice",
            "friend",
            "--exclude-none",
            "--age=42",
            "--address-street=bd montparnasse",
            "--address-street=far far away",
            "--address-town=paris",
            "--address-country=fr",
            "--address-primary",
            "--address-coords-long=12.3",
            "--address-coords-lat=9.87",
            "--birth-date=1981-02-18",
            "--indent=2",
            "--nickname=aaa",
            "--phone-numbers=12345",
        ],
        input="alc\nalc\n",
    )
    assert result.exit_code == 0, click_result_traceback(result)
    assert json.loads(result.stderr) == {
        "address": {
            "city": "paris",
            "country": "fr",
            "coords": {"system": "4326", "lat": 9.87, "long": 12.3},
            "street": ["bd montparnasse", "far far away"],
            "zip_code": 0,
            "primary": True,
        },
        "age": 42,
        "birth": {"date": "1981-02-18"},
        "is_dead": False,
        "name": "alice",
        "nickname": "**********",
        "relation": "friend",
        "phone_numbers": [{"number": "12345"}],
        "pets": [],
        "memberships": [],
    }

    result = runner.invoke(
        add_person,
        [
            "foo",
            "--address-street=larue",
            "--address-town=laville",
            "--address-country=lepays",
        ],
    )
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--address-country': 'lepays' is not one of 'fr', 'be'"
        in result.stderr
    )

    result = runner.invoke(
        add_person,
        [
            "foo",
            "friend",
            "--age=17",
            "--birth-date=1987-06-05",
            "--nickname=aaa",
            "--is-dead",
        ],
    )
    assert result.exit_code == 2
    assert "--is-dead' and '--age' can't be used together" in result.stderr
    assert "For further information visit" not in result.stderr


def test_as_parameters_update() -> None:
    @click.command("update-person")
    @model.as_parameters(models.Person, "update")
    def update_person(**values: Any) -> None:
        """Modify new person."""
        person = models.Person.model_validate(values)
        click.echo(person.model_dump_json(by_alias=True, exclude_unset=True), err=True)

    runner = CliRunner()
    result = runner.invoke(update_person, ["--help"])
    assert result.exit_code == 0, click_result_traceback(result)
    assert result.stdout == (
        "Usage: update-person [OPTIONS] NAME {friend|family|other}\n"
        "\n"
        "  Modify new person.\n"
        "\n"
        "Options:\n"
        "  --nickname TEXT                 Your secret nickname.  [required]\n"
        "  --age AGE                       Age.\n"
        "  --address-zip-code ZIP_CODE     ZIP code.\n"
        "  --address-town CITY             City.\n"
        "  --address-country [fr|be]\n"
        "  --address-primary / --no-address-primary\n"
        "                                  Is this person's primary address?\n"
        "  --address-coords-long LONG      Longitude.\n"
        "  --address-coords-lat LAT        Latitude.\n"
        "  --birth-date DATE               Date of birth.  [required]\n"
        "  --is-dead / --no-is-dead        Is dead.\n"
        "  --add-pet PET                   Add pet. (Can be used multiple times.)\n"
        "  --remove-pet PET                Remove pet. (Can be used multiple times.)\n"
        "  --add-to GROUP                  Add to group. (Can be used multiple times.)\n"
        "  --remove-from GROUP             Remove from group. (Can be used multiple\n"
        "                                  times.)\n"
        "  --help                          Show this message and exit.\n"
    )

    result = runner.invoke(
        update_person,
        ["alice", "--age=5", "--birthdate=2042-02-31"],
    )
    assert result.exit_code == 2, result.output
    assert "Error: No such option: --birthdate" in result.output

    result = runner.invoke(
        update_person,
        ["alice", "other", "--nickname=a", "--age=5", "--birth-date=1987-06-05"],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {
        "name": "alice",
        "nickname": "**********",
        "relation": "other",
        "age": 5,
        "birth": {"date": "1987-06-05"},
        "pets": [],
        "memberships": [],
    }

    result = runner.invoke(
        update_person,
        ["alice", "friend", "--nickname=a", "--age=abc", "--birth-date=2010-02-03"],
    )
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--age': Input should be a valid integer"
        in result.output
    )

    result = runner.invoke(
        update_person,
        [
            "bob",
            "family",
            "--nickname=b",
            "--birth-date=1987-06-05",
            "--address-town=laville",
            "--address-country=be",
            "--address-coords-long=123",
            "--address-coords-lat=moving",
        ],
    )
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--address-coords-lat': Input should be a valid number"
        in result.output
    )

    runner = CliRunner()
    result = runner.invoke(
        update_person,
        [
            "marcel",
            "other",
            "--nickname=a",
            "--age=46",
            "--birth-date=1978-03-09",
            "--add-pet=snoopy",
            "--add-pet=pluto",
            "--remove-pet=droopy",
            "--remove-pet=goofy",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {
        "name": "marcel",
        "nickname": "**********",
        "relation": "other",
        "age": 46,
        "birth": {"date": "1978-03-09"},
        "pets": [
            {"name": "snoopy", "state": "present"},
            {"name": "pluto", "state": "present"},
            {"name": "droopy", "state": "absent"},
            {"name": "goofy", "state": "absent"},
        ],
        "memberships": [],
    }


def test_unnest() -> None:
    params = {
        "name": "alice",
        "age": 42,
        "address_city": "paris",
        "address_country": "fr",
        "address_street": ["bd montparnasse"],
        "address_zip_code": 0,
        "address_primary": True,
        "address_coords_long": 0,
        "address_coords_lat": 1.2,
    }
    assert model.unnest(models.Person, params) == {
        "name": "alice",
        "age": 42,
        "address": {
            "city": "paris",
            "coords": {"long": 0, "lat": 1.2},
            "country": "fr",
            "street": ["bd montparnasse"],
            "zip_code": 0,
            "primary": True,
        },
    }

    with pytest.raises(ValueError, match="invalid"):
        model.unnest(models.Person, {"age": None, "invalid": "value"})
    with pytest.raises(ValueError, match="in_va_lid"):
        model.unnest(models.Person, {"age": None, "in_va_lid": "value"})


def test_parse_params_as() -> None:
    address_params = {
        "city": "paris",
        "country": "fr",
        "street": ["bd montparnasse"],
        "zip_code": 0,
        "primary": True,
    }
    address = models.Address(
        street=["bd montparnasse"],
        zip_code=0,
        city="paris",
        country="fr",
        primary=True,
    )
    assert model.parse_params_as(models.Address, address_params) == address

    params = {
        "name": "alice",
        "relation": "other",
        "nickname": "la malice",
        "age": 42,
        "address": address_params,
        "birth": {"date": "1976-05-04"},
    }
    person = models.Person(
        name="alice",
        nickname="la malice",
        relation="other",
        age=42,
        address=address,
        birth=models.BirthInformation(date=date(1976, 5, 4)),  # type: ignore[call-arg]
    )
    assert model.parse_params_as(models.Person, params) == person

    params_nested = {
        "name": "alice",
        "relation": "other",
        "nickname": "la malice",
        "age": 42,
        "birth_date": "1976-05-04",
    }
    params_nested.update({f"address_{k}": v for k, v in address_params.items()})
    assert model.parse_params_as(models.Person, params_nested) == person
