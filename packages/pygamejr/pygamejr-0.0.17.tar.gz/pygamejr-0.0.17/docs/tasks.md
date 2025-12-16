# pygamejr Improvement Tasks Checklist

Note: Each task is actionable and ordered from foundational architecture decisions to code-level quality, developer experience, and examples. Check off tasks as they are completed.

1. [ ] Define project scope and public API surface
   - [ ] Document core goals (educational library vs. mini-engine) and non-goals in README
   - [ ] Enumerate supported modules to be considered public (pygamejr.__init__.__all__) and commit to semver for them
2. [ ] Create high-level architecture document
   - [ ] Describe modules (base, sprite, resources, quest, utils) and their responsibilities
   - [ ] Diagram data flow for display/screen, game loop, resources, and quest/map loading
3. [ ] Decouple display initialization from module import side effects
   - [ ] Remove implicit display init in quest.py (pygamejr.get_screen() at import time)
   - [ ] Provide explicit initialization API (e.g., pygamejr.init_display(size=(w,h), flags=...))
   - [ ] Guard any image loading that requires display with lazy loaders or headless paths
4. [ ] Eliminate global mutable state patterns where possible
   - [ ] Replace global screen and clock usage with injectable context (pass screen/clock or a GameContext)
   - [ ] Wrap tmxdata (global in quest.py) into a Quest/Map object instance
5. [ ] Introduce configuration management
   - [ ] Centralize constants (e.g., TILE_SIZE, window position) into a config module/dataclass
   - [ ] Provide environment variable overrides and sane defaults
6. [ ] Improve resource loading abstraction
   - [ ] Validate existence and readability of resource paths; raise clear errors
   - [ ] Cache loaded assets (images, maps) with weakref or LRU to avoid redundant IO
   - [ ] Ensure packaging includes all resource files (pyproject.toml include settings)
7. [ ] Make window positioning and screen-size logic cross-platform and optional
   - [ ] Replace hard-coded SDL_VIDEO_WINDOW_POS side effect with an opt-in function
   - [ ] Rework tkinter-based get_curr_screen_geometry to be optional and safe in headless environments
8. [ ] Add logging instead of print/side effects
   - [ ] Configure a library logger (pygamejr.logger) with no handlers by default
   - [ ] Add debug logs around init, resource loading, map parsing, and animations
9. [ ] Strengthen error handling with clear exceptions
   - [ ] Wrap pytmx loading with try/except and custom exceptions (e.g., MapLoadError)
   - [ ] Validate tile indices before access; handle out-of-bounds gracefully
