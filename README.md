# GravityMaze-RollingCube-
# 🎮 Gravity Maze: Rolling Cube

A 3D maze-based puzzle game developed using **Python, PyOpenGL, and GLUT**, where the player controls a rolling cube through progressively challenging maze levels.

The objective is to navigate through the maze, avoid hazards, collect rewards, activate checkpoints, and reach the goal while managing limited abilities and time.

## ✨ Features

* 🎲 **3D Rolling Cube Gameplay**
* 🧩 **Multiple Maze Levels**
* 🗺️ **Procedurally Generated / Dynamic Level Structure**
* 🏁 **Goal and Gate System**
* ❤️ **Checkpoint System**
* 🪙 **Collectible Coins**
* ⏱️ **Time-Based Bonuses**
* 🕳️ **Pit Hazards**
* ⚠️ **Moving and Patrolling Hazards**
* 🔄 **Rotating / Sliding Obstacles**
* 💥 **Special Abilities**

  * `G` — Gravity Slam
  * `V` — Vault
  * `L` — Torch
  * `N` — Marker
  * `K` — Magnet
* 📷 **Multiple Camera Modes**
* 🔁 **Level Restart System**
* 🎯 **Cheat Mode**
* 🧭 **Progressive Difficulty**

## 🕹️ Controls

| Key   | Action          |
| ----- | --------------- |
| `W`   | Move forward    |
| `A`   | Move left       |
| `S`   | Move backward   |
| `D`   | Move right      |
| `G`   | Gravity Slam    |
| `V`   | Vault           |
| `L`   | Toggle Torch    |
| `N`   | Place Marker    |
| `K`   | Activate Magnet |
| `R`   | Restart Level   |
| `C`   | Change Camera   |
| `ESC` | Exit            |

> Controls may vary depending on the final implementation.

## 🧱 Levels

The game contains multiple maze sizes with increasing complexity:

* **6 × 6**
* **8 × 8**
* **10 × 10**

The goal location is selected based on maze traversal, with the game incorporating paths, gates, checkpoints, hazards, and collectibles to make each level more challenging.

## 🛠️ Technologies Used

* **Python**
* **PyOpenGL**
* **GLUT**
* **OpenGL**
* **BFS (Breadth-First Search)**
* 3D transformations and camera systems
* Collision and proximity detection
* Game-state management

## 🧠 Algorithms & Game Logic

The project combines computer graphics concepts with algorithmic game logic.

### BFS-Based Maze Navigation

**Breadth-First Search (BFS)** is used to analyze the maze and determine reachable cells and suitable goal locations.

### Dynamic Gameplay Systems

The game tracks:

* Player position
* Goal and gate locations
* Hazard occupancy
* Checkpoints
* Coins
* Time bonuses
* Ability charges
* Level progression

## 🎨 Graphics

The game uses OpenGL to render a 3D environment containing:

* Maze walls
* Rolling cube
* Ground and obstacles
* Collectibles
* Hazards
* Goal and gate
* Lighting effects
* Camera perspectives

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/GravityMaze-RollingCube.git
cd GravityMaze-RollingCube
```

### 2. Install dependencies

Make sure Python is installed, then install the required OpenGL packages:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

### 3. Run the game

```bash
python main.py
```

> Replace `main.py` with the actual entry-point filename if your project uses a different file.

## 📁 Project Structure

```text
GravityMaze-RollingCube/
│
├── main.py
├── assets/
├── src/
├── README.md
└── requirements.txt
```

The exact structure may vary depending on the final project organization.

## 🎓 Academic Project

This project was developed as part of a **Computer Graphics / OpenGL course project**.

The project demonstrates practical implementation of:

* 3D graphics
* OpenGL rendering
* Camera transformations
* Lighting
* Collision detection
* BFS-based game logic
* Interactive controls
* Game-state management
* Level design and progression

## 👨‍💻 Authors

**Dibyaraj Mitra**

Developed as a group project for **BRAC University — CSE423 Computer Graphics**.

## 📜 License

This project is intended primarily for **educational and academic purposes**.
