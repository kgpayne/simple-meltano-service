# POC Meltano-as-a-Service

Can Meltano be wrapped in a RESTful service? Yes! But it isn't (yet) ideal:

- Using `subprocess` can be problematic. Ideally we'd have access to `meltano` as an importable library. This idea is also not new.
- Running installs "just in time" is slower than prebuilt images, and may result in install failures. This can be mitigated with caching (e.g. using a self-hosted PyPi mirror) or streamlined packaging (pex et. al.) or both!
- Injecting secrets via env vars requires the calling client to understand the Tap/Target settings well enough to correctly set each env var.
- Running multiple EL requests via FastAPI threads will likely overwhelm the host. In production we'd very likely want to use Celery or SQS or some other background worker construct to offload pipeline runs onto a pool of workers. For MVP this can be mitigated using a massive host 😅
- This approach hamstrings some Meltano features, such as scheduling. As pipelines are triggered by an API call, the calling service must keep track of when to call `/run/`. This isn't necessarily a problem if scheduling is handled externally anyway.