10. [ ] Add static typing and type checking
    - [ ] Add type hints across public API and key internals (base.py, quest.py, sprite/*, utils/*)
    - [ ] Enable mypy with a minimal configuration; fix revealed issues
11. [ ] Establish code style and linters
    - [ ] Add black, isort, and flake8/ruff configuration
    - [ ] Add pre-commit hooks for formatting and linting
12. [ ] Testing infrastructure
    - [ ] Set up pytest with basic unit tests (utils, resolve_path, resources)
    - [ ] Add integration tests for map loading using a headless video driver (SDL_VIDEODRIVER=dummy)
    - [ ] Add tests for movement logic (Player.move_forward, collisions, win detection)
13. [ ] Refactor quest/Player responsibilities
    - [ ] Separate map rendering from player logic (Renderer vs. Actor)
    - [ ] Expose movement commands via methods that do not mutate global state
    - [ ] Replace frame-based animation loop coupling with time-based interpolation decoupled from global clock
14. [ ] Sprite system improvements
    - [ ] Use pygame.sprite.Group for batch drawing where appropriate
    - [ ] Add a base update(dt) method contract across sprites
15. [ ] Performance improvements
    - [ ] Pre-render static tile layers to a surface for faster blitting each frame
    - [ ] Avoid per-frame image reloads; ensure images are preloaded and reused
    - [ ] Profile with pygame.time.Clock.get_fps and cProfile on demo scenes
16. [ ] Improve map and tile handling
    - [ ] Fix reliance on pytmx internals (layernames indexing and tile_properties access); use stable APIs
    - [ ] Validate presence of expected layers ("objects", "walls") and fail fast with explanation
    - [ ] Replace load_image workaround with a robust helper that copes with tileset sources and color keys
17. [ ] API consistency and naming
    - [ ] Normalize method/variable names to English consistently (docstrings can remain bilingual if desired)
    - [ ] Provide docstrings for public functions/classes (every_frame, wait_quit, BaseSprite, ImageSprite, Player)
18. [ ] Event and input handling
    - [ ] Extend is_quit to support ESC and window close consistently
    - [ ] Provide an input module abstraction that can be used in examples/demos
19. [ ] Deterministic timing utilities
    - [ ] Revisit every_frame to support fixed time steps and frame limits separate from drawing
    - [ ] Provide a simple game loop helper that supports update(dt)/render separation
20. [ ] Documentation overhaul
    - [ ] Expand README with quickstart, examples, and API sections
    - [ ] Create docs site structure (e.g., MkDocs or Sphinx) with tutorial: building a quest
    - [ ] Document resource management and how to add new maps/assets
21. [ ] Demos and examples
    - [ ] Ensure demo scripts (demo/*.py) use the public API without internal imports
    - [ ] Add a minimal demo for sprites, and another for quests with win/lose states
    - [ ] Add instructions to run demos in headless mode for CI
22. [ ] Continuous Integration
    - [ ] Add GitHub Actions workflow for lint, type-check, and tests on Windows, macOS, Linux
    - [ ] Cache dependencies and ensure SDL dummy video driver for tests
23. [ ] Packaging and distribution
    - [ ] Verify pyproject.toml includes package data (images, quests, tiles) and MANIFEST if needed
    - [ ] Add classifiers, project urls, and minimum Python version
    - [ ] Add a versioning strategy and CHANGELOG.md with Keep a Changelog format
24. [ ] Backward compatibility and deprecations
    - [ ] Mark any breaking API changes; provide deprecation warnings when feasible
    - [ ] Add tests to ensure deprecated paths still function until removal
25. [ ] Resource path safety and portability
    - [ ] Ensure resolve_path works when installed as a package and when running from source
    - [ ] Replace stringly-typed map references with functions or enums (e.g., resources.quest.map("map1"))
26. [ ] Animation system improvements
    - [ ] Replace hard-coded image_index cycling with a generic Animator component (frame durations, loops)
    - [ ] Support per-direction animations uniformly
27. [ ] Robust collision and tile queries
    - [ ] Abstract _is_wall and _is_win into a map query interface with bounds checking
    - [ ] Provide helpers to query objects by type, properties, and coordinates
28. [ ] Localization readiness
    - [ ] Externalize user-facing strings; set up a simple i18n pattern where applicable
29. [ ] Logging and diagnostics tools for users
    - [ ] Add a debug overlay option (fps, tile coords, player state) toggleable via key
30. [ ] Contributor experience
    - [ ] Add CONTRIBUTING.md with development setup, tooling, and coding standards
    - [ ] Add CODE_OF_CONDUCT.md
31. [ ] Security and safety considerations
    - [ ] Sanitize/validate any external map data inputs (avoid arbitrary code in properties)
    - [ ] Avoid importing attacker-controlled modules from map metadata
32. [ ] Optional CLI utilities
    - [ ] Provide a small CLI (pygamejr-demo run quest) to launch included demos
33. [ ] Cross-platform testing and compatibility
    - [ ] Verify behavior on Windows (current), macOS, and Linux; handle differences in paths and SDL
34. [ ] Cleanup unused/commented code
    - [ ] Remove or migrate large commented blocks in sprite/base.py, streamline examples
35. [ ] Maintainability tasks
    - [ ] Add module-level __all__ where appropriate
    - [ ] Split large modules if they grow (quest into map, renderer, actor files)
