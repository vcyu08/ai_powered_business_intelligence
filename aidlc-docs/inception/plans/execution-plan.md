# Execution Plan — InsightForge

## Detailed Analysis Summary

### Change Impact Assessment
- **User-facing changes**: Yes — new Streamlit web application with chat UI and visualizations
- **Structural changes**: Yes — new multi-component Python application (6 source files + tests)
- **Data model changes**: Yes — new LangChain Document-based knowledge base from sales_data.csv
- **API changes**: No — no existing API being modified
- **NFR impact**: Yes — security (API key handling, input validation), PBT (Hypothesis tests), exception handling

### Risk Assessment
- **Risk Level**: Low — greenfield project, no migration or breaking changes
- **Rollback Complexity**: Easy — no existing system to break
- **Testing Complexity**: Moderate — LLM calls require mocking or API key in test environment

---

## Workflow Visualization

```mermaid
flowchart TD
    Start(["User Request"])

    subgraph INCEPTION["🔵 INCEPTION PHASE"]
        WD["Workspace Detection\n✅ COMPLETED"]
        RE["Reverse Engineering\n⬜ SKIPPED"]
        RA["Requirements Analysis\n✅ COMPLETED"]
        US["User Stories\n⬜ SKIPPED"]
        WP["Workflow Planning\n🔄 IN PROGRESS"]
        AD["Application Design\n🟠 EXECUTE"]
        UG["Units Generation\n⬜ SKIPPED"]
    end

    subgraph CONSTRUCTION["🟢 CONSTRUCTION PHASE"]
        FD["Functional Design\n🟠 EXECUTE"]
        NFRA["NFR Requirements\n🟠 EXECUTE"]
        NFRD["NFR Design\n🟠 EXECUTE"]
        ID["Infrastructure Design\n⬜ SKIPPED"]
        CG["Code Generation\n🟢 EXECUTE"]
        BT["Build and Test\n🟢 EXECUTE"]
    end

    subgraph OPERATIONS["🟡 OPERATIONS PHASE"]
        OPS["Operations\nPLACEHOLDER"]
    end

    Start --> WD
    WD --> RA
    RA --> WP
    WP --> AD
    AD --> FD
    FD --> NFRA
    NFRA --> NFRD
    NFRD --> CG
    CG --> BT
    BT -.-> OPS
    BT --> End(["Complete"])

    style WD fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RA fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style WP fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style CG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style BT fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style FD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray:5 5,color:#000
    style NFRA fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray:5 5,color:#000
    style NFRD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray:5 5,color:#000
    style AD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray:5 5,color:#000
    style RE fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray:5 5,color:#000
    style US fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray:5 5,color:#000
    style UG fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray:5 5,color:#000
    style ID fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray:5 5,color:#000
    style OPS fill:#FFF59D,stroke:#F57F17,stroke-width:2px,stroke-dasharray:5 5,color:#000
    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style INCEPTION fill:#BBDEFB,stroke:#1565C0,stroke-width:3px,color:#000
    style CONSTRUCTION fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px,color:#000
    style OPERATIONS fill:#FFF59D,stroke:#F57F17,stroke-width:3px,color:#000
    linkStyle default stroke:#333,stroke-width:2px
```

### Text Alternative
```
INCEPTION PHASE:
  ✅ Workspace Detection    — COMPLETED
  ⬜ Reverse Engineering    — SKIPPED (Greenfield)
  ✅ Requirements Analysis  — COMPLETED
  ⬜ User Stories           — SKIPPED (single-developer capstone)
  🔄 Workflow Planning      — IN PROGRESS
  🟠 Application Design     — EXECUTE
  ⬜ Units Generation       — SKIPPED (single unit, no decomposition needed)

CONSTRUCTION PHASE (single unit — InsightForge):
  🟠 Functional Design      — EXECUTE
  🟠 NFR Requirements       — EXECUTE
  🟠 NFR Design             — EXECUTE
  ⬜ Infrastructure Design  — SKIPPED (local app, no cloud infra)
  🟢 Code Generation        — EXECUTE (ALWAYS)
  🟢 Build and Test         — EXECUTE (ALWAYS)

OPERATIONS PHASE:
  ⬜ Operations             — PLACEHOLDER
```

---

## Phases to Execute

### 🔵 INCEPTION PHASE
- [x] Workspace Detection — COMPLETED
- [x] Reverse Engineering — SKIPPED (Greenfield project)
- [x] Requirements Analysis — COMPLETED
- [x] User Stories — SKIPPED
  - **Rationale**: Single developer capstone, clear requirements from PDF, no multi-persona acceptance criteria needed
- [x] Workflow Planning — IN PROGRESS
- [ ] Application Design — EXECUTE
  - **Rationale**: New multi-component application; component boundaries, methods, and service layer need definition before code generation
- [ ] Units Generation — SKIPPED
  - **Rationale**: Single cohesive application unit; all components are tightly coupled and developed together

### 🟢 CONSTRUCTION PHASE (single unit: InsightForge)
- [ ] Functional Design — EXECUTE
  - **Rationale**: New data models (Document structure, knowledge base schema), business logic (retrieval keyword mapping, statistics computation), PBT-01 property identification required
- [ ] NFR Requirements — EXECUTE
  - **Rationale**: Tech stack decisions needed (LangChain version, Hypothesis framework, Plotly, logging config); security and PBT extension rules require NFR documentation
- [ ] NFR Design — EXECUTE
  - **Rationale**: Security patterns (input validation, error handling, logging), PBT test strategy, and timeout/resiliency design need to be incorporated before code generation
- [ ] Infrastructure Design — SKIPPED
  - **Rationale**: Local Streamlit application; no cloud infrastructure, no IaC, no deployment resources
- [ ] Code Generation — EXECUTE (ALWAYS)
  - **Rationale**: 6 source files + test suite + configuration files to generate
- [ ] Build and Test — EXECUTE (ALWAYS)
  - **Rationale**: Build setup, unit tests, integration test instructions needed

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER
  - **Rationale**: Future deployment workflows; out of scope for this capstone

---

## Estimated Timeline
- **Total Stages to Execute**: 7 (Application Design, Functional Design, NFR Requirements, NFR Design, Code Generation ×2, Build and Test)
- **Single Unit**: InsightForge (all components in one code generation pass)

## Success Criteria
- **Primary Goal**: Working InsightForge Streamlit app that answers business data questions via RAG
- **Key Deliverables**: 6 Python source files, requirements.txt, .env.example, pytest + Hypothesis test suite
- **Quality Gates**: Security rules SECURITY-03/05/09/10/12/15 compliant; PBT tests via Hypothesis; no hardcoded secrets
