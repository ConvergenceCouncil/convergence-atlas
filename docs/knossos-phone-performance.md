# Knossos phone performance

Status: viewer tuning implemented; actual device results pending.

The sourced model remains 17.3 MB, 260,678 triangles and a 2048-square texture. Geometry is unchanged. Coarse-pointer/iOS devices use a 30 FPS cap, pixel ratio at most 1, a 900,000-pixel drawing buffer budget and disabled antialiasing. Hidden and idle orbit scenes skip rendering. Walk uses capped rendering and provisional collision raycasts. Texture resources are disposed when replacing a model. Phone file loads above 60 MB are rejected. These limits do not certify any phone.

The collapsed Performance panel reports active render rate, draw calls, triangles and buffer dimensions. It does not measure GPU duration, memory or thermals. Idle rendering pauses; idle samples are not sustained benchmarks.

## iPhone acceptance test — pending
Record phone model, iOS version and connection. Measure cold load and cached reload separately. Continuously orbit for 60 seconds with Performance expanded; record render rate. Walk for two minutes, repeat after ten minutes, and note stutters, heat, blank textures or reloads. Test background/resume, portrait/landscape and model replacement. Target sustained rendering near the 30 FPS cap during continuous movement; this target is not a measured result.

No iPhone, browser visual or UE5 packaged runtime test has been executed in this environment. UE5 device performance requires a separate packaged build after import and collision validation.

Implementation references: https://threejs.org/manual/pages/responsive.html and https://threejs.org/manual/pages/cleanup.html
