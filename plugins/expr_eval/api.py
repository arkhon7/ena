from __future__ import annotations

import os
import hashlib
import logging
import traceback
import simpleeval as se

from plugins.expr_eval.entities import (
    CalculatorEnv,
    CalculatorEnvLock,
    Macro,
    KeywordNameError,
    LengthError,
    DuplicateMacroError,
    InvalidNameError,
    EnaResponse,
    MacroPackage,
    NameNotDefinedError,
)

from plugins.cache import EnaCache
from pymongo import errors as mongo_errors
from motor import motor_asyncio


from dataclasses import asdict
from dacite import from_dict
from typing import Dict, List

logging = logging.getLogger(__name__)  # type: ignore


class EnaExpr:
    """CORE FUNCTIONS"""

    def __init__(self) -> None:
        self.conn = motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE_URL"))
        self.cache = EnaCache()

    async def calculate(self, expression: str, user_id: str) -> EnaResponse:

        ena_resp: EnaResponse = await self.fetch_environment(user_id)

        calc_env: CalculatorEnv = ena_resp.data
        env_lock: CalculatorEnvLock = calc_env.build()
        env_data = env_lock.resolve_macro_data(env_data=env_lock.resolve_macro_data())

        result = se.simple_eval(expr=expression, functions=env_data)

        return EnaResponse(message="Solved!", data=result)

        # MAKE EXCEPTIONS HANDLERS HERE

    """MAIN API ENDPOINTS"""

    async def create_macro(self, macro_data: Dict) -> EnaResponse:
        db = self.conn.ena_expr_eval_database
        collec = db.macros

        caller = macro_data["caller"]
        owner_id = macro_data["owner_id"]

        macro_data["_id"] = self.generate_uid(f"{owner_id}.{caller}")
        macro: Macro = from_dict(Macro, macro_data)

        try:
            # validation
            ena_resp: EnaResponse = await self.fetch_environment(owner_id)
            calc_env: CalculatorEnv = ena_resp.data
            macro.build().validate().test_macro(env=calc_env)

            # add to cache/db
            if calc_env.macros:
                calc_env.macros.append(macro)

            else:
                calc_env.macros = [macro]

            await collec.insert_one(asdict(macro))
            await self.cache.put_cache(key=owner_id, field_key="calc", data_key="env", data=calc_env)
            await self.update_environment(owner_id, {"$addToSet": {"macros": asdict(macro)}})

            return EnaResponse(message=f"Successfully created **{macro.name}**", data=macro)

        except mongo_errors.DuplicateKeyError:
            e = DuplicateMacroError(macro=macro)
            return EnaResponse(error=e, data=macro)

        except LengthError as e:
            return EnaResponse(error=e, data=macro)

        except InvalidNameError as e:
            return EnaResponse(error=e, data=macro)

        except KeywordNameError as e:
            return EnaResponse(error=e, data=macro)

        except NameNotDefinedError as e:
            return EnaResponse(error=e, data=macro)

        except Exception:
            # for unhandled exceptions
            tb = traceback.format_exc(limit=2)
            return EnaResponse(message=f"```{tb}```", data=tb)  # type: ignore

    async def read_macro(self, macro_id: str) -> Dict:
        db = self.conn.ena_expr_eval_database
        collec = db.macros

        res = await collec.find_one({"_id": macro_id})
        return res

    async def update_macro(self, macro_id: str, **kwargs: str) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.macros
        # validate here later
        await collec.update_one({"_id": macro_id}, kwargs)

    async def delete_macro(self, macro_id: str) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.macros

        await collec.delete_one({"_id": macro_id})

    """FOR SPECIFIC ENDPOINTS"""

    async def fetch_environment(self, user_id: str) -> EnaResponse:
        db = self.conn.ena_expr_eval_database
        collec = db.environments

        if await self.cache.is_cached(key=user_id, field_key="calc", data_key="env"):
            logging.debug(" Env found on cache, loading from cache instead...")
            cached_calc_env: CalculatorEnv = await self.cache.get_cache(key=user_id, field_key="calc", data_key="env")

            return EnaResponse(message=f"fetched env: {cached_calc_env._id}", data=cached_calc_env)

        else:
            logging.debug(f" Env not on cache, fetching environment of '{user_id}' from db...")

            if res := await collec.find_one({"_id": user_id}):
                calc_env = from_dict(CalculatorEnv, res)  # default
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="env", data=calc_env)

            else:
                calc_env = CalculatorEnv(_id=user_id, packages=[], macros=[])
                await collec.insert_one(asdict(calc_env))
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="env", data=calc_env)

            return EnaResponse(message=f"fetched env: {calc_env._id}", data=calc_env)

    async def update_environment(self, user_id: str, query: Dict) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.environments

        await collec.update_one({"_id": user_id}, query)

        logging.debug(f" Updated env of '{user_id}' with query: {query}")

    async def fetch_macros(self, user_id: str) -> EnaResponse:

        db = self.conn.ena_expr_eval_database
        collec = db.macros

        if await self.cache.is_cached(key=user_id, field_key="calc", data_key="macros"):
            cached_macros: List[Macro] = await self.cache.get_cache(key=user_id, field_key="calc", data_key="macros")

            return EnaResponse(message=f"fetched macros: {cached_macros}", data=cached_macros)

        else:
            raw_macros = collec.find({"owner_id": user_id})
            if raw_macros:
                macros: List[Macro] = [from_dict(Macro, raw_macro) async for raw_macro in raw_macros]
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="macros", data=macros)
                return EnaResponse(data=macros)

            else:
                return EnaResponse(message=f"user {user_id} has no packages!", data=None)

    async def fetch_packages(self, user_id: str) -> EnaResponse:

        db = self.conn.ena_expr_eval_database
        collec = db.packages

        if await self.cache.is_cached(key=user_id, field_key="calc", data_key="packages"):
            cached_packages: List[MacroPackage] = await self.cache.get_cache(
                key=user_id, field_key="calc", data_key="packages"
            )

            return EnaResponse(message=f"fetched macros: {cached_packages}", data=cached_packages)

        else:
            raw_packages = collec.find({"owner_id": user_id})
            if raw_packages:
                packages: List[MacroPackage] = [
                    from_dict(MacroPackage, raw_package) async for raw_package in raw_packages
                ]
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="packages", data=packages)
                return EnaResponse(data=packages)

            else:
                return EnaResponse(message=f"user {user_id} has no packages!", data=None)

    @staticmethod
    def generate_uid(ref: str) -> str:
        uid = hashlib.sha256(ref.encode()).hexdigest()

        return uid
