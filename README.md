# PestSense

PestSense is an experimental backend system for **pest forecasting and agricultural decision support**, built around **biological state modeling**, **weather-driven risk assessment**, and **modular domain architecture**.

The project explores how climate, crop development, pest biology, and intervention logic can be modeled together to generate **early pest risk signals** and more grounded agricultural recommendations.

## MVP Focus

The current MVP is intentionally narrow:

* **Crop:** Cotton
* **Initial pests:** Whitefly, Pink Bollworm, and related cotton pest pressure
* **Goal:** validate whether a biological + environmental intelligence system can estimate pest risk early enough to support better intervention timing

This is not intended to be a full production platform yet. The current focus is validating the **forecasting model, domain structure, and scientific assumptions** behind the system.

## Core Idea

Pest outbreaks are not random events. They emerge from interacting biological and environmental conditions over time.

PestSense is being designed around that idea by combining:

* **climate conditions**
* **crop development stage**
* **pest lifecycle progression**
* **environmental suitability**
* **intervention timing and outcomes**

At a high level, the system is moving toward:

**Agricultural Risk = f(Environment, Crop, Pest, Time, Intervention)**

## Architecture Direction

PestSense is being developed as a **backend-first Python project** with a modular, domain-driven structure.

### Stack

* Python
* FastAPI
* Pydantic
* SQLAlchemy / Alembic
* PostgreSQL / SQLite
* Pytest

### Design approach

* Domain-Driven Design (DDD)
* Modular monolith architecture
* State-oriented domain modeling
* Profile-driven biological configuration
* Replaceable scientific engines and strategies

A key design goal is to keep **biological knowledge separate from execution logic**, so forecasting models can evolve without constantly rewriting the system.

## Current Scope

The MVP is centered around a small set of domain capabilities:

* pest, crop, region, and treatment profiles
* climate ingestion and normalized environmental state
* crop stage and pest lifecycle modeling
* suitability and risk scoring
* recommendation logic
* validation against observations and outcomes

## Project Structure

* `app/domain/` — domain models, biological engines, and scientific rules
* `app/application/` — workflows and use-case orchestration
* `app/infrastructure/` — persistence, repositories, and external integrations
* `app/api/` — FastAPI routes and contracts
* `tests/` — domain and application tests
* `alembic/` — database migrations

## Why This Project Exists

My background is in **agriculture and entomology**, and PestSense sits at the intersection of that domain knowledge and backend engineering.

The long-term aim is to build software that does more than store agricultural data — software that can reason about biological development, environmental pressure, and intervention timing in a useful way.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notes

This repository is a public engineering snapshot of the project. Internal research notes and planning material are intentionally excluded from the public version.
