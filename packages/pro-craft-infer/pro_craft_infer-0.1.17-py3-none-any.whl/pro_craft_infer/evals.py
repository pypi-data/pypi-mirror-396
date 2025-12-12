from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from toolkitz.content import create_async_session
from .database import Prompt, UseCase, DataCollection, PromptBase
from tqdm import tqdm as tqdm_sync
import json
import pytest

def calculate_pass_rate_and_assert(results, test_name, PASS_THRESHOLD_PERCENT = 90,bad_case = []):
    """
    辅助函数：计算通过率并根据阈值进行断言。
    results: 包含 True (通过) 或 False (失败) 的列表
    test_name: 测试名称，用于打印信息
    """
    result_text = ""
    if not results:
        pytest.fail(f"测试 '{test_name}' 没有执行任何子用例。")

    total_sub_cases = len(results)
    passed_sub_cases = results.count(True)
    pass_rate = (passed_sub_cases / total_sub_cases) * 100

    result_text +=f"\n--- 测试 '{test_name}' 内部结果 ---\n"
    result_text +=f"总子用例数: {total_sub_cases}\n"
    result_text +=f"通过子用例数: {passed_sub_cases}\n"
    result_text +=f"通过率: {pass_rate:.2f}%\n"

    if pass_rate >= PASS_THRESHOLD_PERCENT:
        result_text += f"通过率 ({pass_rate:.2f}%) 达到或超过 {PASS_THRESHOLD_PERCENT}%。测试通过。\n"
        assert True # 显式断言成功
        x = 0
    else:
        result_text += f"通过率 ({pass_rate:.2f}%) 低于 {PASS_THRESHOLD_PERCENT}%。测试失败。\n"
        result_text += "bad_case:" + '\n'.join(bad_case)
        x = 1
    return result_text,x


async def get_datas(
        database_urls = [""],
        limit_number = 1000)-> list:
    datas = []
    for database_url in database_urls:
        engine = create_async_engine("mysql+aiomysql://" + database_url, echo=False)

        async with create_async_session(engine) as session:
            result = await session.execute(
                select(DataCollection)
                .filter(DataCollection.level=='USECASE',DataCollection.is_deleted==0)
                .order_by(DataCollection.timestamp.desc())
                .limit(limit_number)
            )
            data = result.scalars().all()
            datas += data
    return datas
            

 
