# AI Evacuation System 🧭🔥

The **AI Evacuation System** is a tool designed to optimize and simulate evacuation routes in large buildings during emergencies such as fires. It leverages grid-based maps, interactive editors, and image processing to create and analyze escape paths using AI-based pathfinding algorithms.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Modules](#modules)
  - [Module 1: Pathfinding Visualization](#module-1-pathfinding-visualization)
  - [Module 2: Map Editor with Pygame](#module-2-map-editor-with-pygame)
  - [Module 3: Map Editor with PyQt6 and OpenCV](#module-3-map-editor-with-pyqt6-and-opencv)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [How to Contribute](#how-to-contribute)

---

## Overview

The **AI Evacuation System** allows users to:

1. **Design and Edit Maps** interactively for buildings.
2. **Simulate Evacuation Routes** using grid-based visualization.
3. **Generate Maps** from images using thresholding techniques.
4. **Save Maps** as JSON files for pathfinding analysis.

This project can be extended with AI algorithms like **A***, **Dijkstra**, or other pathfinding methods to optimize evacuation.

---

## Features

- **Grid-based Map Editing**: Interactive tools for creating building layouts with obstacles and open spaces.
- **Image to Grid Conversion**: Automatically convert floor plan images into grid maps using thresholding.
- **Export Maps**: Save building layouts in JSON format for use in AI-based simulations.
- **Path Visualization**: Simulate how evacuees move through a building using generated routes.

---

## Modules

### Module 1: Pathfinding Visualization

- **Purpose**: Visualize grid-based maps and simulate movement paths for evacuation.
- **Technologies**: Pygame
- **Features**:
  - Display grids on-screen.
  - Mark walls/obstacles interactively to simulate building layouts.

---

### Module 2: Map Editor with Pygame

- **Purpose**: Design and edit grid-based maps for building evacuation.
- **Technologies**: Pygame, JSON
- **Features**:
  - **Left-click**: Remove walls or obstacles.
  - **Right-click**: Add walls or obstacles.
  - Save the building layout using the `S` key as a JSON file.

---

### Module 3: Map Editor with PyQt6 and OpenCV

- **Purpose**: Convert floor plan images into grid-based evacuation maps.
- **Technologies**: PyQt6, OpenCV, JSON
- **Features**:
  - Load building floor plan images.
  - Adjust threshold sliders to detect walls and open paths.
  - Generate a grid map and save it as a JSON file.

---

## Dependencies

Install the required libraries:

```bash
pip install pygame pyqt6 opencv-python-headless numpy
```

---

## Usage

1. **Module 1: Pathfinding Visualization**

   ```bash
   python main.py
   ```

   - Visualize and test grid-based building layouts.

2. **Module 2: Map Editor with Pygame**

   ```bash
   python map-maker.py
   ```

   - Design the building layout interactively.
   - Use **Right-click** to add walls and **Left-click** to remove them.
   - Press **S** to save the layout as `map.json`.

3. **Module 3: Map Editor with PyQt6 and OpenCV**

   ```bash
   python image-to-map.py
   ```

   - Load a building floor plan image.
   - Adjust the threshold slider to detect walls.
   - Save the map as `map.json`.

---

## How It Works

1. **Map Design**:
   - Users can create building layouts manually or generate them from floor plan images.
   - The system stores the maps in a JSON format, marking grid coordinates for walls and open paths.

2. **AI Pathfinding**:
   - Use algorithms like **A*** or **Dijkstra** to calculate optimal escape routes.
   - The system simulates evacuee movement across the grid, avoiding walls and obstacles.

3. **Simulation**:
   - Visualize evacuation paths and optimize escape strategies in real time.

---

## How to Contribute

1. Fork the repository.
2. Add new features or optimize pathfinding algorithms.
3. Submit a pull request.

---
