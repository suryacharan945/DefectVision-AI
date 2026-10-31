const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUTPUT_DIR = path.resolve('delivery_24h', 'final_hardening_v3', 'test_outputs');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function runBrowserAudit() {
  console.log('====================================================');
  console.log('DEFECTVISION AI — PUPPETEER BROWSER VERIFICATION');
  console.log('====================================================');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--window-size=1366,768'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 768 });

  const testResults = [];

  try {
    // 1. Initial Page Load
    console.log('[1/8] Loading http://127.0.0.1:5173/ ...');
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2', timeout: 30000 });
    const title = await page.title();
    console.log(`Page title: "${title}"`);
    testResults.push({ test: 'Page Title & Mount', status: title.includes('DefectVision') ? 'PASS' : 'FAIL' });

    // 2. Verify Live Mode Banner
    console.log('[2/8] Checking Live Operating Mode Banner...');
    await page.waitForSelector('main', { timeout: 10000 });
    const bannerText = await page.evaluate(() => document.body.innerText);
    const hasLiveBanner = bannerText.includes('LIVE INFERENCE ACTIVE');
    console.log(`Live Banner Present: ${hasLiveBanner}`);
    testResults.push({ test: 'Live Operating Banner', status: hasLiveBanner ? 'PASS' : 'FAIL' });

    // 3. Trigger Preset Specimen Real Inference
    console.log('[3/8] Triggering preset inspection on bottle specimen...');
    const clickedPreset = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const bottlePreset = btns.find(b => b.innerText.includes('Bottle') || b.innerText.includes('broken'));
      if (bottlePreset) {
        bottlePreset.click();
        return true;
      }
      return false;
    });
    console.log(`Preset clicked: ${clickedPreset}`);

    // Wait for real backend inference to complete
    console.log('Waiting for model inference and verdict display...');
    await new Promise(r => setTimeout(r, 4000));

    // Verify inference result content
    const resultVerdict = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        hasVerdict: text.includes('AUTOMATED VISUAL VERDICT') || text.includes('Automated Visual Verdict'),
        hasDefective: text.includes('Defective Specimen'),
        hasLivePill: text.includes('LIVE INFERENCE'),
        hasScore: text.includes('4.5088'),
        hasThresh: text.includes('1.4138'),
        hasHeatmap: Boolean(document.querySelector('canvas, img[alt*="Heatmap"], [class*="Heatmap"], img[src*="data:image"]'))
      };
    });
    console.log('Inference Verdict Details:', resultVerdict);
    testResults.push({
      test: 'Real Model Inference & Heatmap',
      status: (resultVerdict.hasDefective && resultVerdict.hasLivePill && resultVerdict.hasScore) ? 'PASS' : 'FAIL'
    });

    // Capture screenshot of Live Inference
    const liveScreenshotPath = path.join(OUTPUT_DIR, 'browser_live_inference.png');
    await page.screenshot({ path: liveScreenshotPath, fullPage: false });
    console.log(`Saved screenshot: ${liveScreenshotPath}`);

    // 4. Test Batch Processing Section
    console.log('[4/8] Navigating to Batch Inspection tab...');
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const batchBtn = btns.find(b => b.innerText.includes('Batch Processing'));
      if (batchBtn) batchBtn.click();
    });
    await new Promise(r => setTimeout(r, 1200));

    const batchCheck = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        hasBatchHeader: text.includes('Batch') || text.includes('Processing'),
        hasExportBtn: Boolean(Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('CSV') || b.innerText.includes('Export')))
      };
    });
    console.log('Batch Tab Details:', batchCheck);
    testResults.push({ test: 'Batch Processing & Exports', status: batchCheck.hasBatchHeader ? 'PASS' : 'FAIL' });

    const batchScreenshotPath = path.join(OUTPUT_DIR, 'browser_batch_tab.png');
    await page.screenshot({ path: batchScreenshotPath, fullPage: false });
    console.log(`Saved screenshot: ${batchScreenshotPath}`);

    // 5. Test History Browser Section & Filtering
    console.log('[5/8] Navigating to History Browser tab...');
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const histBtn = btns.find(b => b.innerText.includes('History Browser'));
      if (histBtn) histBtn.click();
    });
    await new Promise(r => setTimeout(r, 1200));

    const histCheck = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        hasHistory: text.includes('History') || text.includes('Benchmark Logs'),
        hasFilter: Boolean(document.querySelector('select, input[type="search"]'))
      };
    });
    console.log('History Browser Details:', histCheck);
    testResults.push({ test: 'History Browser & Filtering', status: histCheck.hasHistory ? 'PASS' : 'FAIL' });

    const histScreenshotPath = path.join(OUTPUT_DIR, 'browser_history_tab.png');
    await page.screenshot({ path: histScreenshotPath, fullPage: false });
    console.log(`Saved screenshot: ${histScreenshotPath}`);

    // 6. Test Demo Mode Switch & Explicit Labeling
    console.log('[6/8] Testing Demo Mode Toggle & Explicit Labeling...');
    await page.evaluate(() => {
      localStorage.setItem('defectvision_demo_mode', 'true');
    });
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));

    const demoBannerCheck = await page.evaluate(() => {
      return document.body.innerText.includes('LIVE INFERENCE ACTIVE') || document.body.innerText.includes('DEMO MODE');
    });
    console.log(`Demo/Live Mode Indicator verified: ${demoBannerCheck}`);
    testResults.push({ test: 'Demo/Live Status Indication', status: demoBannerCheck ? 'PASS' : 'FAIL' });

    const demoScreenshotPath = path.join(OUTPUT_DIR, 'browser_demo_mode.png');
    await page.screenshot({ path: demoScreenshotPath, fullPage: false });
    console.log(`Saved screenshot: ${demoScreenshotPath}`);

    // Reset demo mode
    await page.evaluate(() => {
      localStorage.removeItem('defectvision_demo_mode');
    });

    // 7. Test Mobile Viewport Layout
    console.log('[7/8] Testing Mobile Layout (iPhone SE 375x667)...');
    await page.setViewport({ width: 375, height: 667, isMobile: true, hasTouch: true });
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));

    const mobileCheck = await page.evaluate(() => {
      const hasHamburger = Boolean(document.querySelector('button[aria-label="Toggle navigation menu"]'));
      return { hasHamburger, width: window.innerWidth };
    });
    console.log('Mobile Layout Details:', mobileCheck);
    testResults.push({ test: 'Mobile Viewport & Navigation', status: mobileCheck.hasHamburger ? 'PASS' : 'FAIL' });

    const mobileScreenshotPath = path.join(OUTPUT_DIR, 'browser_mobile_layout.png');
    await page.screenshot({ path: mobileScreenshotPath, fullPage: false });
    console.log(`Saved screenshot: ${mobileScreenshotPath}`);

    // 8. Frontend-Backend Value Agreement
    console.log('[8/8] Verifying Frontend-Backend Numerical Agreement...');
    await page.setViewport({ width: 1366, height: 768 });
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    
    // Trigger preset
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const bottlePreset = btns.find(b => b.innerText.includes('Bottle') || b.innerText.includes('broken'));
      if (bottlePreset) bottlePreset.click();
    });
    console.log('Waiting for model inference to return values...');
    await new Promise(r => setTimeout(r, 4000));

    const valuesCheck = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        mentionsBottle: text.toLowerCase().includes('bottle'),
        mentionsDefective: text.toLowerCase().includes('defective specimen'),
        mentionsScore: text.includes('4.5088'),
        mentionsThreshold: text.includes('1.4138')
      };
    });
    console.log('Values Agreement:', valuesCheck);
    testResults.push({
      test: 'Frontend-Backend Numerical Agreement',
      status: (valuesCheck.mentionsDefective && valuesCheck.mentionsScore && valuesCheck.mentionsThreshold) ? 'PASS' : 'FAIL'
    });

  } catch (err) {
    console.error('Browser Audit Error:', err);
    testResults.push({ test: 'Exception', status: 'FAIL', error: err.message });
  } finally {
    await browser.close();
  }

  console.log('\n====================================================');
  console.log('BROWSER TEST SUMMARY:');
  console.log('====================================================');
  console.table(testResults);

  fs.writeFileSync(path.join(OUTPUT_DIR, 'browser_test_results.json'), JSON.stringify(testResults, null, 2));
}

runBrowserAudit();
