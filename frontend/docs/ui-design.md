# Cyber Graph — UI Design Guide

## 1. Design Philosophy
The cybersecurity analyst interface is built on 4 core pillars:
1. **Dark Security Dashboard**: Dark `#0a0d14` background reducing eye fatigue during 24/7 SOC operations.
2. **Instant Cognitive Clarity**: The security analyst must understand the threat situation within seconds.
3. **High-Contrast Severity Hierarchy**:
   - `CRITICAL`: Neon red (`#ef4444`) with pulse glow.
   - `HIGH`: Vibrant orange (`#f97316`).
   - `MEDIUM`: Amber yellow (`#eab308`).
   - `LOW`: Cyan / Electric blue (`#3b82f6` / `#06b6d4`).
   - `INFO / VERIFIED`: Emerald green (`#10b981`).
4. **Minimal Clutter & High Signal-to-Noise**: Glassmorphic panels, structured key metrics, and drawer overlays.

## 2. Typography & Fonts
- **Primary Text**: Inter (`sans-serif`) for crisp legibility across table rows and narrative text.
- **Data & Telemetry**: JetBrains Mono (`monospace`) for IP addresses, SHA-256 digests, timestamps, and MITRE codes.
