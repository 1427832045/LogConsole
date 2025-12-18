# LogConsole 原型设计 Prompt

**生成日期**: 2024-12-16
**基于**: LogConsole PRD v1.0
**设计系统**: Material Design 3 (Dark Theme)
**生成工具**: Gemini CLI

---

## 使用说明

将以下 prompt 复制粘贴到 AI 编码助手（如 Claude 3.5 Sonnet 或 GPT-4）中，即可生成高保真的 HTML/Tailwind CSS 原型。

---

## 1. Role Definition
You are a **Senior UI/UX Engineer** specializing in developer tools and data-heavy desktop applications. Your expertise lies in creating high-performance, information-dense interfaces using **Material Design 3** principles. You understand the specific needs of backend developers and QA engineers who spend hours analyzing large text files.

## 2. Task Description
Create a high-fidelity, interactive **HTML/Tailwind CSS prototype** for "LogConsole" — a modern, high-performance desktop log viewer.
The goal is to visualize the **MVP (Phase 1)** interface with hints of Phase 2 features (Filtering). The interface must feel native, responsive, and optimized for reading dense text data without visual clutter.

**Key Scenarios to Demonstrate:**
1.  **Main View**: A large log file is open (`application.log`), showing thousands of lines with syntax highlighting.
2.  **Search Active**: The user is searching for "ConnectionRefused", with matches highlighted and a search bar visible.
3.  **Filtering**: A side panel or overlay showing active filters (e.g., "Show only ERROR").

## 3. Tech Stack Specifications
-   **Structure**: Semantic HTML5.
-   **Styling**: Tailwind CSS (v3.x) via CDN.
-   **Icons**: FontAwesome (via CDN) or Heroicons (SVG).
-   **Interactivity**: Vanilla JavaScript for basic UI states (toggling sidebars, switching tabs, simple search simulation).
-   **Font**: Google Fonts (`Inter` for UI, `JetBrains Mono` or `Fira Code` for log content).

## 4. Visual Design Requirements

### A. Color Palette (Dark Theme Default)
The interface should default to a modern "Developer Dark" theme to reduce eye strain.

| Scope | Tailwind Class | Hex Value | Usage |
| :--- | :--- | :--- | :--- |
| **Background** | `bg-gray-900` | `#111827` | Main app background |
| **Surface** | `bg-gray-800` | `#1F2937` | Panels, Toolbar, Status Bar |
| **Border** | `border-gray-700` | `#374151` | Dividers, Borders |
| **Text Primary** | `text-gray-100` | `#F3F4F6` | Main UI text |
| **Text Secondary**| `text-gray-400` | `#9CA3AF` | Labels, Line numbers, timestamps |
| **Accent/Primary**| `text-indigo-400`| `#818CF8` | Active states, Buttons, Links |
| **Log: ERROR** | `text-red-400` | `#F87171` | Error lines/badges (Background: `bg-red-900/20`) |
| **Log: WARN** | `text-amber-400` | `#FBBF24` | Warning lines/badges (Background: `bg-amber-900/20`) |
| **Log: INFO** | `text-blue-400` | `#60A5FA` | Info lines |
| **Log: DEBUG** | `text-gray-500` | `#6B7280` | Debug lines |
| **Highlight** | `bg-yellow-500/40`| `#EAB308` | Search match background |

### B. UI Component Specs

1.  **Main Toolbar (Top)**
    *   **Height**: `h-14` (56px).
    *   **Content**:
        *   Left: App Logo/Icon, Open File button, Export button.
        *   Center: **Search Bar** (Floating or embedded). Width: `w-96`. Inputs for "Regex", "Match Case", "Up/Down" arrows.
        *   Right: Settings icon, "Filter" toggle button (Active state indicator).
    *   **Style**: `bg-gray-800`, border-b `border-gray-700`, flexbox layout.

2.  **Log Viewer Area (Center)**
    *   **Font**: `font-mono` (JetBrains Mono).
    *   **Size**: `text-sm` (13px or 14px).
    *   **Layout**:
        *   **Gutter (Line Numbers)**: Fixed width (`w-16`), text-right, `bg-gray-850`, `text-gray-500`, non-selectable.
        *   **Content Area**: `whitespace-pre`, `overflow-x-auto`.
    *   **Interaction**: Hover effect on lines (`hover:bg-gray-800`). Selected line style (`bg-indigo-900/30`).

