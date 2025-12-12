from pro_craft_infer.evals import get_datas
import pytest
from pro_craft_infer.evals import calculate_pass_rate_and_assert
from tqdm import tqdm as tqdm_sync

@pytest.fixture
async def test_datas():
    result = await get_datas(database_urls=["vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2",
                                      "vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2-test",
                                      ])
    return result


async def test_evals():
    datas = await get_datas(database_urls=["vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2",
                                    "vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2-test",
                                    ])
    
    
    PASS_THRESHOLD_PERCENT = 90
    async def func(input):
        pass

    sub_case_results = []
    bad_case = []
    for data in tqdm_sync(datas):
        try:
            result = await func(data.content)
            sub_case_results.append(True)
        except AssertionError as e:
            sub_case_results.append(False)
            bad_case.append(f"input: 1 未通过, putput: {result}, Error Info: {e}")
        except Exception as e:
            raise Exception(f"意料之外的错误 {e}")
        
    
    print(sub_case_results,'sub_case_results')
    result_text, x = calculate_pass_rate_and_assert(sub_case_results, f"test_pass_{PASS_THRESHOLD_PERCENT}",PASS_THRESHOLD_PERCENT,
                                            bad_case=bad_case)
    
    print(result_text)
    print(x)

