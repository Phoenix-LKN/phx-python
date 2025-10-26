from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gpt4all_client import get_gpt4all_client
from typing import List

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    context: str = ""

class ChatResponse(BaseModel):
    response: str
    confidence: float

class SuggestionRequest(BaseModel):
    lead_data: dict
    worksheet_data: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatMessage):
    try:
        gpt4all = get_gpt4all_client()
        
        prompt = f"Context: {request.context}\n\nUser: {request.message}\n\nAssistant:"
        response = gpt4all.generate(prompt, max_tokens=500)
        
        return ChatResponse(response=response, confidence=0.8)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/suggestions")
async def get_suggestions(request: SuggestionRequest):
    try:
        gpt4all = get_gpt4all_client()
        
        prompt = f"""
        Based on the following lead and worksheet data, provide suggestions for next steps:
        
        Lead Data: {request.lead_data}
        Worksheet Data: {request.worksheet_data}
        
        Provide 3-5 actionable suggestions:
        """
        
        suggestions = gpt4all.generate(prompt, max_tokens=300)
        
        return {"suggestions": suggestions.split('\n')}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/analyze-lead")
async def analyze_lead(lead_data: dict):
    try:
        gpt4all = get_gpt4all_client()
        
        prompt = f"""
        Analyze this lead and provide insights:
        {lead_data}
        
        Provide analysis on:
        1. Lead quality score (1-10)
        2. Potential challenges
        3. Recommended approach
        """
        
        analysis = gpt4all.generate(prompt, max_tokens=400)
        
        return {"analysis": analysis}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
