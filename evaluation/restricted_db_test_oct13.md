# Restricted enrollment database test evidence (2026-10-13)

Environment: isolated Supabase test project drzaxpofuhqchmpkwhpy. Production was not accessed.

Tested in a rolled-back SQL transaction using the existing private test enrollment function. A temporarily granted role-setting permission allowed the SQL administration connection to run the function as robo_test_enrollment_executor.

Checks performed:
- Synthetic Learner B could not consume Learner A's challenge.
- Synthetic Learner A could consume the valid challenge and receive a new cloud identity.
- A second attempt to consume the same challenge returned no enrollment.
- The transaction was rolled back.

Post-test verification: zero rows in enrollment_challenges and cloud_enrollments. The original postgres-to-executor role SET option remained false.

Scope limitation: Database-side SQL only. No Render-to-Supabase connection, custom staging-login authentication, or real authenticated HTTP enrollment was exercised. No database passwords or real learner information were involved.
