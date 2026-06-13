# Resiliency Extension — Mandatory Clarifying Questions

You enabled the Resiliency Baseline extension. Two mandatory questions must be
answered before requirements can be finalized (RESILIENCY-02 and RESILIENCY-03).

**Context**: InsightForge is a local Streamlit application. Most cloud infrastructure
resiliency rules will be marked N/A for a local setup — these questions help capture
your intent and document appropriate exceptions.

---

## Question: RTO/RPO Goals and Disaster Recovery Strategy (RESILIENCY-02)
What are your Recovery Time Objective (RTO) and Recovery Point Objective (RPO) goals?

A) RPO/RTO: Hours — Backup & Restore strategy. Lowest cost. Suitable for non-critical workloads.

B) RPO/RTO: 10s of minutes — Pilot Light strategy. Suitable for important workloads.

C) RPO/RTO: Minutes — Warm Standby strategy. Suitable for business-critical applications.

D) RPO/RTO: Near real-time — Multi-site Active/Active. Highest cost, mission-critical.

E) N/A — This is a local development / educational application. No cross-region DR needed. Single-machine deployment is acceptable.

X) Other (please describe after [Answer]: tag below)

[Answer]: E

---

## Question: Change Management Process (RESILIENCY-03)
How should production changes for this workload be governed?

A) Use our existing organizational change management process (provide name/tool in notes).

B) No formal process exists — propose a lightweight change management approach.

C) N/A — This workload is exempt from formal change management (local educational project, no production deployment).

X) Other (please describe after [Answer]: tag below)

[Answer]: C
