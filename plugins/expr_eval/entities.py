from __future__ import annotations

import re
import random
import logging

from typing import Any, Optional, List, Dict, Generator

from dacite import from_dict
from dataclasses import dataclass, asdict


import simpleeval as se  # noqa: ignore
import keyword


logging = logging.getLogger(__name__)  # type: ignore


@dataclass
class EnaResponse:
    data: Any  # reference of data
    message: Optional[str] = None
    error: Optional[Any] = None


@dataclass
class CalculatorEnv:
    """environment for calc command, used for database operations"""

    _id: str  # a hash based on user id
    packages: Optional[List[MacroPackage]] = None
    macros: Optional[List[Macro]] = None

    def build(self) -> CalculatorEnvLock:
        """called to parse calc env into a lockfile, which readies the env for
        calculation"""
        package_locks = list()
        macro_locks = list()

        if self.packages:
            for package in self.packages:
                package_lock: MacroPackageLock = package.build()
                package_locks.append(package_lock)

        if self.macros:
            for macro in self.macros:
                macro_lock: MacroLock = macro.build()
                macro_locks.append(macro_lock)

        calc_env_lock = CalculatorEnvLock(_id=self._id, packages=package_locks, macros=macro_locks)

        return calc_env_lock


@dataclass
class CalculatorEnvLock:
    """A locked build used in calculation"""

    _id: str  # a hash from calc_env id
    packages: Optional[List[MacroPackageLock]] = None
    macros: Optional[List[MacroLock]] = None

    def resolve_macro_data(self, env_data: Dict = None) -> Dict:
        """This is called to get the caching data for the environment"""
        calc_env = dict()

        if self.packages:
            for package in self.packages:
                for caller, func_str in package.locked_funcs.items():
                    calc_env[caller] = eval(
                        func_str, {"env_data": env_data, "se": se}
                    )  # make into callables and put into environment

        if self.macros:
            for macro in self.macros:
                calc_env[macro.caller] = eval(macro.func_str, {"env_data": env_data, "se": se})
        logging.debug(f"Env data created: {calc_env}")
        return calc_env


@dataclass
class MacroPackage:
    """A dataclass that stores macros, used for receiving/uploading data to
    database"""

    _id: str  # a hash based on prefix
    name: str
    owner_id: str
    description: str
    prefix: str
    dependencies: Optional[List[MacroPackage]] = None
    macros: Optional[List[Macro]] = None
    public: bool = False
    active: bool = False  # should only be activated inside env not on packages collection

    def build(self) -> MacroPackageLock:
        """called to parse the package into a lockfile, which can be used in
        the calc environment"""

        locked_funcs: Dict = dict()
        if macros := self.get_all_macros(asdict(self)):
            for macro in macros:
                macro_lock: MacroLock = macro.build()
                locked_funcs[macro_lock.caller] = macro_lock.func_str

        package_lock = MacroPackageLock(
            _id=self._id,
            name=self.name,
            owner_id=self.owner_id,
            description=self.description,
            prefix=self.prefix,
            locked_funcs=locked_funcs,
        )

        return package_lock

    def get_all_macros(self, data_dict: Dict) -> Generator[Macro, None, None]:
        """Recursion method for getting all macros in a nested package data
        might need to change this soon if it hits the x1000 limit"""

        if self.dependencies or self.macros:
            for k, v in data_dict.items():
                if k == "dependencies" and isinstance(v, List):
                    for dep in v:
                        if step := self.get_all_macros(dep):
                            yield from step

                elif k == "macros" and isinstance(v, List):
                    for raw_macro in v:
                        raw_macro["caller"] = f"{data_dict['prefix']}_{raw_macro['caller']}"

                        macro: Macro = from_dict(Macro, raw_macro)

                        yield macro

    # def resolve_to(self, env: CalculatorEnv) -> MacroPackage:
    #     # function here for adding dependencies into the package.

    #     for macro in env.macros:
    #         ...

    #     for package in env.packages:
    #         ...
    #     ...


@dataclass
class MacroPackageLock:
    """A locked build for package to be used on caching"""

    _id: str  # a hash from package_id
    name: str
    owner_id: str
    description: str
    prefix: str
    locked_funcs: Dict[str, str]

    def validate(self) -> MacroPackageLock:
        valid_pattern = r"^[_a-zA-Z][_a-zA-Z0-9=]+"
        result = re.match(valid_pattern, self.prefix)

        if result:
            if result.group() == self.prefix:
                return self

        raise InvalidNameError(ref=self.prefix)


@dataclass
class Macro:
    """A custom macro that packs a formula"""

    _id: str  # a hash based on owner_id, caller
    name: str
    owner_id: str
    description: str
    caller: str
    formula: str
    variables: Optional[List[str]] = None
    package_id: Optional[str] = None

    def __repr__(self) -> str:
        return f"Macro(_id={self._id}, caller={self.caller})"

    def build(self) -> MacroLock:

        """call this method before using the macro"""
        if self.variables:
            variables_str: str = ", ".join(self.variables)

        else:
            variables_str = ""

        formula: str = self.formula

        func_str = f'lambda {variables_str}: se.simple_eval(f"{formula}", functions=env_data)'

        macro_lock: MacroLock = MacroLock(
            _id=self._id,
            package_id=self.package_id,
            name=self.name,
            owner_id=self.owner_id,
            description=self.description,
            caller=self.caller,
            variables=self.variables,
            formula=self.formula,
            func_str=func_str,
        )

        return macro_lock


