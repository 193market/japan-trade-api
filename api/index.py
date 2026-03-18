from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Japan Trade Data API",
    description="Japan international trade data including exports, imports, trade balance, and foreign direct investment. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE_URL = "https://api.worldbank.org/v2/country/JP/indicator"

INDICATORS = {
    "exports_usd":    {"id": "NE.EXP.GNFS.CD",  "name": "Exports of Goods & Services",  "unit": "Current USD"},
    "imports_usd":    {"id": "NE.IMP.GNFS.CD",  "name": "Imports of Goods & Services",  "unit": "Current USD"},
    "exports_pct":    {"id": "NE.EXP.GNFS.ZS",  "name": "Exports",                       "unit": "% of GDP"},
    "imports_pct":    {"id": "NE.IMP.GNFS.ZS",  "name": "Imports",                       "unit": "% of GDP"},
    "trade_openness": {"id": "NE.TRD.GNFS.ZS",  "name": "Trade Openness",                "unit": "% of GDP"},
    "current_acct":   {"id": "BN.CAB.XOKA.CD",  "name": "Current Account Balance",       "unit": "Current USD"},
    "merch_exports":  {"id": "TX.VAL.MRCH.CD.WT","name": "Merchandise Exports",           "unit": "Current USD"},
    "merch_imports":  {"id": "TM.VAL.MRCH.CD.WT","name": "Merchandise Imports",           "unit": "Current USD"},
    "fdi_inflows":    {"id": "BX.KLT.DINV.CD.WD","name": "FDI Net Inflows",               "unit": "Current USD"},
    "fdi_outflows":   {"id": "BM.KLT.DINV.CD.WD","name": "FDI Net Outflows",              "unit": "Current USD"},
}


async def fetch_wb(indicator_id: str, limit: int = 10):
    url = f"{WB_BASE_URL}/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


@app.get("/")
def root():
    return {
        "api": "Japan Trade Data API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "country": "Japan (JP)",
        "endpoints": [
            "/summary", "/exports", "/imports", "/trade-balance",
            "/trade-openness", "/merchandise", "/fdi", "/current-account"
        ],
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(limit: int = Query(default=5, ge=1, le=30)):
    """All Japan trade indicators snapshot"""
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb(meta["id"], limit)
    formatted = {
        key: {
            "name": INDICATORS[key]["name"],
            "unit": INDICATORS[key]["unit"],
            "data": results[key],
        }
        for key in INDICATORS
    }
    return {
        "country": "Japan",
        "country_code": "JP",
        "source": "World Bank Open Data",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/exports")
async def exports(limit: int = Query(default=10, ge=1, le=60)):
    """Japan exports of goods and services (current USD)"""
    data = await fetch_wb("NE.EXP.GNFS.CD", limit)
    return {
        "indicator": "Exports of Goods & Services",
        "series_id": "NE.EXP.GNFS.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/imports")
async def imports(limit: int = Query(default=10, ge=1, le=60)):
    """Japan imports of goods and services (current USD)"""
    data = await fetch_wb("NE.IMP.GNFS.CD", limit)
    return {
        "indicator": "Imports of Goods & Services",
        "series_id": "NE.IMP.GNFS.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/trade-balance")
async def trade_balance(limit: int = Query(default=10, ge=1, le=60)):
    """Japan current account balance"""
    data = await fetch_wb("BN.CAB.XOKA.CD", limit)
    return {
        "indicator": "Current Account Balance",
        "series_id": "BN.CAB.XOKA.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/trade-openness")
async def trade_openness(limit: int = Query(default=10, ge=1, le=60)):
    """Japan trade (exports + imports) as % of GDP"""
    data = await fetch_wb("NE.TRD.GNFS.ZS", limit)
    return {
        "indicator": "Trade Openness (Exports + Imports / GDP)",
        "series_id": "NE.TRD.GNFS.ZS",
        "unit": "% of GDP",
        "frequency": "Annual",
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/merchandise")
async def merchandise(limit: int = Query(default=10, ge=1, le=60)):
    """Japan merchandise exports and imports"""
    exp = await fetch_wb("TX.VAL.MRCH.CD.WT", limit)
    imp = await fetch_wb("TM.VAL.MRCH.CD.WT", limit)
    return {
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "merchandise_exports": {"series_id": "TX.VAL.MRCH.CD.WT", "unit": "Current USD", "data": exp},
        "merchandise_imports": {"series_id": "TM.VAL.MRCH.CD.WT", "unit": "Current USD", "data": imp},
    }


@app.get("/fdi")
async def fdi(limit: int = Query(default=10, ge=1, le=60)):
    """Japan foreign direct investment inflows and outflows"""
    inflows = await fetch_wb("BX.KLT.DINV.CD.WD", limit)
    outflows = await fetch_wb("BM.KLT.DINV.CD.WD", limit)
    return {
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "fdi_inflows": {"series_id": "BX.KLT.DINV.CD.WD", "unit": "Current USD", "data": inflows},
        "fdi_outflows": {"series_id": "BM.KLT.DINV.CD.WD", "unit": "Current USD", "data": outflows},
    }


@app.get("/current-account")
async def current_account(limit: int = Query(default=10, ge=1, le=60)):
    """Japan current account balance (BoP, current USD)"""
    data = await fetch_wb("BN.CAB.XOKA.CD", limit)
    return {
        "indicator": "Current Account Balance",
        "series_id": "BN.CAB.XOKA.CD",
        "unit": "Current USD (Balance of Payments)",
        "frequency": "Annual",
        "country": "Japan",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }
