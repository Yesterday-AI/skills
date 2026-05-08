#!/usr/bin/env node

/**
 * X-Reader: Read Twitter/X posts and articles via Headless Chromium.
 * 
 * Usage: node read-x.js <url> [--max-chars 5000]
 * 
 * Dependencies:
 *   npm install playwright
 *   npx playwright install chromium
 *   npx playwright install-deps chromium
 */

const { chromium } = require('playwright');

const url = process.argv[2];
const maxCharsFlag = process.argv.indexOf('--max-chars');
const maxChars = maxCharsFlag > -1 ? parseInt(process.argv[maxCharsFlag + 1]) : 10000;

if (!url) {
  console.error('Usage: node read-x.js <url> [--max-chars 5000]');
  process.exit(1);
}

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

    // Wait for dynamic content to render
    await page.waitForTimeout(5000);

    const result = await page.evaluate(() => {
      // Try to get article content (tweet or long-form article)
      const article = document.querySelector('article');
      const text = article ? article.innerText : document.body.innerText;

      // Extract metadata
      const title = document.title || '';
      const ogDesc = document.querySelector('meta[property="og:description"]');
      const desc = ogDesc ? ogDesc.getAttribute('content') : '';

      return { title, description: desc, text };
    });

    const output = {
      url,
      title: result.title,
      description: result.description,
      content: result.text.substring(0, maxChars),
      truncated: result.text.length > maxChars
    };

    console.log(JSON.stringify(output, null, 2));

  } catch (e) {
    console.error(JSON.stringify({ error: e.message, url }));
    process.exit(1);
  }

  await browser.close();
})();
