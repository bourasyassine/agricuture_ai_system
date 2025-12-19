# AI-Enhanced Crop Monitoring System

## How to run locally with Docker
1. From the project root, build and start services:
   - `docker-compose up --build`
2. Open the frontend at `http://localhost:5173`.
3. The backend API is available at `http://localhost:8000/api`.
4. Optional: create a Django user for the simulator if needed:
   - `docker-compose exec backend python manage.py createsuperuser`

## Testing & Evaluation Summary
End-to-end testing plan and data flow:
- Sensor simulator sends readings to `POST /api/sensor-readings/` with JWT auth.
- Backend persists readings, runs anomaly detection, and triggers the rule-based agent.
- Agent outputs alerts/recommendations that are exposed via API endpoints.
- Frontend polls the API and displays alerts and anomaly status.

Basic evaluation metrics to track during a run:
- Number of sensor readings processed (per plot, per minute/hour).
- Number of anomalies detected (total and by plot).
- Severity distribution: low / medium / high counts.
- Example false positives: transient temperature spikes or short humidity noise causing alerts.

Known limitations:
- Rule-based agent relies on static thresholds and cannot adapt to new patterns.
- Simulated data may not reflect real sensor noise or seasonal variability.
- Single-plot testing does not capture multi-field interactions.
- No real-time streaming; batch-like HTTP posts only.
- Simple threshold-based ML logic limits detection of subtle anomalies.
