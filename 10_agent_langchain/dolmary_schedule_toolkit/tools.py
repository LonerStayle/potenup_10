from typing import List, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# 스케줄 등록하는 리스트
# 1. 스케줄 등록 도구
# 2. 스케줄 확인 도구
dol_schedule: List[str] = []
dol_complete_schedule:List[str] = []

# 1-1. 스케줄 스키마 설정
class AddToDoInput(BaseModel):
    item: str = Field(description="오늘 할 돌마리 스케줄 항목")
    
# 1-2. 스케줄 등록 도구 설정
class AddToDoTool(BaseTool):
    name : str = "add_todo"
    description  : str = "돌마리 스케줄에 새 항목을 추가합니다"
    args_schema : Type[BaseModel] = AddToDoInput

    def _run(self, item:str) -> str:
        dol_schedule.append(item)
        return f"{item}이 돌마리 스케쥴에 등록 되었습니다."
    
# 2-1 스케쥴 확인 스키마 
# 2-2. 스케쥴 확인 도구 설정  
class ViewToDoTool(BaseTool):
    name :str = "view_todos"
    description : str = "현재 돌마리 스케쥴 전체 목록을 보여줍니다."

    def _run(self):
        if not dol_schedule:
            return "할일이 없어요"
        all_schedule = "\n".join(dol_schedule)
        return f"할일 목록은 : {all_schedule}\n입니다"
    
class ViewCompleteToDoTool(BaseTool):
    name :str = "view_completes"
    description : str = "이미 진행했던 돌마리 스케쥴 전체 진행이 완료되었습니다."

    def _run(self):
        if not dol_complete_schedule: 
            return "돌마리 스케쥴 진행이 완료되었습니다."
        
        dol_complete_schedule = "\n".join(dol_complete_schedule)
        return f"이미 완료한 스케쥴은 : {dol_complete_schedule}\n입니다"


class DeleteTool(BaseTool):
    name :str = "delete_todo"
    description = "돌마리 스케쥴에 예정되었던 항목을 삭제합니다."

    def _run(self, item:str) -> str:
        dol_schedule.remove(item)
        return f'말씀하신 스케쥴이 삭제되었습니다.'



class CompleteTool(BaseTool):
    name:str = "complete_todo"
    description = "돌마리 스케쥴 진행이 완료되었습니다."

    def _run(self, item:str) -> str:
        dol_complete_schedule.append(item)
        dol_schedule.remove(item)
        return '돌마리 스케쥴에 완료되었습니다.'
        