@dataclass
class MacroLock:
    """A locked build for macro to be used for caching"""

    _id: str  # a hash from macro id
    name: str
    owner_id: str
    description: str
    caller: str
    formula: str
    func_str: str
    variables: Optional[List[str]] = None
    package_id: Optional[str] = None

    def validate(self) -> MacroLock:
        self.is_valid_caller().is_valid_variables()
        return self

    def is_valid_caller(self) -> MacroLock:
        valid_pattern = r"^[_a-zA-Z*][_a-zA-Z0-9=]+"
        result = re.match(valid_pattern, self.caller)

        logging.debug(f" caller '{self.caller}' regex validation result: {result}")
        if result:
            match_res = result.group()
            self.is_valid_length(match_res)
            self.is_equal(match_res, self.caller)
            self.is_not_keyword(match_res)
            logging.debug(f"PASSED: {self.caller}")
            return self

        else:
            self.is_char(self.caller)
            logging.debug(f"PASSED: {self.caller}")
            return self

    def is_valid_variables(self) -> MacroLock:
        # valid_pattern = r"^[_a-zA-Z][_a-zA-Z0-9=]+"
        valid_pattern = r"^[_a-zA-Z0-9*]+(\s*=?\s*[0-9.True|False|]+)?"
        if self.variables:
            for v in self.variables:
                var = v.strip()
                result = re.match(valid_pattern, var)
                logging.debug(f" variable '{var}' regex validation result: {result}")

                if result:

                    match_res = result.group()
                    self.is_valid_length(match_res)
                    self.is_equal(match_res, var)
                    self.is_not_keyword(match_res)
                    logging.debug(f"PASSED: {var}")

                else:
                    self.is_char(var)
                    logging.debug(f"PASSED: {var}")

        return self

    def test_macro(self, env: CalculatorEnv):
        if env.macros:
            env.macros.append(
                Macro(
                    _id=self._id,
                    name=self.name,
                    owner_id=self.owner_id,
                    description=self.description,
                    caller=self.caller,
                    formula=self.formula,
                    variables=self.variables,
                    package_id=self.package_id,
                )
            )
        env_lock = env.build()
        env_data = env_lock.resolve_macro_data(env_lock.resolve_macro_data())
        if self.variables:
            test_str = f"{self.caller}({', '.join([str(random.randint(1, 5)) for _ in self.variables])})"

        else:
            test_str = f"{self.caller}()"

        try:
            if env_data.get(self.caller, False):
                env_data[self.caller] = eval(self.func_str, {"env_data": env_data, "se": se})

                logging.debug(f" testing: {self.formula}")
                se.simple_eval(test_str, functions=env_data)
                logging.debug(f"PASSED: {self.formula}")

            else:
                raise CallerAlreadyUsedError(ref=self.caller)

        except se.NameNotDefined as e:
            raise NameNotDefinedError(ref=e)

        except Exception as e:
            raise Exception(e)

    # tests
    def is_char(self, raw_result: str) -> Optional[bool]:
        if len(raw_result) == 1 and isinstance(raw_result, str):
            return True

        raise InvalidNameError(ref=raw_result)

    def is_valid_length(self, match_result: str) -> Optional[bool]:
        if len(match_result) <= 30:
            return True

        raise LengthError(ref=match_result)

    def is_equal(self, match_result: str, raw_result: str) -> Optional[bool]:
        if match_result == raw_result:
            return True

        raise InvalidNameError(ref=raw_result)

    def is_not_keyword(self, match_result: str) -> Optional[bool]:
        if match_result not in keyword.kwlist:
            return True

        raise KeywordNameError(ref=match_result)


"""EXCEPTIONS"""


class EnaError(Exception):
    def __init__(self, ref: Any = None, message: str = None) -> None:
        super().__init__()
        self.ref = ref
        self.message = message


# uploading errors
class DuplicateMacroError(EnaError):
    def __init__(self, macro: Macro) -> None:
        super().__init__()
        self.ref = macro
        self.message = (
            f"Your macro __{self.ref.name}__ is using an already existing caller "
            f"__{self.ref.caller}__ which conflicts with your other macros. Please change it."
        )


class DuplicatePackageError(EnaError):
    def __init__(self, package: Macro) -> None:
        super().__init__()
        self.ref = package
        self.message = (
            f"Your package __{self.ref.name}__ is using an already existing caller "
            f"__{self.ref.caller}__ which conflicts with your other macros. Please change it."
        )


# validating macro errors
class LengthError(EnaError):
    def __init__(self, ref: str) -> None:
        super().__init__()
        self.ref = ref
        self.message = f"__{self.ref}__ should not be longer than 30 characters!"


class InvalidNameError(EnaError):
    def __init__(self, ref: str) -> None:
        super().__init__()
        self.ref = ref
        self.message = f"__{self.ref}__ is not a valid name!"


class KeywordNameError(EnaError):
    def __init__(self, ref: str) -> None:
        super().__init__()
        self.ref = ref
        self.message = f"__{self.ref}__ is already used! Please use another name for this."


# testing errors
class NameNotDefinedError(EnaError):
    def __init__(self, ref: se.NameNotDefined) -> None:
        super().__init__()
        self.ref = ref
        self.message = (
            f"Your formula __{self.ref.expression}__ is using __{self.ref.name}__ which is not "
            f"a macro, is this a variable? If so, please write it like this ```{{{self.ref.name}}}```"
        )


class CallerAlreadyUsedError(EnaError):
    def __init__(self, ref: str) -> None:
        super().__init__()
        self.ref = ref
        self.message = f"__{self.ref}__ is already used! Please use another name for this."