3.  **Status Bar (Bottom)**
    *   **Height**: `h-8` (32px).
    *   **Content**: File Path, File Size (e.g., "1.2 GB"), Total Lines, Current Encoding (UTF-8), Cursor Position (Ln 1204, Col 45).
    *   **Style**: `bg-gray-900`, `text-xs`, `text-gray-400`, flex items separated by spacers.

4.  **Filter Panel (Right Sidebar - Collapsible)**
    *   **Width**: `w-64`.
    *   **Content**: "Filter Rules" header. List of checkboxes/toggles (e.g., "Hide DEBUG", "Only Errors"). "Add Rule" button.
    *   **Style**: `bg-gray-800`, border-l `border-gray-700`.

### C. Layout Structure
```
+---------------------------------------------------------------+
|  Toolbar (Open, Search Input [Regex][Case], Export, Settings) |
+------+----------------------------------------------+---------+
| Line |                                              | Filter  |
| Num  |  Log Content Area (Scrollable)               | Panel   |
|      |  2024-12-16 10:00:01 [INFO] Started...       | (Open)  |
|      |  2024-12-16 10:00:02 [ERROR] Connection...   |         |
|      |                                              | [ ] Err |
|      |                                              | [x] Deb |
+------+----------------------------------------------+---------+
| Status Bar: /var/log/app.log | 1.2GB | UTF-8 | Ln 45, Col 1   |
+---------------------------------------------------------------+
```

## 5. Implementation Details (Functionality to Simulate)
-   **Static Data**: Generate 50+ lines of realistic log data. Include:
    -   Timestamps (ISO 8601).
    -   Mix of INFO, WARN, ERROR, DEBUG levels.
    -   Stack traces (indented lines) for ERRORs.
    -   JSON objects (pretty printed or raw).
-   **Search Simulation**: When typing in the search box, ensure some words in the log view (e.g., "Database") are pre-highlighted with the `Highlight` color.
-   **Responsiveness**: The Log Content Area must handle overflow correctly (horizontal scroll for long lines) without breaking the main layout.

## 6. Tailwind Configuration
Use arbitrary values where necessary, but adhere to the color palette.
*Example custom config to keep in mind:*
```javascript
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        log: {
          error: '#EF4444',
          warn: '#F59E0B',
          info: '#3B82F6',
          debug: '#9CA3AF'
        }
      }
    }
  }
}
```

## 7. Content Hierarchy
1.  **Log Content**: The most important element. High contrast, readable.
2.  **Search Controls**: Prominent, centrally located.
3.  **Status Information**: Subtle, anchored to the bottom.
4.  **Navigation/Tools**: Peripheral.

## 8. Special Requirements
-   **Scrollbar Styling**: Customize the scrollbars to be thin and dark (Webkit style) to match the dark theme.
-   **Empty States**: If no file is open, show a centered "Drag and drop log file here or click to Open" area.
-   **Line Wrapping**: Add a toggle icon in the toolbar for "Soft Wrap" vs "No Wrap".

## 9. Output Format
Provide a **single HTML file** containing:
1.  The HTML structure.
2.  The Tailwind CDN link.
3.  Google Fonts link.
4.  Embedded `<style>` for custom scrollbars and specific overrides.
5.  Embedded `<script>` to generate the log lines and handle basic UI toggles (Filter panel open/close).

---

## 下一步

1. **生成原型**: 将上述 prompt 提供给 Claude 或 GPT-4，生成 HTML 原型
2. **预览测试**: 在浏览器中打开 HTML 文件，测试交互和布局
3. **迭代优化**: 根据视觉效果调整颜色、间距、字体大小
4. **PyQt 实现**: 将 HTML 原型作为参考，使用 PyQt/PyQt5 实现桌面应用

---

**生成元数据**:
- Gemini 模型: gemini-2.5-pro
- 生成时间: 2024-12-16
- 基于文档: docs/log-console-prd.md
