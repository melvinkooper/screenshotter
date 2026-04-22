# Happy Horizon Brand Guide

## Colors
- **Primary dark (navy):** #0f1a2e (logo, headings)
- **Accent lime:** #c8f04c (CTAs, highlights)
- **Accent lime hover:** #b8e03c
- **Background:** #ffffff (white)
- **Text primary:** #1a1a1a
- **Text secondary:** #666666
- **Text muted:** #999999
- **Border:** #e8e8e0
- **Surface (cards on white):** #f9f9f7

## Typography
- **Font:** Plus Jakarta Sans (Google Fonts)
- **Weights:** 400 (body), 500 (labels), 600 (semi-bold), 700 (bold), 800 (extra-bold headings)
- **Letter-spacing headings:** -0.04em
- **Line-height body:** 1.5

## Buttons
- **Primary:** background #c8f04c, text #1a1a1a, border-radius 9999px, font-weight 700
- **Secondary/dark:** background #1a1a1a, text #c8f04c, border-radius 9999px

## Logo
- File: hh-logo.png
- Dark navy wordmark, use on white backgrounds
- Minimum clear space: 1rem around logo

## Header (standard across all tools)
Every Happy Horizon tool uses this consistent header pattern:

### Structure
```html
<header>
  <div style="display:flex;align-items:center;gap:12px">
    <img src="brand_assets/hh-logo.png" alt="Happy Horizon" style="height:28px;width:auto" />
    <div style="width:1px;height:24px;background:var(--border)"></div>
    <div>
      <div style="font-size:14px;font-weight:700;color:var(--navy);letter-spacing:-.04em">{Tool Name}</div>
      <div style="font-size:10px;color:var(--muted)">{Subtitle}</div>
    </div>
  </div>
  <div id="header-right" style="display:flex;align-items:center;gap:12px">
    <!-- Optional: action buttons go here -->
  </div>
</header>
```

### Styling
- **Height:** 60px
- **Position:** sticky top, z-index 100
- **Background:** rgba(255,255,255,.95) with backdrop-filter blur(12px)
- **Border:** 1px solid #e8e8e0 (bottom)
- **Padding:** 0 28px
- **Layout:** flexbox, space-between, vertically centered
- **Logo:** height 28px, auto width
- **Divider:** 1px wide, 24px tall, border color
- **Tool name:** 14px, weight 700, navy (#0f1a2e), letter-spacing -0.04em
- **Subtitle:** 10px, muted (#999999)

## Credentials & API Keys (HTML/PHP frontends)
API keys and secrets must **never** be hardcoded in HTML, JS, or client-visible source. Use the following server-side injection pattern:

### Pattern
1. Store credentials in `.config.json` (gitignored) at the project root:
   ```json
   {
     "oauth_client_id": "...",
     "gemini_api_key": "..."
   }
   ```
2. Create a `config.php` that reads `.config.json` and serves only the allowed keys as JSON:
   ```php
   <?php
   header('Content-Type: application/json');
   $config = json_decode(file_get_contents(__DIR__ . '/.config.json'), true);
   echo json_encode([
     'oauth_client_id' => $config['oauth_client_id'] ?? null,
     'gemini_api_key'  => $config['gemini_api_key'] ?? null,
   ]);
   ```
3. In JS, fetch credentials at runtime via XHR — never embed them in the source:
   ```js
   fetch('config.php').then(r => r.json()).then(config => {
     GOOGLE_CLIENT_ID = config.oauth_client_id;
     GEMINI_API_KEY   = config.gemini_api_key;
   });
   ```

### Rules
- `.config.json` must be in `.gitignore` — never commit it
- `config.php` acts as a gatekeeper: only expose keys the frontend actually needs
- Never use inline `<script>` variables like `var KEY = "..."` rendered by PHP
- For static/file:// hosting (no PHP), the JS can fall back to fetching `.config.json` directly — but this file must still be gitignored and not deployed publicly
