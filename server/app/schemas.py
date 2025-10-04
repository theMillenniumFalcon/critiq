from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
	repo_url: str
	pr_number: int


class AnalyzeResponse(BaseModel):
	task_id: str
	status: str

