# Product Requirements Document (PRD)

**Project Name:** LABS-Solv-V1
**Team Name:** Team Rocket
**GitHub Repository:** https://github.com/amontejocys/2026-NVIDIA

---

> **Note to Students:** > The questions and examples provided in the specific sections below are **prompts to guide your thinking**, not a rigid checklist. 
> * **Adaptability:** If a specific question doesn't fit your strategy, you may skip or adapt it.
> * **Depth:** You are encouraged to go beyond these examples. If there are other critical technical details relevant to your specific approach, please include them.
> * **Goal:** The objective is to convince the reader that you have a solid plan, not just to fill in boxes.

---

## 1. Team Roles & Responsibilities [You can DM the judges this information instead of including it in the repository]

| Role | Name | GitHub Handle | Discord Handle
| :--- | :--- | :--- | :--- |
| **Project Lead** (Architect) | Krishnam | krishnamiiti29 | krishnam0474 |
| **GPU Acceleration PIC** (Builder) | Ariel Montejo| amontejocys | amontejo |
| **Quality Assurance PIC** (Verifier) | Prem Santh| premliorate| premliorated |
| **Technical Marketing PIC** (Storyteller) | Charis | Charis-E-Shiny | charis0261|

---

## 2. The Architecture
**Owner:** Krishnam Goyal (Project Lead)

### Choice of Quantum Algorithm
* **Algorithm:** QAOA
* **Motivation:** 
    * LABS is a discrete binary problem (each spin is either $+1$ or $-1$). QAOA's "Mixer" and "Cost" layers are mathematically designed to hop between these discrete binary strings more efficiently than a generic VQE circuit.VQE explores the continuous Hilbert space, which is great for finding molecular energies (where electrons can be anywhere). 
    *  QAOA only has two parameters ($\gamma$ and $\beta$) per layer, regardless of how many qubits you have. This makes the classical optimization step much faster—a huge advantage when you have limited time.VQE often requires many more parameters ($\theta_i$) for each gate.
    * To use CD, you have to calculate an "Adiabatic Gauge Potential." For a problem as complex as LABS (which has long-range interactions), this is a mathematical nightmare. If you get the math wrong, your algorithm will perform worse than random guessing.
    *While CD reduces the number of layers ($p$) you need, it often adds a third parameter ($\alpha$) per layer.
   

### Literature Review
* **Reference:** Quantum Approximate Optimization Algorithm (QAOA), Farhi, Goldstone & Gutmann (2014)
* **Relevance:** 
    * Justifies the use of QAOA with low depth circuits


* **Relevance:** [How does this paper support your plan?]
    * * "Evidence of scaling advantage for the quantum approximate optimization algorithm on a classically intractable problem Shaydulin et al  Science Advances 2024
Quantum Optimization Benchmark Library: The Intractable Decathlon (Kipu Quantum, 2025)"


---

## 3. The Acceleration Strategy
Owner: Prem Santh CK (GPU Acceleration Lead)

### Quantum Acceleration (CUDA-Q)Strategy 
* **Strategy:** We aren't just running code; we’re optimizing for the hardware. During our initial phase, we successfully debugged our custom QAOA kernels and passed a rigorous Pi-Rotation Consistency Test to ensure our basis-changes were physically accurate. As we scale to larger $N$, we will utilize FP32 precision to keep our state-vectors lean. If we hit memory limits, we will deploy the nvidia-mgpu backend to distribute the circuit workload across multiple GPUs, ensuring our "Quantum Seeder" stays fast and reliable.

### Classical Acceleration (MTS)
* **Strategy:** We identified that calculating energy for every bit-flip one-by-one was our primary bottleneck. To overcome this, we are overseeing the vectorization of our autocorrelation math using CuPy. Instead of a slow serial approach, we are building a "parallel highway" to evaluate entire batches of sequence neighbors simultaneously on the GPU. This transforms our Memetic Tabu Search from a slow crawl into a high-speed refinement engine that can "polish" quantum seeds in milliseconds.

### Hardware Targets
* **Strategy:** Qbraid (CPU) was used to build our core logic, while the Brev L4 served as our proving ground to ensure our kernels were "hardware-ready" by passing all internal symmetry and rotation validation tests. Production Environment: For the final push to $N=40$ and beyond, we are targeting the Brev A100 (80GB) to leverage its massive memory bandwidth for deep Trotterized QAOA circuits and high-throughput classical refinement.

---

## 4. The Verification Plan
Owner: Prem Santh CK (Quality Assurance Lead)

### Unit Testing Strategy
* **Framework:** pytest and custom validation_kernels
* **AI Hallucination Guardrails:** To ensure our QAOA kernels and classical search logic are correct, Prem Santh has implemented a "Physics-First" property test. Every AI-generated kernel must pass a deterministic energy verification—meaning the output must fall within the theoretical energy bounds of the LABS problem—before it is allowed to be integrated into our main GPU pipeline.

### Core Correctness Checks
* **Check 1 (Symmetry):**  We verify the fundamental property of the LABS problem where a sequence $S$ and its bit-flipped negation $-S$ must produce identical energy values. Our test suite asserts $Energy(S) == Energy(-S)$ to ensure our energy calculation kernel is mathematically sound.
* **Check 2 (Ground Truth):** As a specific quantum check, we verify that our basis-change kernels (rx and rz "sandwiches") correctly flip a qubit from $|0\rangle$ to $|1\rangle$. If the kernel results in a state other than $|1\rangle$, it is flagged as a rotation error.
*  **Check 3 (Ground Truth Benchmarking):** For $N=3$, the known global optimal energy is $1.0$. Our verification suite runs our full hybrid pipeline (QAOA + MTS) for $N=3$ and asserts that the result is exactly $1.0$ before we proceed to larger, unknown sequences.

---

## 5. Execution Strategy & Success Metrics
**Owner:** Technical Marketing PIC

### Agentic Workflow
* **Plan:** [How will you orchestrate your tools?]
    * *Example:* "We are using Cursor as the IDE. We have created a `skills.md` file containing the CUDA-Q documentation so the agent doesn't hallucinate API calls. The QA Lead runs the tests, and if they fail, pastes the error log back into the Agent to refactor."

### Success Metrics
* **Metric 1 (Approximation):** [e.g., Target Ratio > 0.9 for N=30]
* **Metric 2 (Speedup):** [e.g., 10x speedup over the CPU-only Tutorial baseline]
* **Metric 3 (Scale):** [e.g., Successfully run a simulation for N=40]

### Visualization Plan
* **Plot 1:** [e.g., "Time-to-Solution vs. Problem Size (N)" comparing CPU vs. GPU]
* **Plot 2:** [e.g., "Convergence Rate" (Energy vs. Iteration count) for the Quantum Seed vs. Random Seed]

---

## 6. Resource Management Plan
**Owner:** GPU Acceleration PIC 

* **Plan:** [How will you avoid burning all your credits?]
    * *Example:* "We will develop entirely on Qbraid (CPU) until the unit tests pass. We will then spin up a cheap L4 instance on Brev for porting. We will only spin up the expensive A100 instance for the final 2 hours of benchmarking."
    * *Example:* "The GPU Acceleration PIC is responsible for manually shutting down the Brev instance whenever the team takes a meal break."
