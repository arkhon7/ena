"""THIS MODULE SHOULD ONLY RETURN STATUSES"""


from __future__ import annotations

import os
import hashlib
import logging
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
)

from plugins.cache import EnaCache
from pymongo import errors as mongo_errors
from motor import motor_asyncio


from dataclasses import asdict
from dacite import from_dict
from typing import Dict

logging = logging.getLogger(__name__)  # type: ignore


class EnaExpr:
    """CORE FUNCTIONS"""

    def __init__(self) -> None:
        self.conn = motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE_URL"))
        self.cache = EnaCache()

    async def calculate(self, expression: str, user_id: str) -> EnaResponse:

        calc_env: CalculatorEnv = await self.fetch_environment(user_id)
        env_lock: CalculatorEnvLock = calc_env.build()
        env_data = env_lock.resolve_macro_data(env_data=env_lock.resolve_macro_data())

        result = se.simple_eval(expr=expression, functions=env_data)

        return EnaResponse(message="Solved!", data=result)

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
            calc_env: CalculatorEnv = await self.fetch_environment(owner_id)
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
            return EnaResponse(error=e)

        except LengthError as e:
            return EnaResponse(error=e)

        except InvalidNameError as e:
            return EnaResponse(error=e)

        except KeywordNameError as e:
            return EnaResponse(error=e)

    async def read_macro(self, macro_id: str) -> Dict:
        db = self.conn.ena_expr_eval_database
        collec = db.macros

        res = await collec.find_one({"_id": macro_id})
        return res

    async def update_macro(self, macro_id: str, query: Dict) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.macros
        # validate here later
        await collec.update_one({"_id": macro_id}, query)

    async def delete_macro(self, macro_id: str) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.macros

        await collec.delete_one({"_id": macro_id})

    """FOR ENVIRONMENTS [INTERNAL OPERATION ONLY]"""

    async def fetch_environment(self, user_id: str) -> CalculatorEnv:
        db = self.conn.ena_expr_eval_database
        collec = db.environments

        if await self.cache.is_cached(key=user_id, field_key="calc", data_key="env"):
            logging.debug(" Env found on cache, loading from cache instead...")
            cached_calc_env = await self.cache.get_cache(key=user_id, field_key="calc", data_key="env")
            return cached_calc_env

        else:
            logging.debug(f" Env not on cache, fetching environment of '{user_id}' from db...")

            if res := await collec.find_one({"_id": user_id}):
                calc_env = from_dict(CalculatorEnv, res)  # default
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="env", data=calc_env)

            else:
                calc_env = CalculatorEnv(_id=user_id, packages=[], macros=[])
                await collec.insert_one(asdict(calc_env))
                await self.cache.put_cache(key=user_id, field_key="calc", data_key="env", data=calc_env)

            return calc_env

    async def update_environment(self, user_id: str, query: Dict) -> None:
        db = self.conn.ena_expr_eval_database
        collec = db.environments

        await collec.update_one({"_id": user_id}, query)

        logging.debug(f" Updated env of '{user_id}' with query: {query}")

    @staticmethod
    def generate_uid(ref: str) -> str:
        uid = hashlib.sha256(ref.encode()).hexdigest()

        return uid
