/**
 * Dungeon Map Renderer - 2D Canvas-based Map Display
 *
 * Renders explored and known dungeon rooms in a 2D grid layout
 */

class DungeonMapRenderer {
    constructor(canvasId, dungeonData) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.dungeon = dungeonData;

        // Room layout (calculated from room connections)
        this.roomPositions = {};
        this.exploredRooms = new Set();
        this.knownRooms = new Set();

        // Visual settings
        this.roomSize = 60;
        this.roomPadding = 20;
        this.offsetX = 50;
        this.offsetY = 50;

        // Colors (from CSS variables)
        this.colors = {
            explored: '#4a4a3a',
            known: '#333329',
            current: '#d4af37',
            exit: '#8b7355',
            wall: '#2c2416',
            text: '#f4e4c1'
        };

        this.calculateRoomLayout();
    }

    calculateRoomLayout() {
        /**
         * Calculate 2D positions for all rooms based on their connections
         * Uses a simple graph layout algorithm
         */
        const rooms = this.dungeon.rooms;
        const positions = {};

        // Start room at origin
        const startRoom = this.dungeon.start_room || 'room_001';
        positions[startRoom] = { x: 0, y: 0 };

        // Direction vectors
        const directions = {
            'north': { x: 0, y: -1 },
            'south': { x: 0, y: 1 },
            'east': { x: 1, y: 0 },
            'west': { x: -1, y: 0 }
        };

        // BFS to layout connected rooms
        const queue = [startRoom];
        const visited = new Set([startRoom]);

        while (queue.length > 0) {
            const currentRoomId = queue.shift();
            const currentPos = positions[currentRoomId];
            const room = rooms[currentRoomId];

            if (!room || !room.exits) continue;

            // Place connected rooms
            for (const [direction, targetRoomId] of Object.entries(room.exits)) {
                if (visited.has(targetRoomId)) continue;

                const dir = directions[direction];
                if (!dir) continue;

                positions[targetRoomId] = {
                    x: currentPos.x + dir.x,
                    y: currentPos.y + dir.y
                };

                visited.add(targetRoomId);
                queue.push(targetRoomId);
            }
        }

        this.roomPositions = positions;
        this.markStartingRoomsAsKnown(startRoom);
    }

    markStartingRoomsAsKnown(startRoom) {
        /**
         * Mark starting room and adjacent rooms as "known"
         */
        this.knownRooms.add(startRoom);

        const room = this.dungeon.rooms[startRoom];
        if (room && room.exits) {
            for (const targetRoomId of Object.values(room.exits)) {
                this.knownRooms.add(targetRoomId);
            }
        }
    }

    render(currentRoomId) {
        /**
         * Render the dungeon map
         */
        // Clear canvas
        this.ctx.fillStyle = this.colors.wall;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Mark current room as explored
        this.exploredRooms.add(currentRoomId);

        // Mark adjacent rooms as known
        const currentRoom = this.dungeon.rooms[currentRoomId];
        if (currentRoom && currentRoom.exits) {
            for (const targetRoomId of Object.values(currentRoom.exits)) {
                this.knownRooms.add(targetRoomId);
            }
        }

        // Calculate bounds for centering
        const bounds = this.calculateBounds();
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        // Render connections first (so they appear behind rooms)
        for (const [roomId, pos] of Object.entries(this.roomPositions)) {
            if (!this.exploredRooms.has(roomId) && !this.knownRooms.has(roomId)) continue;

            const room = this.dungeon.rooms[roomId];
            if (!room || !room.exits) continue;

            const screenPos = this.gridToScreen(pos.x, pos.y, bounds, centerX, centerY);

            // Draw connections to adjacent rooms
            for (const [direction, targetRoomId] of Object.entries(room.exits)) {
                const targetPos = this.roomPositions[targetRoomId];
                if (!targetPos) continue;

                const targetScreenPos = this.gridToScreen(targetPos.x, targetPos.y, bounds, centerX, centerY);

                // Only draw if both rooms are known or explored
                if (this.exploredRooms.has(roomId) || this.knownRooms.has(targetRoomId)) {
                    this.drawConnection(screenPos, targetScreenPos);
                }
            }
        }

        // Render rooms
        for (const [roomId, pos] of Object.entries(this.roomPositions)) {
            const screenPos = this.gridToScreen(pos.x, pos.y, bounds, centerX, centerY);

            if (roomId === currentRoomId) {
                this.drawRoom(screenPos, 'current', roomId);
            } else if (this.exploredRooms.has(roomId)) {
                this.drawRoom(screenPos, 'explored', roomId);
            } else if (this.knownRooms.has(roomId)) {
                this.drawRoom(screenPos, 'known', roomId);
            }
        }
    }

    calculateBounds() {
        /**
         * Calculate min/max grid coordinates for centering
         */
        let minX = 0, maxX = 0, minY = 0, maxY = 0;

        for (const pos of Object.values(this.roomPositions)) {
            minX = Math.min(minX, pos.x);
            maxX = Math.max(maxX, pos.x);
            minY = Math.min(minY, pos.y);
            maxY = Math.max(maxY, pos.y);
        }

        return { minX, maxX, minY, maxY };
    }

    gridToScreen(gridX, gridY, bounds, centerX, centerY) {
        /**
         * Convert grid coordinates to screen coordinates (centered)
         */
        const gridWidth = bounds.maxX - bounds.minX;
        const gridHeight = bounds.maxY - bounds.minY;

        const x = centerX + (gridX - (bounds.minX + bounds.maxX) / 2) * (this.roomSize + this.roomPadding);
        const y = centerY + (gridY - (bounds.minY + bounds.maxY) / 2) * (this.roomSize + this.roomPadding);

        return { x, y };
    }

    drawConnection(pos1, pos2) {
        /**
         * Draw a line connecting two rooms
         */
        this.ctx.strokeStyle = this.colors.exit;
        this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        this.ctx.moveTo(pos1.x, pos1.y);
        this.ctx.lineTo(pos2.x, pos2.y);
        this.ctx.stroke();
    }

    drawRoom(pos, type, roomId) {
        /**
         * Draw a single room
         */
        const size = this.roomSize;
        const halfSize = size / 2;

        // Room background
        this.ctx.fillStyle = this.colors[type];
        this.ctx.fillRect(pos.x - halfSize, pos.y - halfSize, size, size);

        // Room border
        this.ctx.strokeStyle = type === 'current' ? this.colors.current : this.colors.text;
        this.ctx.lineWidth = type === 'current' ? 4 : 2;
        this.ctx.strokeRect(pos.x - halfSize, pos.y - halfSize, size, size);

        // Room label (number)
        if (type !== 'known') {
            const roomNum = roomId.replace('room_', '').replace(/^0+/, '');
            this.ctx.fillStyle = this.colors.text;
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(roomNum, pos.x, pos.y);
        }

        // Add glow effect for current room
        if (type === 'current') {
            this.ctx.shadowColor = this.colors.current;
            this.ctx.shadowBlur = 20;
            this.ctx.strokeRect(pos.x - halfSize, pos.y - halfSize, size, size);
            this.ctx.shadowBlur = 0;
        }

        // Add question mark for known but not explored
        if (type === 'known') {
            this.ctx.fillStyle = this.colors.text;
            this.ctx.font = 'bold 24px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText('?', pos.x, pos.y);
        }
    }

    updateExploredRooms(exploredRoomIds) {
        /**
         * Update the set of explored rooms
         */
        this.exploredRooms = new Set(exploredRoomIds);
    }

    updateKnownRooms(knownRoomIds) {
        /**
         * Update the set of known rooms
         */
        this.knownRooms = new Set(knownRoomIds);
    }
}

// Export to global scope
window.DungeonMapRenderer = DungeonMapRenderer;
