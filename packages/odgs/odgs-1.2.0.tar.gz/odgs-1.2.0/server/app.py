import json
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.validate_schema import validate_metric

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(PROJECT_ROOT, "standard_metrics.json")

def load_metrics():
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def save_metrics(metrics):
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

@app.get("/api/metrics")
async def get_metrics():
    try:
        return load_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MetricUpdate(BaseModel):
    metric_id: str
    content: Dict[str, Any]

@app.post("/api/metrics/update")
async def update_metric(update: MetricUpdate):
    try:
        metrics = load_metrics()
        updated = False
        for i, m in enumerate(metrics):
            if m['metric_id'] == update.metric_id:
                metrics[i] = update.content
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="Metric not found")
            
        save_metrics(metrics)
        return {"status": "success", "metric": update.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate")
async def validate_single_metric(metric: Dict[str, Any]):
    issues = validate_metric(metric)
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "score": 100 if len(issues) == 0 else 50
    }

@app.get("/api/summary")
async def get_summary():
    metrics = load_metrics()
    total = len(metrics)
    valid_count = 0
    
    for m in metrics:
        if not validate_metric(m):
            valid_count += 1
            
    return {
        "total_metrics": total,
        "valid_metrics": valid_count,
        "hallucination_risk": "Low" if valid_count == total else "High"
    }
