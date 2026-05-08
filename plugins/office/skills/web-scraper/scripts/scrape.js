#!/usr/bin/env node

/**
 * Web Scraper: Extract text + images from any URL via Headless Chromium.
 *
 * Usage:
 *   node scrape.js <url> [options]
 *
 * Options:
 *   --max-chars <n>     Max characters to return (default: 10000)
 *   --wait <ms>         Wait time after load for JS rendering (default: 3000)
 *   --selector <css>    CSS selector to extract (default: auto-detect)
 *   --text              Output plain text only (no JSON)
 *   --no-images         Skip image extraction
 *
 * Output (JSON):
 *   { url, title, description, content, images: [{src, alt}], truncated, chars }
 *
 * Dependencies:
 *   npm install playwright
 *   npx playwright install chromium
 */

const { chromium } = require('playwright');

// --- Parse args ---
const args = process.argv.slice(2);
const url = args.find(a => a.startsWith('http'));

if (!url) {
  console.error('Usage: node scrape.js <url> [--max-chars N] [--wait MS] [--selector CSS] [--text] [--no-images]');
  process.exit(1);
}

function getFlag(name, defaultVal) {
  const idx = args.indexOf(name);
  return idx > -1 ? args[idx + 1] : defaultVal;
}

const maxChars = parseInt(getFlag('--max-chars', '10000'));
const waitMs = parseInt(getFlag('--wait', '3000'));
const selector = getFlag('--selector', null);
const textOnly = args.includes('--text');
const skipImages = args.includes('--no-images');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  try {
    await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: 20000
    });

    await page.waitForTimeout(waitMs);

    const result = await page.evaluate(({ sel, extractImages }) => {
      // --- Find main content element ---
      let el;
      if (sel) {
        el = document.querySelector(sel);
      } else {
        el = document.querySelector('article')
          || document.querySelector('[role="main"]')
          || document.querySelector('main')
          || document.body;
      }

      // --- Extract text ---
      const text = el ? el.innerText : '';

      // --- Extract metadata ---
      const title = document.title || '';
      const ogDesc = document.querySelector('meta[property="og:description"]')
        || document.querySelector('meta[name="description"]');
      const description = ogDesc ? ogDesc.getAttribute('content') : '';

      // --- Extract images ---
      const images = [];
      if (extractImages && el) {
        const imgs = el.querySelectorAll('img');
        const seen = new Set();
        imgs.forEach(img => {
          const src = img.src || '';
          if (!src || seen.has(src)) return;

          // Filter: skip tiny icons (<50px), data URIs, tracking pixels
          const w = img.naturalWidth || img.width || 0;
          const h = img.naturalHeight || img.height || 0;
          if (w > 0 && w < 50 && h > 0 && h < 50) return;
          if (src.startsWith('data:')) return;

          // Classify image type
          let type = 'unknown';
          if (src.includes('pbs.twimg.com/media') || src.includes('tweet_video_thumb')) {
            type = 'tweet-media';
          } else if (src.includes('pbs.twimg.com/profile')) {
            type = 'avatar';
          } else if (src.includes('emoji') || src.includes('twemoji')) {
            type = 'emoji';
          } else if (w >= 200 || h >= 200 || (!w && !h)) {
            type = 'content';
          } else {
            type = 'icon';
          }

          // Only include meaningful images
          if (['tweet-media', 'content'].includes(type)) {
            seen.add(src);
            images.push({
              src,
              alt: img.alt || '',
              type
            });
          }
        });
      }

      return { title, description, text, images };
    }, { sel: selector, extractImages: !skipImages });

    const content = result.text.substring(0, maxChars);

    if (textOnly) {
      console.log(content);
    } else {
      const output = {
        url,
        title: result.title,
        description: result.description,
        content,
        truncated: result.text.length > maxChars,
        chars: content.length
      };

      if (!skipImages) {
        output.images = result.images;
      }

      console.log(JSON.stringify(output, null, 2));
    }

  } catch (e) {
    console.error(JSON.stringify({ error: e.message, url }));
    process.exit(1);
  }

  await browser.close();
})();
