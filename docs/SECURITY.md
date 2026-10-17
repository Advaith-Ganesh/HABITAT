# Sandbox boundary

Bind to 127.0.0.1 only. No authentication or authorisation is implemented. Anyone with local access can create fictional cases or record a review. CORS permits only the local Vite frontend origins; it is not authentication. Do not publish this service or submit real applicant information.

Only typed Pydantic fields are accepted; no names/addresses/arbitrary JSON fields, scripts or uploads. CSV download path is fixed. joblib artifacts must be trusted: never replace the provided file with an untrusted pickle/joblib. The application never executes arbitrary supplied files or sends data to government systems. Policy loading uses an explicit allowlist. Free-text review reasons may still contain sensitive material if a user ignores the fictional-only restriction.

SQLAlchemy binds queries and SQLite event triggers block ordinary UPDATE/DELETE on events. The process/database administrator can remove these controls; no cryptographic audit assurance. The database is ignored by Git and excluded from the source archive. Production requires identity/access controls, tenant isolation, security review, encryption/retention/backup policy, incident handling and human governance.
