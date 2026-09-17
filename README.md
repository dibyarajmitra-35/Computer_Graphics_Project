# 🎮 Computer Graphics Game Collection

A collection of interactive **2D and 3D graphics-based games** developed using **Python, PyOpenGL, GLUT, and OpenGL** as part of the **BRAC University CSE423 Computer Graphics** course.

The repository contains multiple games demonstrating practical applications of computer graphics, animation, keyboard interaction, collision detection, game-state management, object movement, transformations, and interactive gameplay.

---

## 🎮 Games Included

### 🌧️ 1. Stormy Shelter

A weather-based survival game where the player must navigate through a stormy environment while dealing with falling rain and environmental hazards.

**Key Concepts:**

* 🌧️ Animated rain
* 🌩️ Storm/environment effects
* 🏠 Shelter-based gameplay
* 🎮 Keyboard interaction
* 🔄 Real-time animation
* 🖥️ OpenGL rendering

**File:** `Stormy Shelter.py`

---

### 💎 2. Catch the Gem

An interactive collection game where the player attempts to catch falling or moving gems while managing the game environment and score.

**Key Concepts:**

* 💎 Collectible objects
* 🎯 Player-object interaction
* 🕹️ Keyboard controls
* 💥 Collision detection
* 📊 Score/game-state management
* 🔄 Real-time object movement

**File:** `Catch the Gem.py`

---

### 🔫 3. Enemy Hunt

A shooting-based action game where the player must target and eliminate enemies while managing bullets, lives, and gameplay conditions.

**Key Concepts:**

* 🔫 Shooting mechanics
* 👾 Enemy movement
* 🎯 Target detection
* 💥 Collision detection
* ❤️ Life/health system
* 🪙 Score system
* 🔄 Real-time animation
* 🎮 Interactive controls

**File:** `Enemy Hunt.py`

---

### 🎲 4. Gravity Maze: Rolling Cube

A 3D maze-based puzzle game where the player controls a rolling cube through progressively challenging maze levels.

The objective is to navigate through the maze, avoid hazards, collect rewards, activate checkpoints, and reach the goal while managing limited abilities and time.

**Key Features:**

* 🎲 3D rolling cube gameplay
* 🧩 Multiple maze levels
* 🗺️ Dynamic maze structure
* 🏁 Goal and gate system
* ❤️ Checkpoint system
* 🪙 Collectible coins
* ⏱️ Time-based bonuses
* 🕳️ Pit hazards
* ⚠️ Moving and patrolling hazards
* 🔄 Rotating/sliding obstacles
* 💥 Special abilities

  * **G** — Gravity Slam
  * **V** — Vault
  * **L** — Torch
  * **N** — Marker
  * **K** — Magnet
* 📷 Multiple camera modes
* 🔁 Level restart system
* 🎯 Cheat mode
* 🧭 Progressive difficulty

**File:** `Gravity_Maze_Rolling_Cube.py`

---

# ✨ Graphics & Gameplay Concepts

Across the projects, the repository demonstrates several important **Computer Graphics** concepts:

* 🖥️ OpenGL rendering
* 🎨 2D and 3D graphics
* 🔄 Object animation
* 📐 Geometric transformations
* 🎥 Camera systems
* 🕹️ Keyboard interaction
* 💥 Collision detection
* 🎯 Object targeting
* 🌧️ Particle-like effects
* 👾 Enemy movement
* 🧩 Maze generation and navigation
* ❤️ Lives and checkpoints
* 🪙 Collectibles and scoring
* ⏱️ Time-based gameplay
* 🎮 Game-state management
* 🔁 Level progression

---

# 🧠 Algorithms & Game Logic

The projects combine graphics programming with interactive game logic.

### Maze Navigation

**Gravity Maze: Rolling Cube** uses **Breadth-First Search (BFS)** to analyze maze connectivity and determine suitable reachable goal locations.

### Collision Detection

The games use position/proximity-based logic to detect interactions between:

* Player and enemies
* Player and collectibles
* Projectiles and enemies
* Player and obstacles
* Player and hazards
* Player and goal objects

### Animation

Real-time animation is implemented by continuously updating object positions and redrawing the scene.

Examples include:

* Falling rain
* Moving enemies
* Moving collectibles
* Rolling cube
* Rotating obstacles
* Patrolling hazards

---

# 🛠️ Technologies Used

* **Python**
* **PyOpenGL**
* **GLUT**
* **OpenGL**
* **BFS (Breadth-First Search)**
* **2D/3D transformations**
* **Collision detection**
* **Real-time animation**
* **Game-state management**

---

# 🕹️ Project Controls

Controls vary between games depending on their gameplay mechanics.

### Gravity Maze: Rolling Cube

| Key | Action          |
| --- | --------------- |
| W   | Move Forward    |
| A   | Move Left       |
| S   | Move Backward   |
| D   | Move Right      |
| G   | Gravity Slam    |
| V   | Vault           |
| L   | Toggle Torch    |
| N   | Place Marker    |
| K   | Activate Magnet |
| R   | Restart Level   |
| C   | Change Camera   |
| ESC | Exit            |

The controls for the other games may vary depending on their implementation.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/dibyarajmitra-35/Computer_Graphics_Project.git
cd Computer_Graphics_Project
```

## 2. Install Dependencies

Make sure Python is installed, then install the required OpenGL packages:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

## 3. Run a Game

For example:

```bash
python "Stormy Shelter.py"
```

or:

```bash
python "Catch the Gem.py"
```

```bash
python "Enemy Hunt.py"
```

```bash
python "Gravity_Maze_Rolling_Cube.py"
```

---

# 📁 Project Structure

```text
Computer_Graphics_Project/
│
├── Catch the Gem.py
├── Dynamic Dots.py
├── Enemy Hunt.py
├── Gravity_Maze_Rolling_Cube.py
├── Stormy Shelter.py
│
├── Hello_openGL.py
├── Lets_draw_sth.py
│
├── First Program.zip
├── OpenGL.zip
│
├── .gitignore
└── README.md
```

---

# 🎓 Academic Project

These projects were developed as part of the **CSE423 — Computer Graphics** course at **BRAC University**.

The collection demonstrates practical implementation of:

* 2D graphics
* 3D graphics
* OpenGL rendering
* Animation
* Transformations
* Camera systems
* Collision detection
* Interactive controls
* Game-state management
* Algorithmic game logic
* Level design
* Real-time rendering

---

# 👨‍💻 Author

**Dibyaraj Mitra**

Developed as part of the **BRAC University CSE423 Computer Graphics** course.

---

# 📜 License

These projects are intended primarily for **educational and academic purposes**.
