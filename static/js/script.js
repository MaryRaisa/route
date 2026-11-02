/**
 * SMART QR GUIDE AIRPORT - FRONTEND ENGINE
 * Handles interactive map rendering, wrong-turn detection, voice guidance,
 * live flight gate updates, and QR scanner logic.
 */

// Global speech synthesis tracker
let speechUtterance = null;
let isSpeaking = false;
let isPaused = false;
let gatePollInterval = null;

// =========================================================================
// 1. AIRPORT SVG MAP RENDERER
// =========================================================================
function renderAirportMap(svgId, routeData, allNodes, allEdges, options = {}) {
    const svg = document.getElementById(svgId);
    if (!svg) return;

    // Clear previous SVG content
    svg.innerHTML = '';

    // Canvas size (1000 x 720)
    const width = 1000;
    const height = 720;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    const ns = "http://www.w3.org/2000/svg";

    // 1. Draw Terminal Architectural Zones (Floor Plan Background)
    const zones = [
        { name: "ENTRANCE & TICKETING HALL", x: 40, y: 110, w: 340, h: 440, fill: "#F8FAFC", stroke: "#E2E8F0" },
        { name: "SECURITY SCREENING ZONE", x: 420, y: 190, w: 140, h: 360, fill: "#EFF6FF", stroke: "#BFDBFE" },
        { name: "CENTRAL DEPARTURE CONCOURSE", x: 590, y: 110, w: 150, h: 480, fill: "#F0FDF4", stroke: "#BBF7D0" },
        { name: "CONCOURSE A - GATES A1-A5", x: 770, y: 110, w: 190, h: 230, fill: "#FFF7ED", stroke: "#FED7AA" },
        { name: "CONCOURSE B - GATES B1-B5", x: 770, y: 370, w: 190, h: 260, fill: "#FAF5FF", stroke: "#E9D5FF" },
        { name: "ARRIVALS & BAGGAGE RECLAIM", x: 40, y: 560, w: 380, h: 140, fill: "#F1F5F9", stroke: "#CBD5E1" }
    ];

    zones.forEach(z => {
        const rect = document.createElementNS(ns, "rect");
        rect.setAttribute("x", z.x);
        rect.setAttribute("y", z.y);
        rect.setAttribute("width", z.w);
        rect.setAttribute("height", z.h);
        rect.setAttribute("rx", "12");
        rect.setAttribute("fill", z.fill);
        rect.setAttribute("stroke", z.stroke);
        rect.setAttribute("stroke-width", "1.5");
        svg.appendChild(rect);

        const txt = document.createElementNS(ns, "text");
        txt.setAttribute("x", z.x + 15);
        txt.setAttribute("y", z.y + 24);
        txt.setAttribute("fill", "#94A3B8");
        txt.setAttribute("font-size", "10");
        txt.setAttribute("font-weight", "700");
        txt.setAttribute("letter-spacing", "1px");
        txt.textContent = z.name;
        svg.appendChild(txt);
    });

    // 2. Draw Graph Paths / Edges
    const pathGroup = document.createElementNS(ns, "g");
    pathGroup.setAttribute("id", "map-edges-group");

    // Map route node sequence for path highlighting
    const activeRouteIds = (routeData && routeData.path_ids) ? routeData.path_ids : [];
    const activeEdgesSet = new Set();
    for (let i = 0; i < activeRouteIds.length - 1; i++) {
        const u = activeRouteIds[i];
        const v = activeRouteIds[i + 1];
        activeEdgesSet.add(`${Math.min(u, v)}-${Math.max(u, v)}`);
    }

    if (allEdges && allEdges.length > 0) {
        allEdges.forEach(edge => {
            const line = document.createElementNS(ns, "line");
            line.setAttribute("x1", edge.x1);
            line.setAttribute("y1", edge.y1);
            line.setAttribute("x2", edge.x2);
            line.setAttribute("y2", edge.y2);

            const edgeKey = `${Math.min(edge.source_id, edge.target_id)}-${Math.max(edge.source_id, edge.target_id)}`;
            const isRouteEdge = activeEdgesSet.has(edgeKey);

            if (isRouteEdge) {
                line.setAttribute("class", "map-edge map-edge-highlight");
            } else {
                line.setAttribute("class", "map-edge");
            }
            pathGroup.appendChild(line);
        });
    }
    svg.appendChild(pathGroup);

    // 3. Draw Nodes (Airport Locations)
    const nodeGroup = document.createElementNS(ns, "g");
    nodeGroup.setAttribute("id", "map-nodes-group");

    const startId = routeData ? (routeData.start_node ? routeData.start_node.id : null) : null;
    const endId = routeData ? (routeData.end_node ? routeData.end_node.id : null) : null;

    if (allNodes && allNodes.length > 0) {
        allNodes.forEach(node => {
            const isStart = (node.id === startId);
            const isEnd = (node.id === endId);
            const isPathNode = activeRouteIds.includes(node.id);

            const g = document.createElementNS(ns, "g");
            g.setAttribute("class", "map-node-item");
            g.style.cursor = "pointer";

            // Click listener on node
            g.addEventListener('click', () => {
                if (options.onNodeClick) {
                    options.onNodeClick(node);
                }
            });

            // Outer Pulse Ring for Start Node
            if (isStart) {
                const pulse = document.createElementNS(ns, "circle");
                pulse.setAttribute("cx", node.x_coordinate);
                pulse.setAttribute("cy", node.y_coordinate);
                pulse.setAttribute("r", "20");
                pulse.setAttribute("fill", "rgba(0, 168, 255, 0.25)");
                pulse.setAttribute("class", "map-node-active");
                g.appendChild(pulse);
            }

            // Outer Target Ring for Destination Node
            if (isEnd) {
                const targetRing = document.createElementNS(ns, "circle");
                targetRing.setAttribute("cx", node.x_coordinate);
                targetRing.setAttribute("cy", node.y_coordinate);
                targetRing.setAttribute("r", "22");
                targetRing.setAttribute("fill", "none");
                targetRing.setAttribute("stroke", "#06D6A0");
                targetRing.setAttribute("stroke-width", "3");
                targetRing.setAttribute("stroke-dasharray", "4 3");
                g.appendChild(targetRing);
            }

            // Main Circle Marker
            const circle = document.createElementNS(ns, "circle");
            circle.setAttribute("cx", node.x_coordinate);
            circle.setAttribute("cy", node.y_coordinate);
            circle.setAttribute("r", isStart || isEnd ? "14" : "11");
            circle.setAttribute("class", "map-node-circle");

            // Color node depending on status
            if (isStart) {
                circle.setAttribute("fill", "#00A8FF");
                circle.setAttribute("stroke", "#0B192C");
            } else if (isEnd) {
                circle.setAttribute("fill", "#06D6A0");
                circle.setAttribute("stroke", "#0B192C");
            } else if (isPathNode) {
                circle.setAttribute("fill", "#E0F2FE");
                circle.setAttribute("stroke", "#00A8FF");
            } else {
                circle.setAttribute("fill", getNodeColorByType(node.location_type));
                circle.setAttribute("stroke", "#64748B");
            }
            g.appendChild(circle);

            // Icon / Indicator letter inside node
            const iconText = document.createElementNS(ns, "text");
            iconText.setAttribute("x", node.x_coordinate);
            iconText.setAttribute("y", node.y_coordinate + 4);
            iconText.setAttribute("text-anchor", "middle");
            iconText.setAttribute("fill", (isStart || isEnd) ? "#FFFFFF" : "#1E293B");
            iconText.setAttribute("font-size", "9");
            iconText.setAttribute("font-weight", "800");
            iconText.textContent = getNodeAbbreviation(node.location_type);
            g.appendChild(iconText);

            // Label Below Node
            const label = document.createElementNS(ns, "text");
            label.setAttribute("x", node.x_coordinate);
            label.setAttribute("y", node.y_coordinate + (isStart || isEnd ? 26 : 22));
            label.setAttribute("class", "map-node-label");
            if (isStart || isEnd) {
                label.setAttribute("font-weight", "800");
                label.setAttribute("fill", isStart ? "#0077B6" : "#059669");
            }
            label.textContent = node.location_name;
            g.appendChild(label);

            nodeGroup.appendChild(g);
        });
    }
    svg.appendChild(nodeGroup);
}

