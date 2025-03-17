from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import openai
from routellm.controller import Controller
import time
import logging
import traceback
import datetime  # Import the datetime module
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, text
from dotenv import load_dotenv
import random

load_dotenv()  # Load environment variables from .env

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log', mode='a')
    ]
)

logger = logging.getLogger("moolai-api")
logger.setLevel(logging.INFO)

# Define the LoggingMiddleware class
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Simple request log
        logger.info(f">>> {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Simple response log
            logger.info(f"<<< {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"!!! Request failed: {str(e)}")
            raise

# Initialize FastAPI app and add middleware
app = FastAPI()
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------

DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise EnvironmentError("DB_URL environment variable is not set.")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the LLMResult model
class LLMResult(Base):
    __tablename__ = "llm_results"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(512), index=True)  # Reduce length for index
    selected_model = Column(String(256))
    latency = Column(Float)
    cost = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost_gpt4 = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    month = Column(Integer)  # Add month column
    year = Column(Integer)  # Add year column
    is_openai = Column(Boolean)  # Add is_openai column

#Base.metadata.create_all(bind=engine)  # Create tables if they don't exist # moved inside the endpoints where it's needed. This will execute only if an endpoint is reached and called.

# -----------------------------------------------------------------------------
# OpenAI API Key
# -----------------------------------------------------------------------------

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
openai.api_key = OPENAI_API_KEY

# -----------------------------------------------------------------------------
# Routers Configuration
# -----------------------------------------------------------------------------

controller = None
try:
    controller = Controller(
        routers=["mf"],
        strong_model="gpt-4o",
        weak_model="gpt-3.5-turbo",
        config={
            "mf": {"checkpoint_path": "routellm/mf_gpt4_augmented"},
        }
    )
except Exception as e:
    print(f"Error initializing controller: {str(e)}")

# -----------------------------------------------------------------------------
# Data Models (Pydantic)
# -----------------------------------------------------------------------------

class PromptRequest(BaseModel):
    prompt: str

class RouteLLMResponse(BaseModel):
    response: str
    model_used: str
    latency: float
    cost: float
    input_tokens: int
    output_tokens: int
    selected_model: str

class DashboardData(BaseModel):
    total_savings: float
    total_api_calls: int
    openai_api_calls: int
    moolai_api_calls: int
    total_cost: float
    openai_cost: float
    moolai_cost: float
    cost_optimization_impact: List[Dict]
    monthly_cost_breakdown: List[Dict]
    api_call_vs_cost_distribution_savings: float
    api_call_vs_cost_distribution_call_percentage_openai: float
    api_call_vs_cost_distribution_call_percentage_moolai: float
    api_call_vs_cost_distribution_cost_percentage_openai: float
    api_call_vs_cost_distribution_cost_percentage_moolai: float
    monthly_api_calls_comparison: List[Dict]
    total_tokens_openai: int  # New field for total OpenAI tokens
    total_tokens_moolai: int   # New field for total MoolAI tokens
    total_tokens: int #New field for the Cost optimization impact and call distribution graph
    total_cost_gpt4: float


# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    if "gpt-4" in model_name.lower():
        return (input_tokens * 5e-6) + (output_tokens * 1.5e-5)
    elif "gpt-3.5" in model_name.lower():
        return (input_tokens * 2.5e-7) + (output_tokens * 1.25e-6)
    else:
        return 0.0

def calculate_gpt4_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens * 5e-6) + (output_tokens * 1.5e-5)

