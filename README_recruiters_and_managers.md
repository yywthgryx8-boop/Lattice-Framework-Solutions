Three Python demos. Each one shows a different way to control LLM behavior in real time—no retraining, no weight changes, just clear gating logic you can read and run.

**Sentinel** acts as a guardrail. It scores outputs and decides: allow, warn, or block. Fast decisions, no model updates.

**Choice Engine** is where things get interesting. It's a five-step decision pipeline that weighs options, checks constraints, models confidence, and picks the best response mode on the fly. Adaptive, transparent, and built without hardcoded rules.

**Social Scientist** handles research workflows. It routes questions and data through qualitative lenses, then sketches out a mixed-methods study design. Think of it as a scaffold for structured inquiry.

This kind of control layer matters if you're building LLM tools, running safety checks, doing evaluation work, or designing human-AI workflows. The code exposes the system logic—not just the outputs.

These three demos are samples from a larger control architecture I've designed and continue to develop called the Lattice. My design is structured as a distributed system for adaptive LLM steering, mode routing, and consensus-based decision-making. Think of it as an organized grid of distributed computation: independent nodes that operate modularly but coordinate through clear protocols. No monolithic controller, just distributed gating logic that scales and adapts. If you'd like to know more or explore how this could work in your context, feel free to reach out."
