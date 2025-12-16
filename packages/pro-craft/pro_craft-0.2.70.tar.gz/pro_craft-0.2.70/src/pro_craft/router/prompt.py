from .models import *
from fastapi import APIRouter, Depends, HTTPException, status, Header
from toolkitz.core import create_async_session
import logging
from pro_craft import AsyncIntel


def create_router(model_name: str,
                  database_url: str,
                  test_database_url: str = None,
                  product_database_url: str = None
                  ):
    
    test_database_url = "mysql+aiomysql://" + test_database_url
    product_database_url = "mysql+aiomysql://" + product_database_url


    intels = AsyncIntel(
        database_url=database_url,
        model_name=model_name,
        )

    async def verify_api_key(authorization: Optional[str] = Header(None)):
        if authorization != "1234":
            raise HTTPException(status_code=401, detail="Error Server Position2")

    router = APIRouter(
        tags=["prompt"], # 这里使用 Depends 确保每次请求都验证
        dependencies = [Depends(verify_api_key)]
    )

    @router.get("/registered_prompt",
                description="获取已注册的提示词",
                response_model=PromptResponse)
    async def registered_prompt():
        try:
            async with create_async_session(intels.engine) as session:
                result = await intels.get_all_prompt_id(session)
            
            return PromptResponse(msg = "success",content=result)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )
        
    @router.post("/get_prompt",
                description="获得现行提示词",
                response_model=PromptResponse)
    async def get_prompt(request: GetPromptRequest):
        try:
            async with create_async_session(intels.engine) as session:
                result = await intels.get_prompt(
                    prompt_id=request.prompt_id,
                    version = request.version,
                    session=session
                )
            return PromptResponse(msg = "success",content={"prompt": result.prompt, "version": result.version})
    
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )
        
    @router.post("/update_prompt",
                description="更新现行提示词",
                response_model=PromptResponse)
    async def update_prompt(request: UpdatePromptRequest):
        try:
            async with create_async_session(intels.engine) as session:
                await intels.save_prompt(
                                prompt_id = request.prompt_id,
                                new_prompt = request.prompt,
                                use_case = "",
                                action_type = "inference",
                                demand = "上传",
                                score = 70,
                                session = session)
                return PromptResponse(msg = "success",content="")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )

    @router.post("/rollback_prompt",
                description="回滚现行提示词",
                response_model=PromptResponse)
    async def roll_back(request: RollBackPromptRequest):
        try:
            async with create_async_session(intels.engine) as session:
                result = await intels.get_prompt(
                    prompt_id=request.prompt_id,
                    version = request.version,
                    session=session
                )
                assert result.version == request.version
                await intels.save_prompt(
                                prompt_id = request.prompt_id,
                                new_prompt = result.prompt,
                                use_case = result.use_case,
                                action_type = "inference",
                                demand = "",
                                score = 61,
                                session = session)
            return PromptResponse(msg = "success",content="")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )
        
    
    @router.post("/sync_test_database",
                 description="同步到测试数据库",
                response_model=PromptResponse)
    async def sync_test_database():
        try:
            result = await intels.sync_production_database(test_database_url)
            return PromptResponse(msg = "success",content="")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )
    
    @router.post("/sync_product_database",
                 description="同步到生产数据库",
                response_model=PromptResponse)
    async def sync_product_database():
        try:
            result = await intels.sync_production_database(product_database_url)
            return PromptResponse(msg = "success",content="")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{e}"
            )

    return router
