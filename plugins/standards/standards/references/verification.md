# Verification

- Define the observable contract before choosing the test surface.
- Run the narrowest relevant test first, then broaden in proportion to blast radius.
- Exercise absence, boundaries, failures, concurrency, and external effects when relevant.
- Treat fresh command output as evidence; do not infer a check passed because a related step was green.
- Report unverified surfaces and accepted races explicitly.