def get_response(prompt: str, router: str = "mf") -> RouteLLMResponse:
    """Get response from the LLM controller."""
    global controller

    if controller is None:
        logger.error("Controller not initialized")
        raise HTTPException(status_code=500, detail="Controller not initialized.")

    try:
        logger.info(f"Routing prompt to controller...")
        start_time = time.time()

        response = controller.chat.completions.create(
            model=f"router-{router}-0.11593",
            messages=[{"role": "user", "content": prompt}]
        )

        end_time = time.time()
        latency = end_time - start_time

        input_tokens = len(prompt)
        output_tokens = len(response.choices[0].message.content)
        selected_model = response.model
        cost = calculate_cost(selected_model, input_tokens, output_tokens)

        logger.info(f"Response received - Model: {selected_model} - Time: {latency:.2f}s")

        return RouteLLMResponse(
            response=response.choices[0].message.content,
            model_used=f"RouteLLM Router ({router.upper()})",
            latency=latency,
            cost=cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            selected_model=selected_model,
        )

    except Exception as e:
        logger.error(f"Error in get_response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.post("/process_prompt", response_model=RouteLLMResponse)
async def process_prompt(request: PromptRequest):
    """Process a single prompt."""
    logger.info(f"Processing prompt: {request.prompt[:50]}...")

    try:
        response = get_response(request.prompt)
        logger.info(f"Prompt processed - Model: {response.model_used} - Cost: ${response.cost:.4f}")
        return response
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        raise

class QuestionsRequest(BaseModel):
    questions: List[str]

# Dependency Injection for Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/process_50_questions")
async def process_50_questions(request: QuestionsRequest, db: SessionLocal = Depends(get_db)):
    """Processes a list of questions, calculates metrics, and stores results in the database."""
    # creating a table if it does not exist
    Base.metadata.create_all(bind=db.bind)
    logger.debug(f"Starting processing of {len(request.questions)} questions")
    start_time = time.time()

    questions = request.questions
    metrics = []
    total_cost_gpt4 = 0
    strong_model_calls = 0
    weak_model_calls = 0
    total_latency = 0

    try:
        for i, question in enumerate(questions, 1):
            logger.debug(f"Processing question {i}/{len(request.questions)}: {question[:50]}...")
            llm_response = get_response(question)

            cost_gpt4 = calculate_gpt4_cost(llm_response.input_tokens, llm_response.output_tokens)
            total_cost_gpt4 += cost_gpt4

            selected_model = llm_response.selected_model

            # Determine if the call was to OpenAI or MoolAI based on the selected model
            is_openai = "gpt-4" in selected_model.lower()

            # Standardize the selected model name
            if "gpt-3.5" in selected_model.lower():
                selected_model = "Mool AI"
            #    is_openai = False # removed
            elif "gpt-4" in selected_model.lower():
                selected_model = "GPT-4"
             #   is_openai = True # Removed

            current_date = datetime.datetime.utcnow()
            # Store results in the database
            db_result = LLMResult(
                question=question,
                selected_model=selected_model,
                latency=llm_response.latency,
                cost=llm_response.cost,
                input_tokens=llm_response.input_tokens,
                output_tokens=llm_response.output_tokens,
                cost_gpt4=cost_gpt4,
                date=current_date,  # Use the datetime object directly
                month=current_date.month,
                year=current_date.year,
                is_openai=is_openai, #Here
            )
            db.add(db_result)
            db.commit()
            db.refresh(db_result)  # Refresh to get the assigned ID

            metrics.append({
                "Question": question,
                "Selected Model": selected_model,
                "Latency (s)": llm_response.latency,
                "Cost ($)": llm_response.cost,
                "Input Tokens": llm_response.input_tokens,
                "Output Tokens": llm_response.output_tokens,
                "Cost_GPT4 ($)": cost_gpt4
            })

            if is_openai:  # Use is_openai value directly based on call.
                strong_model_calls += 1
            else:
                weak_model_calls += 1

            total_latency += llm_response.latency

            logger.debug(f"Question {i} processed. Model: {selected_model}, Cost: ${llm_response.cost:.4f}")

        end_time = time.time()
        total_processing_time = end_time - start_time

        #logger.info(f"Total processing time for 50: {total_processing_time:.2f}s")
        logger.info(f"""
        Processing completed:
        - Total questions: {len(questions)}
        - Total processing time: {total_processing_time:.2f}s
        """)

        # Return metrics to client instead of cached data
        return {"metrics": metrics}

    except Exception as e:
        logger.error(f"Error processing questions batch: {str(e)}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/populate_historical_data")
async def populate_historical_data(db: SessionLocal = Depends(get_db)):
    start_date = datetime.datetime(2024, 11, 18)
    end_date = datetime.datetime(2024, 11, 18)
    current_date = start_date

    while current_date <= end_date:
        # Your list of 50 questions
        questions = [
            "What is the capital of France?",
            "Explain the process of photosynthesis.",
            "What is Bernoulli's Principle?",
            "How does entropy relate to the Second Law of Thermodynamics? ",
            "Explain how a transistor works in a circuit.",
            "Why do superconductors work at extremely low temperatures?",
            "How does quantum entanglement defy classical physics?",
            "What is the Trolley Problem in ethics?",
            "How does Kant's categorical imperative differ from utilitarianism?",
            "What are the philosophical implications of AI consciousness?"
        ]

        for question in questions:
            llm_response = get_response(question)
            
            cost_gpt4 = calculate_gpt4_cost(llm_response.input_tokens, llm_response.output_tokens)
            
            is_openai = "gpt-4" in llm_response.selected_model.lower()
            selected_model = "Mool AI" if "gpt-3.5" in llm_response.selected_model.lower() else "GPT-4"

            db_result = LLMResult(
                question=question,
                selected_model=selected_model,
                latency=llm_response.latency,
                cost=llm_response.cost,
                input_tokens=llm_response.input_tokens,
                output_tokens=llm_response.output_tokens,
                cost_gpt4=cost_gpt4,
                date=current_date,
                month=current_date.month,
                year=current_date.year,
                is_openai=is_openai,
            )
            db.add(db_result)
        
        db.commit()
        current_date += datetime.timedelta(days=1)

    return {"message": "Historical data population complete."}


@app.get("/dashboard_data", response_model=DashboardData)
async def get_dashboard_data(db: SessionLocal = Depends(get_db)):
    """Retrieves dashboard data for display from database."""
    #Creating the table if it does not exist
    Base.metadata.create_all(bind=db.bind)

    logger.debug("Dashboard data requested")

    try:
        # Recalculate all
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        # Calculate Total Cost GPT4
        total_cost_gpt4 = db.query(func.sum(LLMResult.cost_gpt4)).scalar() or 0

        # Calculate Total Savings with MoolAI
        total_savings = total_cost_gpt4 - (db.query(func.sum(LLMResult.cost)).scalar() or 0)

        # Calculate Total API Calls
        total_api_calls = db.query(func.count(LLMResult.id)).scalar() or 0

        # Calculate OpenAI and MoolAI API Calls
        openai_calls = db.query(func.count(LLMResult.id)).filter(LLMResult.is_openai == True).scalar() or 0
        moolai_calls = db.query(func.count(LLMResult.id)).filter(LLMResult.is_openai == False).scalar() or 0

        # Calculate Total Cost
        total_cost = db.query(func.sum(LLMResult.cost)).scalar() or 0

        # Calculate OpenAI and MoolAI Cost
        openai_cost = db.query(func.sum(LLMResult.cost)).filter(LLMResult.is_openai == True).scalar() or 0
        moolai_cost = db.query(func.sum(LLMResult.cost)).filter(LLMResult.is_openai == False).scalar() or 0

        # Calculate Cost Optimization Impact (Last 5 Months)
        cost_optimization_impact = []
        for i in range(5):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1

            potential_cost = db.query(func.sum(LLMResult.cost_gpt4)).filter(
                LLMResult.month == month, LLMResult.year == year
            ).scalar() or 0
            actual_cost = db.query(func.sum(LLMResult.cost)).filter(
                LLMResult.month == month, LLMResult.year == year
            ).scalar() or 0
            cost_optimization_impact.append({"month": month, "potential_cost": potential_cost or 0, "actual_cost": actual_cost or 0})

        # Calculate Monthly Cost Breakdown (Last 15 Days)
        monthly_cost_breakdown = []
        today = datetime.datetime.now()
        for i in range(15):
            date = today - datetime.timedelta(days=i)
            openai_cost_day = db.query(func.sum(LLMResult.cost)).filter(
                func.date(LLMResult.date) == date.date(), LLMResult.is_openai == True
            ).scalar() or 0
            moolai_cost_day = db.query(func.sum(LLMResult.cost)).filter(
                func.date(LLMResult.date) == date.date(), LLMResult.is_openai == False
            ).scalar() or 0
            monthly_cost_breakdown.append({"date": date.strftime("%Y-%m-%d"), "openai_cost": openai_cost_day or 0, "moolai_cost": moolai_cost_day or 0})

        # Calculate API Call vs Cost Distribution
        total_calls = db.query(func.count(LLMResult.id)).scalar() or 0
        openai_calls = db.query(func.count(LLMResult.id)).filter(LLMResult.is_openai == True).scalar() or 0
        moolai_calls = db.query(func.count(LLMResult.id)).filter(LLMResult.is_openai == False).scalar() or 0
        api_call_vs_cost_distribution_savings = total_cost_gpt4 - total_cost

        api_call_vs_cost_distribution_call_percentage_openai = (openai_calls / total_calls) * 100 if total_calls > 0 else 0
        # Check for division by zero
        api_call_vs_cost_distribution_call_percentage_moolai = (moolai_calls / total_calls) * 100 if total_calls > 0 else 0

        total_cost_total = db.query(func.sum(LLMResult.cost)).scalar() or 0
        openai_cost_total = db.query(func.sum(LLMResult.cost)).filter(LLMResult.is_openai == True).scalar() or 0
        moolai_cost_total = db.query(func.sum(LLMResult.cost)).filter(LLMResult.is_openai == False).scalar() or 0

        api_call_vs_cost_distribution_cost_percentage_openai = (openai_cost_total / total_cost_total) * 100 if total_cost_total > 0 else 0
        api_call_vs_cost_distribution_cost_percentage_moolai = (moolai_cost_total / total_cost_total) * 100 if total_cost_total > 0 else 0

        # Calculate Monthly API Calls Comparison (Last 15 Days)
        monthly_api_calls_comparison = []
        today = datetime.datetime.now()
        for i in range(15):
            date = today - datetime.timedelta(days=i)
            openai_calls_day = db.query(func.count(LLMResult.id)).filter(
                func.date(LLMResult.date) == date.date(), LLMResult.is_openai == True
            ).scalar() or 0
            moolai_calls_day = db.query(func.count(LLMResult.id)).filter(
                func.date(LLMResult.date) == date.date(), LLMResult.is_openai == False
            ).scalar() or 0
            monthly_api_calls_comparison.append({"date": date.strftime("%Y-%m-%d"), "openai_calls": openai_calls_day or 0, "moolai_calls": moolai_calls_day or 0})

        # Calculate Total Tokens for OpenAI and MoolAI
        total_tokens_openai = db.query(func.sum(LLMResult.input_tokens + LLMResult.output_tokens)).filter(LLMResult.is_openai == True).scalar() or 0
        total_tokens_moolai = db.query(func.sum(LLMResult.input_tokens + LLMResult.output_tokens)).filter(LLMResult.is_openai == False).scalar() or 0

        # Calculate the total tokens altogether
        total_tokens = db.query(func.sum(LLMResult.input_tokens + LLMResult.output_tokens)).scalar() or 0

        results = {
            "total_savings": total_savings,
            "total_api_calls": total_calls,
            "openai_api_calls": openai_calls,
            "moolai_api_calls": moolai_calls,
            "total_cost": total_cost,
            "openai_cost": openai_cost,
            "moolai_cost": moolai_cost,
            "cost_optimization_impact": cost_optimization_impact,
            "monthly_cost_breakdown": monthly_cost_breakdown,
            "api_call_vs_cost_distribution_savings": api_call_vs_cost_distribution_savings,
            "api_call_vs_cost_distribution_call_percentage_openai": api_call_vs_cost_distribution_call_percentage_openai , #Had defaults
            "api_call_vs_cost_distribution_call_percentage_moolai": api_call_vs_cost_distribution_call_percentage_moolai , #Had defaults
            "api_call_vs_cost_distribution_cost_percentage_openai": api_call_vs_cost_distribution_cost_percentage_openai,
            "api_call_vs_cost_distribution_cost_percentage_moolai": api_call_vs_cost_distribution_cost_percentage_moolai,
            "monthly_api_calls_comparison": monthly_api_calls_comparison,
            "total_tokens_openai": total_tokens_openai,
            "total_tokens_moolai": total_tokens_moolai,
            "total_tokens": total_tokens,
            "total_cost_gpt4": total_cost_gpt4
            
        }

        logger.info("Returning dashboard data from database")
        return results

    except Exception as e:
        logger.error(f"Error retrieving dashboard data from database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving dashboard data from database"
        )

# -----------------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------------

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    # Creating the table on start up to begin operations
    Base.metadata.create_all(bind=engine)
    logger.info("=== FastAPI Server Starting ===")
    logger.info("Endpoints available:")
    logger.info("  POST /process_prompt")
    logger.info("  POST /process_50_questions")
    logger.info("  GET  /dashboard_data")
    logger.info("  POST /populate_historical_data")
# -----------------------------------------------------------------------------
# End of File
# -----------------------------------------------------------------------------