function getNodeColorByType(type) {
    switch (type) {
        case 'Entrance': return '#DCFCE7';
        case 'Check-in': return '#E0F2FE';
        case 'Security': return '#FEF3C7';
        case 'Gate': return '#F1F5F9';
        case 'Lounge': return '#F3E8FF';
        case 'Restroom': return '#CCFBF1';
        case 'Amenities': return '#FFEDD5';
        case 'Baggage': return '#E2E8F0';
        default: return '#FFFFFF';
    }
}

function getNodeAbbreviation(type) {
    switch (type) {
        case 'Entrance': return 'IN';
        case 'Check-in': return 'C';
        case 'Security': return 'S';
        case 'Gate': return 'G';
        case 'Lounge': return 'L';
        case 'Restroom': return 'WC';
        case 'Amenities': return 'F';
        case 'Baggage': return 'B';
        default: return '•';
    }
}

// =========================================================================
// 2. VOICE GUIDANCE (WEB SPEECH SYNTHESIS API)
// =========================================================================
function speakDirections(text, lang = 'en') {
    if (!('speechSynthesis' in window)) {
        alert("Speech synthesis is not supported in this browser.");
        return;
    }

    window.speechSynthesis.cancel(); // Stop any active speech

    const utterance = new SpeechSynthesisUtterance(text);

    // Map language code to standard speech BCP 47 tag
    let langCode = 'en-US';
    if (lang === 'ta') langCode = 'ta-IN';
    else if (lang === 'hi') langCode = 'hi-IN';
    utterance.lang = langCode;

    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
        isSpeaking = true;
        isPaused = false;
        updateVoiceButtonStates();
    };

    utterance.onend = () => {
        isSpeaking = false;
        isPaused = false;
        updateVoiceButtonStates();
    };

    utterance.onerror = (e) => {
        console.warn("Speech synthesis notice:", e);
        isSpeaking = false;
        isPaused = false;
        updateVoiceButtonStates();
    };

    speechUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

