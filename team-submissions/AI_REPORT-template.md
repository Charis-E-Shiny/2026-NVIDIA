## Milestone 4: AI Post-Mortem Report

**Our team treated AI as a "Co-Developer" and technical consultant rather than a simple code generator. We maintained a strict boundary: the AI proposed architectures and mathematical translations, while the humans handled integration and physical validation.**


**Architecture & Design:** We used AI to bridge the gap between abstract physics papers and executable CUDA-Q kernels. It helped us design a hybrid solver that uses QAOA to "seed" the search space and a Memetic Tabu Search (MTS) to polish the results.

**Performance Engineering:** AI was instrumental in drafting our CuPy integration. By moving from serial Python loops to vectorized GPU arrays, we transformed our bottleneck into a parallel execution engine.

**Human-in-the-Loop:** Every AI suggestion was treated as a draft. We manually reviewed all gate signs and parameter schedules to ensure they didn't violate the fundamental constraints of the LABS problem.

## 2. Verification Strategy
Because quantum code is prone to subtle logic errors and "hallucinations" regarding hardware capabilities, we built an automated safety net from the start.

### Unit Tests & Hallucination Guardrails

**The Pi-Rotation Test:** AI frequently struggled with the sign conventions of basis-change "sandwiches." We implemented a specific test that performs a $\pi$ rotation on the Y-axis; if the qubit didn't flip deterministically to $|1\rangle$, the code was rejected.

**Energy Symmetry Validation:** Since LABS energy must be identical for a sequence and its reverse, we implemented test_reverse_symmetry_post_qaoa. This caught early AI errors where indexing logic subtly broke the symmetry.

**Ground Truth Checks:** We verified our GPU kernels against known optimal energies for small N values (N=3,6). This ensured our "Physics math" was 100% accurate before we scaled to N=30+.

## 3. The "Vibe" Log
### Win: AI Saved Days on Vectorization
Moving the autocorrelation math from a nested loop to CuPy would have taken us hours of manual indexing math. The AI provided a blueprint for energy_batch_cupy that allowed us to evaluate over 1,000 sequences simultaneously on the GPU.

### Learn: Precision Prompting

Early on, we asked the AI for generic CUDA code, which was useless for CUDA-Q. We learned to "seed" our prompts with actual documentation and existing code snippets. By asking for "minimal-change patches" instead of full rewrites, we received much more stable, production-ready code.

### Fail: Hallucinated Syntax

The AI repeatedly suggested using standard Python prefixes like cudaq.rx() inside the quantum kernels. This is a compiler violation in the MLIR environment. We had to manually strip these prefixes to the shorthand rx() and rz(), reinforcing the need for human oversight of platform-specific DSLs.

## 4. Context Dump
Examples of prompts that drove our development:

"Translate this correlation equation into a vectorized CuPy function for a 2D batch of bitstrings."

"Create a verification kernel in CUDA-Q to test if my Rx/Rz basis-change logic correctly flips a qubit state."

"Design a benchmarking plan that scales N and GPU architectures without altering the core solver logic."
## 5. Final Reflection
Our objective was to use AI thoughtfully. It served as a high-speed engine for iteration and boilerplate reduction, while we maintained control over the "Physics" and the "Validation." The result is a verified, hardware-portable QAOA-only solver that is ready for the most complex LABS benchmarks.
