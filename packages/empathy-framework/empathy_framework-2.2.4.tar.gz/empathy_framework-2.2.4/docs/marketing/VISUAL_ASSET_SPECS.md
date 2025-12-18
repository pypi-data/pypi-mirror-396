# Visual Asset Specifications

**Purpose:** Guide for creating visual assets using Adobe Stock, AI tools, or custom design.

---

## Required Assets

### 1. Product Hunt Thumbnail
**Dimensions:** 1270 x 760 px
**Purpose:** Main product image on Product Hunt listing

**Concept:**
- Clean, modern design with dark/light gradient background
- Central visual showing interconnected nodes (representing memory/agents)
- Text overlay: "Empathy Framework" and tagline
- Subtle tech aesthetic without being cluttered

**Key Elements:**
- Memory visualization (brain + database icon hybrid)
- Connection lines between nodes
- Professional, enterprise-ready feel

**Stock Search Terms:**
- "AI neural network abstract"
- "memory technology visualization"
- "connected nodes technology"
- "enterprise software abstract"

---

### 2. Memory Architecture Diagram
**Dimensions:** 1200 x 800 px (or 16:9 aspect ratio)
**Purpose:** Explain dual-layer memory system

**Content:**
```
┌─────────────────────────────────────────────────────┐
│                   Working Memory                     │
│              (In-process, session-only)              │
└──────────────────────┬──────────────────────────────┘
                       │ Promote
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Short-Term Memory                  │
│                 (Redis, configurable TTL)            │
└──────────────────────┬──────────────────────────────┘
                       │ Commit
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Long-Term Memory                   │
│              (Patterns, git-based, encrypted)        │
└─────────────────────────────────────────────────────┘
```

**Style:**
- Clean boxes with rounded corners
- Arrows showing data flow
- Color coding: Blue (short-term), Green (long-term), Gray (working)
- Icons for each tier (Redis logo, database, brain)

---

### 3. 5 Problems / 6 Solutions Infographic
**Dimensions:** 1200 x 1600 px (vertical) or 1600 x 900 px (horizontal)
**Purpose:** Visual summary of value proposition

**Content:**

**Problems (Left/Top):**
1. Stateless (icon: empty brain)
2. Cloud-dependent (icon: cloud with lock)
3. Isolated (icon: disconnected nodes)
4. Reactive (icon: alarm/warning)
5. Expensive (icon: dollar sign)

**Solutions (Right/Bottom):**
1. Persistent Memory (icon: brain + database)
2. Local-First (icon: building/server)
3. Multi-Agent (icon: connected nodes)
4. Anticipatory (icon: crystal ball/future)
5. Smart Routing (icon: cost graph down)
6. Enterprise-Ready (icon: shield/checkmark)

**Style:**
- Split design: problems in red/warning colors, solutions in green/positive
- Icons should be simple, line-art style
- Arrow or transformation visual connecting problems to solutions

---

### 4. Quick Start Screenshot
**Dimensions:** 1200 x 600 px
**Purpose:** Show the 2-command setup

**Content:**
Terminal screenshot showing:
```bash
$ pip install empathy-framework
Successfully installed empathy-framework-2.1.1

$ empathy-memory serve
🚀 Starting Empathy Memory Control Panel...
✓ Redis started on port 6379
✓ API server running at http://localhost:8765
✓ Memory system ready
```

**Style:**
- Dark terminal theme (VS Code or iTerm2 style)
- Syntax highlighting
- Clean, readable font
- Success checkmarks in green

---

### 5. Comparison Table Image
**Dimensions:** 1200 x 800 px
**Purpose:** Visual comparison with competitors

**Content:**
| Capability | Empathy | SonarQube | Copilot |
|------------|---------|-----------|---------|
| Persistent Memory | ✅ | ❌ | ❌ |
| Local-First | ✅ | ❌ | ❌ |
| Multi-Agent | ✅ | ❌ | ❌ |
| Anticipatory | ✅ | ❌ | ❌ |
| Free for Small Teams | ✅ | ❌ | ❌ |

**Style:**
- Clean table design
- Empathy column highlighted
- Green checkmarks, red X marks
- Professional, not cluttered

---

### 6. Social Media Cards
**Dimensions:** 1200 x 630 px (Twitter/LinkedIn)
**Purpose:** Link preview images

**Variants needed:**
1. **Main card:** "Empathy Framework" + tagline + logo
2. **Memory card:** Focus on persistent memory
3. **Enterprise card:** Focus on local-first/compliance
4. **Agents card:** Focus on multi-agent orchestration

**Style:**
- Consistent branding across all
- Dark gradient background
- Clean typography
- Subtle tech pattern

---

### 7. Logo Variations
**Dimensions:** Various (SVG preferred)
**Purpose:** Branding across platforms

**Needed:**
1. Full logo (icon + text)
2. Icon only (square, for favicons)
3. Dark background version
4. Light background version

**Concept:**
- Brain or memory-related icon
- "E" for Empathy stylized
- Professional, enterprise feel
- Not too playful

---

## AI Image Generation Prompts

### For Midjourney/DALL-E:

**Product Hero:**
```
Abstract technology visualization, interconnected glowing nodes forming a brain-like network, dark blue gradient background, soft cyan and purple accent lights, enterprise software aesthetic, clean minimal design, professional, 4k, high detail --ar 16:9
```

**Memory Architecture:**
```
Technical diagram illustration, three-tier architecture with flowing data streams, Redis database icon, brain neural network, git repository, clean white background with subtle grid, blue and green color scheme, infographic style --ar 16:9
```

**AI Collaboration:**
```
Abstract representation of AI agents collaborating, multiple connected spheres with light beams between them, futuristic but professional, enterprise tech aesthetic, dark gradient background, glowing connection lines --ar 16:9
```

---

## Color Palette

**Primary:**
- Dark Blue: #1a1a2e
- Accent Blue: #4361ee
- Accent Cyan: #00d4ff

**Secondary:**
- Success Green: #10b981
- Warning Orange: #f59e0b
- Error Red: #ef4444

**Neutral:**
- Light Gray: #f3f4f6
- Medium Gray: #6b7280
- Dark Gray: #1f2937

---

## Typography

**Headings:** Inter Bold or SF Pro Display Bold
**Body:** Inter Regular or SF Pro Text
**Code:** JetBrains Mono or Fira Code

---

## File Naming Convention

```
empathy-[asset-type]-[variant]-[dimensions].png

Examples:
empathy-thumbnail-main-1270x760.png
empathy-diagram-memory-1200x800.png
empathy-social-twitter-1200x630.png
empathy-logo-dark-512x512.png
```

---

## Checklist

- [ ] Product Hunt thumbnail (1270x760)
- [ ] Memory architecture diagram (1200x800)
- [ ] 5 Problems / 6 Solutions infographic
- [ ] Quick start terminal screenshot (1200x600)
- [ ] Comparison table image (1200x800)
- [ ] Social media cards (1200x630) x 4 variants
- [ ] Logo variations (SVG + PNG)
- [ ] Founder photo (optional, for Product Hunt)

---

## Notes

- All assets should feel cohesive and professional
- Avoid clipart or overly stock-looking images
- Enterprise customers should feel comfortable using these
- Dark mode friendly designs preferred
- Keep text readable at small sizes
