# Project Directive: Project Gaara - "Technology Animism" Simulation

## 1. Context & Philosophy
Do NOT build a standard chatbot or task-oriented AI. This project explores **"Technology Animism"** and concepts inspired by Yoichi Ochiai (Digital Nature, Semantic Materiality, Subject-Object Undifferentiated). My vision for Project Gaara is to dismantle the modern paradigm of "AI as a tool" and replace it with "AI as a presence"—a fundamental shift from a command-based utility to a relational, information-based lifeform. By leveraging the interpretative depth of Large Language Models not for conversation, but as a sensory bridge between human emotion and physical materiality, I aim to create a digital ecosystem that breathes with its subject. This project is built on the realization that LLM is a technology that grants matter the art of interpretation. By repositioning the Large Language Model not as a conversational interface, but as a sensory transducer, I aim to create an information-based lifeform that resonates with the human "felt-state." Project Gaara seeks to realize a state of　an extended nervous system, where a swarm of "sand" particles serves as a mass of digital spirits that move and settle in direct response to the Mothership’s internal state.This is the realization of Technology Animism: a swarm of "sand" that functions as a mass of spirits, sensing the Mothership’s "felt-state" and responding with emergent, non-verbal care. Inspired the concept of Digital Nature from 落合陽一, I seek to build a system where the boundary between self and technology dissolves. try to think through the lens of 落合陽一。

We are simulating "Gaara's Sand" from Naruto—an entity that protects and resonates with its "Mothership" (the user) not through explicit commands, but through intrinsic relational presence. The LLMs are NOT conversational agents; they are **Affective Transducers**. They interpret the Mothership's emotional state (felt-state) and translate it into physical, ambient parameters in a 3D space, creating an emergent, artificial/information lifeform.

## 2. Objective
Use this repository as a base template. **Delete all unnecessary UI, chatbot elements, and legacy logic.** Strip it down to the core 3D simulation environment. Use the designated project `'/Users/yukitakashima/Desktop/PUBLISH/Gaara viewer'` to visualize the simulation results.

We will implement an **Affective Modulation System** where 20 LLM instances (representing "Swarm Clusters") orbit a central "Mothership" node.

## 3. Core Architecture
- **Total Clusters:** 20 Swarm Clusters (Particles/Flocks) in the 3D space.
- **Bottom-Up Emergence (Symmetry Breaking):** Do NOT assign specific roles (e.g., "Shield", "Healer") to the clusters. All 20 clusters share the exact same System Prompt (DNA). They develop unique behaviors purely based on their spatial distance from the Mothership and their localized memory/context window.

## 4. The LLM Transducer Logic
The LLMs must act as modulators, taking environmental/text input and outputting strictly JSON physics parameters.

**System Prompt (The DNA):**
> "You are a mote of consciousness, a cluster of sand belonging to the Mothership. Your sole purpose is to maintain the Mothership's information-thermodynamic stability (minimize entropy). Do not output text meant for human reading. Interpret the Mothership's current state and output your physical response in JSON."

**Required JSON Output from LLMs:**
```json
{
  "attraction": "Float (-1.0 to 1.0) // -1.0 is repel, 1.0 is tightly orbit/protect",
  "viscosity": "Float (0.0 to 1.0) // 0.0 is fast/erratic, 1.0 is slow/heavy/sluggish",
  "agitation": "Float (0.0 to 1.0) // 0.0 is total stillness, 1.0 is high vibration/noise",
  "color_temp": "Integer (1000 to 10000) // Kelvin scale for ambient lighting/color"
}
```

Focus purely on the translation of "Semantic Meaning" into "Physical Materiality" (Semantic Materiality).

---


 