function pauseSpeech() {
    if (window.speechSynthesis && isSpeaking && !isPaused) {
        window.speechSynthesis.pause();
        isPaused = true;
        updateVoiceButtonStates();
    }
}

function resumeSpeech() {
    if (window.speechSynthesis && isSpeaking && isPaused) {
        window.speechSynthesis.resume();
        isPaused = false;
        updateVoiceButtonStates();
    }
}

function stopSpeech() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        isPaused = false;
        updateVoiceButtonStates();
    }
}

function updateVoiceButtonStates() {
    const playBtn = document.getElementById('btn-voice-play');
    const pauseBtn = document.getElementById('btn-voice-pause');
    const stopBtn = document.getElementById('btn-voice-stop');

    if (playBtn) playBtn.disabled = isSpeaking && !isPaused;
    if (pauseBtn) pauseBtn.disabled = !isSpeaking;
    if (stopBtn) stopBtn.disabled = !isSpeaking;
}

// =========================================================================
// 3. WRONG-TURN DETECTION & AUTOMATIC REROUTING
// =========================================================================
function simulateCheckpointScan(scannedLocId, plannedPathIds, destinationId, lang = 'en', onComplete) {
    fetch('/api/check-checkpoint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            scanned_loc_id: scannedLocId,
            planned_path_ids: plannedPathIds,
            destination_id: destinationId,
            lang: lang
        })
    })
    .then(res => res.json())
    .then(data => {
        if (onComplete) {
            onComplete(data);
        }
    })
    .catch(err => {
        console.error("Error checking checkpoint:", err);
    });
}

// =========================================================================
// 4. LIVE FLIGHT GATE CHANGE MONITORING
// =========================================================================
function startGatePolling(flightNumber, currentGateName, onGateChanged) {
    if (!flightNumber || flightNumber === 'N/A') return;

    if (gatePollInterval) clearInterval(gatePollInterval);

    gatePollInterval = setInterval(() => {
        fetch(`/api/flight-updates/${encodeURIComponent(flightNumber)}`)
            .then(res => res.json())
            .then(data => {
                if (data && data.found) {
                    if (data.boarding_gate && data.boarding_gate !== currentGateName) {
                        clearInterval(gatePollInterval);
                        if (onGateChanged) {
                            onGateChanged(data.boarding_gate, data);
                        }
                    }
                }
            })
            .catch(err => console.warn("Polling error:", err));
    }, 6000);
}

// =========================================================================
// 5. CAMERA QR CODE SCANNER INITIALIZATION
// =========================================================================
function initQrScanner(containerId, onScanSuccess) {
    if (typeof Html5Qrcode === 'undefined') {
        console.warn("Html5Qrcode library not loaded.");
        return;
    }

    const html5QrCode = new Html5Qrcode(containerId);
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
    };

    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            // Prefer back camera on mobile
            let cameraId = devices[0].id;
            for (let d of devices) {
                if (d.label.toLowerCase().includes('back') || d.label.toLowerCase().includes('environment')) {
                    cameraId = d.id;
                    break;
                }
            }

            html5QrCode.start(
                cameraId,
                config,
                (decodedText) => {
                    html5QrCode.stop().then(() => {
                        onScanSuccess(decodedText);
                    });
                },
                (errorMessage) => {
                    // Scanning errors are frequent until QR comes in view
                }
            ).catch(err => {
                console.warn("Camera start failed, showing manual option:", err);
            });
        }
    }).catch(err => {
        console.warn("Unable to query camera list:", err);
    });

    return html5QrCode;
}
