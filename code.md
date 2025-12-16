# Análisis de Código - .

**Fecha de generación:** 2025-12-16 21:41:01

**Directorio analizado:** `.`

**Total de archivos procesados:** 36

---

### security_report.html

**Ruta:** `security_report.html`

```html
0001 |  <!-- adapters/output/templates/report.html -->
0002 | <!DOCTYPE html>
0003 | <html lang="es">
0004 | <head>
0005 |     <meta charset="UTF-8">
0006 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0007 |     <title>🛡️ Security Analysis Platform v3.0 - Report</title>
0008 | <!-- adapters/output/templates/styles.html -->
0009 | <style>
0010 | /* === RESET & BASE === */
0011 | * {
0012 |     margin: 0;
0013 |     padding: 0;
0014 |     box-sizing: border-box;
0015 | }
0016 | 
0017 | body {
0018 |     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
0019 |     line-height: 1.6;
0020 |     color: #1f2937;
0021 |     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
0022 |     min-height: 100vh;
0023 | }
0024 | 
0025 | /* === LAYOUT === */
0026 | .container {
0027 |     max-width: 1200px;
0028 |     margin: 20px auto;
0029 |     background: white;
0030 |     border-radius: 16px;
0031 |     box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
0032 |     overflow: hidden;
0033 | }
0034 | 
0035 | /* === HEADER === */
0036 | .header {
0037 |     background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
0038 |     color: white;
0039 |     padding: 2rem;
0040 |     position: relative;
0041 | }
0042 | 
0043 | .header::before {
0044 |     content: '';
0045 |     position: absolute;
0046 |     top: 0;
0047 |     left: 0;
0048 |     right: 0;
0049 |     bottom: 0;
0050 |     background: url('image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
0051 |     opacity: 0.3;
0052 | }
0053 | 
0054 | .header-content {
0055 |     position: relative;
0056 |     z-index: 1;
0057 |     text-align: center;
0058 | }
0059 | 
0060 | .header h1 {
0061 |     font-size: 2.5rem;
0062 |     font-weight: 700;
0063 |     margin-bottom: 1rem;
0064 |     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
0065 | }
0066 | 
0067 | .header-grid {
0068 |     display: grid;
0069 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0070 |     gap: 1rem;
0071 |     margin-top: 1.5rem;
0072 | }
0073 | 
0074 | .header-item {
0075 |     background: rgba(255, 255, 255, 0.15);
0076 |     padding: 1rem;
0077 |     border-radius: 12px;
0078 |     backdrop-filter: blur(10px);
0079 |     border: 1px solid rgba(255, 255, 255, 0.2);
0080 | }
0081 | 
0082 | .header-label {
0083 |     font-size: 0.875rem;
0084 |     opacity: 0.9;
0085 |     margin-bottom: 0.25rem;
0086 | }
0087 | 
0088 | .header-value {
0089 |     font-size: 1.25rem;
0090 |     font-weight: 600;
0091 | }
0092 | 
0093 | /* === CONTENT === */
0094 | .content {
0095 |     padding: 2rem;
0096 | }
0097 | 
0098 | .section {
0099 |     margin-bottom: 3rem;
0100 | }
0101 | 
0102 | .section-title {
0103 |     font-size: 1.875rem;
0104 |     font-weight: 700;
0105 |     color: #1f2937;
0106 |     margin-bottom: 1.5rem;
0107 |     padding-bottom: 0.75rem;
0108 |     border-bottom: 3px solid #4f46e5;
0109 |     position: relative;
0110 | }
0111 | 
0112 | .section-title::after {
0113 |     content: '';
0114 |     position: absolute;
0115 |     bottom: -3px;
0116 |     left: 0;
0117 |     width: 60px;
0118 |     height: 3px;
0119 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0120 | }
0121 | 
0122 | /* === METRICS === */
0123 | .metrics-grid {
0124 |     display: grid;
0125 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0126 |     gap: 1.5rem;
0127 |     margin-bottom: 2rem;
0128 | }
0129 | 
0130 | .metric-card {
0131 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0132 |     border-radius: 16px;
0133 |     padding: 1.5rem;
0134 |     text-align: center;
0135 |     transition: transform 0.3s ease, box-shadow 0.3s ease;
0136 |     position: relative;
0137 |     overflow: hidden;
0138 | }
0139 | 
0140 | .metric-card::before {
0141 |     content: '';
0142 |     position: absolute;
0143 |     top: 0;
0144 |     left: 0;
0145 |     right: 0;
0146 |     height: 4px;
0147 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0148 | }
0149 | 
0150 | .metric-card:hover {
0151 |     transform: translateY(-4px);
0152 |     box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
0153 | }
0154 | 
0155 | .metric-icon {
0156 |     font-size: 2rem;
0157 |     margin-bottom: 0.5rem;
0158 | }
0159 | 
0160 | .metric-value {
0161 |     font-size: 2.5rem;
0162 |     font-weight: 700;
0163 |     margin-bottom: 0.5rem;
0164 |     background: linear-gradient(135deg, #4f46e5, #7c3aed);
0165 |     -webkit-background-clip: text;
0166 |     -webkit-text-fill-color: transparent;
0167 |     background-clip: text;
0168 | }
0169 | 
0170 | .metric-label {
0171 |     color: #64748b;
0172 |     font-size: 0.875rem;
0173 |     font-weight: 500;
0174 |     text-transform: uppercase;
0175 |     letter-spacing: 0.05em;
0176 | }
0177 | 
0178 | /* === VULNERABILITIES === */
0179 | .vulnerabilities-list {
0180 |     display: grid;
0181 |     gap: 1.5rem;
0182 | }
0183 | 
0184 | .vulnerability-card {
0185 |     background: white;
0186 |     border: 1px solid #e5e7eb;
0187 |     border-radius: 16px;
0188 |     overflow: hidden;
0189 |     transition: all 0.3s ease;
0190 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0191 | }
0192 | 
0193 | .vulnerability-card:hover {
0194 |     box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
0195 |     transform: translateY(-2px);
0196 | }
0197 | 
0198 | .vulnerability-card.critical {
0199 |     border-left: 6px solid #dc2626;
0200 | }
0201 | 
0202 | .vulnerability-card.high {
0203 |     border-left: 6px solid #ea580c;
0204 | }
0205 | 
0206 | .vulnerability-card.medium {
0207 |     border-left: 6px solid #d97706;
0208 | }
0209 | 
0210 | .vulnerability-card.low {
0211 |     border-left: 6px solid #16a34a;
0212 | }
0213 | 
0214 | .vulnerability-card.info {
0215 |     border-left: 6px solid #0ea5e9;
0216 | }
0217 | 
0218 | .vuln-header {
0219 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0220 |     padding: 1.5rem;
0221 |     border-bottom: 1px solid #e5e7eb;
0222 |     display: flex;
0223 |     justify-content: space-between;
0224 |     align-items: flex-start;
0225 |     gap: 1rem;
0226 | }
0227 | 
0228 | .vuln-title {
0229 |     font-size: 1.25rem;
0230 |     font-weight: 600;
0231 |     color: #1f2937;
0232 |     flex: 1;
0233 | }
0234 | 
0235 | .vuln-badges {
0236 |     display: flex;
0237 |     gap: 0.5rem;
0238 |     flex-shrink: 0;
0239 | }
0240 | 
0241 | .badge {
0242 |     padding: 0.25rem 0.75rem;
0243 |     border-radius: 12px;
0244 |     font-size: 0.75rem;
0245 |     font-weight: 600;
0246 |     text-transform: uppercase;
0247 |     letter-spacing: 0.05em;
0248 | }
0249 | 
0250 | .badge.severity-critical {
0251 |     background: #dc2626;
0252 |     color: white;
0253 | }
0254 | 
0255 | .badge.severity-high {
0256 |     background: #ea580c;
0257 |     color: white;
0258 | }
0259 | 
0260 | .badge.severity-medium {
0261 |     background: #d97706;
0262 |     color: white;
0263 | }
0264 | 
0265 | .badge.severity-low {
0266 |     background: #16a34a;
0267 |     color: white;
0268 | }
0269 | 
0270 | .badge.severity-info {
0271 |     background: #0ea5e9;
0272 |     color: white;
0273 | }
0274 | 
0275 | .badge.type-badge {
0276 |     background: #6b7280;
0277 |     color: white;
0278 | }
0279 | 
0280 | .vuln-body {
0281 |     padding: 1.5rem;
0282 | }
0283 | 
0284 | .vuln-meta {
0285 |     display: grid;
0286 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0287 |     gap: 1rem;
0288 |     margin-bottom: 1.5rem;
0289 | }
0290 | 
0291 | .meta-item {
0292 |     background: #f8fafc;
0293 |     padding: 0.75rem;
0294 |     border-radius: 8px;
0295 |     border: 1px solid #e5e7eb;
0296 | }
0297 | 
0298 | .meta-label {
0299 |     font-size: 0.75rem;
0300 |     font-weight: 600;
0301 |     color: #6b7280;
0302 |     text-transform: uppercase;
0303 |     letter-spacing: 0.05em;
0304 |     margin-bottom: 0.25rem;
0305 | }
0306 | 
0307 | .meta-value {
0308 |     font-weight: 500;
0309 |     color: #1f2937;
0310 | }
0311 | 
0312 | .meta-value a {
0313 |     color: #4f46e5;
0314 |     text-decoration: none;
0315 | }
0316 | 
0317 | .meta-value a:hover {
0318 |     text-decoration: underline;
0319 | }
0320 | 
0321 | .vuln-description,
0322 | .vuln-code,
0323 | .vuln-remediation {
0324 |     margin-bottom: 1.5rem;
0325 | }
0326 | 
0327 | .vuln-description h4,
0328 | .vuln-code h4,
0329 | .vuln-remediation h4 {
0330 |     font-size: 1rem;
0331 |     font-weight: 600;
0332 |     color: #374151;
0333 |     margin-bottom: 0.75rem;
0334 |     display: flex;
0335 |     align-items: center;
0336 |     gap: 0.5rem;
0337 | }
0338 | 
0339 | .code-block {
0340 |     background: #0f172a;
0341 |     color: #e2e8f0;
0342 |     padding: 1rem;
0343 |     border-radius: 8px;
0344 |     font-family: 'JetBrains Mono', 'Fira Code', Monaco, monospace;
0345 |     font-size: 0.875rem;
0346 |     overflow-x: auto;
0347 |     line-height: 1.5;
0348 |     border: 1px solid #334155;
0349 | }
0350 | 
0351 | .advice-content {
0352 |     background: #dbeafe;
0353 |     padding: 1rem;
0354 |     border-radius: 8px;
0355 |     border-left: 4px solid #3b82f6;
0356 |     color: #1e40af;
0357 | }
0358 | 
0359 | /* === NO VULNERABILITIES === */
0360 | .no-vulnerabilities {
0361 |     text-align: center;
0362 |     padding: 4rem 2rem;
0363 |     background: linear-gradient(135deg, #22c55e, #16a34a);
0364 |     color: white;
0365 |     border-radius: 16px;
0366 | }
0367 | 
0368 | .no-vulns-icon {
0369 |     font-size: 4rem;
0370 |     margin-bottom: 1rem;
0371 | }
0372 | 
0373 | .no-vulnerabilities h2 {
0374 |     font-size: 2rem;
0375 |     margin-bottom: 1rem;
0376 | }
0377 | 
0378 | /* === REMEDIATION === */
0379 | .remediation-summary {
0380 |     background: #f0f9ff;
0381 |     padding: 1rem;
0382 |     border-radius: 8px;
0383 |     border-left: 4px solid #0ea5e9;
0384 |     margin-bottom: 2rem;
0385 | }
0386 | 
0387 | .remediation-plans {
0388 |     display: grid;
0389 |     gap: 2rem;
0390 | }
0391 | 
0392 | .remediation-card {
0393 |     background: white;
0394 |     border: 1px solid #e5e7eb;
0395 |     border-radius: 12px;
0396 |     padding: 1.5rem;
0397 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0398 | }
0399 | 
0400 | .plan-header {
0401 |     display: flex;
0402 |     justify-content: space-between;
0403 |     align-items: center;
0404 |     margin-bottom: 1rem;
0405 | }
0406 | 
0407 | .plan-header h3 {
0408 |     font-size: 1.25rem;
0409 |     font-weight: 600;
0410 |     color: #1f2937;
0411 | }
0412 | 
0413 | .priority-badge {
0414 |     padding: 0.25rem 0.75rem;
0415 |     border-radius: 20px;
0416 |     font-size: 0.75rem;
0417 |     font-weight: 600;
0418 |     text-transform: uppercase;
0419 | }
0420 | 
0421 | .priority-badge.priority-immediate {
0422 |     background: #dc2626;
0423 |     color: white;
0424 | }
0425 | 
0426 | .priority-badge.priority-high {
0427 |     background: #ea580c;
0428 |     color: white;
0429 | }
0430 | 
0431 | .priority-badge.priority-medium {
0432 |     background: #d97706;
0433 |     color: white;
0434 | }
0435 | 
0436 | .priority-badge.priority-low {
0437 |     background: #16a34a;
0438 |     color: white;
0439 | }
0440 | 
0441 | .plan-meta {
0442 |     display: flex;
0443 |     gap: 1rem;
0444 |     margin-bottom: 1.5rem;
0445 |     flex-wrap: wrap;
0446 | }
0447 | 
0448 | .plan-stat {
0449 |     background: #f3f4f6;
0450 |     padding: 0.5rem 1rem;
0451 |     border-radius: 6px;
0452 |     font-size: 0.875rem;
0453 |     font-weight: 500;
0454 | }
0455 | 
0456 | .plan-steps {
0457 |     margin-bottom: 1.5rem;
0458 | }
0459 | 
0460 | .plan-steps h4 {
0461 |     font-size: 1rem;
0462 |     font-weight: 600;
0463 |     margin-bottom: 1rem;
0464 |     color: #374151;
0465 | }
0466 | 
0467 | .plan-steps ol {
0468 |     list-style: none;
0469 |     counter-reset: step-counter;
0470 | }
0471 | 
0472 | .remediation-step {
0473 |     counter-increment: step-counter;
0474 |     margin-bottom: 1rem;
0475 |     padding: 1rem;
0476 |     background: #f8fafc;
0477 |     border-radius: 8px;
0478 |     border-left: 4px solid #4f46e5;
0479 |     position: relative;
0480 |     padding-left: 3rem;
0481 | }
0482 | 
0483 | .remediation-step::before {
0484 |     content: counter(step-counter);
0485 |     position: absolute;
0486 |     left: 1rem;
0487 |     top: 1rem;
0488 |     background: #4f46e5;
0489 |     color: white;
0490 |     width: 1.5rem;
0491 |     height: 1.5rem;
0492 |     border-radius: 50%;
0493 |     display: flex;
0494 |     align-items: center;
0495 |     justify-content: center;
0496 |     font-weight: 600;
0497 |     font-size: 0.875rem;
0498 | }
0499 | 
0500 | .step-header {
0501 |     display: flex;
0502 |     justify-content: space-between;
0503 |     align-items: flex-start;
0504 |     margin-bottom: 0.5rem;
0505 | }
0506 | 
0507 | .step-meta {
0508 |     font-size: 0.75rem;
0509 |     color: #6b7280;
0510 |     background: #e5e7eb;
0511 |     padding: 0.25rem 0.5rem;
0512 |     border-radius: 4px;
0513 | }
0514 | 
0515 | .step-description {
0516 |     color: #4b5563;
0517 |     margin-bottom: 0.75rem;
0518 | }
0519 | 
0520 | .step-code {
0521 |     background: #f3f4f6;
0522 |     color: #374151;
0523 |     padding: 0.75rem;
0524 |     border-radius: 6px;
0525 |     font-family: 'JetBrains Mono', monospace;
0526 |     font-size: 0.8rem;
0527 |     border: 1px solid #d1d5db;
0528 | }
0529 | 
0530 | .risk-warning {
0531 |     background: #fef2f2;
0532 |     padding: 1rem;
0533 |     border-radius: 8px;
0534 |     border-left: 4px solid #ef4444;
0535 |     color: #991b1b;
0536 | }
0537 | 
0538 | .risk-warning h5 {
0539 |     font-weight: 600;
0540 |     margin-bottom: 0.5rem;
0541 | }
0542 | 
0543 | /* === TECHNICAL DETAILS === */
0544 | .technical-details {
0545 |     background: #f8fafc;
0546 |     border: 1px solid #e5e7eb;
0547 |     border-radius: 12px;
0548 |     overflow: hidden;
0549 | }
0550 | 
0551 | .details-toggle {
0552 |     background: #f1f5f9;
0553 |     padding: 1rem 1.5rem;
0554 |     cursor: pointer;
0555 |     font-weight: 600;
0556 |     color: #374151;
0557 |     display: flex;
0558 |     align-items: center;
0559 |     gap: 0.5rem;
0560 |     border: none;
0561 |     width: 100%;
0562 |     text-align: left;
0563 |     transition: background 0.2s;
0564 | }
0565 | 
0566 | .details-toggle:hover {
0567 |     background: #e2e8f0;
0568 | }
0569 | 
0570 | .details-toggle::after {
0571 |     content: '▶';
0572 |     margin-left: auto;
0573 |     transition: transform 0.3s;
0574 | }
0575 | 
0576 | .technical-details[open] .details-toggle::after {
0577 |     transform: rotate(90deg);
0578 | }
0579 | 
0580 | .details-content {
0581 |     padding: 1.5rem;
0582 | }
0583 | 
0584 | .tech-grid {
0585 |     display: grid;
0586 |     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
0587 |     gap: 1.5rem;
0588 |     margin-bottom: 1.5rem;
0589 | }
0590 | 
0591 | .tech-item h4 {
0592 |     font-weight: 600;
0593 |     color: #374151;
0594 |     margin-bottom: 0.75rem;
0595 | }
0596 | 
0597 | .tech-item ul {
0598 |     list-style: none;
0599 |     padding-left: 0;
0600 | }
0601 | 
0602 | .tech-item li {
0603 |     padding: 0.25rem 0;
0604 |     color: #6b7280;
0605 | }
0606 | 
0607 | .analysis-summary {
0608 |     background: white;
0609 |     padding: 1rem;
0610 |     border-radius: 8px;
0611 |     border: 1px solid #e5e7eb;
0612 | }
0613 | 
0614 | .analysis-summary h4 {
0615 |     font-weight: 600;
0616 |     color: #374151;
0617 |     margin-bottom: 0.75rem;
0618 | }
0619 | 
0620 | .analysis-summary pre {
0621 |     background: #f8fafc;
0622 |     padding: 1rem;
0623 |     border-radius: 6px;
0624 |     font-size: 0.875rem;
0625 |     color: #4b5563;
0626 |     white-space: pre-wrap;
0627 |     word-wrap: break-word;
0628 | }
0629 | 
0630 | /* === FOOTER === */
0631 | .footer {
0632 |     background: #1f2937;
0633 |     color: white;
0634 |     padding: 2rem;
0635 |     text-align: center;
0636 | }
0637 | 
0638 | .footer-content p {
0639 |     margin-bottom: 0.5rem;
0640 | }
0641 | 
0642 | /* === RESPONSIVE DESIGN === */
0643 | @media (max-width: 768px) {
0644 |     .container {
0645 |         margin: 10px;
0646 |         border-radius: 8px;
0647 |     }
0648 |     
0649 |     .header {
0650 |         padding: 1.5rem;
0651 |     }
0652 |     
0653 |     .header h1 {
0654 |         font-size: 2rem;
0655 |     }
0656 |     
0657 |     .header-grid {
0658 |         grid-template-columns: 1fr;
0659 |     }
0660 |     
0661 |     .content {
0662 |         padding: 1.5rem;
0663 |     }
0664 |     
0665 |     .metrics-grid {
0666 |         grid-template-columns: 1fr;
0667 |     }
0668 |     
0669 |     .vuln-header {
0670 |         flex-direction: column;
0671 |         align-items: flex-start;
0672 |     }
0673 |     
0674 |     .vuln-meta {
0675 |         grid-template-columns: 1fr;
0676 |     }
0677 |     
0678 |     .plan-header {
0679 |         flex-direction: column;
0680 |         align-items: flex-start;
0681 |         gap: 0.5rem;
0682 |     }
0683 |     
0684 |     .plan-meta {
0685 |         flex-direction: column;
0686 |     }
0687 |     
0688 |     .step-header {
0689 |         flex-direction: column;
0690 |         align-items: flex-start;
0691 |     }
0692 | }
0693 | 
0694 | /* === ANIMATIONS === */
0695 | @keyframes fadeIn {
0696 |     from {
0697 |         opacity: 0;
0698 |         transform: translateY(20px);
0699 |     }
0700 |     to {
0701 |         opacity: 1;
0702 |         transform: translateY(0);
0703 |     }
0704 | }
0705 | 
0706 | .section {
0707 |     animation: fadeIn 0.6s ease-out;
0708 | }
0709 | 
0710 | /* === PRINT STYLES === */
0711 | @media print {
0712 |     body {
0713 |         background: white;
0714 |     }
0715 |     
0716 |     .container {
0717 |         box-shadow: none;
0718 |         margin: 0;
0719 |     }
0720 |     
0721 |     .header {
0722 |         background: #4f46e5 !important;
0723 |         -webkit-print-color-adjust: exact;
0724 |         color-adjust: exact;
0725 |     }
0726 |     
0727 |     .technical-details {
0728 |         border: 1px solid #ccc;
0729 |     }
0730 |     
0731 |     .details-content {
0732 |         display: block !important;
0733 |     }
0734 |     
0735 |     .details-toggle {
0736 |         display: none;
0737 |     }
0738 |     
0739 |     .vulnerability-card {
0740 |         break-inside: avoid;
0741 |         page-break-inside: avoid;
0742 |         margin-bottom: 1rem;
0743 |     }
0744 | }
0745 | </style></head>
0746 | <body>
0747 |     <div class="container">
0748 |         <!-- Header -->
0749 |         <header class="header">
0750 |             <div class="header-content">
0751 |                 <h1>🛡️ Security Analysis Report</h1>
0752 |                 <div class="header-grid">
0753 |                     <div class="header-item">
0754 |                         <div class="header-label">📁 File</div>
0755 |                         <div class="header-value">abap_sample.json</div>
0756 |                     </div>
0757 |                     <div class="header-item">
0758 |                         <div class="header-label">📊 Total Vulnerabilities</div>
0759 |                         <div class="header-value">2</div>
0760 |                     </div>
0761 |                     <div class="header-item">
0762 |                         <div class="header-label">⚡ High Priority</div>
0763 |                         <div class="header-value">2</div>
0764 |                     </div>
0765 |                     <div class="header-item">
0766 |                         <div class="header-label">🎯 Risk Score</div>
0767 |                         <div class="header-value">7.0/10</div>
0768 |                     </div>
0769 |                 </div>
0770 |             </div>
0771 |         </header>
0772 | 
0773 |         <main class="content">
0774 |             <!-- Executive Summary -->
0775 |             <section class="section">
0776 |                 <h2 class="section-title">📈 Executive Summary</h2>
0777 |                 
0778 |                 <div class="metrics-grid">
0779 |                     <div class="metric-card high">
0780 |                         <div class="metric-icon">⚡</div>
0781 |                         <div class="metric-value">2</div>
0782 |                         <div class="metric-label">ALTA</div>
0783 |                     </div>
0784 |                 </div>
0785 | 
0786 |                 <div class="summary-info">
0787 |                     <p><strong>Analysis completed in 1m 9.3s</strong></p>
0788 |                     <p>🤖 AI-powered triage analyzed 2 vulnerabilities</p>
0789 |                 </div>
0790 |             </section>
0791 | 
0792 |             <!-- Vulnerabilities -->
0793 |             <section class="section">
0794 |                 <h2 class="section-title">🚨 Security Vulnerabilities</h2>
0795 |                 
0796 |                 <div class="vulnerabilities-list">
0797 |                     <div class="vulnerability-card high">
0798 |                         <div class="vuln-header">
0799 |                             <h3 class="vuln-title">
0800 |                                 ⚡ 1. Directory Traversal
0801 |                             </h3>
0802 |                             <div class="vuln-badges">
0803 |                                 <span class="badge severity-high">
0804 |                                     ALTA
0805 |                                 </span>
0806 |                                 <span class="badge type-badge">Directory Traversal</span>
0807 |                             </div>
0808 |                         </div>
0809 |                         
0810 |                         <div class="vuln-body">
0811 |                             <div class="vuln-meta">
0812 |                                 <div class="meta-item">
0813 |                                     <span class="meta-label">📍 Location</span>
0814 |                                     <span class="meta-value">test-code\YAL0029.TXT:679</span>
0815 |                                 </div>
0816 |                                 <div class="meta-item">
0817 |                                     <span class="meta-label">🆔 ID</span>
0818 |                                     <span class="meta-value">abap-directory-traversal-001</span>
0819 |                                 </div>
0820 |                                 <div class="meta-item">
0821 |                                     <span class="meta-label">🔗 CWE</span>
0822 |                                     <span class="meta-value">
0823 |                                         <a href="https://cwe.mitre.org/data/definitions/22.html" target="_blank">
0824 |                                             CWE-22
0825 |                                         </a>
0826 |                                     </span>
0827 |                                 </div>
0828 |                             </div>
0829 |                             
0830 |                             <div class="vuln-description">
0831 |                                 <h4>📝 Description</h4>
0832 |                                 <p>File operation with unvalidated path may allow directory traversal</p>
0833 |                             </div>
0834 |                             
0835 |                             <div class="vuln-code">
0836 |                                 <h4>💻 Code Context</h4>
0837 |                                 <pre class="code-block">  2 |      ELSEIF rb_ser EQ abap_true.
0838 |   3 |        CONCATENATE p_path p_nfich INTO ld_path SEPARATED BY &#39;/&#39;.
0839 |   4 | &gt;&gt;     OPEN DATASET ld_path FOR OUTPUT IN TEXT MODE ENCODING UTF-8.
0840 |   5 |        IF sy-subrc EQ 0.
0841 |   6 |          lf_fich_open = abap_true.
0842 |   7 |        ELSE.</pre>
0843 |                             </div>
0844 |                             
0845 |                             <div class="vuln-remediation">
0846 |                                 <h4>💡 Remediation Advice</h4>
0847 |                                 <div class="advice-content">
0848 |     Prevent directory traversal:
0849 |     - Validate file paths using FILE_VALIDATE_NAME
0850 |     - Use absolute paths with proper validation
0851 |     - Implement allowlist for accessible directories
0852 |     - Check sy-subrc after FILE_VALIDATE_NAME call
0853 |     
0854 |     Example:
0855 |     CALL FUNCTION &#39;FILE_VALIDATE_NAME&#39;
0856 |       EXPORTING logical_filename = file_path
0857 |       EXCEPTIONS OTHERS = 1.
0858 |     IF sy-subrc = 0.
0859 |       &#34; Safe to use file_path
0860 |     ENDIF.
0861 |     </div>
0862 |                             </div>
0863 |                         </div>
0864 |                     </div>
0865 |                     <div class="vulnerability-card high">
0866 |                         <div class="vuln-header">
0867 |                             <h3 class="vuln-title">
0868 |                                 ⚡ 2. Directory Traversal
0869 |                             </h3>
0870 |                             <div class="vuln-badges">
0871 |                                 <span class="badge severity-high">
0872 |                                     ALTA
0873 |                                 </span>
0874 |                                 <span class="badge type-badge">Directory Traversal</span>
0875 |                             </div>
0876 |                         </div>
0877 |                         
0878 |                         <div class="vuln-body">
0879 |                             <div class="vuln-meta">
0880 |                                 <div class="meta-item">
0881 |                                     <span class="meta-label">📍 Location</span>
0882 |                                     <span class="meta-value">test-code\YAL0029.TXT:780</span>
0883 |                                 </div>
0884 |                                 <div class="meta-item">
0885 |                                     <span class="meta-label">🆔 ID</span>
0886 |                                     <span class="meta-value">abap-directory-traversal-001</span>
0887 |                                 </div>
0888 |                                 <div class="meta-item">
0889 |                                     <span class="meta-label">🔗 CWE</span>
0890 |                                     <span class="meta-value">
0891 |                                         <a href="https://cwe.mitre.org/data/definitions/22.html" target="_blank">
0892 |                                             CWE-22
0893 |                                         </a>
0894 |                                     </span>
0895 |                                 </div>
0896 |                             </div>
0897 |                             
0898 |                             <div class="vuln-description">
0899 |                                 <h4>📝 Description</h4>
0900 |                                 <p>File operation with unvalidated path may allow directory traversal</p>
0901 |                             </div>
0902 |                             
0903 |                             <div class="vuln-code">
0904 |                                 <h4>💻 Code Context</h4>
0905 |                                 <pre class="code-block">  2 |          IF sy-subrc EQ 0.
0906 |   3 |    *       Si la compresion ha ido bien, se borra el fichero original
0907 |   4 | &gt;&gt;         DELETE DATASET ld_path.
0908 |   5 |          ENDIF.
0909 |   6 |        ENDIF.
0910 |   7 |      ENDIF.</pre>
0911 |                             </div>
0912 |                             
0913 |                             <div class="vuln-remediation">
0914 |                                 <h4>💡 Remediation Advice</h4>
0915 |                                 <div class="advice-content">
0916 |     Prevent directory traversal:
0917 |     - Validate file paths using FILE_VALIDATE_NAME
0918 |     - Use absolute paths with proper validation
0919 |     - Implement allowlist for accessible directories
0920 |     - Check sy-subrc after FILE_VALIDATE_NAME call
0921 |     
0922 |     Example:
0923 |     CALL FUNCTION &#39;FILE_VALIDATE_NAME&#39;
0924 |       EXPORTING logical_filename = file_path
0925 |       EXCEPTIONS OTHERS = 1.
0926 |     IF sy-subrc = 0.
0927 |       &#34; Safe to use file_path
0928 |     ENDIF.
0929 |     </div>
0930 |                             </div>
0931 |                         </div>
0932 |                     </div>
0933 |                 </div>
0934 |             </section>
0935 | 
0936 |             <!-- Remediation Plans -->
0937 |             <section class="section">
0938 |                 <h2 class="section-title">🛠️ Remediation Plans</h2>
0939 |                 
0940 |                 <div class="remediation-summary">
0941 |                     <p>2 actionable remediation plans generated, prioritized by risk and complexity.</p>
0942 |                 </div>
0943 |                 
0944 |                 <div class="remediation-plans">
0945 |                     <div class="remediation-card">
0946 |                         <div class="plan-header">
0947 |                             <h3>🔧 Directory Traversal</h3>
0948 |                             <span class="priority-badge priority-high">
0949 |                                 HIGH
0950 |                             </span>
0951 |                         </div>
0952 |                         
0953 | 							<div class="plan-meta">
0954 | 								<span class="plan-stat">📊 Complexity: 5.0/10</span>
0955 | 								<span class="plan-stat">📋 4 steps</span>
0956 | 							</div>
0957 | 
0958 |                         <div class="plan-steps">
0959 |                             <h4>Implementation Steps:</h4>
0960 |                             <ol>
0961 |                                 <li class="remediation-step">
0962 |                                     <div class="step-header">
0963 |                                         <strong>Manual Security Review</strong>
0964 |                                         <span class="step-meta">30min • medium</span>
0965 |                                     </div>
0966 |                                     <div class="step-description">Review Directory Traversal in test-code\YAL0029.TXT</div>
0967 |                                 </li>
0968 |                                 <li class="remediation-step">
0969 |                                     <div class="step-header">
0970 |                                         <strong>Research Best Practices</strong>
0971 |                                         <span class="step-meta">15min • easy</span>
0972 |                                     </div>
0973 |                                     <div class="step-description">Research security best practices for Directory Traversal</div>
0974 |                                 </li>
0975 |                                 <li class="remediation-step">
0976 |                                     <div class="step-header">
0977 |                                         <strong>Implement Fix</strong>
0978 |                                         <span class="step-meta">120min • hard</span>
0979 |                                     </div>
0980 |                                     <div class="step-description">Apply appropriate security fix</div>
0981 |                                 </li>
0982 |                                 <li class="remediation-step">
0983 |                                     <div class="step-header">
0984 |                                         <strong>Validate Fix</strong>
0985 |                                         <span class="step-meta">30min • medium</span>
0986 |                                     </div>
0987 |                                     <div class="step-description">Test that vulnerability is fixed</div>
0988 |                                 </li>
0989 |                             </ol>
0990 |                         </div>
0991 |                         
0992 |                         <div class="risk-warning">
0993 |                             <h5>⚠️ Risk if not addressed:</h5>
0994 |                             <p>Security risk: Directory Traversal</p>
0995 |                         </div>
0996 |                     </div>
0997 |                     <div class="remediation-card">
0998 |                         <div class="plan-header">
0999 |                             <h3>🔧 Directory Traversal</h3>
1000 |                             <span class="priority-badge priority-high">
1001 |                                 HIGH
1002 |                             </span>
1003 |                         </div>
1004 |                         
1005 | 							<div class="plan-meta">
1006 | 								<span class="plan-stat">📊 Complexity: 5.0/10</span>
1007 | 								<span class="plan-stat">📋 4 steps</span>
1008 | 							</div>
1009 | 
1010 |                         <div class="plan-steps">
1011 |                             <h4>Implementation Steps:</h4>
1012 |                             <ol>
1013 |                                 <li class="remediation-step">
1014 |                                     <div class="step-header">
1015 |                                         <strong>Manual Security Review</strong>
1016 |                                         <span class="step-meta">30min • medium</span>
1017 |                                     </div>
1018 |                                     <div class="step-description">Review Directory Traversal in test-code\YAL0029.TXT</div>
1019 |                                 </li>
1020 |                                 <li class="remediation-step">
1021 |                                     <div class="step-header">
1022 |                                         <strong>Research Best Practices</strong>
1023 |                                         <span class="step-meta">15min • easy</span>
1024 |                                     </div>
1025 |                                     <div class="step-description">Research security best practices for Directory Traversal</div>
1026 |                                 </li>
1027 |                                 <li class="remediation-step">
1028 |                                     <div class="step-header">
1029 |                                         <strong>Implement Fix</strong>
1030 |                                         <span class="step-meta">120min • hard</span>
1031 |                                     </div>
1032 |                                     <div class="step-description">Apply appropriate security fix</div>
1033 |                                 </li>
1034 |                                 <li class="remediation-step">
1035 |                                     <div class="step-header">
1036 |                                         <strong>Validate Fix</strong>
1037 |                                         <span class="step-meta">30min • medium</span>
1038 |                                     </div>
1039 |                                     <div class="step-description">Test that vulnerability is fixed</div>
1040 |                                 </li>
1041 |                             </ol>
1042 |                         </div>
1043 |                         
1044 |                         <div class="risk-warning">
1045 |                             <h5>⚠️ Risk if not addressed:</h5>
1046 |                             <p>Security risk: Directory Traversal</p>
1047 |                         </div>
1048 |                     </div>
1049 |                 </div>
1050 |             </section>
1051 | 
1052 |             <!-- Technical Details -->
1053 |             <section class="section">
1054 |                 <details class="technical-details">
1055 |                     <summary class="details-toggle">🔍 Technical Analysis Details</summary>
1056 |                     <div class="details-content">
1057 |                         <div class="tech-grid">
1058 |                             <div class="tech-item">
1059 |                                 <h4>📊 Analysis Statistics</h4>
1060 |                                 <ul>
1061 |                                     <li>Processing time: 1m 9.3s</li>
1062 |                                     <li>File size: 3.67 KB</li>
1063 |                                     <li>Language: Auto-detected</li>
1064 |                                     <li>Chunking: Disabled</li>
1065 |                                 </ul>
1066 |                             </div>
1067 |                             
1068 |                             <div class="tech-item">
1069 |                                 <h4>🤖 LLM Triage Results</h4>
1070 |                                 <ul>
1071 |                                     <li>Confirmed vulnerabilities: 2</li>
1072 |                                     <li>False positives: 0</li>
1073 |                                     <li>Need manual review: 0</li>
1074 |                                     <li>Analysis time: 0.00s</li>
1075 |                                 </ul>
1076 |                             </div>
1077 |                         </div>
1078 |                         
1079 |                         <div class="analysis-summary">
1080 |                             <h4>📋 Analysis Summary</h4>
1081 |                             <pre>Conservative fallback due to LLM error: Could not extract valid JSON from response</pre>
1082 |                         </div>
1083 |                     </div>
1084 |                 </details>
1085 |             </section>
1086 |         </main>
1087 | 
1088 |         <!-- Footer -->
1089 |         <footer class="footer">
1090 |             <div class="footer-content">
1091 |                 <p>Generated by <strong>Security Analysis Platform v3.0</strong> on 2025-12-16 at 21:37:58</p>
1092 |                 <p>For questions about this report, contact your security team.</p>
1093 |             </div>
1094 |         </footer>
1095 |     </div>
1096 | 
1097 | <!-- adapters/output/templates/scripts.html -->
1098 | <script>
1099 | document.addEventListener('DOMContentLoaded', function() {
1100 |     console.log('🛡️ Security Analysis Report v3.0 loaded');
1101 |     
1102 |     // Enhanced interactivity
1103 |     initializeAnimations();
1104 |     setupCopyFunctionality();
1105 |     setupSearchFunctionality();
1106 |     setupKeyboardNavigation();
1107 |     
1108 |     // Report statistics
1109 |     logReportStatistics();
1110 | });
1111 | 
1112 | function initializeAnimations() {
1113 |     // Intersection Observer for scroll animations
1114 |     const observerOptions = {
1115 |         threshold: 0.1,
1116 |         rootMargin: '0px 0px -50px 0px'
1117 |     };
1118 | 
1119 |     const observer = new IntersectionObserver(function(entries) {
1120 |         entries.forEach(function(entry) {
1121 |             if (entry.isIntersecting) {
1122 |                 entry.target.style.opacity = '1';
1123 |                 entry.target.style.transform = 'translateY(0)';
1124 |             }
1125 |         });
1126 |     }, observerOptions);
1127 | 
1128 |     // Apply to vulnerability cards
1129 |     document.querySelectorAll('.vulnerability-card, .remediation-card').forEach(function(el) {
1130 |         el.style.opacity = '0';
1131 |         el.style.transform = 'translateY(20px)';
1132 |         el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
1133 |         observer.observe(el);
1134 |     });
1135 | }
1136 | 
1137 | function setupCopyFunctionality() {
1138 |     // Add copy buttons to vulnerability IDs and CWE links
1139 |     document.querySelectorAll('.meta-value').forEach(function(element) {
1140 |         const text = element.textContent.trim();
1141 |         
1142 |         if (text.match(/^(VULN-|ABAP-|CWE-)/)) {
1143 |             element.style.cursor = 'pointer';
1144 |             element.title = 'Click to copy ' + text;
1145 |             
1146 |             element.addEventListener('click', function() {
1147 |                 copyToClipboard(text);
1148 |                 showToast('✅ Copied: ' + text);
1149 |             });
1150 |         }
1151 |     });
1152 | }
1153 | 
1154 | function setupSearchFunctionality() {
1155 |     // Create search box
1156 |     const searchBox = document.createElement('div');
1157 |     searchBox.innerHTML = `
1158 |         <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
1159 |             <input type="text" id="vulnerabilitySearch" placeholder="🔍 Search vulnerabilities..." 
1160 |                    style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; width: 250px;">
1161 |         </div>
1162 |     `;
1163 |     document.body.appendChild(searchBox);
1164 |     
1165 |     const searchInput = document.getElementById('vulnerabilitySearch');
1166 |     searchInput.addEventListener('input', function(e) {
1167 |         const query = e.target.value.toLowerCase();
1168 |         filterVulnerabilities(query);
1169 |     });
1170 | }
1171 | 
1172 | function setupKeyboardNavigation() {
1173 |     document.addEventListener('keydown', function(e) {
1174 |         // Ctrl+F or Cmd+F to focus search
1175 |         if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
1176 |             e.preventDefault();
1177 |             const searchInput = document.getElementById('vulnerabilitySearch');
1178 |             if (searchInput) {
1179 |                 searchInput.focus();
1180 |             }
1181 |         }
1182 |         
1183 |         // Escape to clear search
1184 |         if (e.key === 'Escape') {
1185 |             const searchInput = document.getElementById('vulnerabilitySearch');
1186 |             if (searchInput && searchInput === document.activeElement) {
1187 |                 searchInput.value = '';
1188 |                 filterVulnerabilities('');
1189 |                 searchInput.blur();
1190 |             }
1191 |         }
1192 |     });
1193 | }
1194 | 
1195 | function filterVulnerabilities(query) {
1196 |     const cards = document.querySelectorAll('.vulnerability-card');
1197 |     let visibleCount = 0;
1198 |     
1199 |     cards.forEach(function(card) {
1200 |         const text = card.textContent.toLowerCase();
1201 |         const isVisible = query === '' || text.includes(query);
1202 |         
1203 |         card.style.display = isVisible ? 'block' : 'none';
1204 |         if (isVisible) visibleCount++;
1205 |     });
1206 |     
1207 |     // Update search results indicator
1208 |     updateSearchResults(visibleCount, cards.length, query);
1209 | }
1210 | 
1211 | function updateSearchResults(visible, total, query) {
1212 |     let indicator = document.getElementById('searchResults');
1213 |     
1214 |     if (!indicator) {
1215 |         indicator = document.createElement('div');
1216 |         indicator.id = 'searchResults';
1217 |         indicator.style.cssText = `
1218 |             position: fixed;
1219 |             bottom: 20px;
1220 |             right: 20px;
1221 |             background: #4f46e5;
1222 |             color: white;
1223 |             padding: 8px 12px;
1224 |             border-radius: 6px;
1225 |             font-size: 0.875rem;
1226 |             z-index: 1000;
1227 |             transition: opacity 0.3s;
1228 |         `;
1229 |         document.body.appendChild(indicator);
1230 |     }
1231 |     
1232 |     if (query) {
1233 |         indicator.textContent = `Found ${visible} of ${total} vulnerabilities`;
1234 |         indicator.style.opacity = '1';
1235 |     } else {
1236 |         indicator.style.opacity = '0';
1237 |     }
1238 | }
1239 | 
1240 | function copyToClipboard(text) {
1241 |     if (navigator.clipboard) {
1242 |         navigator.clipboard.writeText(text).catch(function() {
1243 |             fallbackCopy(text);
1244 |         });
1245 |     } else {
1246 |         fallbackCopy(text);
1247 |     }
1248 | }
1249 | 
1250 | function fallbackCopy(text) {
1251 |     const textArea = document.createElement('textarea');
1252 |     textArea.value = text;
1253 |     textArea.style.position = 'fixed';
1254 |     textArea.style.left = '-9999px';
1255 |     document.body.appendChild(textArea);
1256 |     textArea.focus();
1257 |     textArea.select();
1258 |     
1259 |     try {
1260 |         document.execCommand('copy');
1261 |     } catch (err) {
1262 |         console.warn('Copy failed:', err);
1263 |     }
1264 |     
1265 |     document.body.removeChild(textArea);
1266 | }
1267 | 
1268 | function showToast(message) {
1269 |     const toast = document.createElement('div');
1270 |     toast.textContent = message;
1271 |     toast.style.cssText = `
1272 |         position: fixed;
1273 |         top: 20px;
1274 |         left: 50%;
1275 |         transform: translateX(-50%);
1276 |         background: #10b981;
1277 |         color: white;
1278 |         padding: 12px 20px;
1279 |         border-radius: 8px;
1280 |         z-index: 9999;
1281 |         animation: slideInDown 0.3s ease-out;
1282 |         font-weight: 500;
1283 |     `;
1284 |     
1285 |     document.body.appendChild(toast);
1286 |     
1287 |     setTimeout(function() {
1288 |         toast.style.animation = 'slideOutUp 0.3s ease-out';
1289 |         setTimeout(function() {
1290 |             document.body.removeChild(toast);
1291 |         }, 300);
1292 |     }, 2000);
1293 | }
1294 | 
1295 | function logReportStatistics() {
1296 |     const stats = {
1297 |         totalVulnerabilities: 2,
1298 |         highPriority: 2,
1299 |         riskScore: 7.0,
1300 |         processingTime: '1m 9.3s',
1301 |         chunking: false,
1302 |         llmAnalysis: true,
1303 |         reportVersion: '3.0'
1304 |     };
1305 |     
1306 |     console.log('📊 Report Statistics:', stats);
1307 |     
1308 |     // Performance metrics
1309 |     console.log('⚡ Performance Metrics:');
1310 |     console.log('  • DOM Ready:', performance.now().toFixed(2) + 'ms');
1311 |     console.log('  • Interactive elements:', document.querySelectorAll('[onclick], [data-action]').length);
1312 |     console.log('  • Vulnerability cards:', document.querySelectorAll('.vulnerability-card').length);
1313 | }
1314 | 
1315 | // CSS animations for toasts
1316 | const additionalStyles = `
1317 | @keyframes slideInDown {
1318 |     from {
1319 |         opacity: 0;
1320 |         transform: translate(-50%, -100%);
1321 |     }
1322 |     to {
1323 |         opacity: 1;
1324 |         transform: translate(-50%, 0);
1325 |     }
1326 | }
1327 | 
1328 | @keyframes slideOutUp {
1329 |     from {
1330 |         opacity: 1;
1331 |         transform: translate(-50%, 0);
1332 |     }
1333 |     to {
1334 |         opacity: 0;
1335 |         transform: translate(-50%, -100%);
1336 |     }
1337 | }
1338 | `;
1339 | 
1340 | const styleSheet = document.createElement('style');
1341 | styleSheet.textContent = additionalStyles;
1342 | document.head.appendChild(styleSheet);
1343 | </script></body>
1344 | </html>```

---

### setup.py

**Ruta:** `setup.py`

```py
0001 | # setup.py
0002 | from setuptools import setup, find_packages
0003 | from pathlib import Path
0004 | 
0005 | readme_path = Path(__file__).parent / "README.md"
0006 | long_description = ""
0007 | if readme_path.exists():
0008 |     try:
0009 |         long_description = readme_path.read_text(encoding="utf-8")
0010 |     except Exception:
0011 |         long_description = "LLM-Powered Vulnerability Triage"
0012 | 
0013 | setup(
0014 |     name="llm-triage",
0015 |     version="3.0.0",
0016 |     description="LLM-Powered Vulnerability Triage with CVSS Filtering and Deduplication",
0017 |     long_description=long_description,
0018 |     long_description_content_type="text/markdown",
0019 |     author="Security Team",
0020 |     author_email="security@research.com",
0021 |     url="https://github.com/your-org/llm-vuln-triage",
0022 |     packages=find_packages(),
0023 |     include_package_data=True,
0024 |     install_requires=[
0025 |         "pydantic>=2.0.0",
0026 |         "click>=8.0.0",
0027 |         "jinja2>=3.0.0",
0028 |         "requests>=2.31.0",
0029 |     ],
0030 |     extras_require={
0031 |         "dev": [
0032 |             "pytest>=7.0.0",
0033 |             "pytest-asyncio>=0.21.0",
0034 |             "black>=23.0.0",
0035 |         ],
0036 |         "openai": ["openai>=1.0.0"],
0037 |     },
0038 |     entry_points={
0039 |         "console_scripts": [
0040 |             "llm-triage=application.cli:cli",
0041 |             "vuln-triage=application.cli:cli",
0042 |         ],
0043 |     },
0044 |     python_requires=">=3.8",
0045 |     package_data={
0046 |         "adapters.output": ["templates/*.html"],
0047 |     },
0048 | )
```

---

### adapters\__init__.py

**Ruta:** `adapters\__init__.py`

```py
```

---

### adapters\output\html_generator.py

**Ruta:** `adapters\output\html_generator.py`

```py
0001 | # adapters/output/html_generator.py
0002 | """
0003 | HTML Report Generator - Optimized
0004 | =================================
0005 | 
0006 | Responsibilities:
0007 | - Generate HTML reports from analysis results
0008 | - Apply templates with Jinja2
0009 | - Handle fallback generation
0010 | """
0011 | 
0012 | import logging
0013 | from pathlib import Path
0014 | from datetime import datetime
0015 | from typing import Dict, Any, Optional
0016 | from jinja2 import Environment, FileSystemLoader, select_autoescape
0017 | 
0018 | from core.models import AnalysisReport, Vulnerability
0019 | from shared.metrics import MetricsCollector
0020 | 
0021 | logger = logging.getLogger(__name__)
0022 | 
0023 | 
0024 | class OptimizedHTMLGenerator:
0025 |     """Optimized HTML generator with Jinja2 templates"""
0026 |     
0027 |     def __init__(
0028 |         self,
0029 |         template_dir: Optional[Path] = None,
0030 |         metrics: Optional[MetricsCollector] = None
0031 |     ):
0032 |         """
0033 |         Initialize HTML generator
0034 |         
0035 |         Args:
0036 |             template_dir: Templates directory
0037 |             metrics: Optional metrics collector
0038 |         """
0039 |         self.template_dir = template_dir or Path(__file__).parent / "templates"
0040 |         self.metrics = metrics
0041 |         
0042 |         # Configure Jinja2
0043 |         self.env = Environment(
0044 |             loader=FileSystemLoader(str(self.template_dir)),
0045 |             autoescape=select_autoescape(['html', 'xml']),
0046 |             trim_blocks=True,
0047 |             lstrip_blocks=True
0048 |         )
0049 |         
0050 |         # Register filters
0051 |         self._register_filters()
0052 |         
0053 |         logger.info("📄 HTML Generator initialized")
0054 |     
0055 |     def generate_report(
0056 |         self,
0057 |         analysis_report: AnalysisReport,
0058 |         output_file: str
0059 |     ) -> bool:
0060 |         """
0061 |         Generate HTML report
0062 |         
0063 |         Args:
0064 |             analysis_report: Complete analysis report
0065 |             output_file: Output file path
0066 |         
0067 |         Returns:
0068 |             True if successful
0069 |         """
0070 |         try:
0071 |             logger.info(f"📝 Generating HTML: {output_file}")
0072 |             
0073 |             # Prepare context
0074 |             context = self._prepare_context(analysis_report)
0075 |             
0076 |             # Render template
0077 |             template = self.env.get_template('report.html')
0078 |             html_content = template.render(**context)
0079 |             
0080 |             # Write file
0081 |             output_path = Path(output_file)
0082 |             output_path.parent.mkdir(parents=True, exist_ok=True)
0083 |             
0084 |             with open(output_path, 'w', encoding='utf-8') as f:
0085 |                 f.write(html_content)
0086 |             
0087 |             # Record metrics
0088 |             file_size = output_path.stat().st_size
0089 |             if self.metrics:
0090 |                 self.metrics.record_report_generation(
0091 |                     "html",
0092 |                     file_size,
0093 |                     len(analysis_report.scan_result.vulnerabilities),
0094 |                     True
0095 |                 )
0096 |             
0097 |             logger.info(f"✅ Report generated: {output_file} ({file_size:,} bytes)")
0098 |             return True
0099 |             
0100 |         except Exception as e:
0101 |             logger.error(f"❌ HTML generation failed: {e}")
0102 |             if self.metrics:
0103 |                 self.metrics.record_report_generation("html", success=False, error=str(e))
0104 |             
0105 |             # Try fallback
0106 |             return self._generate_fallback(analysis_report, output_file)
0107 |     
0108 |     # ════════════════════════════════════════════════════════════════
0109 |     # PRIVATE HELPERS
0110 |     # ════════════════════════════════════════════════════════════════
0111 |     
0112 |     def _prepare_context(self, report: AnalysisReport) -> Dict[str, Any]:
0113 |         """Prepare template context"""
0114 |         scan = report.scan_result
0115 |         vulns = scan.vulnerabilities
0116 |         
0117 |         # Calculate metrics
0118 |         severity_stats = self._calc_severity_stats(vulns)
0119 |         risk_score = self._calc_risk_score(vulns)
0120 |         
0121 |         return {
0122 |             # Main data
0123 |             'report': report,
0124 |             'scan_result': scan,
0125 |             'triage_result': report.triage_result,
0126 |             'remediation_plans': report.remediation_plans,
0127 |             
0128 |             # Metrics
0129 |             'total_vulnerabilities': len(vulns),
0130 |             'high_priority_count': len([v for v in vulns if v.is_high_priority]),
0131 |             'severity_stats': severity_stats,
0132 |             'risk_score': risk_score,
0133 |             
0134 |             # Metadata
0135 |             'generation_timestamp': datetime.now(),
0136 |             'report_version': '3.0',
0137 |             'platform_name': 'Security Analysis Platform v3.0'
0138 |         }
0139 |     
0140 |     def _calc_severity_stats(self, vulns: list) -> Dict[str, int]:
0141 |         """Calculate severity distribution"""
0142 |         from collections import Counter
0143 |         return dict(Counter(v.severity.value for v in vulns))
0144 |     
0145 |     def _calc_risk_score(self, vulns: list) -> float:
0146 |         """Calculate risk score (0-10)"""
0147 |         if not vulns:
0148 |             return 0.0
0149 |         
0150 |         from shared.constants import SEVERITY_WEIGHTS
0151 |         
0152 |         total = sum(SEVERITY_WEIGHTS.get(v.severity.value, 0) for v in vulns)
0153 |         max_possible = len(vulns) * 10.0
0154 |         
0155 |         normalized = (total / max_possible) * 10.0 if max_possible > 0 else 0.0
0156 |         return round(min(normalized, 10.0), 1)
0157 |     
0158 |     def _generate_fallback(
0159 |         self,
0160 |         report: AnalysisReport,
0161 |         output_file: str
0162 |     ) -> bool:
0163 |         """Generate minimal fallback report"""
0164 |         logger.warning("⚠️  Generating fallback report")
0165 |         
0166 |         try:
0167 |             scan = report.scan_result
0168 |             vuln_count = len(scan.vulnerabilities)
0169 |             
0170 |             html = f"""<!DOCTYPE html>
0171 | <html lang="es">
0172 | <head>
0173 |     <meta charset="UTF-8">
0174 |     <title>Security Analysis Report - Fallback</title>
0175 |     <style>
0176 |         body {{ font-family: system-ui; margin: 20px; line-height: 1.6; }}
0177 |         .header {{ background: #4f46e5; color: white; padding: 20px; border-radius: 8px; }}
0178 |         .summary {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; }}
0179 |         .vuln {{ background: #fef2f2; padding: 15px; margin: 10px 0; border-radius: 8px; }}
0180 |     </style>
0181 | </head>
0182 | <body>
0183 |     <div class="header">
0184 |         <h1>🛡️ Security Analysis Report</h1>
0185 |         <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
0186 |     </div>
0187 |     
0188 |     <div class="summary">
0189 |         <h2>📊 Summary</h2>
0190 |         <p><strong>File:</strong> {scan.file_info.get('filename', 'Unknown')}</p>
0191 |         <p><strong>Vulnerabilities:</strong> {vuln_count}</p>
0192 |         <p><strong>Time:</strong> {report.total_processing_time_seconds:.2f}s</p>
0193 |     </div>
0194 | """
0195 |             
0196 |             if vuln_count > 0:
0197 |                 html += '<div class="summary"><h2>🚨 Vulnerabilities</h2>'
0198 |                 
0199 |                 for i, vuln in enumerate(scan.vulnerabilities[:10], 1):
0200 |                     html += f'''
0201 |     <div class="vuln">
0202 |         <h3>{i}. {vuln.title}</h3>
0203 |         <p><strong>Severity:</strong> {vuln.severity.value}</p>
0204 |         <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number}</p>
0205 |         <p>{vuln.description[:200]}...</p>
0206 |     </div>'''
0207 |                 
0208 |                 if vuln_count > 10:
0209 |                     html += f'<p><em>... and {vuln_count - 10} more vulnerabilities</em></p>'
0210 |                 
0211 |                 html += '</div>'
0212 |             else:
0213 |                 html += '''
0214 |     <div class="summary">
0215 |         <h2>✅ No Vulnerabilities Found</h2>
0216 |     </div>'''
0217 |             
0218 |             html += '''
0219 |     <div class="summary">
0220 |         <p>⚠️ Simplified report due to template error</p>
0221 |         <p>Generated by Security Analysis Platform v3.0</p>
0222 |     </div>
0223 | </body>
0224 | </html>'''
0225 |             
0226 |             with open(output_file, 'w', encoding='utf-8') as f:
0227 |                 f.write(html)
0228 |             
0229 |             logger.info(f"✅ Fallback report generated: {output_file}")
0230 |             return True
0231 |             
0232 |         except Exception as e:
0233 |             logger.error(f"❌ Even fallback failed: {e}")
0234 |             return False
0235 |     
0236 |     def _register_filters(self):
0237 |         """Register Jinja2 filters"""
0238 |         from shared.formatters import (
0239 |             format_bytes, format_duration, format_severity_icon, truncate_text
0240 |         )
0241 |         
0242 |         self.env.filters['format_bytes'] = format_bytes
0243 |         self.env.filters['format_duration'] = format_duration
0244 |         self.env.filters['severity_icon'] = format_severity_icon
0245 |         self.env.filters['truncate_smart'] = truncate_text
0246 |         
0247 |         # Severity class filter
0248 |         def severity_class(severity):
0249 |             classes = {
0250 |                 'CRÍTICA': 'critical',
0251 |                 'ALTA': 'high',
0252 |                 'MEDIA': 'medium',
0253 |                 'BAJA': 'low',
0254 |                 'INFO': 'info'
0255 |             }
0256 |             sev_str = severity if isinstance(severity, str) else str(severity)
0257 |             return classes.get(sev_str.upper(), 'default')
0258 |         
0259 |         self.env.filters['severity_class'] = severity_class
```

---

### adapters\output\__init__.py

**Ruta:** `adapters\output\__init__.py`

```py
```

---

### adapters\output\templates\report.html

**Ruta:** `adapters\output\templates\report.html`

```html
0001 |  <!-- adapters/output/templates/report.html -->
0002 | <!DOCTYPE html>
0003 | <html lang="es">
0004 | <head>
0005 |     <meta charset="UTF-8">
0006 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0007 |     <title>🛡️ {{ platform_name }} - Report</title>
0008 |     {% include 'styles.html' %}
0009 | </head>
0010 | <body>
0011 |     <div class="container">
0012 |         <!-- Header -->
0013 |         <header class="header">
0014 |             <div class="header-content">
0015 |                 <h1>🛡️ Security Analysis Report</h1>
0016 |                 <div class="header-grid">
0017 |                     <div class="header-item">
0018 |                         <div class="header-label">📁 File</div>
0019 |                         <div class="header-value">{{ scan_result.file_info.filename }}</div>
0020 |                     </div>
0021 |                     <div class="header-item">
0022 |                         <div class="header-label">📊 Total Vulnerabilities</div>
0023 |                         <div class="header-value">{{ total_vulnerabilities }}</div>
0024 |                     </div>
0025 |                     <div class="header-item">
0026 |                         <div class="header-label">⚡ High Priority</div>
0027 |                         <div class="header-value">{{ high_priority_count }}</div>
0028 |                     </div>
0029 |                     <div class="header-item">
0030 |                         <div class="header-label">🎯 Risk Score</div>
0031 |                         <div class="header-value">{{ risk_score }}/10</div>
0032 |                     </div>
0033 |                 </div>
0034 |             </div>
0035 |         </header>
0036 | 
0037 |         <main class="content">
0038 |             <!-- Executive Summary -->
0039 |             <section class="section">
0040 |                 <h2 class="section-title">📈 Executive Summary</h2>
0041 |                 
0042 |                 <div class="metrics-grid">
0043 |                     {% for severity, count in severity_stats.items() %}
0044 |                     {% if count > 0 %}
0045 |                     <div class="metric-card {{ severity | severity_class }}">
0046 |                         <div class="metric-icon">{{ severity | severity_icon }}</div>
0047 |                         <div class="metric-value">{{ count }}</div>
0048 |                         <div class="metric-label">{{ severity }}</div>
0049 |                     </div>
0050 |                     {% endif %}
0051 |                     {% endfor %}
0052 |                 </div>
0053 | 
0054 |                 <div class="summary-info">
0055 |                     <p><strong>Analysis completed in {{ report.total_processing_time_seconds | format_duration }}</strong></p>
0056 |                     {% if report.chunking_enabled %}
0057 |                     <p>🧩 Advanced chunking was used for optimal analysis</p>
0058 |                     {% endif %}
0059 |                     {% if triage_result %}
0060 |                     <p>🤖 AI-powered triage analyzed {{ triage_result.total_analyzed }} vulnerabilities</p>
0061 |                     {% endif %}
0062 |                 </div>
0063 |             </section>
0064 | 
0065 |             <!-- Vulnerabilities -->
0066 |             {% if scan_result.vulnerabilities %}
0067 |             <section class="section">
0068 |                 <h2 class="section-title">🚨 Security Vulnerabilities</h2>
0069 |                 
0070 |                 <div class="vulnerabilities-list">
0071 |                     {% for vuln in scan_result.vulnerabilities %}
0072 |                     <div class="vulnerability-card {{ vuln.severity.value | severity_class }}">
0073 |                         <div class="vuln-header">
0074 |                             <h3 class="vuln-title">
0075 |                                 {{ vuln.severity | severity_icon }} {{ loop.index }}. {{ vuln.title }}
0076 |                             </h3>
0077 |                             <div class="vuln-badges">
0078 |                                 <span class="badge severity-{{ vuln.severity.value | severity_class }}">
0079 |                                     {{ vuln.severity.value }}
0080 |                                 </span>
0081 |                                 <span class="badge type-badge">{{ vuln.type.value }}</span>
0082 |                             </div>
0083 |                         </div>
0084 |                         
0085 |                         <div class="vuln-body">
0086 |                             <div class="vuln-meta">
0087 |                                 <div class="meta-item">
0088 |                                     <span class="meta-label">📍 Location</span>
0089 |                                     <span class="meta-value">{{ vuln.file_path }}:{{ vuln.line_number }}</span>
0090 |                                 </div>
0091 |                                 <div class="meta-item">
0092 |                                     <span class="meta-label">🆔 ID</span>
0093 |                                     <span class="meta-value">{{ vuln.id }}</span>
0094 |                                 </div>
0095 |                                 {% if vuln.cwe_id %}
0096 |                                 <div class="meta-item">
0097 |                                     <span class="meta-label">🔗 CWE</span>
0098 |                                     <span class="meta-value">
0099 |                                         <a href="https://cwe.mitre.org/data/definitions/{{ vuln.cwe_id.replace('CWE-', '') }}.html" target="_blank">
0100 |                                             {{ vuln.cwe_id }}
0101 |                                         </a>
0102 |                                     </span>
0103 |                                 </div>
0104 |                                 {% endif %}
0105 |                             </div>
0106 |                             
0107 |                             <div class="vuln-description">
0108 |                                 <h4>📝 Description</h4>
0109 |                                 <p>{{ vuln.description }}</p>
0110 |                             </div>
0111 |                             
0112 |                             {% if vuln.code_snippet %}
0113 |                             <div class="vuln-code">
0114 |                                 <h4>💻 Code Context</h4>
0115 |                                 <pre class="code-block">{{ vuln.code_snippet | truncate_smart(500) }}</pre>
0116 |                             </div>
0117 |                             {% endif %}
0118 |                             
0119 |                             {% if vuln.remediation_advice %}
0120 |                             <div class="vuln-remediation">
0121 |                                 <h4>💡 Remediation Advice</h4>
0122 |                                 <div class="advice-content">{{ vuln.remediation_advice }}</div>
0123 |                             </div>
0124 |                             {% endif %}
0125 |                         </div>
0126 |                     </div>
0127 |                     {% endfor %}
0128 |                 </div>
0129 |             </section>
0130 |             {% else %}
0131 |             <section class="section">
0132 |                 <div class="no-vulnerabilities">
0133 |                     <div class="no-vulns-icon">✅</div>
0134 |                     <h2>No Vulnerabilities Found</h2>
0135 |                     <p>Excellent! No security vulnerabilities were detected in the analyzed code.</p>
0136 |                 </div>
0137 |             </section>
0138 |             {% endif %}
0139 | 
0140 |             <!-- Remediation Plans -->
0141 |             {% if remediation_plans %}
0142 |             <section class="section">
0143 |                 <h2 class="section-title">🛠️ Remediation Plans</h2>
0144 |                 
0145 |                 <div class="remediation-summary">
0146 |                     <p>{{ remediation_plans | length }} actionable remediation plans generated, prioritized by risk and complexity.</p>
0147 |                 </div>
0148 |                 
0149 |                 <div class="remediation-plans">
0150 |                     {% for plan in remediation_plans %}
0151 |                     <div class="remediation-card">
0152 |                         <div class="plan-header">
0153 |                             <h3>🔧 {{ plan.vulnerability_type.value }}</h3>
0154 |                             <span class="priority-badge priority-{{ plan.priority_level }}">
0155 |                                 {{ plan.priority_level.upper() }}
0156 |                             </span>
0157 |                         </div>
0158 |                         
0159 | 							<div class="plan-meta">
0160 | 								<span class="plan-stat">📊 Complexity: {{ plan.complexity_score }}/10</span>
0161 | 								<span class="plan-stat">📋 {{ plan.steps | length }} steps</span>
0162 | 							</div>
0163 | 
0164 |                         <div class="plan-steps">
0165 |                             <h4>Implementation Steps:</h4>
0166 |                             <ol>
0167 |                                 {% for step in plan.steps %}
0168 |                                 <li class="remediation-step">
0169 |                                     <div class="step-header">
0170 |                                         <strong>{{ step.title }}</strong>
0171 |                                         <span class="step-meta">{{ step.estimated_minutes }}min • {{ step.difficulty }}</span>
0172 |                                     </div>
0173 |                                     <div class="step-description">{{ step.description }}</div>
0174 |                                     {% if step.code_example %}
0175 |                                     <pre class="step-code">{{ step.code_example | truncate_smart(200) }}</pre>
0176 |                                     {% endif %}
0177 |                                 </li>
0178 |                                 {% endfor %}
0179 |                             </ol>
0180 |                         </div>
0181 |                         
0182 |                         {% if plan.risk_if_not_fixed %}
0183 |                         <div class="risk-warning">
0184 |                             <h5>⚠️ Risk if not addressed:</h5>
0185 |                             <p>{{ plan.risk_if_not_fixed }}</p>
0186 |                         </div>
0187 |                         {% endif %}
0188 |                     </div>
0189 |                     {% endfor %}
0190 |                 </div>
0191 |             </section>
0192 |             {% endif %}
0193 | 
0194 |             <!-- Technical Details -->
0195 |             <section class="section">
0196 |                 <details class="technical-details">
0197 |                     <summary class="details-toggle">🔍 Technical Analysis Details</summary>
0198 |                     <div class="details-content">
0199 |                         <div class="tech-grid">
0200 |                             <div class="tech-item">
0201 |                                 <h4>📊 Analysis Statistics</h4>
0202 |                                 <ul>
0203 |                                     <li>Processing time: {{ report.total_processing_time_seconds | format_duration }}</li>
0204 |                                     <li>File size: {{ scan_result.file_info.size_bytes | format_bytes }}</li>
0205 |                                     <li>Language: {{ scan_result.language_detected or 'Auto-detected' }}</li>
0206 |                                     <li>Chunking: {{ 'Enabled' if report.chunking_enabled else 'Disabled' }}</li>
0207 |                                 </ul>
0208 |                             </div>
0209 |                             
0210 |                             {% if triage_result %}
0211 |                             <div class="tech-item">
0212 |                                 <h4>🤖 LLM Triage Results</h4>
0213 |                                 <ul>
0214 |                                     <li>Confirmed vulnerabilities: {{ triage_result.confirmed_count }}</li>
0215 |                                     <li>False positives: {{ triage_result.false_positive_count }}</li>
0216 |                                     <li>Need manual review: {{ triage_result.needs_review_count }}</li>
0217 |                                     <li>Analysis time: {{ triage_result.llm_analysis_time_seconds | format_duration }}</li>
0218 |                                 </ul>
0219 |                             </div>
0220 |                             {% endif %}
0221 |                         </div>
0222 |                         
0223 |                         {% if triage_result and triage_result.analysis_summary %}
0224 |                         <div class="analysis-summary">
0225 |                             <h4>📋 Analysis Summary</h4>
0226 |                             <pre>{{ triage_result.analysis_summary }}</pre>
0227 |                         </div>
0228 |                         {% endif %}
0229 |                     </div>
0230 |                 </details>
0231 |             </section>
0232 |         </main>
0233 | 
0234 |         <!-- Footer -->
0235 |         <footer class="footer">
0236 |             <div class="footer-content">
0237 |                 <p>Generated by <strong>{{ platform_name }}</strong> on {{ generation_timestamp.strftime('%Y-%m-%d at %H:%M:%S') }}</p>
0238 |                 <p>For questions about this report, contact your security team.</p>
0239 |             </div>
0240 |         </footer>
0241 |     </div>
0242 | 
0243 |     {% include 'scripts.html' %}
0244 | </body>
0245 | </html>
```

---

### adapters\output\templates\scripts.html

**Ruta:** `adapters\output\templates\scripts.html`

```html
0001 | <!-- adapters/output/templates/scripts.html -->
0002 | <script>
0003 | document.addEventListener('DOMContentLoaded', function() {
0004 |     console.log('🛡️ Security Analysis Report v3.0 loaded');
0005 |     
0006 |     // Enhanced interactivity
0007 |     initializeAnimations();
0008 |     setupCopyFunctionality();
0009 |     setupSearchFunctionality();
0010 |     setupKeyboardNavigation();
0011 |     
0012 |     // Report statistics
0013 |     logReportStatistics();
0014 | });
0015 | 
0016 | function initializeAnimations() {
0017 |     // Intersection Observer for scroll animations
0018 |     const observerOptions = {
0019 |         threshold: 0.1,
0020 |         rootMargin: '0px 0px -50px 0px'
0021 |     };
0022 | 
0023 |     const observer = new IntersectionObserver(function(entries) {
0024 |         entries.forEach(function(entry) {
0025 |             if (entry.isIntersecting) {
0026 |                 entry.target.style.opacity = '1';
0027 |                 entry.target.style.transform = 'translateY(0)';
0028 |             }
0029 |         });
0030 |     }, observerOptions);
0031 | 
0032 |     // Apply to vulnerability cards
0033 |     document.querySelectorAll('.vulnerability-card, .remediation-card').forEach(function(el) {
0034 |         el.style.opacity = '0';
0035 |         el.style.transform = 'translateY(20px)';
0036 |         el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
0037 |         observer.observe(el);
0038 |     });
0039 | }
0040 | 
0041 | function setupCopyFunctionality() {
0042 |     // Add copy buttons to vulnerability IDs and CWE links
0043 |     document.querySelectorAll('.meta-value').forEach(function(element) {
0044 |         const text = element.textContent.trim();
0045 |         
0046 |         if (text.match(/^(VULN-|ABAP-|CWE-)/)) {
0047 |             element.style.cursor = 'pointer';
0048 |             element.title = 'Click to copy ' + text;
0049 |             
0050 |             element.addEventListener('click', function() {
0051 |                 copyToClipboard(text);
0052 |                 showToast('✅ Copied: ' + text);
0053 |             });
0054 |         }
0055 |     });
0056 | }
0057 | 
0058 | function setupSearchFunctionality() {
0059 |     // Create search box
0060 |     const searchBox = document.createElement('div');
0061 |     searchBox.innerHTML = `
0062 |         <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
0063 |             <input type="text" id="vulnerabilitySearch" placeholder="🔍 Search vulnerabilities..." 
0064 |                    style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; width: 250px;">
0065 |         </div>
0066 |     `;
0067 |     document.body.appendChild(searchBox);
0068 |     
0069 |     const searchInput = document.getElementById('vulnerabilitySearch');
0070 |     searchInput.addEventListener('input', function(e) {
0071 |         const query = e.target.value.toLowerCase();
0072 |         filterVulnerabilities(query);
0073 |     });
0074 | }
0075 | 
0076 | function setupKeyboardNavigation() {
0077 |     document.addEventListener('keydown', function(e) {
0078 |         // Ctrl+F or Cmd+F to focus search
0079 |         if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
0080 |             e.preventDefault();
0081 |             const searchInput = document.getElementById('vulnerabilitySearch');
0082 |             if (searchInput) {
0083 |                 searchInput.focus();
0084 |             }
0085 |         }
0086 |         
0087 |         // Escape to clear search
0088 |         if (e.key === 'Escape') {
0089 |             const searchInput = document.getElementById('vulnerabilitySearch');
0090 |             if (searchInput && searchInput === document.activeElement) {
0091 |                 searchInput.value = '';
0092 |                 filterVulnerabilities('');
0093 |                 searchInput.blur();
0094 |             }
0095 |         }
0096 |     });
0097 | }
0098 | 
0099 | function filterVulnerabilities(query) {
0100 |     const cards = document.querySelectorAll('.vulnerability-card');
0101 |     let visibleCount = 0;
0102 |     
0103 |     cards.forEach(function(card) {
0104 |         const text = card.textContent.toLowerCase();
0105 |         const isVisible = query === '' || text.includes(query);
0106 |         
0107 |         card.style.display = isVisible ? 'block' : 'none';
0108 |         if (isVisible) visibleCount++;
0109 |     });
0110 |     
0111 |     // Update search results indicator
0112 |     updateSearchResults(visibleCount, cards.length, query);
0113 | }
0114 | 
0115 | function updateSearchResults(visible, total, query) {
0116 |     let indicator = document.getElementById('searchResults');
0117 |     
0118 |     if (!indicator) {
0119 |         indicator = document.createElement('div');
0120 |         indicator.id = 'searchResults';
0121 |         indicator.style.cssText = `
0122 |             position: fixed;
0123 |             bottom: 20px;
0124 |             right: 20px;
0125 |             background: #4f46e5;
0126 |             color: white;
0127 |             padding: 8px 12px;
0128 |             border-radius: 6px;
0129 |             font-size: 0.875rem;
0130 |             z-index: 1000;
0131 |             transition: opacity 0.3s;
0132 |         `;
0133 |         document.body.appendChild(indicator);
0134 |     }
0135 |     
0136 |     if (query) {
0137 |         indicator.textContent = `Found ${visible} of ${total} vulnerabilities`;
0138 |         indicator.style.opacity = '1';
0139 |     } else {
0140 |         indicator.style.opacity = '0';
0141 |     }
0142 | }
0143 | 
0144 | function copyToClipboard(text) {
0145 |     if (navigator.clipboard) {
0146 |         navigator.clipboard.writeText(text).catch(function() {
0147 |             fallbackCopy(text);
0148 |         });
0149 |     } else {
0150 |         fallbackCopy(text);
0151 |     }
0152 | }
0153 | 
0154 | function fallbackCopy(text) {
0155 |     const textArea = document.createElement('textarea');
0156 |     textArea.value = text;
0157 |     textArea.style.position = 'fixed';
0158 |     textArea.style.left = '-9999px';
0159 |     document.body.appendChild(textArea);
0160 |     textArea.focus();
0161 |     textArea.select();
0162 |     
0163 |     try {
0164 |         document.execCommand('copy');
0165 |     } catch (err) {
0166 |         console.warn('Copy failed:', err);
0167 |     }
0168 |     
0169 |     document.body.removeChild(textArea);
0170 | }
0171 | 
0172 | function showToast(message) {
0173 |     const toast = document.createElement('div');
0174 |     toast.textContent = message;
0175 |     toast.style.cssText = `
0176 |         position: fixed;
0177 |         top: 20px;
0178 |         left: 50%;
0179 |         transform: translateX(-50%);
0180 |         background: #10b981;
0181 |         color: white;
0182 |         padding: 12px 20px;
0183 |         border-radius: 8px;
0184 |         z-index: 9999;
0185 |         animation: slideInDown 0.3s ease-out;
0186 |         font-weight: 500;
0187 |     `;
0188 |     
0189 |     document.body.appendChild(toast);
0190 |     
0191 |     setTimeout(function() {
0192 |         toast.style.animation = 'slideOutUp 0.3s ease-out';
0193 |         setTimeout(function() {
0194 |             document.body.removeChild(toast);
0195 |         }, 300);
0196 |     }, 2000);
0197 | }
0198 | 
0199 | function logReportStatistics() {
0200 |     const stats = {
0201 |         totalVulnerabilities: {{ total_vulnerabilities }},
0202 |         highPriority: {{ high_priority_count }},
0203 |         riskScore: {{ risk_score }},
0204 |         processingTime: '{{ report.total_processing_time_seconds | format_duration }}',
0205 |         chunking: {{ 'true' if report.chunking_enabled else 'false' }},
0206 |         llmAnalysis: {{ 'true' if triage_result else 'false' }},
0207 |         reportVersion: '{{ report_version }}'
0208 |     };
0209 |     
0210 |     console.log('📊 Report Statistics:', stats);
0211 |     
0212 |     // Performance metrics
0213 |     console.log('⚡ Performance Metrics:');
0214 |     console.log('  • DOM Ready:', performance.now().toFixed(2) + 'ms');
0215 |     console.log('  • Interactive elements:', document.querySelectorAll('[onclick], [data-action]').length);
0216 |     console.log('  • Vulnerability cards:', document.querySelectorAll('.vulnerability-card').length);
0217 | }
0218 | 
0219 | // CSS animations for toasts
0220 | const additionalStyles = `
0221 | @keyframes slideInDown {
0222 |     from {
0223 |         opacity: 0;
0224 |         transform: translate(-50%, -100%);
0225 |     }
0226 |     to {
0227 |         opacity: 1;
0228 |         transform: translate(-50%, 0);
0229 |     }
0230 | }
0231 | 
0232 | @keyframes slideOutUp {
0233 |     from {
0234 |         opacity: 1;
0235 |         transform: translate(-50%, 0);
0236 |     }
0237 |     to {
0238 |         opacity: 0;
0239 |         transform: translate(-50%, -100%);
0240 |     }
0241 | }
0242 | `;
0243 | 
0244 | const styleSheet = document.createElement('style');
0245 | styleSheet.textContent = additionalStyles;
0246 | document.head.appendChild(styleSheet);
0247 | </script>
```

---

### adapters\output\templates\styles.html

**Ruta:** `adapters\output\templates\styles.html`

```html
0001 | <!-- adapters/output/templates/styles.html -->
0002 | <style>
0003 | /* === RESET & BASE === */
0004 | * {
0005 |     margin: 0;
0006 |     padding: 0;
0007 |     box-sizing: border-box;
0008 | }
0009 | 
0010 | body {
0011 |     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
0012 |     line-height: 1.6;
0013 |     color: #1f2937;
0014 |     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
0015 |     min-height: 100vh;
0016 | }
0017 | 
0018 | /* === LAYOUT === */
0019 | .container {
0020 |     max-width: 1200px;
0021 |     margin: 20px auto;
0022 |     background: white;
0023 |     border-radius: 16px;
0024 |     box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
0025 |     overflow: hidden;
0026 | }
0027 | 
0028 | /* === HEADER === */
0029 | .header {
0030 |     background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
0031 |     color: white;
0032 |     padding: 2rem;
0033 |     position: relative;
0034 | }
0035 | 
0036 | .header::before {
0037 |     content: '';
0038 |     position: absolute;
0039 |     top: 0;
0040 |     left: 0;
0041 |     right: 0;
0042 |     bottom: 0;
0043 |     background: url('image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
0044 |     opacity: 0.3;
0045 | }
0046 | 
0047 | .header-content {
0048 |     position: relative;
0049 |     z-index: 1;
0050 |     text-align: center;
0051 | }
0052 | 
0053 | .header h1 {
0054 |     font-size: 2.5rem;
0055 |     font-weight: 700;
0056 |     margin-bottom: 1rem;
0057 |     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
0058 | }
0059 | 
0060 | .header-grid {
0061 |     display: grid;
0062 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0063 |     gap: 1rem;
0064 |     margin-top: 1.5rem;
0065 | }
0066 | 
0067 | .header-item {
0068 |     background: rgba(255, 255, 255, 0.15);
0069 |     padding: 1rem;
0070 |     border-radius: 12px;
0071 |     backdrop-filter: blur(10px);
0072 |     border: 1px solid rgba(255, 255, 255, 0.2);
0073 | }
0074 | 
0075 | .header-label {
0076 |     font-size: 0.875rem;
0077 |     opacity: 0.9;
0078 |     margin-bottom: 0.25rem;
0079 | }
0080 | 
0081 | .header-value {
0082 |     font-size: 1.25rem;
0083 |     font-weight: 600;
0084 | }
0085 | 
0086 | /* === CONTENT === */
0087 | .content {
0088 |     padding: 2rem;
0089 | }
0090 | 
0091 | .section {
0092 |     margin-bottom: 3rem;
0093 | }
0094 | 
0095 | .section-title {
0096 |     font-size: 1.875rem;
0097 |     font-weight: 700;
0098 |     color: #1f2937;
0099 |     margin-bottom: 1.5rem;
0100 |     padding-bottom: 0.75rem;
0101 |     border-bottom: 3px solid #4f46e5;
0102 |     position: relative;
0103 | }
0104 | 
0105 | .section-title::after {
0106 |     content: '';
0107 |     position: absolute;
0108 |     bottom: -3px;
0109 |     left: 0;
0110 |     width: 60px;
0111 |     height: 3px;
0112 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0113 | }
0114 | 
0115 | /* === METRICS === */
0116 | .metrics-grid {
0117 |     display: grid;
0118 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0119 |     gap: 1.5rem;
0120 |     margin-bottom: 2rem;
0121 | }
0122 | 
0123 | .metric-card {
0124 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0125 |     border-radius: 16px;
0126 |     padding: 1.5rem;
0127 |     text-align: center;
0128 |     transition: transform 0.3s ease, box-shadow 0.3s ease;
0129 |     position: relative;
0130 |     overflow: hidden;
0131 | }
0132 | 
0133 | .metric-card::before {
0134 |     content: '';
0135 |     position: absolute;
0136 |     top: 0;
0137 |     left: 0;
0138 |     right: 0;
0139 |     height: 4px;
0140 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0141 | }
0142 | 
0143 | .metric-card:hover {
0144 |     transform: translateY(-4px);
0145 |     box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
0146 | }
0147 | 
0148 | .metric-icon {
0149 |     font-size: 2rem;
0150 |     margin-bottom: 0.5rem;
0151 | }
0152 | 
0153 | .metric-value {
0154 |     font-size: 2.5rem;
0155 |     font-weight: 700;
0156 |     margin-bottom: 0.5rem;
0157 |     background: linear-gradient(135deg, #4f46e5, #7c3aed);
0158 |     -webkit-background-clip: text;
0159 |     -webkit-text-fill-color: transparent;
0160 |     background-clip: text;
0161 | }
0162 | 
0163 | .metric-label {
0164 |     color: #64748b;
0165 |     font-size: 0.875rem;
0166 |     font-weight: 500;
0167 |     text-transform: uppercase;
0168 |     letter-spacing: 0.05em;
0169 | }
0170 | 
0171 | /* === VULNERABILITIES === */
0172 | .vulnerabilities-list {
0173 |     display: grid;
0174 |     gap: 1.5rem;
0175 | }
0176 | 
0177 | .vulnerability-card {
0178 |     background: white;
0179 |     border: 1px solid #e5e7eb;
0180 |     border-radius: 16px;
0181 |     overflow: hidden;
0182 |     transition: all 0.3s ease;
0183 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0184 | }
0185 | 
0186 | .vulnerability-card:hover {
0187 |     box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
0188 |     transform: translateY(-2px);
0189 | }
0190 | 
0191 | .vulnerability-card.critical {
0192 |     border-left: 6px solid #dc2626;
0193 | }
0194 | 
0195 | .vulnerability-card.high {
0196 |     border-left: 6px solid #ea580c;
0197 | }
0198 | 
0199 | .vulnerability-card.medium {
0200 |     border-left: 6px solid #d97706;
0201 | }
0202 | 
0203 | .vulnerability-card.low {
0204 |     border-left: 6px solid #16a34a;
0205 | }
0206 | 
0207 | .vulnerability-card.info {
0208 |     border-left: 6px solid #0ea5e9;
0209 | }
0210 | 
0211 | .vuln-header {
0212 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0213 |     padding: 1.5rem;
0214 |     border-bottom: 1px solid #e5e7eb;
0215 |     display: flex;
0216 |     justify-content: space-between;
0217 |     align-items: flex-start;
0218 |     gap: 1rem;
0219 | }
0220 | 
0221 | .vuln-title {
0222 |     font-size: 1.25rem;
0223 |     font-weight: 600;
0224 |     color: #1f2937;
0225 |     flex: 1;
0226 | }
0227 | 
0228 | .vuln-badges {
0229 |     display: flex;
0230 |     gap: 0.5rem;
0231 |     flex-shrink: 0;
0232 | }
0233 | 
0234 | .badge {
0235 |     padding: 0.25rem 0.75rem;
0236 |     border-radius: 12px;
0237 |     font-size: 0.75rem;
0238 |     font-weight: 600;
0239 |     text-transform: uppercase;
0240 |     letter-spacing: 0.05em;
0241 | }
0242 | 
0243 | .badge.severity-critical {
0244 |     background: #dc2626;
0245 |     color: white;
0246 | }
0247 | 
0248 | .badge.severity-high {
0249 |     background: #ea580c;
0250 |     color: white;
0251 | }
0252 | 
0253 | .badge.severity-medium {
0254 |     background: #d97706;
0255 |     color: white;
0256 | }
0257 | 
0258 | .badge.severity-low {
0259 |     background: #16a34a;
0260 |     color: white;
0261 | }
0262 | 
0263 | .badge.severity-info {
0264 |     background: #0ea5e9;
0265 |     color: white;
0266 | }
0267 | 
0268 | .badge.type-badge {
0269 |     background: #6b7280;
0270 |     color: white;
0271 | }
0272 | 
0273 | .vuln-body {
0274 |     padding: 1.5rem;
0275 | }
0276 | 
0277 | .vuln-meta {
0278 |     display: grid;
0279 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0280 |     gap: 1rem;
0281 |     margin-bottom: 1.5rem;
0282 | }
0283 | 
0284 | .meta-item {
0285 |     background: #f8fafc;
0286 |     padding: 0.75rem;
0287 |     border-radius: 8px;
0288 |     border: 1px solid #e5e7eb;
0289 | }
0290 | 
0291 | .meta-label {
0292 |     font-size: 0.75rem;
0293 |     font-weight: 600;
0294 |     color: #6b7280;
0295 |     text-transform: uppercase;
0296 |     letter-spacing: 0.05em;
0297 |     margin-bottom: 0.25rem;
0298 | }
0299 | 
0300 | .meta-value {
0301 |     font-weight: 500;
0302 |     color: #1f2937;
0303 | }
0304 | 
0305 | .meta-value a {
0306 |     color: #4f46e5;
0307 |     text-decoration: none;
0308 | }
0309 | 
0310 | .meta-value a:hover {
0311 |     text-decoration: underline;
0312 | }
0313 | 
0314 | .vuln-description,
0315 | .vuln-code,
0316 | .vuln-remediation {
0317 |     margin-bottom: 1.5rem;
0318 | }
0319 | 
0320 | .vuln-description h4,
0321 | .vuln-code h4,
0322 | .vuln-remediation h4 {
0323 |     font-size: 1rem;
0324 |     font-weight: 600;
0325 |     color: #374151;
0326 |     margin-bottom: 0.75rem;
0327 |     display: flex;
0328 |     align-items: center;
0329 |     gap: 0.5rem;
0330 | }
0331 | 
0332 | .code-block {
0333 |     background: #0f172a;
0334 |     color: #e2e8f0;
0335 |     padding: 1rem;
0336 |     border-radius: 8px;
0337 |     font-family: 'JetBrains Mono', 'Fira Code', Monaco, monospace;
0338 |     font-size: 0.875rem;
0339 |     overflow-x: auto;
0340 |     line-height: 1.5;
0341 |     border: 1px solid #334155;
0342 | }
0343 | 
0344 | .advice-content {
0345 |     background: #dbeafe;
0346 |     padding: 1rem;
0347 |     border-radius: 8px;
0348 |     border-left: 4px solid #3b82f6;
0349 |     color: #1e40af;
0350 | }
0351 | 
0352 | /* === NO VULNERABILITIES === */
0353 | .no-vulnerabilities {
0354 |     text-align: center;
0355 |     padding: 4rem 2rem;
0356 |     background: linear-gradient(135deg, #22c55e, #16a34a);
0357 |     color: white;
0358 |     border-radius: 16px;
0359 | }
0360 | 
0361 | .no-vulns-icon {
0362 |     font-size: 4rem;
0363 |     margin-bottom: 1rem;
0364 | }
0365 | 
0366 | .no-vulnerabilities h2 {
0367 |     font-size: 2rem;
0368 |     margin-bottom: 1rem;
0369 | }
0370 | 
0371 | /* === REMEDIATION === */
0372 | .remediation-summary {
0373 |     background: #f0f9ff;
0374 |     padding: 1rem;
0375 |     border-radius: 8px;
0376 |     border-left: 4px solid #0ea5e9;
0377 |     margin-bottom: 2rem;
0378 | }
0379 | 
0380 | .remediation-plans {
0381 |     display: grid;
0382 |     gap: 2rem;
0383 | }
0384 | 
0385 | .remediation-card {
0386 |     background: white;
0387 |     border: 1px solid #e5e7eb;
0388 |     border-radius: 12px;
0389 |     padding: 1.5rem;
0390 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0391 | }
0392 | 
0393 | .plan-header {
0394 |     display: flex;
0395 |     justify-content: space-between;
0396 |     align-items: center;
0397 |     margin-bottom: 1rem;
0398 | }
0399 | 
0400 | .plan-header h3 {
0401 |     font-size: 1.25rem;
0402 |     font-weight: 600;
0403 |     color: #1f2937;
0404 | }
0405 | 
0406 | .priority-badge {
0407 |     padding: 0.25rem 0.75rem;
0408 |     border-radius: 20px;
0409 |     font-size: 0.75rem;
0410 |     font-weight: 600;
0411 |     text-transform: uppercase;
0412 | }
0413 | 
0414 | .priority-badge.priority-immediate {
0415 |     background: #dc2626;
0416 |     color: white;
0417 | }
0418 | 
0419 | .priority-badge.priority-high {
0420 |     background: #ea580c;
0421 |     color: white;
0422 | }
0423 | 
0424 | .priority-badge.priority-medium {
0425 |     background: #d97706;
0426 |     color: white;
0427 | }
0428 | 
0429 | .priority-badge.priority-low {
0430 |     background: #16a34a;
0431 |     color: white;
0432 | }
0433 | 
0434 | .plan-meta {
0435 |     display: flex;
0436 |     gap: 1rem;
0437 |     margin-bottom: 1.5rem;
0438 |     flex-wrap: wrap;
0439 | }
0440 | 
0441 | .plan-stat {
0442 |     background: #f3f4f6;
0443 |     padding: 0.5rem 1rem;
0444 |     border-radius: 6px;
0445 |     font-size: 0.875rem;
0446 |     font-weight: 500;
0447 | }
0448 | 
0449 | .plan-steps {
0450 |     margin-bottom: 1.5rem;
0451 | }
0452 | 
0453 | .plan-steps h4 {
0454 |     font-size: 1rem;
0455 |     font-weight: 600;
0456 |     margin-bottom: 1rem;
0457 |     color: #374151;
0458 | }
0459 | 
0460 | .plan-steps ol {
0461 |     list-style: none;
0462 |     counter-reset: step-counter;
0463 | }
0464 | 
0465 | .remediation-step {
0466 |     counter-increment: step-counter;
0467 |     margin-bottom: 1rem;
0468 |     padding: 1rem;
0469 |     background: #f8fafc;
0470 |     border-radius: 8px;
0471 |     border-left: 4px solid #4f46e5;
0472 |     position: relative;
0473 |     padding-left: 3rem;
0474 | }
0475 | 
0476 | .remediation-step::before {
0477 |     content: counter(step-counter);
0478 |     position: absolute;
0479 |     left: 1rem;
0480 |     top: 1rem;
0481 |     background: #4f46e5;
0482 |     color: white;
0483 |     width: 1.5rem;
0484 |     height: 1.5rem;
0485 |     border-radius: 50%;
0486 |     display: flex;
0487 |     align-items: center;
0488 |     justify-content: center;
0489 |     font-weight: 600;
0490 |     font-size: 0.875rem;
0491 | }
0492 | 
0493 | .step-header {
0494 |     display: flex;
0495 |     justify-content: space-between;
0496 |     align-items: flex-start;
0497 |     margin-bottom: 0.5rem;
0498 | }
0499 | 
0500 | .step-meta {
0501 |     font-size: 0.75rem;
0502 |     color: #6b7280;
0503 |     background: #e5e7eb;
0504 |     padding: 0.25rem 0.5rem;
0505 |     border-radius: 4px;
0506 | }
0507 | 
0508 | .step-description {
0509 |     color: #4b5563;
0510 |     margin-bottom: 0.75rem;
0511 | }
0512 | 
0513 | .step-code {
0514 |     background: #f3f4f6;
0515 |     color: #374151;
0516 |     padding: 0.75rem;
0517 |     border-radius: 6px;
0518 |     font-family: 'JetBrains Mono', monospace;
0519 |     font-size: 0.8rem;
0520 |     border: 1px solid #d1d5db;
0521 | }
0522 | 
0523 | .risk-warning {
0524 |     background: #fef2f2;
0525 |     padding: 1rem;
0526 |     border-radius: 8px;
0527 |     border-left: 4px solid #ef4444;
0528 |     color: #991b1b;
0529 | }
0530 | 
0531 | .risk-warning h5 {
0532 |     font-weight: 600;
0533 |     margin-bottom: 0.5rem;
0534 | }
0535 | 
0536 | /* === TECHNICAL DETAILS === */
0537 | .technical-details {
0538 |     background: #f8fafc;
0539 |     border: 1px solid #e5e7eb;
0540 |     border-radius: 12px;
0541 |     overflow: hidden;
0542 | }
0543 | 
0544 | .details-toggle {
0545 |     background: #f1f5f9;
0546 |     padding: 1rem 1.5rem;
0547 |     cursor: pointer;
0548 |     font-weight: 600;
0549 |     color: #374151;
0550 |     display: flex;
0551 |     align-items: center;
0552 |     gap: 0.5rem;
0553 |     border: none;
0554 |     width: 100%;
0555 |     text-align: left;
0556 |     transition: background 0.2s;
0557 | }
0558 | 
0559 | .details-toggle:hover {
0560 |     background: #e2e8f0;
0561 | }
0562 | 
0563 | .details-toggle::after {
0564 |     content: '▶';
0565 |     margin-left: auto;
0566 |     transition: transform 0.3s;
0567 | }
0568 | 
0569 | .technical-details[open] .details-toggle::after {
0570 |     transform: rotate(90deg);
0571 | }
0572 | 
0573 | .details-content {
0574 |     padding: 1.5rem;
0575 | }
0576 | 
0577 | .tech-grid {
0578 |     display: grid;
0579 |     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
0580 |     gap: 1.5rem;
0581 |     margin-bottom: 1.5rem;
0582 | }
0583 | 
0584 | .tech-item h4 {
0585 |     font-weight: 600;
0586 |     color: #374151;
0587 |     margin-bottom: 0.75rem;
0588 | }
0589 | 
0590 | .tech-item ul {
0591 |     list-style: none;
0592 |     padding-left: 0;
0593 | }
0594 | 
0595 | .tech-item li {
0596 |     padding: 0.25rem 0;
0597 |     color: #6b7280;
0598 | }
0599 | 
0600 | .analysis-summary {
0601 |     background: white;
0602 |     padding: 1rem;
0603 |     border-radius: 8px;
0604 |     border: 1px solid #e5e7eb;
0605 | }
0606 | 
0607 | .analysis-summary h4 {
0608 |     font-weight: 600;
0609 |     color: #374151;
0610 |     margin-bottom: 0.75rem;
0611 | }
0612 | 
0613 | .analysis-summary pre {
0614 |     background: #f8fafc;
0615 |     padding: 1rem;
0616 |     border-radius: 6px;
0617 |     font-size: 0.875rem;
0618 |     color: #4b5563;
0619 |     white-space: pre-wrap;
0620 |     word-wrap: break-word;
0621 | }
0622 | 
0623 | /* === FOOTER === */
0624 | .footer {
0625 |     background: #1f2937;
0626 |     color: white;
0627 |     padding: 2rem;
0628 |     text-align: center;
0629 | }
0630 | 
0631 | .footer-content p {
0632 |     margin-bottom: 0.5rem;
0633 | }
0634 | 
0635 | /* === RESPONSIVE DESIGN === */
0636 | @media (max-width: 768px) {
0637 |     .container {
0638 |         margin: 10px;
0639 |         border-radius: 8px;
0640 |     }
0641 |     
0642 |     .header {
0643 |         padding: 1.5rem;
0644 |     }
0645 |     
0646 |     .header h1 {
0647 |         font-size: 2rem;
0648 |     }
0649 |     
0650 |     .header-grid {
0651 |         grid-template-columns: 1fr;
0652 |     }
0653 |     
0654 |     .content {
0655 |         padding: 1.5rem;
0656 |     }
0657 |     
0658 |     .metrics-grid {
0659 |         grid-template-columns: 1fr;
0660 |     }
0661 |     
0662 |     .vuln-header {
0663 |         flex-direction: column;
0664 |         align-items: flex-start;
0665 |     }
0666 |     
0667 |     .vuln-meta {
0668 |         grid-template-columns: 1fr;
0669 |     }
0670 |     
0671 |     .plan-header {
0672 |         flex-direction: column;
0673 |         align-items: flex-start;
0674 |         gap: 0.5rem;
0675 |     }
0676 |     
0677 |     .plan-meta {
0678 |         flex-direction: column;
0679 |     }
0680 |     
0681 |     .step-header {
0682 |         flex-direction: column;
0683 |         align-items: flex-start;
0684 |     }
0685 | }
0686 | 
0687 | /* === ANIMATIONS === */
0688 | @keyframes fadeIn {
0689 |     from {
0690 |         opacity: 0;
0691 |         transform: translateY(20px);
0692 |     }
0693 |     to {
0694 |         opacity: 1;
0695 |         transform: translateY(0);
0696 |     }
0697 | }
0698 | 
0699 | .section {
0700 |     animation: fadeIn 0.6s ease-out;
0701 | }
0702 | 
0703 | /* === PRINT STYLES === */
0704 | @media print {
0705 |     body {
0706 |         background: white;
0707 |     }
0708 |     
0709 |     .container {
0710 |         box-shadow: none;
0711 |         margin: 0;
0712 |     }
0713 |     
0714 |     .header {
0715 |         background: #4f46e5 !important;
0716 |         -webkit-print-color-adjust: exact;
0717 |         color-adjust: exact;
0718 |     }
0719 |     
0720 |     .technical-details {
0721 |         border: 1px solid #ccc;
0722 |     }
0723 |     
0724 |     .details-content {
0725 |         display: block !important;
0726 |     }
0727 |     
0728 |     .details-toggle {
0729 |         display: none;
0730 |     }
0731 |     
0732 |     .vulnerability-card {
0733 |         break-inside: avoid;
0734 |         page-break-inside: avoid;
0735 |         margin-bottom: 1rem;
0736 |     }
0737 | }
0738 | </style>
```

---

### adapters\output\templates\__init__.py

**Ruta:** `adapters\output\templates\__init__.py`

```py
```

---

### adapters\processing\chunker.py

**Ruta:** `adapters\processing\chunker.py`

```py
0001 | # adapters/processing/chunker.py
0002 | """
0003 | Chunker - Simplified
0004 | ===================
0005 | 
0006 | Responsibilities:
0007 | - Split large vulnerability lists
0008 | - Apply intelligent chunking strategies
0009 | - Handle overlap for context
0010 | """
0011 | 
0012 | import logging
0013 | import math
0014 | from typing import List, Optional
0015 | from dataclasses import dataclass
0016 | 
0017 | from core.models import ScanResult, Vulnerability
0018 | 
0019 | logger = logging.getLogger(__name__)
0020 | 
0021 | 
0022 | # ════════════════════════════════════════════════════════════════════
0023 | # DATA CLASSES
0024 | # ════════════════════════════════════════════════════════════════════
0025 | 
0026 | @dataclass
0027 | class ChunkMetadata:
0028 |     """Metadata for a chunk"""
0029 |     id: int
0030 |     strategy: str
0031 |     total_chunks: int
0032 |     vulnerability_count: int
0033 |     estimated_size_bytes: int
0034 |     has_overlap: bool = False
0035 | 
0036 | 
0037 | @dataclass
0038 | class VulnerabilityChunk:
0039 |     """Single chunk of vulnerabilities"""
0040 |     id: int
0041 |     vulnerabilities: List[Vulnerability]
0042 |     metadata: ChunkMetadata
0043 |     
0044 |     @property
0045 |     def size_estimate(self) -> int:
0046 |         """Quick size estimation"""
0047 |         return sum(
0048 |             len(v.title) + len(v.description) + len(v.code_snippet or "")
0049 |             for v in self.vulnerabilities
0050 |         )
0051 | 
0052 | 
0053 | # ════════════════════════════════════════════════════════════════════
0054 | # CHUNKER
0055 | # ════════════════════════════════════════════════════════════════════
0056 | 
0057 | class OptimizedChunker:
0058 |     """Intelligent chunker with multiple strategies"""
0059 |     
0060 |     def __init__(self, config: dict):
0061 |         """
0062 |         Initialize chunker
0063 |         
0064 |         Args:
0065 |             config: Configuration dict with:
0066 |                 - max_vulnerabilities_per_chunk
0067 |                 - max_size_bytes
0068 |                 - overlap_vulnerabilities
0069 |                 - min_chunk_size
0070 |         """
0071 |         self.max_vulns = config.get("max_vulnerabilities_per_chunk", 5)
0072 |         self.max_bytes = config.get("max_size_bytes", 8000)
0073 |         self.overlap = config.get("overlap_vulnerabilities", 1)
0074 |         self.min_size = config.get("min_chunk_size", 3)
0075 |     
0076 |     def should_chunk(self, scan_result: ScanResult) -> bool:
0077 |         """
0078 |         Determine if chunking is needed
0079 |         
0080 |         Args:
0081 |             scan_result: Scan result with vulnerabilities
0082 |         
0083 |         Returns:
0084 |             True if chunking is recommended
0085 |         """
0086 |         vuln_count = len(scan_result.vulnerabilities)
0087 |         
0088 |         # Check count threshold
0089 |         if vuln_count > self.max_vulns:
0090 |             logger.info(f"📦 Chunking needed: {vuln_count} > {self.max_vulns} vulnerabilities")
0091 |             return True
0092 |         
0093 |         # Check size threshold
0094 |         estimated_size = self._estimate_total_size(scan_result.vulnerabilities)
0095 |         if estimated_size > self.max_bytes:
0096 |             logger.info(f"📦 Chunking needed: {estimated_size} > {self.max_bytes} bytes")
0097 |             return True
0098 |         
0099 |         return False
0100 |     
0101 |     def create_chunks(self, scan_result: ScanResult) -> List[VulnerabilityChunk]:
0102 |         """
0103 |         Create chunks from scan result
0104 |         
0105 |         Args:
0106 |             scan_result: Scan result to chunk
0107 |         
0108 |         Returns:
0109 |             List of vulnerability chunks
0110 |         """
0111 |         vulnerabilities = scan_result.vulnerabilities
0112 |         
0113 |         if not vulnerabilities:
0114 |             return []
0115 |         
0116 |         # No chunking needed
0117 |         if not self.should_chunk(scan_result):
0118 |             return [self._create_single_chunk(vulnerabilities)]
0119 |         
0120 |         # Select strategy
0121 |         strategy = self._select_strategy(vulnerabilities)
0122 |         
0123 |         try:
0124 |             if strategy == "by_count":
0125 |                 return self._chunk_by_count(vulnerabilities)
0126 |             else:  # by_size
0127 |                 return self._chunk_by_size(vulnerabilities)
0128 |         except Exception as e:
0129 |             logger.error(f"Chunking failed: {e}, using emergency chunking")
0130 |             return self._emergency_chunking(vulnerabilities)
0131 |     
0132 |     # ════════════════════════════════════════════════════════════════
0133 |     # PRIVATE METHODS
0134 |     # ════════════════════════════════════════════════════════════════
0135 |     
0136 |     def _create_single_chunk(
0137 |         self,
0138 |         vulnerabilities: List[Vulnerability]
0139 |     ) -> VulnerabilityChunk:
0140 |         """Create single chunk (no splitting)"""
0141 |         return VulnerabilityChunk(
0142 |             id=1,
0143 |             vulnerabilities=vulnerabilities,
0144 |             metadata=ChunkMetadata(
0145 |                 id=1,
0146 |                 strategy="no_chunking",
0147 |                 total_chunks=1,
0148 |                 vulnerability_count=len(vulnerabilities),
0149 |                 estimated_size_bytes=self._estimate_total_size(vulnerabilities)
0150 |             )
0151 |         )
0152 |     
0153 |     def _select_strategy(self, vulnerabilities: List[Vulnerability]) -> str:
0154 |         """Select optimal chunking strategy"""
0155 |         avg_desc_length = sum(
0156 |             len(v.description) for v in vulnerabilities
0157 |         ) / len(vulnerabilities)
0158 |         
0159 |         # Long descriptions → chunk by size
0160 |         if avg_desc_length > 300:
0161 |             return "by_size"
0162 |         
0163 |         return "by_count"
0164 |     
0165 |     def _chunk_by_count(
0166 |         self,
0167 |         vulnerabilities: List[Vulnerability]
0168 |     ) -> List[VulnerabilityChunk]:
0169 |         """Chunk by vulnerability count with overlap"""
0170 |         chunks = []
0171 |         chunk_size = self.max_vulns
0172 |         step = chunk_size - self.overlap
0173 |         
0174 |         for i in range(0, len(vulnerabilities), step):
0175 |             chunk_vulns = vulnerabilities[i:i + chunk_size]
0176 |             
0177 |             # Merge small final chunk into previous
0178 |             if i > 0 and len(chunk_vulns) < self.min_size and chunks:
0179 |                 chunks[-1].vulnerabilities.extend(chunk_vulns)
0180 |                 chunks[-1].metadata.vulnerability_count += len(chunk_vulns)
0181 |                 break
0182 |             
0183 |             chunk = VulnerabilityChunk(
0184 |                 id=len(chunks) + 1,
0185 |                 vulnerabilities=chunk_vulns,
0186 |                 metadata=ChunkMetadata(
0187 |                     id=len(chunks) + 1,
0188 |                     strategy="by_count",
0189 |                     total_chunks=0,  # Updated later
0190 |                     vulnerability_count=len(chunk_vulns),
0191 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns),
0192 |                     has_overlap=(i > 0 and self.overlap > 0)
0193 |                 )
0194 |             )
0195 |             chunks.append(chunk)
0196 |         
0197 |         # Update total_chunks
0198 |         for chunk in chunks:
0199 |             chunk.metadata.total_chunks = len(chunks)
0200 |         
0201 |         logger.info(f"✅ Created {len(chunks)} chunks (by_count)")
0202 |         return chunks
0203 |     
0204 |     def _chunk_by_size(
0205 |         self,
0206 |         vulnerabilities: List[Vulnerability]
0207 |     ) -> List[VulnerabilityChunk]:
0208 |         """Chunk by size with overlap"""
0209 |         chunks = []
0210 |         current_vulns = []
0211 |         current_size = 0
0212 |         
0213 |         for vuln in vulnerabilities:
0214 |             vuln_size = self._estimate_vuln_size(vuln)
0215 |             
0216 |             # Create new chunk if size exceeded
0217 |             if current_size + vuln_size > self.max_bytes and current_vulns:
0218 |                 chunk = VulnerabilityChunk(
0219 |                     id=len(chunks) + 1,
0220 |                     vulnerabilities=current_vulns.copy(),
0221 |                     metadata=ChunkMetadata(
0222 |                         id=len(chunks) + 1,
0223 |                         strategy="by_size",
0224 |                         total_chunks=0,
0225 |                         vulnerability_count=len(current_vulns),
0226 |                         estimated_size_bytes=current_size
0227 |                     )
0228 |                 )
0229 |                 chunks.append(chunk)
0230 |                 
0231 |                 # Start new chunk with overlap
0232 |                 overlap_vulns = current_vulns[-self.overlap:] if self.overlap > 0 else []
0233 |                 current_vulns = overlap_vulns + [vuln]
0234 |                 current_size = sum(
0235 |                     self._estimate_vuln_size(v) for v in current_vulns
0236 |                 )
0237 |             else:
0238 |                 current_vulns.append(vuln)
0239 |                 current_size += vuln_size
0240 |         
0241 |         # Add final chunk
0242 |         if current_vulns:
0243 |             chunk = VulnerabilityChunk(
0244 |                 id=len(chunks) + 1,
0245 |                 vulnerabilities=current_vulns,
0246 |                 metadata=ChunkMetadata(
0247 |                     id=len(chunks) + 1,
0248 |                     strategy="by_size",
0249 |                     total_chunks=0,
0250 |                     vulnerability_count=len(current_vulns),
0251 |                     estimated_size_bytes=current_size
0252 |                 )
0253 |             )
0254 |             chunks.append(chunk)
0255 |         
0256 |         # Update total_chunks
0257 |         for chunk in chunks:
0258 |             chunk.metadata.total_chunks = len(chunks)
0259 |         
0260 |         logger.info(f"✅ Created {len(chunks)} chunks (by_size)")
0261 |         return chunks
0262 |     
0263 |     def _emergency_chunking(
0264 |         self,
0265 |         vulnerabilities: List[Vulnerability]
0266 |     ) -> List[VulnerabilityChunk]:
0267 |         """Emergency chunking with very small chunks"""
0268 |         logger.warning("⚠️  Using emergency chunking (3 vulns per chunk)")
0269 |         
0270 |         emergency_size = 3
0271 |         chunks = []
0272 |         
0273 |         for i in range(0, len(vulnerabilities), emergency_size):
0274 |             chunk_vulns = vulnerabilities[i:i + emergency_size]
0275 |             
0276 |             chunk = VulnerabilityChunk(
0277 |                 id=len(chunks) + 1,
0278 |                 vulnerabilities=chunk_vulns,
0279 |                 metadata=ChunkMetadata(
0280 |                     id=len(chunks) + 1,
0281 |                     strategy="emergency",
0282 |                     total_chunks=math.ceil(len(vulnerabilities) / emergency_size),
0283 |                     vulnerability_count=len(chunk_vulns),
0284 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns)
0285 |                 )
0286 |             )
0287 |             chunks.append(chunk)
0288 |         
0289 |         return chunks
0290 |     
0291 |     def _estimate_total_size(self, vulnerabilities: List[Vulnerability]) -> int:
0292 |         """Estimate total size of vulnerability list"""
0293 |         return sum(self._estimate_vuln_size(v) for v in vulnerabilities)
0294 |     
0295 |     def _estimate_vuln_size(self, vulnerability: Vulnerability) -> int:
0296 |         """Estimate size of single vulnerability"""
0297 |         base_size = len(vulnerability.title) + len(vulnerability.description)
0298 |         code_size = len(vulnerability.code_snippet or "")
0299 |         
0300 |         # Factor for JSON metadata (1.3x)
0301 |         return int((base_size + code_size) * 1.3)
```

---

### adapters\processing\__init__.py

**Ruta:** `adapters\processing\__init__.py`

```py
```

---

### application\cli.py

**Ruta:** `application\cli.py`

```py
0001 | # application/cli.py
0002 | """
0003 | CLI Interface - Clean & User-Friendly
0004 | =====================================
0005 | 
0006 | Responsibilities:
0007 | - Parse command-line arguments
0008 | - Display user-friendly messages
0009 | - Handle errors gracefully
0010 | - Orchestrate analysis workflow
0011 | """
0012 | 
0013 | import asyncio
0014 | import sys
0015 | from pathlib import Path
0016 | from typing import Optional
0017 | import click
0018 | 
0019 | from application.factory import create_factory
0020 | from application.use_cases import AnalysisUseCase, CLIUseCase
0021 | from infrastructure.config import settings
0022 | 
0023 | # ════════════════════════════════════════════════════════════════════
0024 | # CLI GROUP
0025 | # ════════════════════════════════════════════════════════════════════
0026 | 
0027 | @click.group()
0028 | @click.version_option("3.0.0", prog_name="Security Analysis Platform")
0029 | def cli():
0030 |     """🛡️  Security Analysis Platform v3.0 - LLM-Powered Vulnerability Analysis"""
0031 |     pass
0032 | 
0033 | 
0034 | # ════════════════════════════════════════════════════════════════════
0035 | # ANALYZE COMMAND
0036 | # ════════════════════════════════════════════════════════════════════
0037 | 
0038 | @cli.command()
0039 | @click.argument('input_file', type=click.Path(exists=True))
0040 | @click.option('-o', '--output', default='security_report.html', help='Output HTML file')
0041 | @click.option('-l', '--language', type=str, help='Programming language (python, java, abap)')
0042 | @click.option('-v', '--verbose', is_flag=True, help='Verbose output')
0043 | @click.option('--basic-mode', is_flag=True, help='Run without LLM analysis')
0044 | # LLM Provider Options
0045 | @click.option(
0046 |     '--llm-provider',
0047 |     type=click.Choice(['openai', 'watsonx'], case_sensitive=False),
0048 |     help='LLM provider (overrides env config)'
0049 | )
0050 | @click.option('--llm-model', type=str, help='Specific model (e.g., gpt-4o, gpt-4-turbo)')
0051 | # Feature Flags
0052 | @click.option('--no-dedup', is_flag=True, help='Disable duplicate removal')
0053 | @click.option(
0054 |     '--dedup-strategy',
0055 |     type=click.Choice(['strict', 'moderate', 'loose'], case_sensitive=False),
0056 |     default='moderate',
0057 |     help='Deduplication strategy'
0058 | )
0059 | @click.option('--force-chunking', is_flag=True, help='Force chunking for large datasets')
0060 | @click.option('--disable-chunking', is_flag=True, help='Disable chunking completely')
0061 | def analyze(
0062 |     input_file, output, language, verbose, basic_mode,
0063 |     llm_provider, llm_model,
0064 |     no_dedup, dedup_strategy,
0065 |     force_chunking, disable_chunking
0066 | ):
0067 |     """
0068 |     Analyze security vulnerabilities from SAST tool output
0069 |     
0070 |     Example:
0071 |         security-analyzer analyze vulnerabilities.json
0072 |         security-analyzer analyze scan.json --llm-provider openai -o report.html
0073 |     """
0074 |     # Display header
0075 |     click.echo("="*60)
0076 |     click.echo("🛡️  Security Analysis Platform v3.0")
0077 |     click.echo("="*60)
0078 |     
0079 |     # Display configuration
0080 |     click.echo(f"\n📁 Input:  {Path(input_file).name}")
0081 |     click.echo(f"📄 Output: {output}")
0082 |     
0083 |     if language:
0084 |         click.echo(f"💻 Language: {language}")
0085 |     
0086 |     # LLM Configuration
0087 |     if llm_provider:
0088 |         click.echo(f"🤖 LLM Provider: {llm_provider.upper()}")
0089 |     if llm_model:
0090 |         click.echo(f"📦 LLM Model: {llm_model}")
0091 |     
0092 |     # Feature flags
0093 |     if no_dedup:
0094 |         click.echo("🔄 Deduplication: DISABLED")
0095 |     else:
0096 |         click.echo(f"🔄 Deduplication: {dedup_strategy.upper()}")
0097 |     
0098 |     if basic_mode:
0099 |         click.echo("⚡ Mode: BASIC (no LLM)")
0100 |     
0101 |     click.echo("")
0102 |     
0103 |     try:
0104 |         # Run analysis
0105 |         success = asyncio.run(_run_analysis(
0106 |             input_file=input_file,
0107 |             output=output,
0108 |             language=language,
0109 |             verbose=verbose,
0110 |             basic_mode=basic_mode,
0111 |             llm_provider=llm_provider,
0112 |             llm_model=llm_model,
0113 |             enable_dedup=not no_dedup,
0114 |             dedup_strategy=dedup_strategy,
0115 |             force_chunking=force_chunking,
0116 |             disable_chunking=disable_chunking
0117 |         ))
0118 |         
0119 |         sys.exit(0 if success else 1)
0120 |         
0121 |     except KeyboardInterrupt:
0122 |         click.echo("\n\n🛑 Analysis interrupted by user")
0123 |         sys.exit(1)
0124 |     except Exception as e:
0125 |         click.echo(f"\n❌ Fatal error: {e}")
0126 |         if verbose:
0127 |             import traceback
0128 |             traceback.print_exc()
0129 |         sys.exit(1)
0130 | 
0131 | 
0132 | async def _run_analysis(
0133 |     input_file: str,
0134 |     output: str,
0135 |     language: Optional[str],
0136 |     verbose: bool,
0137 |     basic_mode: bool,
0138 |     llm_provider: Optional[str],
0139 |     llm_model: Optional[str],
0140 |     enable_dedup: bool,
0141 |     dedup_strategy: str,
0142 |     force_chunking: bool,
0143 |     disable_chunking: bool
0144 | ) -> bool:
0145 |     """Execute analysis workflow"""
0146 |     
0147 |     try:
0148 |         # Create factory with overrides
0149 |         factory = create_factory(
0150 |             llm_provider_override=llm_provider,
0151 |             llm_model_override=llm_model
0152 |         )
0153 |         
0154 |         # Configure deduplication
0155 |         factory.enable_dedup = enable_dedup
0156 |         factory.dedup_strategy = dedup_strategy
0157 |         
0158 |         # Check LLM availability
0159 |         if not basic_mode and not settings.has_llm_provider and not llm_provider:
0160 |             click.echo("⚠️  No LLM configured - switching to basic mode")
0161 |             basic_mode = True
0162 |         
0163 |         # Display active provider
0164 |         if not basic_mode:
0165 |             active_provider = factory._get_effective_provider()
0166 |             click.echo(f"✅ Using LLM: {active_provider.upper()}\n")
0167 |         
0168 |         # Create services
0169 |         analysis_use_case = AnalysisUseCase(
0170 |             scanner_service=factory.create_scanner_service(),
0171 |             triage_service=factory.create_triage_service(),
0172 |             remediation_service=factory.create_remediation_service(),
0173 |             reporter_service=factory.create_reporter_service(),
0174 |             chunker=factory.create_chunker(),
0175 |             metrics=factory.get_metrics()
0176 |         )
0177 |         
0178 |         # Create CLI use case
0179 |         cli_use_case = CLIUseCase(analysis_use_case)
0180 |         
0181 |         # Execute
0182 |         return await cli_use_case.execute_cli_analysis(
0183 |             input_file=input_file,
0184 |             output_file=output,
0185 |             language=language,
0186 |             verbose=verbose,
0187 |             disable_llm=basic_mode,
0188 |             force_chunking=force_chunking,
0189 |             disable_chunking=disable_chunking
0190 |         )
0191 |         
0192 |     except Exception as e:
0193 |         click.echo(f"❌ Analysis failed: {e}")
0194 |         if verbose:
0195 |             import traceback
0196 |             traceback.print_exc()
0197 |         return False
0198 | 
0199 | 
0200 | # ════════════════════════════════════════════════════════════════════
0201 | # VALIDATE COMMAND
0202 | # ════════════════════════════════════════════════════════════════════
0203 | 
0204 | @cli.command()
0205 | @click.argument('input_file', type=click.Path(exists=True))
0206 | def validate(input_file):
0207 |     """
0208 |     Validate input file format and structure
0209 |     
0210 |     Example:
0211 |         security-analyzer validate vulnerabilities.json
0212 |     """
0213 |     click.echo("="*60)
0214 |     click.echo("🔍 Validating Input File")
0215 |     click.echo("="*60)
0216 |     click.echo(f"\nFile: {input_file}\n")
0217 |     
0218 |     try:
0219 |         from core.services.scanner import ScannerService
0220 |         
0221 |         scanner = ScannerService()
0222 |         
0223 |         # Basic validation
0224 |         scanner._validate_file(input_file)
0225 |         click.echo("✅ File validation: PASSED")
0226 |         
0227 |         # Load and analyze
0228 |         raw_data = scanner._load_file(input_file)
0229 |         click.echo("✅ JSON format: VALID")
0230 |         
0231 |         # Structure analysis
0232 |         if isinstance(raw_data, list):
0233 |             click.echo(f"📊 Format: List with {len(raw_data)} items")
0234 |         elif isinstance(raw_data, dict):
0235 |             keys = list(raw_data.keys())[:5]
0236 |             click.echo(f"📊 Format: Object with keys: {keys}")
0237 |             
0238 |             # Look for vulnerabilities
0239 |             for key in ['findings', 'vulnerabilities', 'issues', 'results']:
0240 |                 if key in raw_data and isinstance(raw_data[key], list):
0241 |                     count = len(raw_data[key])
0242 |                     click.echo(f"🎯 Found {count} items in '{key}'")
0243 |                     break
0244 |         
0245 |         # Parse test
0246 |         vulns = scanner.parser.parse(raw_data)
0247 |         click.echo(f"\n✅ Parsing test: Found {len(vulns)} vulnerabilities")
0248 |         
0249 |         if vulns:
0250 |             # Severity distribution
0251 |             from collections import Counter
0252 |             severity_dist = Counter(v.severity.value for v in vulns)
0253 |             
0254 |             click.echo("\n📈 Severity Distribution:")
0255 |             for severity, count in severity_dist.items():
0256 |                 click.echo(f"   {severity}: {count}")
0257 |             
0258 |             # CVSS check
0259 |             cvss_scores = [
0260 |                 v.meta.get('cvss_score') for v in vulns
0261 |                 if v.meta.get('cvss_score') is not None
0262 |             ]
0263 |             
0264 |             if cvss_scores:
0265 |                 click.echo(f"\n📊 CVSS Scores:")
0266 |                 click.echo(f"   Count: {len(cvss_scores)}")
0267 |                 click.echo(f"   Min: {min(cvss_scores):.1f}")
0268 |                 click.echo(f"   Max: {max(cvss_scores):.1f}")
0269 |                 click.echo(f"   Avg: {sum(cvss_scores)/len(cvss_scores):.1f}")
0270 |             else:
0271 |                 click.echo("\n⚠️  No CVSS scores found")
0272 |         
0273 |         click.echo("\n" + "="*60)
0274 |         click.echo("✅ Validation Complete")
0275 |         click.echo("="*60)
0276 |         
0277 |     except Exception as e:
0278 |         click.echo(f"\n❌ Validation failed: {e}")
0279 |         sys.exit(1)
0280 | 
0281 | 
0282 | # ════════════════════════════════════════════════════════════════════
0283 | # EXAMPLES COMMAND
0284 | # ════════════════════════════════════════════════════════════════════
0285 | 
0286 | @cli.command()
0287 | def examples():
0288 |     """Show usage examples"""
0289 |     click.echo("""
0290 | ╔════════════════════════════════════════════════════════════════╗
0291 | ║  🎓 Security Analysis Platform - Usage Examples               ║
0292 | ╚════════════════════════════════════════════════════════════════╝
0293 | 
0294 | 📝 BASIC USAGE:
0295 |    security-analyzer analyze vulnerabilities.json
0296 | 
0297 | 🎯 WITH LLM PROVIDER:
0298 |    # Use OpenAI
0299 |    security-analyzer analyze scan.json --llm-provider openai
0300 |    
0301 |    # Use WatsonX
0302 |    security-analyzer analyze scan.json --llm-provider watsonx
0303 |    
0304 |    # Specify model
0305 |    security-analyzer analyze scan.json \\
0306 |        --llm-provider openai \\
0307 |        --llm-model gpt-4-turbo
0308 | 
0309 | 💻 LANGUAGE-SPECIFIC:
0310 |    security-analyzer analyze abap_scan.json --language abap
0311 |    security-analyzer analyze py_scan.json --language python
0312 | 
0313 | 🔧 CUSTOM OUTPUT:
0314 |    security-analyzer analyze scan.json -o my_report.html
0315 | 
0316 | 🔄 DEDUPLICATION:
0317 |    # Strict (keep most findings)
0318 |    security-analyzer analyze scan.json --dedup-strategy strict
0319 |    
0320 |    # Moderate (balanced - default)
0321 |    security-analyzer analyze scan.json --dedup-strategy moderate
0322 |    
0323 |    # Loose (aggressive dedup)
0324 |    security-analyzer analyze scan.json --dedup-strategy loose
0325 |    
0326 |    # Disable deduplication
0327 |    security-analyzer analyze scan.json --no-dedup
0328 | 
0329 | ⚡ MODES:
0330 |    # Basic mode (no LLM)
0331 |    security-analyzer analyze scan.json --basic-mode
0332 |    
0333 |    # Verbose output
0334 |    security-analyzer analyze scan.json --verbose
0335 | 
0336 | 🧩 CHUNKING:
0337 |    # Force chunking (for large files)
0338 |    security-analyzer analyze large_scan.json --force-chunking
0339 |    
0340 |    # Disable chunking
0341 |    security-analyzer analyze scan.json --disable-chunking
0342 | 
0343 | 🔍 VALIDATION:
0344 |    security-analyzer validate vulnerabilities.json
0345 | 
0346 | 📚 COMPLETE EXAMPLE:
0347 |    security-analyzer analyze production_scan.json \\
0348 |        --llm-provider openai \\
0349 |        --llm-model gpt-4o \\
0350 |        --language java \\
0351 |        --dedup-strategy moderate \\
0352 |        -o prod_report.html \\
0353 |        --verbose
0354 | 
0355 | 🔑 ENVIRONMENT VARIABLES:
0356 |    OPENAI_API_KEY=sk-proj-xxxxx           # OpenAI key
0357 |    RESEARCH_API_KEY=your_key              # WatsonX key
0358 |    LLM_PRIMARY_PROVIDER=openai            # Default provider
0359 |    LOG_LEVEL=INFO                         # Logging level
0360 |    CACHE_ENABLED=true                     # Enable caching
0361 |    DEDUP_STRATEGY=moderate                # Default dedup
0362 | 
0363 | 💡 TIPS:
0364 |    • Use --verbose for detailed logs
0365 |    • Validate files before analysis
0366 |    • OpenAI is faster, WatsonX is cost-effective
0367 |    • Deduplication reduces noise significantly
0368 |    • Cache speeds up repeated analysis
0369 | 
0370 | 📖 Documentation: https://github.com/your-org/security-analyzer
0371 | """)
0372 | 
0373 | 
0374 | # ════════════════════════════════════════════════════════════════════
0375 | # CONFIG COMMAND
0376 | # ════════════════════════════════════════════════════════════════════
0377 | 
0378 | @cli.command()
0379 | def config():
0380 |     """Display current configuration"""
0381 |     from infrastructure.config import settings
0382 |     
0383 |     click.echo("="*60)
0384 |     click.echo("⚙️  Current Configuration")
0385 |     click.echo("="*60)
0386 |     
0387 |     # LLM Configuration
0388 |     click.echo("\n🤖 LLM Providers:")
0389 |     click.echo(f"   OpenAI:  {'✅ Configured' if settings.openai_api_key else '❌ Not configured'}")
0390 |     click.echo(f"   WatsonX: {'✅ Configured' if settings.watsonx_api_key else '❌ Not configured'}")
0391 |     
0392 |     if settings.has_llm_provider:
0393 |         try:
0394 |             provider = settings.get_available_llm_provider()
0395 |             click.echo(f"\n   Active Provider: {provider.upper()}")
0396 |             config = settings.get_llm_config(provider)
0397 |             click.echo(f"   Model: {config['model']}")
0398 |             click.echo(f"   Temperature: {config['temperature']}")
0399 |             click.echo(f"   Max Tokens: {config['max_tokens']}")
0400 |             click.echo(f"   Timeout: {config['timeout']}s")
0401 |         except Exception as e:
0402 |             click.echo(f"\n   ⚠️  Error: {e}")
0403 |     
0404 |     # Features
0405 |     click.echo("\n🔧 Features:")
0406 |     click.echo(f"   Cache: {'✅ Enabled' if settings.cache_enabled else '❌ Disabled'}")
0407 |     click.echo(f"   Deduplication: {'✅ Enabled' if settings.dedup_enabled else '❌ Disabled'}")
0408 |     click.echo(f"   Metrics: {'✅ Enabled' if settings.metrics_enabled else '❌ Disabled'}")
0409 |     
0410 |     # Cache
0411 |     if settings.cache_enabled:
0412 |         click.echo(f"\n💾 Cache:")
0413 |         click.echo(f"   Directory: {settings.cache_directory}")
0414 |         click.echo(f"   TTL: {settings.cache_ttl_hours} hours")
0415 |     
0416 |     # Chunking
0417 |     click.echo(f"\n🧩 Chunking:")
0418 |     click.echo(f"   Max vulns/chunk: {settings.chunking_max_vulnerabilities}")
0419 |     
0420 |     # Logging
0421 |     click.echo(f"\n📝 Logging:")
0422 |     click.echo(f"   Level: {settings.log_level}")
0423 |     
0424 |     click.echo("\n" + "="*60)
0425 | 
0426 | 
0427 | # ════════════════════════════════════════════════════════════════════
0428 | # TEST COMMAND
0429 | # ════════════════════════════════════════════════════════════════════
0430 | 
0431 | @cli.command()
0432 | @click.option('--provider', type=click.Choice(['openai', 'watsonx']), help='Test specific provider')
0433 | def test(provider):
0434 |     """Test LLM connection"""
0435 |     from infrastructure.llm.client import LLMClient
0436 |     
0437 |     click.echo("="*60)
0438 |     click.echo("🧪 Testing LLM Connection")
0439 |     click.echo("="*60)
0440 |     
0441 |     # Determine provider
0442 |     if provider:
0443 |         test_provider = provider
0444 |     else:
0445 |         if not settings.has_llm_provider:
0446 |             click.echo("\n❌ No LLM provider configured")
0447 |             click.echo("Set OPENAI_API_KEY or RESEARCH_API_KEY")
0448 |             sys.exit(1)
0449 |         test_provider = settings.get_available_llm_provider()
0450 |     
0451 |     click.echo(f"\n🤖 Testing: {test_provider.upper()}\n")
0452 |     
0453 |     try:
0454 |         # Create client
0455 |         client = LLMClient(llm_provider=test_provider)
0456 |         click.echo(f"✅ Client created")
0457 |         click.echo(f"   Model: {client.model_name}")
0458 |         
0459 |         # Test message
0460 |         async def run_test():
0461 |             test_message = "Return only this JSON: {\"status\": \"ok\", \"message\": \"test successful\"}"
0462 |             
0463 |             click.echo(f"\n📡 Sending test request...")
0464 |             response = await client._call_api(test_message, temperature=0.0)
0465 |             
0466 |             click.echo(f"✅ Response received ({len(response)} chars)")
0467 |             click.echo(f"\nPreview:\n{response[:200]}...")
0468 |         
0469 |         asyncio.run(run_test())
0470 |         
0471 |         click.echo("\n" + "="*60)
0472 |         click.echo("✅ Test Successful")
0473 |         click.echo("="*60)
0474 |         
0475 |     except Exception as e:
0476 |         click.echo(f"\n❌ Test failed: {e}")
0477 |         sys.exit(1)
0478 | 
0479 | 
0480 | # ════════════════════════════════════════════════════════════════════
0481 | # MAIN ENTRY POINT
0482 | # ════════════════════════════════════════════════════════════════════
0483 | 
0484 | if __name__ == '__main__':
0485 |     cli()
```

---

### application\factory.py

**Ruta:** `application\factory.py`

```py
0001 | # application/factory.py
0002 | """
0003 | Service Factory - Clean & Simple
0004 | ================================
0005 | 
0006 | Responsibilities:
0007 | - Create and configure services
0008 | - Handle provider overrides from CLI
0009 | - Manage shared dependencies (cache, metrics)
0010 | """
0011 | 
0012 | import logging
0013 | from typing import Optional
0014 | 
0015 | from core.services.scanner import ScannerService
0016 | from core.services.triage import TriageService
0017 | from core.services.remediation import RemediationService
0018 | from core.services.reporter import ReporterService
0019 | from infrastructure.llm.client import LLMClient
0020 | from infrastructure.cache import AnalysisCache
0021 | from infrastructure.config import settings
0022 | from adapters.processing.chunker import OptimizedChunker
0023 | from shared.metrics import MetricsCollector
0024 | from shared.logger import setup_logging
0025 | 
0026 | logger = logging.getLogger(__name__)
0027 | 
0028 | 
0029 | class ServiceFactory:
0030 |     """Simplified service factory with clean dependencies"""
0031 |     
0032 |     def __init__(
0033 |         self,
0034 |         enable_cache: bool = True,
0035 |         log_level: str = "INFO",
0036 |         llm_provider_override: Optional[str] = None,
0037 |         llm_model_override: Optional[str] = None
0038 |     ):
0039 |         # Setup logging
0040 |         setup_logging(log_level)
0041 |         
0042 |         # Store settings reference
0043 |         self.settings = settings
0044 |         
0045 |         # Overrides from CLI
0046 |         self.llm_provider_override = llm_provider_override
0047 |         self.llm_model_override = llm_model_override
0048 |         
0049 |         # Shared components
0050 |         self.metrics = MetricsCollector() if settings.metrics_enabled else None
0051 |         self.cache = self._create_cache() if enable_cache else None
0052 |         
0053 |         # Deduplication config (set by CLI)
0054 |         self.enable_dedup = True
0055 |         self.dedup_strategy = 'moderate'
0056 |         
0057 |         # Debug mode
0058 |         self.debug_mode = False
0059 |         
0060 |         # Validate and log
0061 |         self._log_initialization()
0062 |     
0063 |     def _create_cache(self) -> Optional[AnalysisCache]:
0064 |         """Create cache instance"""
0065 |         try:
0066 |             return AnalysisCache(
0067 |                 cache_dir=settings.cache_directory,
0068 |                 ttl_hours=settings.cache_ttl_hours
0069 |             )
0070 |         except Exception as e:
0071 |             logger.warning(f"Cache creation failed: {e}")
0072 |             return None
0073 |     
0074 |     def _log_initialization(self):
0075 |         """Log factory initialization"""
0076 |         provider = self._get_effective_provider()
0077 |         logger.info(f"🏭 Factory initialized: {provider}")
0078 |         
0079 |         if self.llm_provider_override:
0080 |             logger.info(f"   Provider override: {self.llm_provider_override}")
0081 |         
0082 |         if self.llm_model_override:
0083 |             logger.info(f"   Model override: {self.llm_model_override}")
0084 |     
0085 |     def _get_effective_provider(self) -> str:
0086 |         """Get effective LLM provider"""
0087 |         if self.llm_provider_override:
0088 |             return self.llm_provider_override
0089 |         
0090 |         if settings.has_llm_provider:
0091 |             return settings.get_available_llm_provider()
0092 |         
0093 |         return "none"
0094 |     
0095 |     # ════════════════════════════════════════════════════════════════
0096 |     # SERVICE CREATION
0097 |     # ════════════════════════════════════════════════════════════════
0098 |     
0099 |     def create_scanner_service(self) -> ScannerService:
0100 |         """Create scanner service"""
0101 |         return ScannerService(
0102 |             cache=self.cache,
0103 |             enable_deduplication=self.enable_dedup,
0104 |             dedup_strategy=self.dedup_strategy
0105 |         )
0106 |     
0107 |     def create_llm_client(self) -> Optional[LLMClient]:
0108 |         """Create LLM client with overrides"""
0109 |         # Determine provider
0110 |         if self.llm_provider_override:
0111 |             provider = self.llm_provider_override
0112 |         else:
0113 |             if not settings.has_llm_provider:
0114 |                 return None
0115 |             provider = settings.get_available_llm_provider()
0116 |         
0117 |         try:
0118 |             # Create client
0119 |             client = LLMClient(
0120 |                 llm_provider=provider,
0121 |                 enable_debug=self.debug_mode
0122 |             )
0123 |             
0124 |             # Override model if specified
0125 |             if self.llm_model_override:
0126 |                 logger.info(f"🔄 Model override: {self.llm_model_override}")
0127 |                 client.model_name = self.llm_model_override
0128 |                 client.model[provider] = self.llm_model_override
0129 |             
0130 |             return client
0131 |             
0132 |         except Exception as e:
0133 |             logger.error(f"Failed to create LLM client: {e}")
0134 |             return None
0135 |     
0136 |     def create_triage_service(self) -> Optional[TriageService]:
0137 |         """Create triage service"""
0138 |         llm_client = self.create_llm_client()
0139 |         if not llm_client:
0140 |             return None
0141 |         
0142 |         return TriageService(llm_client=llm_client, metrics=self.metrics)
0143 |     
0144 |     def create_remediation_service(self) -> Optional[RemediationService]:
0145 |         """Create remediation service"""
0146 |         llm_client = self.create_llm_client()
0147 |         if not llm_client:
0148 |             return None
0149 |         
0150 |         return RemediationService(llm_client=llm_client, metrics=self.metrics)
0151 |     
0152 |     def create_reporter_service(self) -> ReporterService:
0153 |         """Create reporter service"""
0154 |         return ReporterService(metrics=self.metrics)
0155 |     
0156 |     def create_chunker(self) -> OptimizedChunker:
0157 |         """Create chunker"""
0158 |         return OptimizedChunker(settings.chunking_config)
0159 |     
0160 |     def get_metrics(self) -> Optional[MetricsCollector]:
0161 |         """Get metrics collector"""
0162 |         return self.metrics
0163 |     
0164 |     # ════════════════════════════════════════════════════════════════
0165 |     # DEBUG MODE
0166 |     # ════════════════════════════════════════════════════════════════
0167 |     
0168 |     def enable_debug_mode(self):
0169 |         """Enable debug mode"""
0170 |         self.debug_mode = True
0171 |         logger.info("🔍 Debug mode enabled")
0172 |     
0173 |     def disable_debug_mode(self):
0174 |         """Disable debug mode"""
0175 |         self.debug_mode = False
0176 |         logger.info("🔍 Debug mode disabled")
0177 | 
0178 | 
0179 | # ════════════════════════════════════════════════════════════════════
0180 | # FACTORY FUNCTIONS
0181 | # ════════════════════════════════════════════════════════════════════
0182 | 
0183 | def create_factory(
0184 |     llm_provider_override: Optional[str] = None,
0185 |     llm_model_override: Optional[str] = None
0186 | ) -> ServiceFactory:
0187 |     """
0188 |     Create factory with optional CLI overrides
0189 |     
0190 |     Args:
0191 |         llm_provider_override: Override provider (openai|watsonx)
0192 |         llm_model_override: Override model name
0193 |     
0194 |     Returns:
0195 |         Configured ServiceFactory
0196 |     """
0197 |     return ServiceFactory(
0198 |         enable_cache=settings.cache_enabled,
0199 |         log_level=settings.log_level,
0200 |         llm_provider_override=llm_provider_override,
0201 |         llm_model_override=llm_model_override
0202 |     )
0203 | 
0204 | 
0205 | def create_debug_factory(
0206 |     llm_provider_override: Optional[str] = None
0207 | ) -> ServiceFactory:
0208 |     """Create factory with debug enabled"""
0209 |     factory = create_factory(llm_provider_override=llm_provider_override)
0210 |     factory.enable_debug_mode()
0211 |     return factory
```

---

### application\use_cases.py

**Ruta:** `application\use_cases.py`

```py
0001 | # application/use_cases.py
0002 | """
0003 | Use Cases - Application Logic
0004 | =============================
0005 | 
0006 | Responsibilities:
0007 | - Orchestrate analysis workflow
0008 | - Handle errors gracefully
0009 | - Manage chunking decisions
0010 | - Generate reports
0011 | """
0012 | 
0013 | import asyncio
0014 | import logging
0015 | from pathlib import Path
0016 | from typing import Optional, List
0017 | from datetime import datetime
0018 | 
0019 | from core.models import AnalysisReport, ScanResult, Vulnerability
0020 | from core.services.scanner import ScannerService
0021 | from core.services.triage import TriageService
0022 | from core.services.remediation import RemediationService
0023 | from core.services.reporter import ReporterService
0024 | from adapters.processing.chunker import OptimizedChunker
0025 | from shared.metrics import MetricsCollector
0026 | 
0027 | logger = logging.getLogger(__name__)
0028 | 
0029 | 
0030 | # ════════════════════════════════════════════════════════════════════
0031 | # MAIN ANALYSIS USE CASE
0032 | # ════════════════════════════════════════════════════════════════════
0033 | 
0034 | class AnalysisUseCase:
0035 |     """Main analysis workflow orchestrator"""
0036 |     
0037 |     def __init__(
0038 |         self,
0039 |         scanner_service: ScannerService,
0040 |         triage_service: Optional[TriageService] = None,
0041 |         remediation_service: Optional[RemediationService] = None,
0042 |         reporter_service: Optional[ReporterService] = None,
0043 |         chunker: Optional[OptimizedChunker] = None,
0044 |         metrics: Optional[MetricsCollector] = None
0045 |     ):
0046 |         self.scanner = scanner_service
0047 |         self.triage = triage_service
0048 |         self.remediation = remediation_service
0049 |         self.reporter = reporter_service
0050 |         self.chunker = chunker
0051 |         self.metrics = metrics
0052 |     
0053 |     async def execute_full_analysis(
0054 |         self,
0055 |         file_path: str,
0056 |         output_file: Optional[str] = None,
0057 |         language: Optional[str] = None,
0058 |         tool_hint: Optional[str] = None,
0059 |         force_chunking: bool = False,
0060 |         disable_chunking: bool = False
0061 |     ) -> AnalysisReport:
0062 |         """
0063 |         Execute complete analysis pipeline
0064 |         
0065 |         Steps:
0066 |         1. Scan and normalize
0067 |         2. Triage with LLM (optional)
0068 |         3. Generate remediation plans (optional)
0069 |         4. Create report
0070 |         5. Generate HTML output (optional)
0071 |         """
0072 |         start_time = asyncio.get_event_loop().time()
0073 |         
0074 |         try:
0075 |             logger.info(f"🚀 Starting analysis: {file_path}")
0076 |             
0077 |             # Step 1: Scan
0078 |             scan_result = await self.scanner.scan_file(
0079 |                 file_path=file_path,
0080 |                 language=language,
0081 |                 tool_hint=tool_hint
0082 |             )
0083 |             
0084 |             if not scan_result.vulnerabilities:
0085 |                 logger.info("✅ No vulnerabilities found")
0086 |                 return self._create_clean_report(scan_result, start_time)
0087 |             
0088 |             # Step 2: Triage (if LLM available)
0089 |             triage_result = None
0090 |             if self.triage:
0091 |                 triage_result = await self._perform_triage(
0092 |                     scan_result, language, force_chunking, disable_chunking
0093 |                 )
0094 |             
0095 |             # Step 3: Remediation (if triage confirmed vulns)
0096 |             remediation_plans = []
0097 |             if self.remediation and triage_result:
0098 |                 confirmed_vulns = self._get_confirmed_vulns(
0099 |                     scan_result.vulnerabilities, triage_result
0100 |                 )
0101 |                 if confirmed_vulns:
0102 |                     remediation_plans = await self.remediation.generate_remediation_plans(
0103 |                         confirmed_vulns, language
0104 |                     )
0105 |             
0106 |             # Step 4: Create report
0107 |             total_time = asyncio.get_event_loop().time() - start_time
0108 |             report = self._create_report(
0109 |                 scan_result, triage_result, remediation_plans,
0110 |                 total_time, force_chunking, disable_chunking, language, tool_hint
0111 |             )
0112 |             
0113 |             # Step 5: Generate HTML (if requested)
0114 |             if output_file and self.reporter:
0115 |                 await self.reporter.generate_html_report(report, output_file)
0116 |             
0117 |             # Record metrics
0118 |             if self.metrics:
0119 |                 self.metrics.record_complete_analysis(
0120 |                     file_path=file_path,
0121 |                     vulnerability_count=len(scan_result.vulnerabilities),
0122 |                     confirmed_count=len(remediation_plans),
0123 |                     total_time=total_time,
0124 |                     chunking_used=self._was_chunking_used(scan_result, force_chunking, disable_chunking),
0125 |                     language=language,
0126 |                     success=True
0127 |                 )
0128 |             
0129 |             logger.info(f"✅ Analysis complete in {total_time:.2f}s")
0130 |             return report
0131 |             
0132 |         except Exception as e:
0133 |             total_time = asyncio.get_event_loop().time() - start_time
0134 |             if self.metrics:
0135 |                 self.metrics.record_complete_analysis(
0136 |                     file_path=file_path,
0137 |                     total_time=total_time,
0138 |                     success=False,
0139 |                     error=str(e)
0140 |                 )
0141 |             logger.error(f"❌ Analysis failed: {e}")
0142 |             raise
0143 |     
0144 |     async def execute_basic_analysis(
0145 |         self,
0146 |         file_path: str,
0147 |         output_file: Optional[str] = None,
0148 |         tool_hint: Optional[str] = None
0149 |     ) -> AnalysisReport:
0150 |         """Execute basic analysis without LLM"""
0151 |         start_time = asyncio.get_event_loop().time()
0152 |         
0153 |         logger.info(f"🚀 Starting basic analysis: {file_path}")
0154 |         
0155 |         # Only scan
0156 |         scan_result = await self.scanner.scan_file(
0157 |             file_path=file_path,
0158 |             tool_hint=tool_hint
0159 |         )
0160 |         
0161 |         total_time = asyncio.get_event_loop().time() - start_time
0162 |         
0163 |         # Create basic report
0164 |         report = AnalysisReport(
0165 |             scan_result=scan_result,
0166 |             triage_result=None,
0167 |             remediation_plans=[],
0168 |             analysis_config={"mode": "basic", "tool_hint": tool_hint},
0169 |             total_processing_time_seconds=total_time,
0170 |             chunking_enabled=False
0171 |         )
0172 |         
0173 |         # Generate HTML if requested
0174 |         if output_file and self.reporter:
0175 |             await self.reporter.generate_html_report(report, output_file)
0176 |         
0177 |         logger.info(f"✅ Basic analysis complete in {total_time:.2f}s")
0178 |         return report
0179 |     
0180 |     # ════════════════════════════════════════════════════════════════
0181 |     # PRIVATE HELPERS
0182 |     # ════════════════════════════════════════════════════════════════
0183 |     
0184 |     async def _perform_triage(
0185 |         self,
0186 |         scan_result: ScanResult,
0187 |         language: Optional[str],
0188 |         force_chunking: bool,
0189 |         disable_chunking: bool
0190 |     ):
0191 |         """Perform triage with optional chunking"""
0192 |         should_chunk = (
0193 |             self.chunker and
0194 |             self.chunker.should_chunk(scan_result) and
0195 |             not disable_chunking
0196 |         ) or force_chunking
0197 |         
0198 |         if should_chunk and self.chunker:
0199 |             logger.info("🧩 Using chunked analysis")
0200 |             return await self._analyze_with_chunking(scan_result, language)
0201 |         else:
0202 |             logger.info("📊 Using direct analysis")
0203 |             return await self.triage.analyze_vulnerabilities(
0204 |                 scan_result.vulnerabilities, language
0205 |             )
0206 |     
0207 |     async def _analyze_with_chunking(self, scan_result: ScanResult, language: Optional[str]):
0208 |         """Analyze with chunking"""
0209 |         chunks = self.chunker.create_chunks(scan_result)
0210 |         logger.info(f"📦 Processing {len(chunks)} chunks")
0211 |         
0212 |         # Process with concurrency limit
0213 |         semaphore = asyncio.Semaphore(2)
0214 |         
0215 |         async def process_chunk(chunk):
0216 |             async with semaphore:
0217 |                 return await self.triage.analyze_vulnerabilities(
0218 |                     chunk.vulnerabilities, language, chunk.id
0219 |                 )
0220 |         
0221 |         # Execute
0222 |         results = await asyncio.gather(
0223 |             *[process_chunk(chunk) for chunk in chunks],
0224 |             return_exceptions=True
0225 |         )
0226 |         
0227 |         # Filter successful
0228 |         successful = [r for r in results if not isinstance(r, Exception)]
0229 |         
0230 |         if not successful:
0231 |             raise Exception("All chunk analyses failed")
0232 |         
0233 |         # Consolidate
0234 |         return self._consolidate_results(successful)
0235 |     
0236 |     def _consolidate_results(self, chunk_results):
0237 |         """Consolidate multiple chunk results"""
0238 |         all_decisions = []
0239 |         seen_ids = set()
0240 |         
0241 |         for result in chunk_results:
0242 |             for decision in result.decisions:
0243 |                 if decision.vulnerability_id not in seen_ids:
0244 |                     all_decisions.append(decision)
0245 |                     seen_ids.add(decision.vulnerability_id)
0246 |         
0247 |         from collections import Counter
0248 |         from core.models import TriageResult
0249 |         
0250 |         decision_counts = Counter(d.decision.value for d in all_decisions)
0251 |         summary = (
0252 |             f"Consolidated from {len(chunk_results)} chunks. "
0253 |             f"Total: {len(all_decisions)}. "
0254 |             f"Distribution: {dict(decision_counts)}"
0255 |         )
0256 |         
0257 |         return TriageResult(
0258 |             decisions=all_decisions,
0259 |             analysis_summary=summary,
0260 |             llm_analysis_time_seconds=sum(r.llm_analysis_time_seconds for r in chunk_results)
0261 |         )
0262 |     
0263 |     def _get_confirmed_vulns(
0264 |         self,
0265 |         vulnerabilities: List[Vulnerability],
0266 |         triage_result
0267 |     ) -> List[Vulnerability]:
0268 |         """Extract confirmed vulnerabilities"""
0269 |         from core.models import AnalysisStatus
0270 |         
0271 |         confirmed_ids = {
0272 |             d.vulnerability_id for d in triage_result.decisions
0273 |             if d.decision == AnalysisStatus.CONFIRMED
0274 |         }
0275 |         
0276 |         return [v for v in vulnerabilities if v.id in confirmed_ids]
0277 |     
0278 |     def _create_report(
0279 |         self,
0280 |         scan_result: ScanResult,
0281 |         triage_result,
0282 |         remediation_plans: List,
0283 |         total_time: float,
0284 |         force_chunking: bool,
0285 |         disable_chunking: bool,
0286 |         language: Optional[str],
0287 |         tool_hint: Optional[str]
0288 |     ) -> AnalysisReport:
0289 |         """Create comprehensive analysis report"""
0290 |         chunking_used = self._was_chunking_used(scan_result, force_chunking, disable_chunking)
0291 |         
0292 |         return AnalysisReport(
0293 |             scan_result=scan_result,
0294 |             triage_result=triage_result,
0295 |             remediation_plans=remediation_plans,
0296 |             analysis_config={
0297 |                 "language": language,
0298 |                 "tool_hint": tool_hint,
0299 |                 "force_chunking": force_chunking,
0300 |                 "disable_chunking": disable_chunking,
0301 |                 "chunking_used": chunking_used,
0302 |                 "chunks_processed": (
0303 |                     len(self.chunker.create_chunks(scan_result)) if chunking_used else 0
0304 |                 )
0305 |             },
0306 |             total_processing_time_seconds=total_time,
0307 |             chunking_enabled=chunking_used
0308 |         )
0309 |     
0310 |     def _create_clean_report(self, scan_result: ScanResult, start_time: float) -> AnalysisReport:
0311 |         """Create report for files with no vulnerabilities"""
0312 |         total_time = asyncio.get_event_loop().time() - start_time
0313 |         
0314 |         return AnalysisReport(
0315 |             scan_result=scan_result,
0316 |             triage_result=None,
0317 |             remediation_plans=[],
0318 |             analysis_config={"no_vulnerabilities_found": True},
0319 |             total_processing_time_seconds=total_time,
0320 |             chunking_enabled=False
0321 |         )
0322 |     
0323 |     def _was_chunking_used(
0324 |         self,
0325 |         scan_result: ScanResult,
0326 |         force_chunking: bool,
0327 |         disable_chunking: bool
0328 |     ) -> bool:
0329 |         """Determine if chunking was used"""
0330 |         # Priority 1: Explicitly disabled
0331 |         if disable_chunking:
0332 |             return False
0333 |         
0334 |         # Priority 2: Explicitly forced
0335 |         if force_chunking and self.chunker and scan_result.vulnerabilities:
0336 |             return True
0337 |         
0338 |         # Priority 3: Automatic decision
0339 |         if self.chunker and scan_result.vulnerabilities:
0340 |             return self.chunker.should_chunk(scan_result)
0341 |         
0342 |         return False
0343 | 
0344 | 
0345 | # ════════════════════════════════════════════════════════════════════
0346 | # CLI USE CASE
0347 | # ════════════════════════════════════════════════════════════════════
0348 | 
0349 | class CLIUseCase:
0350 |     """CLI-specific use case with user-friendly output"""
0351 |     
0352 |     def __init__(self, analysis_use_case: AnalysisUseCase):
0353 |         self.analysis = analysis_use_case
0354 |     
0355 |     async def execute_cli_analysis(
0356 |         self,
0357 |         input_file: str,
0358 |         output_file: str = "security_report.html",
0359 |         language: Optional[str] = None,
0360 |         verbose: bool = False,
0361 |         disable_llm: bool = False,
0362 |         force_chunking: bool = False,
0363 |         disable_chunking: bool = False
0364 |     ) -> bool:
0365 |         """Execute analysis with CLI-friendly output"""
0366 |         
0367 |         try:
0368 |             # Validate input
0369 |             input_path = Path(input_file)
0370 |             if not input_path.exists():
0371 |                 print(f"❌ File not found: {input_file}")
0372 |                 return False
0373 |             
0374 |             print(f"🔍 Analyzing: {input_path.name}")
0375 |             
0376 |             # Execute analysis
0377 |             if disable_llm:
0378 |                 result = await self.analysis.execute_basic_analysis(input_file, output_file)
0379 |                 print("✅ Basic analysis completed")
0380 |             else:
0381 |                 result = await self.analysis.execute_full_analysis(
0382 |                     file_path=input_file,
0383 |                     output_file=output_file,
0384 |                     language=language,
0385 |                     force_chunking=force_chunking,
0386 |                     disable_chunking=disable_chunking
0387 |                 )
0388 |                 print("✅ Full analysis completed")
0389 |             
0390 |             # Display results
0391 |             self._display_results(result, output_file)
0392 |             return True
0393 |             
0394 |         except KeyboardInterrupt:
0395 |             print("\n🛑 Interrupted by user")
0396 |             return False
0397 |         except Exception as e:
0398 |             print(f"\n❌ Analysis failed: {e}")
0399 |             if verbose:
0400 |                 import traceback
0401 |                 traceback.print_exc()
0402 |             return False
0403 |     
0404 |     def _display_results(self, result: AnalysisReport, output_file: str) -> None:
0405 |         """Display results in CLI format"""
0406 |         print("\n" + "="*60)
0407 |         print("📊 ANALYSIS RESULTS")
0408 |         print("="*60)
0409 |         
0410 |         # Basic stats
0411 |         scan = result.scan_result
0412 |         print(f"\n📁 File: {scan.file_info['filename']}")
0413 |         print(f"🔢 Total vulnerabilities: {len(scan.vulnerabilities)}")
0414 |         
0415 |         # Deduplication stats
0416 |         if 'duplicates_removed' in scan.file_info:
0417 |             dups = scan.file_info['duplicates_removed']
0418 |             if dups > 0:
0419 |                 print(f"🔄 Duplicates removed: {dups}")
0420 |         
0421 |         # Severity distribution
0422 |         if scan.vulnerabilities:
0423 |             print("\n📈 Severity Distribution:")
0424 |             for severity, count in scan.severity_distribution.items():
0425 |                 if count > 0:
0426 |                     icons = {"CRÍTICA": "🔥", "ALTA": "⚡", "MEDIA": "⚠️", "BAJA": "📝", "INFO": "ℹ️"}
0427 |                     icon = icons.get(severity, "•")
0428 |                     print(f"   {icon} {severity}: {count}")
0429 |         
0430 |         # Triage results
0431 |         if result.triage_result:
0432 |             triage = result.triage_result
0433 |             print(f"\n🤖 LLM Analysis:")
0434 |             print(f"   ✅ Confirmed: {triage.confirmed_count}")
0435 |             print(f"   ❌ False positives: {triage.false_positive_count}")
0436 |             print(f"   🔍 Need review: {triage.needs_review_count}")
0437 |         
0438 |         # Remediation plans
0439 |         if result.remediation_plans:
0440 |             print(f"\n🛠️  Remediation plans: {len(result.remediation_plans)}")
0441 |         
0442 |         # Performance
0443 |         print(f"\n⏱️  Processing time: {result.total_processing_time_seconds:.2f}s")
0444 |         if result.chunking_enabled:
0445 |             print("🧩 Chunking: Enabled")
0446 |         
0447 |         # Output file
0448 |         if Path(output_file).exists():
0449 |             size_kb = Path(output_file).stat().st_size / 1024
0450 |             print(f"\n📄 Report: {output_file} ({size_kb:.1f} KB)")
0451 |         
0452 |         print("\n💡 Open the HTML file in your browser to view the detailed report")
0453 |         print("="*60)
```

---

### application\__init__.py

**Ruta:** `application\__init__.py`

```py
```

---

### core\exceptions.py

**Ruta:** `core\exceptions.py`

```py
0001 | # core/exceptions.py
0002 | """
0003 | Custom Exceptions - Simplified
0004 | ==============================
0005 | 
0006 | Domain-specific exceptions for clean error handling.
0007 | """
0008 | 
0009 | from typing import Dict, Any, Optional
0010 | 
0011 | 
0012 | class SecurityAnalysisError(Exception):
0013 |     """Base exception for all application errors"""
0014 |     
0015 |     def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
0016 |         """
0017 |         Initialize exception
0018 |         
0019 |         Args:
0020 |             message: Error message
0021 |             details: Optional error details
0022 |         """
0023 |         self.message = message
0024 |         self.details = details or {}
0025 |         super().__init__(self.message)
0026 |     
0027 |     def __str__(self) -> str:
0028 |         """String representation"""
0029 |         if self.details:
0030 |             return f"{self.message} | Details: {self.details}"
0031 |         return self.message
0032 | 
0033 | 
0034 | class ValidationError(SecurityAnalysisError):
0035 |     """Validation error (invalid input)"""
0036 |     pass
0037 | 
0038 | 
0039 | class ParsingError(SecurityAnalysisError):
0040 |     """Parsing error (invalid format)"""
0041 |     pass
0042 | 
0043 | 
0044 | class LLMError(SecurityAnalysisError):
0045 |     """LLM provider error"""
0046 |     
0047 |     def __init__(
0048 |         self,
0049 |         message: str,
0050 |         raw_response: Optional[str] = None,
0051 |         details: Optional[Dict[str, Any]] = None
0052 |     ):
0053 |         """
0054 |         Initialize LLM error
0055 |         
0056 |         Args:
0057 |             message: Error message
0058 |             raw_response: Optional raw LLM response
0059 |             details: Optional error details
0060 |         """
0061 |         self.raw_response = raw_response
0062 |         super().__init__(message, details)
0063 | 
0064 | 
0065 | class ChunkingError(SecurityAnalysisError):
0066 |     """Chunking process error"""
0067 |     pass
0068 | 
0069 | 
0070 | class CacheError(SecurityAnalysisError):
0071 |     """Cache operation error"""
0072 |     pass
0073 | 
0074 | 
0075 | class ConfigurationError(SecurityAnalysisError):
0076 |     """Configuration error"""
0077 |     pass
```

---

### core\models.py

**Ruta:** `core\models.py`

```py
0001 | # core/models.py
0002 | """
0003 | Domain Models - Simplified & Optimized
0004 | =====================================
0005 | 
0006 | Clean domain models with validation and computed properties.
0007 | """
0008 | 
0009 | from pydantic import BaseModel, Field, field_validator, computed_field
0010 | from typing import List, Optional, Dict, Any
0011 | from datetime import datetime
0012 | from enum import Enum
0013 | 
0014 | 
0015 | # ═══════════════════════════════════════════════════════════════════
0016 | # ENUMS - Centralized
0017 | # ═══════════════════════════════════════════════════════════════════
0018 | 
0019 | class SeverityLevel(str, Enum):
0020 |     """Vulnerability severity levels"""
0021 |     CRITICAL = "CRÍTICA"
0022 |     HIGH = "ALTA"
0023 |     MEDIUM = "MEDIA"
0024 |     LOW = "BAJA"
0025 |     INFO = "INFO"
0026 |     
0027 |     @property
0028 |     def weight(self) -> float:
0029 |         """Numeric weight for scoring"""
0030 |         weights = {
0031 |             self.CRITICAL: 10.0,
0032 |             self.HIGH: 7.0,
0033 |             self.MEDIUM: 4.0,
0034 |             self.LOW: 2.0,
0035 |             self.INFO: 0.5
0036 |         }
0037 |         return weights[self]
0038 | 
0039 | 
0040 | class VulnerabilityType(str, Enum):
0041 |     """Common vulnerability types"""
0042 |     SQL_INJECTION = "SQL Injection"
0043 |     XSS = "Cross-Site Scripting"
0044 |     PATH_TRAVERSAL = "Directory Traversal"
0045 |     CODE_INJECTION = "Code Injection"
0046 |     AUTH_BYPASS = "Authentication Bypass"
0047 |     BROKEN_ACCESS_CONTROL = "Broken Access Control"
0048 |     INSECURE_CRYPTO = "Insecure Cryptography"
0049 |     SENSITIVE_DATA_EXPOSURE = "Sensitive Data Exposure"
0050 |     SECURITY_MISCONFIGURATION = "Security Misconfiguration"
0051 |     OTHER = "Other Security Issue"
0052 | 
0053 | 
0054 | class AnalysisStatus(str, Enum):
0055 |     """Triage analysis status"""
0056 |     CONFIRMED = "confirmed"
0057 |     FALSE_POSITIVE = "false_positive"
0058 |     NEEDS_MANUAL_REVIEW = "needs_manual_review"
0059 | 
0060 | 
0061 | # ═══════════════════════════════════════════════════════════════════
0062 | # VULNERABILITY MODEL
0063 | # ═══════════════════════════════════════════════════════════════════
0064 | 
0065 | class Vulnerability(BaseModel):
0066 |     """Core vulnerability model with validation"""
0067 |     
0068 |     # Identity
0069 |     id: str = Field(..., min_length=1)
0070 |     type: VulnerabilityType
0071 |     severity: SeverityLevel
0072 |     
0073 |     # Description
0074 |     title: str = Field(..., min_length=1, max_length=200)
0075 |     description: str = Field(..., min_length=10)
0076 |     
0077 |     # Location
0078 |     file_path: str = Field(..., min_length=1)
0079 |     line_number: int = Field(ge=0, default=0)
0080 |     code_snippet: Optional[str] = None
0081 |     
0082 |     # Security metadata
0083 |     cwe_id: Optional[str] = Field(None, pattern=r"^CWE-\d+$")
0084 |     confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
0085 |     
0086 |     # Source
0087 |     source_tool: Optional[str] = None
0088 |     rule_id: Optional[str] = None
0089 |     
0090 |     # Remediation
0091 |     impact_description: Optional[str] = None
0092 |     remediation_advice: Optional[str] = None
0093 |     
0094 |     # Metadata
0095 |     created_at: datetime = Field(default_factory=datetime.now)
0096 |     meta: Dict[str, Any] = Field(default_factory=dict)
0097 |     
0098 |     @field_validator('severity', mode='before')
0099 |     @classmethod
0100 |     def normalize_severity(cls, v) -> SeverityLevel:
0101 |         """Normalize severity from various formats"""
0102 |         if isinstance(v, SeverityLevel):
0103 |             return v
0104 |         
0105 |         if isinstance(v, str):
0106 |             # Mapping table
0107 |             severity_map = {
0108 |                 'CRITICAL': SeverityLevel.CRITICAL,
0109 |                 'CRÍTICA': SeverityLevel.CRITICAL,
0110 |                 'BLOCKER': SeverityLevel.CRITICAL,
0111 |                 'HIGH': SeverityLevel.HIGH,
0112 |                 'ALTA': SeverityLevel.HIGH,
0113 |                 'MAJOR': SeverityLevel.HIGH,
0114 |                 'MEDIUM': SeverityLevel.MEDIUM,
0115 |                 'MEDIA': SeverityLevel.MEDIUM,
0116 |                 'LOW': SeverityLevel.LOW,
0117 |                 'BAJA': SeverityLevel.LOW,
0118 |                 'MINOR': SeverityLevel.MEDIUM,
0119 |                 'INFO': SeverityLevel.INFO,
0120 |             }
0121 |             return severity_map.get(v.upper(), SeverityLevel.MEDIUM)
0122 |         
0123 |         return SeverityLevel.MEDIUM
0124 |     
0125 |     @computed_field
0126 |     @property
0127 |     def priority_score(self) -> int:
0128 |         """Priority score for sorting (0-100)"""
0129 |         base = int(self.severity.weight * 10)
0130 |         if self.confidence_level:
0131 |             base = int(base * self.confidence_level)
0132 |         return base
0133 |     
0134 |     @computed_field
0135 |     @property
0136 |     def is_high_priority(self) -> bool:
0137 |         """Check if high priority"""
0138 |         return self.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
0139 | 
0140 | 
0141 | # ═══════════════════════════════════════════════════════════════════
0142 | # TRIAGE MODELS
0143 | # ═══════════════════════════════════════════════════════════════════
0144 | 
0145 | class TriageDecision(BaseModel):
0146 |     """Single triage decision"""
0147 |     vulnerability_id: str
0148 |     decision: AnalysisStatus
0149 |     confidence_score: float = Field(ge=0.0, le=1.0)
0150 |     reasoning: str = Field(..., min_length=10)
0151 |     llm_model_used: str
0152 |     analyzed_at: datetime = Field(default_factory=datetime.now)
0153 | 
0154 | 
0155 | class TriageResult(BaseModel):
0156 |     """Complete triage analysis result"""
0157 |     decisions: List[TriageDecision] = Field(default_factory=list)
0158 |     analysis_summary: str
0159 |     llm_analysis_time_seconds: float = Field(ge=0.0)
0160 |     
0161 |     @computed_field
0162 |     @property
0163 |     def total_analyzed(self) -> int:
0164 |         return len(self.decisions)
0165 |     
0166 |     @computed_field
0167 |     @property
0168 |     def confirmed_count(self) -> int:
0169 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.CONFIRMED)
0170 |     
0171 |     @computed_field
0172 |     @property
0173 |     def false_positive_count(self) -> int:
0174 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.FALSE_POSITIVE)
0175 |     
0176 |     @computed_field
0177 |     @property
0178 |     def needs_review_count(self) -> int:
0179 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.NEEDS_MANUAL_REVIEW)
0180 | 
0181 | 
0182 | # ═══════════════════════════════════════════════════════════════════
0183 | # REMEDIATION MODELS
0184 | # ═══════════════════════════════════════════════════════════════════
0185 | 
0186 | class RemediationStep(BaseModel):
0187 |     """Single remediation step"""
0188 |     step_number: int = Field(ge=1)
0189 |     title: str = Field(..., min_length=1, max_length=200)
0190 |     description: str = Field(..., min_length=10)
0191 |     code_example: Optional[str] = None
0192 |     estimated_minutes: Optional[int] = Field(None, ge=1)
0193 |     difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
0194 |     tools_required: List[str] = Field(default_factory=list)
0195 | 
0196 | 
0197 | class RemediationPlan(BaseModel):
0198 |     """Complete remediation plan"""
0199 |     vulnerability_id: str
0200 |     vulnerability_type: VulnerabilityType
0201 |     priority_level: str = Field(..., pattern=r"^(immediate|high|medium|low)$")
0202 |     complexity_score: float = Field(ge=0.0, le=10.0, default=5.0)
0203 |     steps: List[RemediationStep] = Field(..., min_length=1)
0204 |     risk_if_not_fixed: str = "Security vulnerability should be remediated."
0205 |     references: List[str] = Field(default_factory=list)
0206 |     llm_model_used: str
0207 |     created_at: datetime = Field(default_factory=datetime.now)
0208 | 
0209 | 
0210 | # ═══════════════════════════════════════════════════════════════════
0211 | # SCAN RESULT
0212 | # ═══════════════════════════════════════════════════════════════════
0213 | 
0214 | class ScanResult(BaseModel):
0215 |     """Scan result with statistics"""
0216 |     file_info: Dict[str, Any]
0217 |     vulnerabilities: List[Vulnerability] = Field(default_factory=list)
0218 |     scan_timestamp: datetime = Field(default_factory=datetime.now)
0219 |     scan_duration_seconds: float = Field(ge=0.0, default=0.0)
0220 |     language_detected: Optional[str] = None
0221 |     
0222 |     @computed_field
0223 |     @property
0224 |     def vulnerability_count(self) -> int:
0225 |         return len(self.vulnerabilities)
0226 |     
0227 |     @computed_field
0228 |     @property
0229 |     def severity_distribution(self) -> Dict[str, int]:
0230 |         """Count by severity"""
0231 |         from collections import Counter
0232 |         return dict(Counter(v.severity.value for v in self.vulnerabilities))
0233 |     
0234 |     @computed_field
0235 |     @property
0236 |     def high_priority_count(self) -> int:
0237 |         return sum(1 for v in self.vulnerabilities if v.is_high_priority)
0238 | 
0239 | 
0240 | # ═══════════════════════════════════════════════════════════════════
0241 | # ANALYSIS REPORT
0242 | # ═══════════════════════════════════════════════════════════════════
0243 | 
0244 | class AnalysisReport(BaseModel):
0245 |     """Final analysis report"""
0246 |     report_id: str = Field(
0247 |         default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
0248 |     )
0249 |     generated_at: datetime = Field(default_factory=datetime.now)
0250 |     scan_result: ScanResult
0251 |     triage_result: Optional[TriageResult] = None
0252 |     remediation_plans: List[RemediationPlan] = Field(default_factory=list)
0253 |     analysis_config: Dict[str, Any] = Field(default_factory=dict)
0254 |     total_processing_time_seconds: float = Field(ge=0.0)
0255 |     chunking_enabled: bool = False
0256 |     
0257 |     @computed_field
0258 |     @property
0259 |     def executive_summary(self) -> Dict[str, Any]:
0260 |         """Auto-generated executive summary"""
0261 |         return {
0262 |             "total_vulnerabilities": self.scan_result.vulnerability_count,
0263 |             "high_priority_count": self.scan_result.high_priority_count,
0264 |             "severity_distribution": self.scan_result.severity_distribution,
0265 |             "processing_time": f"{self.total_processing_time_seconds:.2f}s",
0266 |             "confirmed_vulnerabilities": (
0267 |                 self.triage_result.confirmed_count if self.triage_result else 0
0268 |             ),
0269 |             "remediation_plans_generated": len(self.remediation_plans)
0270 |         }
```

---

### core\__init__.py

**Ruta:** `core\__init__.py`

```py
```

---

### core\services\remediation.py

**Ruta:** `core\services\remediation.py`

```py
0001 | # core/services/remediation.py
0002 | """
0003 | Remediation Service - Simplified
0004 | ================================
0005 | 
0006 | Responsibilities:
0007 | - Generate remediation plans
0008 | - Prioritize plans
0009 | - Customize steps per vulnerability
0010 | """
0011 | 
0012 | import logging
0013 | import asyncio
0014 | from typing import List, Optional, Dict
0015 | from collections import defaultdict
0016 | 
0017 | from ..models import (
0018 |     Vulnerability, RemediationPlan, RemediationStep, VulnerabilityType
0019 | )
0020 | from ..exceptions import LLMError
0021 | from infrastructure.llm.client import LLMClient
0022 | from shared.metrics import MetricsCollector
0023 | 
0024 | logger = logging.getLogger(__name__)
0025 | 
0026 | 
0027 | class RemediationService:
0028 |     """Simplified remediation service"""
0029 |     
0030 |     def __init__(
0031 |         self,
0032 |         llm_client: LLMClient,
0033 |         metrics: Optional[MetricsCollector] = None
0034 |     ):
0035 |         self.llm_client = llm_client
0036 |         self.metrics = metrics
0037 |     
0038 |     async def generate_remediation_plans(
0039 |         self,
0040 |         vulnerabilities: List[Vulnerability],
0041 |         language: Optional[str] = None
0042 |     ) -> List[RemediationPlan]:
0043 |         """
0044 |         Generate remediation plans for confirmed vulnerabilities
0045 |         
0046 |         Args:
0047 |             vulnerabilities: List of confirmed vulnerabilities
0048 |             language: Programming language
0049 |         
0050 |         Returns:
0051 |             List of prioritized remediation plans
0052 |         """
0053 |         if not vulnerabilities:
0054 |             logger.info("No vulnerabilities - no plans needed")
0055 |             return []
0056 |         
0057 |         logger.info(f"🛠️  Generating plans for {len(vulnerabilities)} vulnerabilities")
0058 |         
0059 |         # Group by type for efficient batch processing
0060 |         grouped = self._group_by_type(vulnerabilities)
0061 |         
0062 |         all_plans = []
0063 |         for vuln_type, vulns in grouped.items():
0064 |             try:
0065 |                 plans = await self._generate_for_type(vuln_type, vulns, language)
0066 |                 all_plans.extend(plans)
0067 |             except Exception as e:
0068 |                 logger.error(f"Failed to generate plans for {vuln_type}: {e}")
0069 |                 # Add fallback plans
0070 |                 fallback = self._create_fallback_plans(vulns)
0071 |                 all_plans.extend(fallback)
0072 |         
0073 |         # Prioritize
0074 |         prioritized = self._prioritize_plans(all_plans)
0075 |         
0076 |         logger.info(f"✅ Generated {len(prioritized)} remediation plans")
0077 |         return prioritized
0078 |     
0079 |     # ════════════════════════════════════════════════════════════════
0080 |     # PRIVATE HELPERS
0081 |     # ════════════════════════════════════════════════════════════════
0082 |     
0083 |     def _group_by_type(
0084 |         self,
0085 |         vulnerabilities: List[Vulnerability]
0086 |     ) -> Dict[VulnerabilityType, List[Vulnerability]]:
0087 |         """Group vulnerabilities by type"""
0088 |         groups = defaultdict(list)
0089 |         for vuln in vulnerabilities:
0090 |             groups[vuln.type].append(vuln)
0091 |         return dict(groups)
0092 |     
0093 |     async def _generate_for_type(
0094 |         self,
0095 |         vuln_type: VulnerabilityType,
0096 |         vulnerabilities: List[Vulnerability],
0097 |         language: Optional[str]
0098 |     ) -> List[RemediationPlan]:
0099 |         """Generate plans for specific vulnerability type"""
0100 |         start_time = asyncio.get_event_loop().time()
0101 |         
0102 |         try:
0103 |             # Prepare request
0104 |             request = self._prepare_request(vuln_type, vulnerabilities, language)
0105 |             
0106 |             # Get LLM response
0107 |             response = await self.llm_client.generate_remediation_plan(
0108 |                 request, vuln_type.value, language
0109 |             )
0110 |             
0111 |             # Create individual plans from template
0112 |             plans = self._create_individual_plans(response, vulnerabilities)
0113 |             
0114 |             # Record metrics
0115 |             if self.metrics:
0116 |                 generation_time = asyncio.get_event_loop().time() - start_time
0117 |                 self.metrics.record_remediation_generation(
0118 |                     vuln_type.value, len(vulnerabilities), generation_time, True
0119 |                 )
0120 |             
0121 |             return plans
0122 |             
0123 |         except Exception as e:
0124 |             if self.metrics:
0125 |                 generation_time = asyncio.get_event_loop().time() - start_time
0126 |                 self.metrics.record_remediation_generation(
0127 |                     vuln_type.value, len(vulnerabilities), generation_time, False, str(e)
0128 |                 )
0129 |             raise
0130 |     
0131 |     def _prepare_request(
0132 |         self,
0133 |         vuln_type: VulnerabilityType,
0134 |         vulnerabilities: List[Vulnerability],
0135 |         language: Optional[str]
0136 |     ) -> str:
0137 |         """Prepare structured remediation request"""
0138 |         header = f"# REMEDIATION PLAN REQUEST\n"
0139 |         header += f"Type: {vuln_type.value}\n"
0140 |         header += f"Language: {language or 'Unknown'}\n"
0141 |         header += f"Count: {len(vulnerabilities)}\n\n"
0142 |         
0143 |         vuln_details = []
0144 |         for i, vuln in enumerate(vulnerabilities, 1):
0145 |             detail = f"""## VULNERABILITY {i} - {vuln.id}
0146 | - Severity: {vuln.severity.value}
0147 | - File: {vuln.file_path}:{vuln.line_number}
0148 | - Title: {vuln.title}
0149 | - Description: {vuln.description}"""
0150 |             
0151 |             if vuln.code_snippet:
0152 |                 detail += f"\n- Code:\n{vuln.code_snippet[:500]}"
0153 |             
0154 |             vuln_details.append(detail)
0155 |         
0156 |         return header + "\n\n".join(vuln_details)
0157 |     
0158 |     def _create_individual_plans(
0159 |         self,
0160 |         template_plan: RemediationPlan,
0161 |         vulnerabilities: List[Vulnerability]
0162 |     ) -> List[RemediationPlan]:
0163 |         """Create individual plans from template"""
0164 |         plans = []
0165 |         
0166 |         for vuln in vulnerabilities:
0167 |             customized = RemediationPlan(
0168 |                 vulnerability_id=vuln.id,
0169 |                 vulnerability_type=vuln.type,
0170 |                 priority_level=self._calculate_priority(vuln),
0171 |                 steps=self._customize_steps(template_plan.steps, vuln),
0172 |                 risk_if_not_fixed=template_plan.risk_if_not_fixed,
0173 |                 references=template_plan.references,
0174 |                 complexity_score=self._adjust_complexity(
0175 |                     template_plan.complexity_score, vuln
0176 |                 ),
0177 |                 llm_model_used=template_plan.llm_model_used
0178 |             )
0179 |             plans.append(customized)
0180 |         
0181 |         return plans
0182 |     
0183 |     def _calculate_priority(self, vuln: Vulnerability) -> str:
0184 |         """Calculate priority level"""
0185 |         priority_map = {
0186 |             "CRÍTICA": "immediate",
0187 |             "ALTA": "high",
0188 |             "MEDIA": "medium",
0189 |             "BAJA": "low",
0190 |             "INFO": "low"
0191 |         }
0192 |         return priority_map.get(vuln.severity.value, "medium")
0193 |     
0194 |     def _customize_steps(
0195 |         self,
0196 |         template_steps: List[RemediationStep],
0197 |         vulnerability: Vulnerability
0198 |     ) -> List[RemediationStep]:
0199 |         """Customize steps for specific vulnerability"""
0200 |         customized = []
0201 |         
0202 |         for step in template_steps:
0203 |             try:
0204 |                 # Try to format with placeholders
0205 |                 formatted_title = step.title.format(
0206 |                     file=vulnerability.file_path,
0207 |                     line=vulnerability.line_number,
0208 |                     vuln_type=vulnerability.type.value
0209 |                 )
0210 |                 formatted_desc = step.description.format(
0211 |                     vulnerability_id=vulnerability.id,
0212 |                     file_path=vulnerability.file_path,
0213 |                     severity=vulnerability.severity.value
0214 |                 )
0215 |             except KeyError:
0216 |                 # No placeholders, use original
0217 |                 formatted_title = step.title
0218 |                 formatted_desc = step.description
0219 |             
0220 |             customized_step = RemediationStep(
0221 |                 step_number=step.step_number,
0222 |                 title=formatted_title,
0223 |                 description=formatted_desc,
0224 |                 code_example=step.code_example,
0225 |                 estimated_minutes=step.estimated_minutes,
0226 |                 difficulty=step.difficulty,
0227 |                 tools_required=step.tools_required
0228 |             )
0229 |             customized.append(customized_step)
0230 |         
0231 |         return customized
0232 |     
0233 |     def _adjust_complexity(
0234 |         self,
0235 |         base_complexity: float,
0236 |         vulnerability: Vulnerability
0237 |     ) -> float:
0238 |         """Adjust complexity based on vulnerability"""
0239 |         # Severity multipliers
0240 |         multipliers = {
0241 |             "CRÍTICA": 1.2,
0242 |             "ALTA": 1.1,
0243 |             "MEDIA": 1.0,
0244 |             "BAJA": 0.9,
0245 |             "INFO": 0.8
0246 |         }
0247 |         
0248 |         multiplier = multipliers.get(vulnerability.severity.value, 1.0)
0249 |         adjusted = base_complexity * multiplier
0250 |         
0251 |         # Clamp to 1-10 range
0252 |         return min(max(adjusted, 1.0), 10.0)
0253 |     
0254 |     def _create_fallback_plans(
0255 |         self,
0256 |         vulnerabilities: List[Vulnerability]
0257 |     ) -> List[RemediationPlan]:
0258 |         """Create basic fallback plans when LLM fails"""
0259 |         logger.warning("⚠️  Creating fallback remediation plans")
0260 |         
0261 |         fallback_plans = []
0262 |         
0263 |         for vuln in vulnerabilities:
0264 |             basic_steps = [
0265 |                 RemediationStep(
0266 |                     step_number=1,
0267 |                     title="Manual Security Review",
0268 |                     description=f"Review {vuln.type.value} in {vuln.file_path}",
0269 |                     estimated_minutes=30,
0270 |                     difficulty="medium"
0271 |                 ),
0272 |                 RemediationStep(
0273 |                     step_number=2,
0274 |                     title="Research Best Practices",
0275 |                     description=f"Research security best practices for {vuln.type.value}",
0276 |                     estimated_minutes=15,
0277 |                     difficulty="easy"
0278 |                 ),
0279 |                 RemediationStep(
0280 |                     step_number=3,
0281 |                     title="Implement Fix",
0282 |                     description="Apply appropriate security fix",
0283 |                     estimated_minutes=120,
0284 |                     difficulty="hard"
0285 |                 ),
0286 |                 RemediationStep(
0287 |                     step_number=4,
0288 |                     title="Validate Fix",
0289 |                     description="Test that vulnerability is fixed",
0290 |                     estimated_minutes=30,
0291 |                     difficulty="medium"
0292 |                 )
0293 |             ]
0294 |             
0295 |             plan = RemediationPlan(
0296 |                 vulnerability_id=vuln.id,
0297 |                 vulnerability_type=vuln.type,
0298 |                 priority_level=self._calculate_priority(vuln),
0299 |                 steps=basic_steps,
0300 |                 risk_if_not_fixed=f"Security risk: {vuln.type.value}",
0301 |                 complexity_score=5.0,
0302 |                 llm_model_used="fallback"
0303 |             )
0304 |             
0305 |             fallback_plans.append(plan)
0306 |         
0307 |         return fallback_plans
0308 |     
0309 |     def _prioritize_plans(
0310 |         self,
0311 |         plans: List[RemediationPlan]
0312 |     ) -> List[RemediationPlan]:
0313 |         """Sort plans by priority and complexity"""
0314 |         priority_weights = {
0315 |             "immediate": 4,
0316 |             "high": 3,
0317 |             "medium": 2,
0318 |             "low": 1
0319 |         }
0320 |         
0321 |         return sorted(
0322 |             plans,
0323 |             key=lambda p: (
0324 |                 priority_weights.get(p.priority_level, 0),
0325 |                 -p.complexity_score  # Lower complexity = higher priority
0326 |             ),
0327 |             reverse=True
0328 |         )
```

---

### core\services\reporter.py

**Ruta:** `core\services\reporter.py`

```py
0001 | # core/services/reporter.py
0002 | """
0003 | Reporter Service - Simplified
0004 | =============================
0005 | 
0006 | Responsibilities:
0007 | - Generate HTML reports
0008 | - Track metrics
0009 | """
0010 | 
0011 | import logging
0012 | from pathlib import Path
0013 | from typing import Optional
0014 | 
0015 | from ..models import AnalysisReport
0016 | from adapters.output.html_generator import OptimizedHTMLGenerator
0017 | from shared.metrics import MetricsCollector
0018 | 
0019 | logger = logging.getLogger(__name__)
0020 | 
0021 | 
0022 | class ReporterService:
0023 |     """Simplified reporter service"""
0024 |     
0025 |     def __init__(
0026 |         self,
0027 |         html_generator: Optional[OptimizedHTMLGenerator] = None,
0028 |         metrics: Optional[MetricsCollector] = None
0029 |     ):
0030 |         self.html_generator = html_generator or OptimizedHTMLGenerator()
0031 |         self.metrics = metrics
0032 |     
0033 |     async def generate_html_report(
0034 |         self,
0035 |         analysis_report: AnalysisReport,
0036 |         output_file: str
0037 |     ) -> bool:
0038 |         """
0039 |         Generate HTML report with metrics
0040 |         
0041 |         Args:
0042 |             analysis_report: Complete analysis report
0043 |             output_file: Output file path
0044 |         
0045 |         Returns:
0046 |             True if successful
0047 |         """
0048 |         try:
0049 |             logger.info(f"📄 Generating HTML report: {output_file}")
0050 |             
0051 |             # Generate report
0052 |             success = self.html_generator.generate_report(
0053 |                 analysis_report,
0054 |                 output_file
0055 |             )
0056 |             
0057 |             if success:
0058 |                 file_size = Path(output_file).stat().st_size
0059 |                 
0060 |                 # Record metrics
0061 |                 if self.metrics:
0062 |                     self.metrics.record_report_generation(
0063 |                         "html",
0064 |                         file_size,
0065 |                         len(analysis_report.scan_result.vulnerabilities),
0066 |                         True
0067 |                     )
0068 |                 
0069 |                 logger.info(f"✅ Report generated: {output_file} ({file_size:,} bytes)")
0070 |             else:
0071 |                 if self.metrics:
0072 |                     self.metrics.record_report_generation("html", success=False)
0073 |                 
0074 |                 logger.error(f"❌ Failed to generate: {output_file}")
0075 |             
0076 |             return success
0077 |             
0078 |         except Exception as e:
0079 |             if self.metrics:
0080 |                 self.metrics.record_report_generation(
0081 |                     "html", success=False, error=str(e)
0082 |                 )
0083 |             
0084 |             logger.error(f"❌ Report generation failed: {e}")
0085 |             return False
```

---

### core\services\scanner.py

**Ruta:** `core\services\scanner.py`

```py
0001 | # core/services/scanner.py
0002 | """
0003 | Scanner Service - Clean & Optimized
0004 | ===================================
0005 | 
0006 | Responsibilities:
0007 | - Parse vulnerability files
0008 | - Normalize formats
0009 | - Deduplicate findings
0010 | - Cache results
0011 | """
0012 | 
0013 | import json
0014 | import logging
0015 | from pathlib import Path
0016 | from typing import Optional, Dict, Any, List, Tuple
0017 | from datetime import datetime
0018 | from functools import lru_cache
0019 | 
0020 | from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
0021 | from ..exceptions import ValidationError, ParsingError
0022 | 
0023 | logger = logging.getLogger(__name__)
0024 | 
0025 | 
0026 | # ═══════════════════════════════════════════════════════════════════
0027 | # CONSTANTS
0028 | # ═══════════════════════════════════════════════════════════════════
0029 | 
0030 | SEVERITY_MAPPINGS = {
0031 |     'CRITICAL': SeverityLevel.CRITICAL,
0032 |     'CRÍTICA': SeverityLevel.CRITICAL,
0033 |     'HIGH': SeverityLevel.HIGH,
0034 |     'ALTA': SeverityLevel.HIGH,
0035 |     'MEDIUM': SeverityLevel.MEDIUM,
0036 |     'MEDIA': SeverityLevel.MEDIUM,
0037 |     'LOW': SeverityLevel.LOW,
0038 |     'BAJA': SeverityLevel.LOW,
0039 |     'INFO': SeverityLevel.INFO,
0040 | }
0041 | 
0042 | VULNERABILITY_TYPE_PATTERNS = {
0043 |     'sql injection': VulnerabilityType.SQL_INJECTION,
0044 |     'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
0045 |     'path traversal': VulnerabilityType.PATH_TRAVERSAL,
0046 |     'code injection': VulnerabilityType.CODE_INJECTION,
0047 |     'cross-site scripting': VulnerabilityType.XSS,
0048 |     'xss': VulnerabilityType.XSS,
0049 |     'authentication': VulnerabilityType.AUTH_BYPASS,
0050 |     'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
0051 |     'crypto': VulnerabilityType.INSECURE_CRYPTO,
0052 | }
0053 | 
0054 | 
0055 | # ═══════════════════════════════════════════════════════════════════
0056 | # DEDUPLICATION
0057 | # ═══════════════════════════════════════════════════════════════════
0058 | 
0059 | class DuplicateDetector:
0060 |     """Intelligent duplicate detection with multiple strategies"""
0061 |     
0062 |     def __init__(self, strategy: str = 'moderate'):
0063 |         """
0064 |         Args:
0065 |             strategy: 'strict', 'moderate', or 'loose'
0066 |         """
0067 |         self.strategy = strategy.lower()
0068 |         self._similarity_cache = {}  # Cache for similarity calculations
0069 |     
0070 |     def remove_duplicates(
0071 |         self, vulnerabilities: List[Vulnerability]
0072 |     ) -> Tuple[List[Vulnerability], int]:
0073 |         """
0074 |         Remove duplicates from vulnerability list
0075 |         
0076 |         Returns:
0077 |             Tuple of (unique_vulnerabilities, count_removed)
0078 |         """
0079 |         if len(vulnerabilities) <= 1:
0080 |             return vulnerabilities, 0
0081 |         
0082 |         original_count = len(vulnerabilities)
0083 |         
0084 |         strategies = {
0085 |             'strict': self._dedup_strict,
0086 |             'moderate': self._dedup_moderate,
0087 |             'loose': self._dedup_loose
0088 |         }
0089 |         
0090 |         dedup_func = strategies.get(self.strategy, self._dedup_moderate)
0091 |         unique = dedup_func(vulnerabilities)
0092 |         
0093 |         removed = original_count - len(unique)
0094 |         if removed > 0:
0095 |             logger.info(f"✅ Removed {removed} duplicates ({self.strategy} strategy)")
0096 |         
0097 |         return unique, removed
0098 |     
0099 |     def _dedup_strict(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
0100 |         """Exact match: file+line+type+description hash"""
0101 |         seen = set()
0102 |         unique = []
0103 |         
0104 |         for v in vulns:
0105 |             signature = f"{v.file_path}|{v.line_number}|{v.type.value}|{hash(v.description)}"
0106 |             if signature not in seen:
0107 |                 seen.add(signature)
0108 |                 unique.append(v)
0109 |         
0110 |         return unique
0111 |     
0112 |     def _dedup_moderate(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
0113 |         """Same file+type, nearby location (±5 lines), 80% similar description"""
0114 |         from collections import defaultdict
0115 |         
0116 |         # Group by file and type
0117 |         groups = defaultdict(list)
0118 |         for v in vulns:
0119 |             key = (v.file_path, v.type.value)
0120 |             groups[key].append(v)
0121 |         
0122 |         unique = []
0123 |         for group_vulns in groups.values():
0124 |             # Sort by line number
0125 |             group_vulns.sort(key=lambda v: v.line_number)
0126 |             kept = []
0127 |             
0128 |             for v in group_vulns:
0129 |                 is_duplicate = any(
0130 |                     abs(v.line_number - k.line_number) <= 5 and
0131 |                     self._similarity(v.description, k.description) > 0.8
0132 |                     for k in kept
0133 |                 )
0134 |                 
0135 |                 if not is_duplicate:
0136 |                     kept.append(v)
0137 |             
0138 |             unique.extend(kept)
0139 |         
0140 |         return unique
0141 |     
0142 |     def _dedup_loose(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
0143 |         """Same type, 70% similar description"""
0144 |         from collections import defaultdict
0145 |         
0146 |         groups = defaultdict(list)
0147 |         for v in vulns:
0148 |             groups[v.type.value].append(v)
0149 |         
0150 |         unique = []
0151 |         for group_vulns in groups.values():
0152 |             kept = []
0153 |             for v in group_vulns:
0154 |                 is_duplicate = any(
0155 |                     self._similarity(v.description, k.description) > 0.7
0156 |                     for k in kept
0157 |                 )
0158 |                 
0159 |                 if not is_duplicate:
0160 |                     kept.append(v)
0161 |             
0162 |             unique.extend(kept)
0163 |         
0164 |         return unique
0165 |     
0166 |     @lru_cache(maxsize=1024)
0167 |     def _similarity(self, text1: str, text2: str) -> float:
0168 |         """Jaccard similarity with caching"""
0169 |         if text1 == text2:
0170 |             return 1.0
0171 |         
0172 |         tokens1 = frozenset(text1.lower().split())
0173 |         tokens2 = frozenset(text2.lower().split())
0174 |         
0175 |         if not tokens1 or not tokens2:
0176 |             return 0.0
0177 |         
0178 |         intersection = len(tokens1 & tokens2)
0179 |         union = len(tokens1 | tokens2)
0180 |         
0181 |         return intersection / union if union > 0 else 0.0
0182 | 
0183 | 
0184 | # ═══════════════════════════════════════════════════════════════════
0185 | # VULNERABILITY PARSER
0186 | # ═══════════════════════════════════════════════════════════════════
0187 | 
0188 | class VulnerabilityParser:
0189 |     """Parse vulnerabilities from various SAST tool formats"""
0190 |     
0191 |     def parse(self, data: Dict[str, Any], tool_hint: Optional[str] = None) -> List[Vulnerability]:
0192 |         """
0193 |         Parse vulnerabilities from raw data
0194 |         
0195 |         Args:
0196 |              Raw data from SAST tool
0197 |             tool_hint: Optional hint about tool format
0198 |         
0199 |         Returns:
0200 |             List of parsed Vulnerability objects
0201 |         """
0202 |         findings = self._extract_findings(data)
0203 |         
0204 |         if not findings:
0205 |             logger.warning("No findings found in data")
0206 |             return []
0207 |         
0208 |         # Detect format
0209 |         parser_strategy = self._detect_format(findings[0], tool_hint)
0210 |         logger.info(f"Using parser: {parser_strategy}")
0211 |         
0212 |         # Parse all findings
0213 |         vulnerabilities = []
0214 |         for i, finding in enumerate(findings, 1):
0215 |             try:
0216 |                 vuln = self._parse_finding(finding, i, parser_strategy)
0217 |                 if vuln:
0218 |                     vulnerabilities.append(vuln)
0219 |             except Exception as e:
0220 |                 logger.warning(f"Failed to parse finding {i}: {e}")
0221 |         
0222 |         logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities")
0223 |         return vulnerabilities
0224 |     
0225 |     def _extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
0226 |         """Extract findings from nested structures"""
0227 |         # Direct list
0228 |         if isinstance(data, list):
0229 |             return data
0230 |         
0231 |         # Single object
0232 |         if isinstance(data, dict) and 'rule_id' in data:
0233 |             return [data]
0234 |         
0235 |         # Nested containers
0236 |         if isinstance(data, dict):
0237 |             for key in ['findings', 'vulnerabilities', 'issues', 'results', 'scan_results']:
0238 |                 if key in data and isinstance(data[key], list):
0239 |                     return data[key]
0240 |         
0241 |         return []
0242 |     
0243 |     def _detect_format(self, sample: Dict[str, Any], tool_hint: Optional[str]) -> str:
0244 |         """Detect SAST tool format"""
0245 |         if tool_hint and 'abap' in tool_hint.lower():
0246 |             return 'abap'
0247 |         
0248 |         if 'rule_id' in sample and str(sample.get('rule_id', '')).startswith('abap-'):
0249 |             return 'abap'
0250 |         
0251 |         if 'check_id' in sample:
0252 |             return 'semgrep'
0253 |         
0254 |         if 'ruleId' in sample:
0255 |             return 'sonarqube'
0256 |         
0257 |         return 'generic'
0258 |     
0259 |     def _parse_finding(self, finding: Dict[str, Any], index: int, strategy: str) -> Optional[Vulnerability]:
0260 |         """Parse individual finding based on strategy"""
0261 |         try:
0262 |             if strategy == 'abap':
0263 |                 return self._parse_abap(finding, index)
0264 |             else:
0265 |                 return self._parse_generic(finding, index)
0266 |         except Exception as e:
0267 |             logger.error(f"Failed to parse finding {index}: {e}")
0268 |             return None
0269 |     
0270 |     def _parse_abap(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0271 |         """Parse ABAP-specific finding"""
0272 |         location = finding.get('location', {})
0273 |         
0274 |         return Vulnerability(
0275 |             id=finding.get('rule_id', f'ABAP-{index}'),
0276 |             type=self._normalize_type(finding.get('title', 'Unknown')),
0277 |             severity=SEVERITY_MAPPINGS.get(
0278 |                 finding.get('severity', 'MEDIUM').upper(),
0279 |                 SeverityLevel.MEDIUM
0280 |             ),
0281 |             title=str(finding.get('title', 'ABAP Security Issue')).replace(' Vulnerability', '').strip(),
0282 |             description=finding.get('message', 'No description provided'),
0283 |             file_path=location.get('file', 'Unknown file'),
0284 |             line_number=int(location.get('line', 0)) if location.get('line') else 0,
0285 |             code_snippet=self._extract_code_context(location),
0286 |             cwe_id=self._normalize_cwe(finding.get('cwe')),
0287 |             source_tool='ABAP Security Scanner',
0288 |             rule_id=finding.get('rule_id'),
0289 |             confidence_level=self._extract_confidence(finding),
0290 |             remediation_advice=finding.get('remediation'),
0291 |             meta={
0292 |                 'cvss_score': self._extract_cvss(finding),
0293 |                 'parser_strategy': 'abap',
0294 |                 'parser_version': '3.0'
0295 |             }
0296 |         )
0297 |     
0298 |     def _parse_generic(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0299 |         """Parse generic finding format"""
0300 |         return Vulnerability(
0301 |             id=finding.get('id', f'GENERIC-{index}'),
0302 |             type=VulnerabilityType.OTHER,
0303 |             severity=SeverityLevel.MEDIUM,
0304 |             title=str(finding.get('title', finding.get('message', 'Security Issue')))[:100],
0305 |             description=finding.get('description', finding.get('message', 'No description')),
0306 |             file_path=finding.get('file', finding.get('path', 'Unknown')),
0307 |             line_number=finding.get('line', 0),
0308 |             source_tool=finding.get('tool', 'Generic Scanner'),
0309 |             meta={'parser_strategy': 'generic'}
0310 |         )
0311 |     
0312 |     def _normalize_type(self, title: str) -> VulnerabilityType:
0313 |         """Normalize vulnerability type from title"""
0314 |         if not title:
0315 |             return VulnerabilityType.OTHER
0316 |         
0317 |         title_lower = str(title).lower()
0318 |         
0319 |         for pattern, vuln_type in VULNERABILITY_TYPE_PATTERNS.items():
0320 |             if pattern in title_lower:
0321 |                 return vuln_type
0322 |         
0323 |         return VulnerabilityType.OTHER
0324 |     
0325 |     def _extract_code_context(self, location: Dict[str, Any]) -> Optional[str]:
0326 |         """Extract code context safely"""
0327 |         context = location.get('context', [])
0328 |         line_content = location.get('line_content', '')
0329 |         
0330 |         if isinstance(context, list) and context:
0331 |             safe_lines = []
0332 |             for i, line in enumerate(context):
0333 |                 if line is None:
0334 |                     continue
0335 |                 
0336 |                 # Convert to string safely
0337 |                 line_str = str(line) if not isinstance(line, str) else line
0338 |                 
0339 |                 if line_str.strip():
0340 |                     safe_lines.append(f"{i+1:3d} | {line_str}")
0341 |             
0342 |             if safe_lines:
0343 |                 return '\n'.join(safe_lines)
0344 |         
0345 |         if line_content:
0346 |             return f">>> {str(line_content).strip()}"
0347 |         
0348 |         return None
0349 |     
0350 |     def _normalize_cwe(self, cwe: Optional[str]) -> Optional[str]:
0351 |         """Normalize CWE ID format"""
0352 |         if not cwe:
0353 |             return None
0354 |         
0355 |         cwe_str = str(cwe).strip()
0356 |         if cwe_str.isdigit():
0357 |             return f"CWE-{cwe_str}"
0358 |         elif cwe_str.startswith('CWE-'):
0359 |             return cwe_str
0360 |         
0361 |         return None
0362 |     
0363 |     def _extract_confidence(self, finding: Dict[str, Any]) -> Optional[float]:
0364 |         """Extract confidence level"""
0365 |         confidence = finding.get('confidence')
0366 |         if confidence:
0367 |             try:
0368 |                 if isinstance(confidence, str) and '%' in confidence:
0369 |                     return float(confidence.replace('%', '')) / 100.0
0370 |                 return float(confidence)
0371 |             except (ValueError, TypeError):
0372 |                 pass
0373 |         return None
0374 |     
0375 |     def _extract_cvss(self, finding: Dict[str, Any]) -> Optional[float]:
0376 |         """Extract CVSS score"""
0377 |         for key in ['cvss_score', 'cvss', 'score']:
0378 |             if key in finding:
0379 |                 try:
0380 |                     score = float(finding[key])
0381 |                     if 0 <= score <= 10:
0382 |                         return score
0383 |                 except:
0384 |                     pass
0385 |         return None
0386 | 
0387 | 
0388 | # ═══════════════════════════════════════════════════════════════════
0389 | # SCANNER SERVICE
0390 | # ═══════════════════════════════════════════════════════════════════
0391 | 
0392 | class ScannerService:
0393 |     """Main scanner service - orchestrates parsing and deduplication"""
0394 |     
0395 |     def __init__(
0396 |         self,
0397 |         cache=None,
0398 |         enable_deduplication: bool = True,
0399 |         dedup_strategy: str = 'moderate'
0400 |     ):
0401 |         self.parser = VulnerabilityParser()
0402 |         self.cache = cache
0403 |         self.dedup_detector = (
0404 |             DuplicateDetector(dedup_strategy) if enable_deduplication else None
0405 |         )
0406 |     
0407 |     async def scan_file(
0408 |         self,
0409 |         file_path: str,
0410 |         language: Optional[str] = None,
0411 |         tool_hint: Optional[str] = None
0412 |     ) -> ScanResult:
0413 |         """
0414 |         Scan and normalize vulnerability file
0415 |         
0416 |         Args:
0417 |             file_path: Path to vulnerability file
0418 |             language: Programming language (optional)
0419 |             tool_hint: SAST tool hint (optional)
0420 |         
0421 |         Returns:
0422 |             ScanResult with parsed vulnerabilities
0423 |         """
0424 |         logger.info(f"📁 Scanning file: {file_path}")
0425 |         start_time = datetime.now()
0426 |         
0427 |         # Validate file
0428 |         self._validate_file(file_path)
0429 |         
0430 |         # Check cache
0431 |         if self.cache:
0432 |             cached_result = await self._check_cache(file_path, language, tool_hint)
0433 |             if cached_result:
0434 |                 logger.info("✅ Using cached result")
0435 |                 return cached_result
0436 |         
0437 |         # Load and parse
0438 |         raw_data = self._load_file(file_path)
0439 |         vulnerabilities = self.parser.parse(raw_data, tool_hint)
0440 |         
0441 |         # Deduplicate
0442 |         removed_dups = 0
0443 |         if self.dedup_detector:
0444 |             vulnerabilities, removed_dups = self.dedup_detector.remove_duplicates(vulnerabilities)
0445 |         
0446 |         # Create result
0447 |         file_info = {
0448 |             'filename': Path(file_path).name,
0449 |             'full_path': str(Path(file_path).absolute()),
0450 |             'size_bytes': Path(file_path).stat().st_size,
0451 |             'language': language,
0452 |             'tool_hint': tool_hint,
0453 |             'duplicates_removed': removed_dups
0454 |         }
0455 |         
0456 |         scan_duration = (datetime.now() - start_time).total_seconds()
0457 |         
0458 |         scan_result = ScanResult(
0459 |             file_info=file_info,
0460 |             vulnerabilities=vulnerabilities,
0461 |             scan_duration_seconds=scan_duration,
0462 |             language_detected=language
0463 |         )
0464 |         
0465 |         # Cache result
0466 |         if self.cache:
0467 |             await self._save_to_cache(file_path, scan_result, language, tool_hint)
0468 |         
0469 |         logger.info(f"✅ Scan complete: {len(vulnerabilities)} vulnerabilities in {scan_duration:.2f}s")
0470 |         return scan_result
0471 |     
0472 |     def _validate_file(self, file_path: str) -> None:
0473 |         """Validate input file"""
0474 |         path = Path(file_path)
0475 |         
0476 |         if not path.exists():
0477 |             raise ValidationError(f"File not found: {file_path}")
0478 |         
0479 |         if path.suffix.lower() != '.json':
0480 |             raise ValidationError(f"Unsupported file type: {path.suffix}")
0481 |         
0482 |         # 100MB limit
0483 |         if path.stat().st_size > 100 * 1024 * 1024:
0484 |             raise ValidationError(f"File too large: {path.stat().st_size / 1024 / 1024:.1f}MB")
0485 |     
0486 |     def _load_file(self, file_path: str) -> Dict[str, Any]:
0487 |         """Load and parse JSON file"""
0488 |         try:
0489 |             with open(file_path, 'r', encoding='utf-8') as f:
0490 |                 return json.load(f)
0491 |         except json.JSONDecodeError as e:
0492 |             raise ParsingError(f"Invalid JSON: {e}")
0493 |         except Exception as e:
0494 |             raise ParsingError(f"Error reading file: {e}")
0495 |         
0496 |     async def _check_cache(
0497 |         self, file_path: str, language: Optional[str], tool_hint: Optional[str]
0498 |     ) -> Optional[ScanResult]:
0499 |         """Check cache for existing result"""
0500 |         if not self.cache:
0501 |             return None
0502 |         
0503 |         try:
0504 |             with open(file_path, 'r', encoding='utf-8') as f:
0505 |                 content = f.read()
0506 |             
0507 |             cached_data = self.cache.get(content, language, tool_hint)
0508 |             if cached_data:
0509 |                 return ScanResult(**cached_data)
0510 |         except Exception as e:
0511 |             logger.warning(f"Cache check failed: {e}")
0512 |         
0513 |         return None
0514 |     
0515 |     async def _save_to_cache(
0516 |         self,
0517 |         file_path: str,
0518 |         scan_result: ScanResult,
0519 |         language: Optional[str],
0520 |         tool_hint: Optional[str]
0521 |     ) -> None:
0522 |         """Save result to cache"""
0523 |         if not self.cache:
0524 |             return
0525 |         
0526 |         try:
0527 |             with open(file_path, 'r', encoding='utf-8') as f:
0528 |                 content = f.read()
0529 |             
0530 |             self.cache.put(content, scan_result.model_dump(), language, tool_hint)
0531 |             logger.debug("✅ Result cached")
0532 |         except Exception as e:
0533 |             logger.warning(f"Cache save failed: {e}")
```

---

### core\services\triage.py

**Ruta:** `core\services\triage.py`

```py
0001 | # core/services/triage.py
0002 | """
0003 | Triage Service - Simplified
0004 | ===========================
0005 | 
0006 | Responsibilities:
0007 | - Orchestrate vulnerability triage
0008 | - Handle chunked analysis
0009 | - Create conservative fallbacks
0010 | """
0011 | 
0012 | import logging
0013 | import asyncio
0014 | from typing import List, Optional
0015 | 
0016 | from ..models import Vulnerability, TriageResult, TriageDecision, AnalysisStatus
0017 | from ..exceptions import LLMError
0018 | from infrastructure.llm.client import LLMClient
0019 | from shared.metrics import MetricsCollector
0020 | 
0021 | logger = logging.getLogger(__name__)
0022 | 
0023 | 
0024 | class TriageService:
0025 |     """Simplified triage service with clean dependencies"""
0026 |     
0027 |     def __init__(
0028 |         self,
0029 |         llm_client: LLMClient,
0030 |         metrics: Optional[MetricsCollector] = None
0031 |     ):
0032 |         self.llm_client = llm_client
0033 |         self.metrics = metrics
0034 |     
0035 |     async def analyze_vulnerabilities(
0036 |         self,
0037 |         vulnerabilities: List[Vulnerability],
0038 |         language: Optional[str] = None,
0039 |         chunk_id: Optional[int] = None
0040 |     ) -> TriageResult:
0041 |         """
0042 |         Analyze vulnerabilities with LLM triage
0043 |         
0044 |         Args:
0045 |             vulnerabilities: List of vulnerabilities to analyze
0046 |             language: Programming language
0047 |             chunk_id: Optional chunk identifier
0048 |         
0049 |         Returns:
0050 |             TriageResult with decisions
0051 |         """
0052 |         # Handle empty list
0053 |         if not vulnerabilities:
0054 |             return self._create_empty_result()
0055 |         
0056 |         start_time = asyncio.get_event_loop().time()
0057 |         
0058 |         try:
0059 |             logger.info(f"🔍 Analyzing {len(vulnerabilities)} vulnerabilities")
0060 |             
0061 |             # Prepare request
0062 |             request = self._prepare_request(vulnerabilities, language, chunk_id)
0063 |             
0064 |             # Get LLM analysis
0065 |             llm_response = await self.llm_client.analyze_vulnerabilities(
0066 |                 request, language
0067 |             )
0068 |             
0069 |             # Validate and complete result
0070 |             validated = self._validate_result(llm_response, vulnerabilities)
0071 |             
0072 |             # Record metrics
0073 |             analysis_time = asyncio.get_event_loop().time() - start_time
0074 |             if self.metrics:
0075 |                 self.metrics.record_triage_analysis(
0076 |                     len(vulnerabilities), analysis_time, True, chunk_id
0077 |                 )
0078 |             
0079 |             logger.info(f"✅ Triage complete: {validated.confirmed_count} confirmed")
0080 |             return validated
0081 |             
0082 |         except Exception as e:
0083 |             analysis_time = asyncio.get_event_loop().time() - start_time
0084 |             if self.metrics:
0085 |                 self.metrics.record_triage_analysis(
0086 |                     len(vulnerabilities), analysis_time, False, chunk_id, str(e)
0087 |                 )
0088 |             
0089 |             logger.error(f"❌ Triage failed: {e}")
0090 |             return self._create_fallback_result(vulnerabilities, str(e))
0091 |     
0092 |     # ════════════════════════════════════════════════════════════════
0093 |     # PRIVATE HELPERS
0094 |     # ════════════════════════════════════════════════════════════════
0095 |     
0096 |     def _prepare_request(
0097 |         self,
0098 |         vulnerabilities: List[Vulnerability],
0099 |         language: Optional[str],
0100 |         chunk_id: Optional[int]
0101 |     ) -> str:
0102 |         """Prepare structured analysis request"""
0103 |         header = f"# VULNERABILITY TRIAGE REQUEST\n"
0104 |         if chunk_id:
0105 |             header += f"Chunk ID: {chunk_id}\n"
0106 |         header += f"Language: {language or 'Unknown'}\n"
0107 |         header += f"Total: {len(vulnerabilities)}\n\n"
0108 |         
0109 |         vuln_blocks = []
0110 |         for i, vuln in enumerate(vulnerabilities, 1):
0111 |             block = f"""## VULNERABILITY {i}
0112 | - ID: {vuln.id}
0113 | - TYPE: {vuln.type.value}
0114 | - SEVERITY: {vuln.severity.value}
0115 | - FILE: {vuln.file_path}:{vuln.line_number}
0116 | - TITLE: {vuln.title}
0117 | - DESCRIPTION: {vuln.description}"""
0118 |             
0119 |             if vuln.code_snippet:
0120 |                 snippet = vuln.code_snippet[:300]
0121 |                 block += f"\n- CODE: {snippet}"
0122 |             
0123 |             if vuln.cwe_id:
0124 |                 block += f"\n- CWE: {vuln.cwe_id}"
0125 |             
0126 |             vuln_blocks.append(block)
0127 |         
0128 |         return header + "\n\n".join(vuln_blocks)
0129 |     
0130 |     def _validate_result(
0131 |         self,
0132 |         llm_result: TriageResult,
0133 |         original_vulns: List[Vulnerability]
0134 |     ) -> TriageResult:
0135 |         """Validate and complete LLM result"""
0136 |         original_ids = {v.id for v in original_vulns}
0137 |         analyzed_ids = {d.vulnerability_id for d in llm_result.decisions}
0138 |         
0139 |         # Find missing vulnerabilities
0140 |         missing_ids = original_ids - analyzed_ids
0141 |         
0142 |         if missing_ids:
0143 |             logger.warning(f"⚠️  LLM missed {len(missing_ids)} vulnerabilities")
0144 |             
0145 |             # Add conservative decisions for missing
0146 |             for missing_id in missing_ids:
0147 |                 vuln = next(v for v in original_vulns if v.id == missing_id)
0148 |                 conservative = self._create_conservative_decision(vuln)
0149 |                 llm_result.decisions.append(conservative)
0150 |         
0151 |         return llm_result
0152 |     
0153 |     def _create_conservative_decision(
0154 |         self,
0155 |         vulnerability: Vulnerability
0156 |     ) -> TriageDecision:
0157 |         """Create conservative decision for unanalyzed vulnerability"""
0158 |         # High severity = confirmed, others = review
0159 |         if vulnerability.is_high_priority:
0160 |             decision = AnalysisStatus.CONFIRMED
0161 |             confidence = 0.7
0162 |             reasoning = f"Conservative: {vulnerability.severity.value} assumed confirmed"
0163 |         else:
0164 |             decision = AnalysisStatus.NEEDS_MANUAL_REVIEW
0165 |             confidence = 0.5
0166 |             reasoning = "Conservative: requires manual review"
0167 |         
0168 |         return TriageDecision(
0169 |             vulnerability_id=vulnerability.id,
0170 |             decision=decision,
0171 |             confidence_score=confidence,
0172 |             reasoning=reasoning,
0173 |             llm_model_used="conservative_fallback"
0174 |         )
0175 |     
0176 |     def _create_fallback_result(
0177 |         self,
0178 |         vulnerabilities: List[Vulnerability],
0179 |         error: str
0180 |     ) -> TriageResult:
0181 |         """Create fallback result when LLM fails"""
0182 |         logger.warning("⚠️  Creating conservative fallback result")
0183 |         
0184 |         decisions = [
0185 |             self._create_conservative_decision(vuln)
0186 |             for vuln in vulnerabilities
0187 |         ]
0188 |         
0189 |         return TriageResult(
0190 |             decisions=decisions,
0191 |             analysis_summary=f"Conservative fallback due to LLM error: {error}",
0192 |             llm_analysis_time_seconds=0.0
0193 |         )
0194 |     
0195 |     def _create_empty_result(self) -> TriageResult:
0196 |         """Create empty result for no vulnerabilities"""
0197 |         return TriageResult(
0198 |             decisions=[],
0199 |             analysis_summary="No vulnerabilities to analyze",
0200 |             llm_analysis_time_seconds=0.0
0201 |         )
```

---

### core\services\__init__.py

**Ruta:** `core\services\__init__.py`

```py
```

---

### infrastructure\cache.py

**Ruta:** `infrastructure\cache.py`

```py
0001 | # infrastructure/cache.py
0002 | """
0003 | Analysis Cache - Simplified
0004 | ===========================
0005 | 
0006 | Responsibilities:
0007 | - Cache analysis results
0008 | - Check TTL
0009 | - Clean expired entries
0010 | """
0011 | 
0012 | import hashlib
0013 | import json
0014 | import pickle
0015 | import logging
0016 | from pathlib import Path
0017 | from typing import Dict, Any, Optional
0018 | from datetime import datetime, timedelta
0019 | 
0020 | logger = logging.getLogger(__name__)
0021 | 
0022 | 
0023 | class AnalysisCache:
0024 |     """Simple file-based cache with TTL"""
0025 |     
0026 |     def __init__(self, cache_dir: str = ".security_cache", ttl_hours: int = 24):
0027 |         """
0028 |         Initialize cache
0029 |         
0030 |         Args:
0031 |             cache_dir: Cache directory path
0032 |             ttl_hours: Time to live in hours
0033 |         """
0034 |         self.cache_dir = Path(cache_dir)
0035 |         self.ttl_hours = ttl_hours
0036 |         
0037 |         # Create directory
0038 |         self.cache_dir.mkdir(parents=True, exist_ok=True)
0039 |         
0040 |         # Clean expired on init
0041 |         self._cleanup_expired()
0042 |         
0043 |         logger.info(f"💾 Cache initialized: {cache_dir} (TTL: {ttl_hours}h)")
0044 |     
0045 |     def get(
0046 |         self,
0047 |         content: str,
0048 |         language: Optional[str] = None,
0049 |         tool_hint: Optional[str] = None
0050 |     ) -> Optional[Dict[str, Any]]:
0051 |         """
0052 |         Get cached result
0053 |         
0054 |         Args:
0055 |             content: File content (used for key)
0056 |             language: Programming language
0057 |             tool_hint: Tool hint
0058 |         
0059 |         Returns:
0060 |             Cached data or None if not found/expired
0061 |         """
0062 |         try:
0063 |             cache_key = self._generate_key(content, language, tool_hint)
0064 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0065 |             
0066 |             # Check exists
0067 |             if not cache_file.exists():
0068 |                 return None
0069 |             
0070 |             # Check TTL
0071 |             file_age = datetime.now() - datetime.fromtimestamp(
0072 |                 cache_file.stat().st_mtime
0073 |             )
0074 |             
0075 |             if file_age > timedelta(hours=self.ttl_hours):
0076 |                 logger.debug(f"Cache expired: {cache_key}")
0077 |                 cache_file.unlink()
0078 |                 return None
0079 |             
0080 |             # Load data
0081 |             with open(cache_file, 'rb') as f:
0082 |                 data = pickle.load(f)
0083 |             
0084 |             logger.info(f"✅ Cache hit: {cache_key}")
0085 |             return data
0086 |             
0087 |         except Exception as e:
0088 |             logger.warning(f"Cache read failed: {e}")
0089 |             return None
0090 |     
0091 |     def put(
0092 |         self,
0093 |         content: str,
0094 |         data: Dict[str, Any],
0095 |         language: Optional[str] = None,
0096 |         tool_hint: Optional[str] = None
0097 |     ) -> None:
0098 |         """
0099 |         Store result in cache
0100 |         
0101 |         Args:
0102 |             content: File content (used for key)
0103 |              Data to cache
0104 |             language: Programming language
0105 |             tool_hint: Tool hint
0106 |         """
0107 |         try:
0108 |             cache_key = self._generate_key(content, language, tool_hint)
0109 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0110 |             
0111 |             # Write data
0112 |             with open(cache_file, 'wb') as f:
0113 |                 pickle.dump(data, f)
0114 |             
0115 |             logger.debug(f"💾 Cached: {cache_key}")
0116 |             
0117 |         except Exception as e:
0118 |             logger.warning(f"Cache write failed: {e}")
0119 |     
0120 |     def clear(self) -> int:
0121 |         """
0122 |         Clear all cache entries
0123 |         
0124 |         Returns:
0125 |             Number of entries cleared
0126 |         """
0127 |         count = 0
0128 |         
0129 |         for cache_file in self.cache_dir.glob("*.cache"):
0130 |             try:
0131 |                 cache_file.unlink()
0132 |                 count += 1
0133 |             except Exception as e:
0134 |                 logger.warning(f"Failed to delete {cache_file}: {e}")
0135 |         
0136 |         logger.info(f"🗑️  Cache cleared: {count} entries")
0137 |         return count
0138 |     
0139 |     def get_stats(self) -> Dict[str, Any]:
0140 |         """
0141 |         Get cache statistics
0142 |         
0143 |         Returns:
0144 |             Dict with cache stats
0145 |         """
0146 |         cache_files = list(self.cache_dir.glob("*.cache"))
0147 |         
0148 |         total_size = sum(f.stat().st_size for f in cache_files)
0149 |         
0150 |         return {
0151 |             "total_entries": len(cache_files),
0152 |             "total_size_bytes": total_size,
0153 |             "total_size_mb": total_size / (1024 * 1024),
0154 |             "cache_dir": str(self.cache_dir),
0155 |             "ttl_hours": self.ttl_hours
0156 |         }
0157 |     
0158 |     # ════════════════════════════════════════════════════════════════
0159 |     # PRIVATE HELPERS
0160 |     # ════════════════════════════════════════════════════════════════
0161 |     
0162 |     def _generate_key(
0163 |         self,
0164 |         content: str,
0165 |         language: Optional[str],
0166 |         tool_hint: Optional[str]
0167 |     ) -> str:
0168 |         """Generate cache key from content hash"""
0169 |         key_data = f"{content}|{language or ''}|{tool_hint or ''}"
0170 |         return hashlib.sha256(key_data.encode()).hexdigest()[:16]
0171 |     
0172 |     def _cleanup_expired(self) -> None:
0173 |         """Remove expired cache entries"""
0174 |         try:
0175 |             cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)
0176 |             removed = 0
0177 |             
0178 |             for cache_file in self.cache_dir.glob("*.cache"):
0179 |                 file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
0180 |                 if file_time < cutoff_time:
0181 |                     cache_file.unlink()
0182 |                     removed += 1
0183 |             
0184 |             if removed > 0:
0185 |                 logger.info(f"🗑️  Cleaned {removed} expired cache entries")
0186 |                 
0187 |         except Exception as e:
0188 |             logger.warning(f"Cache cleanup failed: {e}")
```

---

### infrastructure\config.py

**Ruta:** `infrastructure\config.py`

```py
0001 | # infrastructure/config.py
0002 | """
0003 | ⚙️ Configuration Management - Simplified & Fixed
0004 | ================================================
0005 | """
0006 | 
0007 | import os
0008 | import logging
0009 | from typing import Dict, Any, Optional
0010 | from pathlib import Path
0011 | 
0012 | logger = logging.getLogger(__name__)
0013 | 
0014 | 
0015 | class Settings:
0016 |     """Simplified settings manager with smart defaults"""
0017 |     
0018 |     def __init__(self):
0019 |         """Load configuration from environment"""
0020 |         
0021 |         # Load .env if available
0022 |         self._load_dotenv()
0023 |         
0024 |         # ═══════════════════════════════════════════════════════════
0025 |         # LLM CONFIGURATION
0026 |         # ═══════════════════════════════════════════════════════════
0027 |         
0028 |         self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
0029 |         self.watsonx_api_key = os.getenv("RESEARCH_API_KEY", "").strip()
0030 |         self.llm_primary_provider = os.getenv("LLM_PRIMARY_PROVIDER", "openai").lower()
0031 |         
0032 |         # LLM parameters
0033 |         self.llm_temperature = self._get_float("LLM_TEMPERATURE", 0.1)
0034 |         self.llm_max_tokens = self._get_int("LLM_MAX_TOKENS", 2048)
0035 |         self.llm_timeout = self._get_int("LLM_TIMEOUT", 180)
0036 |         self.llm_user_email = os.getenv("LLM_USER_EMAIL", "franciscojavier.suarez_css@research.com")
0037 |         
0038 |         # Models
0039 |         self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5")
0040 |         self.watsonx_model = os.getenv("WATSONX_MODEL", "meta-llama/llama-3-3-70b-instruct")
0041 |         
0042 |         # Research API URL
0043 |         self.research_api_url = os.getenv(
0044 |             "RESEARCH_API_URL",
0045 |             "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
0046 |         )
0047 |         
0048 |         # ═══════════════════════════════════════════════════════════
0049 |         # FEATURE FLAGS
0050 |         # ═══════════════════════════════════════════════════════════
0051 |         
0052 |         self.cache_enabled = self._get_bool("CACHE_ENABLED", True)
0053 |         self.metrics_enabled = self._get_bool("METRICS_ENABLED", True)
0054 |         self.dedup_enabled = self._get_bool("DEDUP_ENABLED", True)
0055 |         
0056 |         # ═══════════════════════════════════════════════════════════
0057 |         # PARAMETERS
0058 |         # ═══════════════════════════════════════════════════════════
0059 |         
0060 |         self.chunking_max_vulnerabilities = self._get_int("CHUNKING_MAX_VULNS", 5)
0061 |         self.cache_ttl_hours = self._get_int("CACHE_TTL_HOURS", 24)
0062 |         self.cache_directory = os.getenv("CACHE_DIR", ".security_cache")
0063 |         self.dedup_strategy = os.getenv("DEDUP_STRATEGY", "moderate").lower()
0064 |         self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
0065 |         
0066 |         # ═══════════════════════════════════════════════════════════
0067 |         # VALIDATE & LOG
0068 |         # ═══════════════════════════════════════════════════════════
0069 |         
0070 |         self._validate()
0071 |         self._log_config()
0072 |     
0073 |     # ════════════════════════════════════════════════════════════════
0074 |     # PROPERTIES
0075 |     # ════════════════════════════════════════════════════════════════
0076 |     
0077 |     @property
0078 |     def has_llm_provider(self) -> bool:
0079 |         """Check if at least one LLM provider is configured"""
0080 |         return bool(self.openai_api_key or self.watsonx_api_key)
0081 |     
0082 |     @property
0083 |     def chunking_config(self) -> Dict[str, Any]:
0084 |         """Get chunking configuration"""
0085 |         return {
0086 |             "max_vulnerabilities_per_chunk": self.chunking_max_vulnerabilities,
0087 |             "max_size_bytes": 8000,
0088 |             "overlap_vulnerabilities": 1,
0089 |             "min_chunk_size": 3
0090 |         }
0091 |     
0092 |     # ════════════════════════════════════════════════════════════════
0093 |     # PUBLIC API
0094 |     # ════════════════════════════════════════════════════════════════
0095 |     
0096 |     def get_available_llm_provider(self) -> str:
0097 |         """Get first available LLM provider"""
0098 |         # Priority 1: Primary provider if has key
0099 |         if self.llm_primary_provider == "openai" and self.openai_api_key:
0100 |             return "openai"
0101 |         
0102 |         if self.llm_primary_provider == "watsonx" and self.watsonx_api_key:
0103 |             return "watsonx"
0104 |         
0105 |         # Priority 2: Fallback to any available
0106 |         if self.openai_api_key:
0107 |             return "openai"
0108 |         
0109 |         if self.watsonx_api_key:
0110 |             return "watsonx"
0111 |         
0112 |         # No provider available
0113 |         raise ValueError(
0114 |             "No LLM provider configured. Set OPENAI_API_KEY or RESEARCH_API_KEY"
0115 |         )
0116 |     
0117 |     def has_provider(self, provider: str) -> bool:
0118 |         """Check if specific provider is available"""
0119 |         if provider.lower() == "openai":
0120 |             return bool(self.openai_api_key)
0121 |         elif provider.lower() == "watsonx":
0122 |             return bool(self.watsonx_api_key)
0123 |         return False
0124 |     
0125 |     def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
0126 |         """Get LLM configuration for specific provider"""
0127 |         if provider is None:
0128 |             provider = self.get_available_llm_provider()
0129 |         
0130 |         provider = provider.lower()
0131 |         
0132 |         if provider == "openai":
0133 |             return {
0134 |                 "provider": "openai",
0135 |                 "api_key": self.openai_api_key,
0136 |                 "model": self.openai_model,
0137 |                 "temperature": self.llm_temperature,
0138 |                 "max_tokens": self.llm_max_tokens,
0139 |                 "timeout": self.llm_timeout,
0140 |                 "base_url": self.research_api_url  # Research API también para OpenAI
0141 |             }
0142 |         
0143 |         elif provider == "watsonx":
0144 |             return {
0145 |                 "provider": "watsonx",
0146 |                 "api_key": self.watsonx_api_key,
0147 |                 "model": self.watsonx_model,
0148 |                 "temperature": self.llm_temperature,
0149 |                 "max_tokens": self.llm_max_tokens,
0150 |                 "timeout": self.llm_timeout,
0151 |                 "base_url": self.research_api_url,
0152 |                 "user_email": self.llm_user_email
0153 |             }
0154 |         
0155 |         else:
0156 |             raise ValueError(f"Unknown provider: {provider}")
0157 |     
0158 |     # ════════════════════════════════════════════════════════════════
0159 |     # PRIVATE HELPERS
0160 |     # ════════════════════════════════════════════════════════════════
0161 |     
0162 |     def _load_dotenv(self):
0163 |         """Load .env file if available"""
0164 |         try:
0165 |             from dotenv import load_dotenv
0166 |             if Path(".env").exists():
0167 |                 load_dotenv()
0168 |         except ImportError:
0169 |             pass
0170 |     
0171 |     def _get_int(self, key: str, default: int) -> int:
0172 |         """Get integer from environment"""
0173 |         value = os.getenv(key)
0174 |         if value is None:
0175 |             return default
0176 |         try:
0177 |             return int(value)
0178 |         except ValueError:
0179 |             logger.warning(f"Invalid int for {key}='{value}', using default: {default}")
0180 |             return default
0181 |     
0182 |     def _get_float(self, key: str, default: float) -> float:
0183 |         """Get float from environment"""
0184 |         value = os.getenv(key)
0185 |         if value is None:
0186 |             return default
0187 |         try:
0188 |             return float(value)
0189 |         except ValueError:
0190 |             logger.warning(f"Invalid float for {key}='{value}', using default: {default}")
0191 |             return default
0192 |     
0193 |     def _get_bool(self, key: str, default: bool) -> bool:
0194 |         """Get boolean from environment"""
0195 |         value = os.getenv(key)
0196 |         if value is None:
0197 |             return default
0198 |         return value.lower() in ('true', '1', 'yes', 'on')
0199 |     
0200 |     def _validate(self):
0201 |         """Validate configuration"""
0202 |         # Validate temperature
0203 |         if not (0.0 <= self.llm_temperature <= 2.0):
0204 |             logger.warning(f"Invalid temperature {self.llm_temperature}, using 0.1")
0205 |             self.llm_temperature = 0.1
0206 |         
0207 |         # Validate dedup strategy
0208 |         if self.dedup_strategy not in ('strict', 'moderate', 'loose'):
0209 |             logger.warning(f"Invalid dedup_strategy '{self.dedup_strategy}', using 'moderate'")
0210 |             self.dedup_strategy = 'moderate'
0211 |         
0212 |         # Validate log level
0213 |         valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
0214 |         if self.log_level not in valid_levels:
0215 |             logger.warning(f"Invalid log_level '{self.log_level}', using 'INFO'")
0216 |             self.log_level = 'INFO'
0217 |         
0218 |         # Create cache directory
0219 |         if self.cache_enabled:
0220 |             Path(self.cache_directory).mkdir(parents=True, exist_ok=True)
0221 |     
0222 |     def _log_config(self):
0223 |         """Log configuration summary - FIXED"""
0224 |         # Don't log during initial setup if logger not configured
0225 |         try:
0226 |             logger.info("="*60)
0227 |             logger.info("⚙️  Configuration Loaded")
0228 |             logger.info("="*60)
0229 |             
0230 |             # LLM Status
0231 |             if self.has_llm_provider:
0232 |                 try:
0233 |                     provider = self.get_available_llm_provider()
0234 |                     logger.info(f"🤖 LLM Provider: {provider.upper()}")
0235 |                     
0236 |                     config = self.get_llm_config(provider)
0237 |                     logger.info(f"   Model: {config['model']}")
0238 |                     logger.info(f"   Temperature: {config['temperature']}")
0239 |                     logger.info(f"   Max Tokens: {config['max_tokens']}")
0240 |                     logger.info(f"   Timeout: {config['timeout']}s")
0241 |                 except ValueError:
0242 |                     logger.warning("⚠️  LLM: No provider configured")
0243 |             else:
0244 |                 logger.warning("⚠️  LLM: No provider configured (basic mode only)")
0245 |             
0246 |             # Features
0247 |             logger.info("🔧 Features:")
0248 |             logger.info(f"   Cache: {'✅' if self.cache_enabled else '❌'}")
0249 |             logger.info(f"   Deduplication: {'✅' if self.dedup_enabled else '❌'} ({self.dedup_strategy})")
0250 |             logger.info(f"   Metrics: {'✅' if self.metrics_enabled else '❌'}")
0251 |             
0252 |             # Chunking
0253 |             logger.info("🧩 Chunking:")
0254 |             logger.info(f"   Max vulns/chunk: {self.chunking_max_vulnerabilities}")
0255 |             
0256 |             logger.info("="*60)
0257 |         except Exception as e:
0258 |             # Silently ignore logging errors during initialization
0259 |             pass
0260 |     
0261 |     def __repr__(self) -> str:
0262 |         """String representation"""
0263 |         provider_status = "configured" if self.has_llm_provider else "not configured"
0264 |         return f"<Settings: LLM={provider_status}, Log={self.log_level}>"
0265 | 
0266 | 
0267 | # ════════════════════════════════════════════════════════════════════
0268 | # GLOBAL INSTANCE
0269 | # ════════════════════════════════════════════════════════════════════
0270 | 
0271 | settings = Settings()
0272 | 
0273 | 
0274 | # ════════════════════════════════════════════════════════════════════
0275 | # CONVENIENCE FUNCTIONS
0276 | # ════════════════════════════════════════════════════════════════════
0277 | 
0278 | def get_config() -> Settings:
0279 |     """Get global settings instance"""
0280 |     return settings
0281 | 
0282 | 
0283 | def reload_config() -> Settings:
0284 |     """Reload configuration"""
0285 |     global settings
0286 |     settings = Settings()
0287 |     return settings
0288 | 
0289 | 
0290 | def validate_llm_config(provider: str) -> bool:
0291 |     """Validate LLM provider configuration"""
0292 |     try:
0293 |         config = settings.get_llm_config(provider)
0294 |         return bool(config["api_key"])
0295 |     except (ValueError, KeyError):
0296 |         return False
```

---

### infrastructure\__init__.py

**Ruta:** `infrastructure\__init__.py`

```py
```

---

### infrastructure\llm\client.py

**Ruta:** `infrastructure\llm\client.py`

```py
0001 | # infrastructure/llm/client.py
0002 | """
0003 | LLM Client - Clean & Optimized
0004 | ==============================
0005 | 
0006 | Responsibilities:
0007 | - HTTP communication with LLM providers
0008 | - Request/response handling
0009 | - Retry logic
0010 | - Error handling
0011 | 
0012 | Does NOT handle:
0013 | - JSON parsing (delegated to response_parser)
0014 | - Prompt construction (delegated to prompts)
0015 | """
0016 | 
0017 | import requests
0018 | import logging
0019 | import time
0020 | import uuid
0021 | import asyncio
0022 | from typing import Dict, Any, Optional
0023 | 
0024 | from core.models import TriageResult, RemediationPlan
0025 | from core.exceptions import LLMError
0026 | from infrastructure.config import settings
0027 | from .response_parser import LLMResponseParser
0028 | from .prompts import PromptManager
0029 | 
0030 | logger = logging.getLogger(__name__)
0031 | 
0032 | 
0033 | class LLMClient:
0034 |     """Simplified LLM client with clean separation of concerns"""
0035 |     
0036 |     def __init__(self, llm_provider: str = "watsonx", enable_debug: bool = False):
0037 |         """
0038 |         Initialize LLM Client
0039 |         
0040 |         Args:
0041 |             llm_provider: "openai" or "watsonx"
0042 |             enable_debug: Enable debug logging
0043 |         """
0044 |         self.llm_provider = llm_provider.lower()
0045 |         self.debug_enabled = enable_debug
0046 |         
0047 |         # Load configuration from settings
0048 |         try:
0049 |             self.config = settings.get_llm_config(self.llm_provider)
0050 |         except ValueError as e:
0051 |             raise ValueError(f"Cannot initialize {llm_provider}: {e}")
0052 |         
0053 |         # Extract config
0054 |         self.api_key = self.config["api_key"]
0055 |         self.model_name = self.config["model"]
0056 |         self.temperature = self.config["temperature"]
0057 |         self.max_tokens = self.config["max_tokens"]
0058 |         self.timeout = self.config["timeout"]
0059 |         
0060 |         # Provider-specific config
0061 |         if self.llm_provider == "watsonx":
0062 |             self.base_url = self.config["base_url"]
0063 |             self.user_email = self.config["user_email"]
0064 |             self.endpoint = "/research/llm/wx/clients"
0065 |         else:  # openai
0066 |             self.base_url = self.config["base_url"]
0067 |             self.endpoint = "/research/llm/openai/clients"
0068 |         
0069 |         # HTTP session
0070 |         self.session = requests.Session()
0071 |         self.session.headers.update({
0072 |             "Content-Type": "application/json",
0073 |             "x-api-key": self.api_key
0074 |         })
0075 |         
0076 |         # Retry configuration
0077 |         self.max_retries = 3
0078 |         self.retry_delay_base = 2
0079 |         
0080 |         # Dependencies
0081 |         self.parser = LLMResponseParser(debug_enabled=enable_debug)
0082 |         self.prompt_manager = PromptManager()
0083 |         
0084 |         logger.info(f"🤖 LLM Client initialized: {self.llm_provider}")
0085 |         logger.info(f"   Model: {self.model_name}")
0086 |         logger.info(f"   Timeout: {self.timeout}s")
0087 |     
0088 |     # ════════════════════════════════════════════════════════════════
0089 |     # PUBLIC API - High-level methods
0090 |     # ════════════════════════════════════════════════════════════════
0091 |     
0092 |     async def analyze_vulnerabilities(
0093 |         self,
0094 |         vulnerabilities_data: str,
0095 |         language: Optional[str] = None
0096 |     ) -> TriageResult:
0097 |         """
0098 |         Analyze vulnerabilities for triage
0099 |         
0100 |         Args:
0101 |             vulnerabilities_ Formatted vulnerability data
0102 |             language: Programming language
0103 |         
0104 |         Returns:
0105 |             TriageResult with decisions
0106 |         """
0107 |         logger.info("🔍 Starting triage analysis")
0108 |         
0109 |         # Get prompt
0110 |         system_prompt = self.prompt_manager.get_triage_system_prompt(language)
0111 |         full_message = self._build_message(system_prompt, vulnerabilities_data)
0112 |         
0113 |         # Call LLM with retry
0114 |         start = time.time()
0115 |         response = await self._call_with_retry(full_message, temperature=0.1)
0116 |         duration = time.time() - start
0117 |         
0118 |         logger.info(f"✅ Response received in {duration:.2f}s")
0119 |         
0120 |         # Parse response
0121 |         result = self.parser.parse_triage_response(response, vulnerabilities_data)
0122 |         
0123 |         return result
0124 |     
0125 |     async def generate_remediation_plan(
0126 |         self,
0127 |         vulnerability_data: str,
0128 |         vuln_type: str = None,
0129 |         language: Optional[str] = None,
0130 |         severity: str = "HIGH"
0131 |     ) -> RemediationPlan:
0132 |         """
0133 |         Generate remediation plan
0134 |         
0135 |         Args:
0136 |             vulnerability_ Vulnerability details
0137 |             vuln_type: Type of vulnerability
0138 |             language: Programming language
0139 |             severity: Severity level
0140 |         
0141 |         Returns:
0142 |             RemediationPlan with steps
0143 |         """
0144 |         logger.info("🛠️  Generating remediation plan")
0145 |         
0146 |         # Get prompt
0147 |         system_prompt = self.prompt_manager.get_remediation_system_prompt(
0148 |             vuln_type=vuln_type or "Security Issue",
0149 |             language=language,
0150 |             severity=severity
0151 |         )
0152 |         full_message = self._build_message(system_prompt, vulnerability_data)
0153 |         
0154 |         # Call LLM with retry
0155 |         start = time.time()
0156 |         response = await self._call_with_retry(full_message, temperature=0.2)
0157 |         duration = time.time() - start
0158 |         
0159 |         logger.info(f"✅ Response received in {duration:.2f}s")
0160 |         
0161 |         # Parse response
0162 |         result = self.parser.parse_remediation_response(response, vuln_type, language)
0163 |         
0164 |         return result
0165 |     
0166 |     # ════════════════════════════════════════════════════════════════
0167 |     # PRIVATE API - HTTP communication
0168 |     # ════════════════════════════════════════════════════════════════
0169 |     
0170 |     async def _call_with_retry(
0171 |         self,
0172 |         message: str,
0173 |         temperature: float = 0.1
0174 |     ) -> str:
0175 |         """
0176 |         Call LLM with exponential backoff retry
0177 |         
0178 |         Args:
0179 |             message: Full message to send
0180 |             temperature: Temperature setting
0181 |         
0182 |         Returns:
0183 |             LLM response text
0184 |         
0185 |         Raises:
0186 |             LLMError: If all retries fail
0187 |         """
0188 |         last_error = None
0189 |         
0190 |         for attempt in range(self.max_retries):
0191 |             try:
0192 |                 logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries}")
0193 |                 
0194 |                 response = await self._call_api(message, temperature)
0195 |                 
0196 |                 if attempt > 0:
0197 |                     logger.info(f"✅ Succeeded on retry {attempt + 1}")
0198 |                 
0199 |                 return response
0200 |                 
0201 |             except LLMError as e:
0202 |                 last_error = e
0203 |                 
0204 |                 if attempt < self.max_retries - 1:
0205 |                     delay = self.retry_delay_base ** (attempt + 1)
0206 |                     logger.warning(f"⚠️  Attempt {attempt + 1} failed: {e}")
0207 |                     logger.warning(f"⏳ Retrying in {delay}s...")
0208 |                     await asyncio.sleep(delay)
0209 |                 else:
0210 |                     logger.error(f"❌ All {self.max_retries} attempts failed")
0211 |         
0212 |         raise last_error or LLMError(f"All {self.max_retries} attempts failed")
0213 |     
0214 |     async def _call_api(self, message: str, temperature: float) -> str:
0215 |         """
0216 |         Single API call (no retry)
0217 |         
0218 |         Args:
0219 |             message: Message to send
0220 |             temperature: Temperature setting
0221 |         
0222 |         Returns:
0223 |             Response content
0224 |         
0225 |         Raises:
0226 |             LLMError: On any API error
0227 |         """
0228 |         url = f"{self.base_url}{self.endpoint}"
0229 |         session_uuid = str(uuid.uuid4())
0230 |         
0231 |         # Build payload
0232 |         payload = {
0233 |             "message": {"role": "user", "content": message},
0234 |             "temperature": temperature,
0235 |             "model": self.model_name,
0236 |             "prompt": None,
0237 |             "uuid": session_uuid,
0238 |             "language": "es",
0239 |             "user": getattr(self, 'user_email', 'user@research.com')
0240 |         }
0241 |         
0242 |         start = time.time()
0243 |         
0244 |         try:
0245 |             logger.debug(f"📡 POST {url}")
0246 |             logger.debug(f"   Model: {self.model_name}")
0247 |             logger.debug(f"   Message: {len(message):,} chars")
0248 |             
0249 |             # Make request
0250 |             response = self.session.post(url, json=payload, timeout=self.timeout)
0251 |             duration = time.time() - start
0252 |             
0253 |             logger.info(f"📡 HTTP {response.status_code} ({duration:.2f}s)")
0254 |             
0255 |             # Check status
0256 |             if response.status_code != 200:
0257 |                 error_msg = f"HTTP {response.status_code}: {response.text[:500]}"
0258 |                 raise LLMError(error_msg)
0259 |             
0260 |             # Extract content
0261 |             content = self._extract_content(response)
0262 |             
0263 |             if not content or not content.strip():
0264 |                 raise LLMError("Empty response from LLM")
0265 |             
0266 |             logger.info(f"✅ Received {len(content):,} chars")
0267 |             return content
0268 |             
0269 |         except requests.exceptions.Timeout:
0270 |             raise LLMError(f"Request timeout after {self.timeout}s")
0271 |         
0272 |         except requests.exceptions.ConnectionError as e:
0273 |             raise LLMError(f"Connection error: {e}")
0274 |         
0275 |         except LLMError:
0276 |             raise
0277 |         
0278 |         except Exception as e:
0279 |             raise LLMError(f"Unexpected error: {e}")
0280 |     
0281 |     def _extract_content(self, response: requests.Response) -> str:
0282 |         """
0283 |         Extract content from API response
0284 |         
0285 |         Args:
0286 |             response: HTTP response
0287 |         
0288 |         Returns:
0289 |             Extracted content string
0290 |         """
0291 |         # Try JSON first
0292 |         try:
0293 |             data = response.json()
0294 |             
0295 |             # Search for content in common fields
0296 |             for field in ['content', 'response', 'message', 'text', 'output', 'result']:
0297 |                 if field in data:
0298 |                     value = data[field]
0299 |                     
0300 |                     # Recursive extraction for nested dicts
0301 |                     if isinstance(value, dict):
0302 |                         nested = self._extract_from_dict(value)
0303 |                         if nested:
0304 |                             return nested
0305 |                     elif value:
0306 |                         return str(value)
0307 |             
0308 |             # No known field, return as JSON string
0309 |             return response.text
0310 |             
0311 |         except ValueError:
0312 |             # Not JSON, return as text
0313 |             return response.text
0314 |     
0315 |     def _extract_from_dict(self, data: Dict) -> Optional[str]:
0316 |         """Recursively extract content from nested dict"""
0317 |         for field in ['content', 'response', 'message', 'text']:
0318 |             if field in data and data[field]:
0319 |                 return str(data[field])
0320 |         return None
0321 |     
0322 |     def _build_message(self, system_prompt: str, user_data: str) -> str:
0323 |         """Build complete message from prompt and data"""
0324 |         return f"""{system_prompt}
0325 | 
0326 | # DATA TO ANALYZE
0327 | 
0328 | {user_data}
0329 | 
0330 | # INSTRUCTIONS
0331 | 
0332 | Return ONLY valid JSON with no markdown wrappers.
0333 | Ensure all required fields are present.
0334 | """
0335 |     
0336 |     def __repr__(self) -> str:
0337 |         return f"<LLMClient: {self.llm_provider}, model={self.model_name}>"
```

---

### infrastructure\llm\prompts.py

**Ruta:** `infrastructure\llm\prompts.py`

```py
0001 | # infrastructure/llm/prompts.py
0002 | """
0003 | Prompt Management - Optimized
0004 | =============================
0005 | 
0006 | Responsibilities:
0007 | - Manage LLM prompts
0008 | - Provide language-specific guidance
0009 | - Ensure consistent prompt structure
0010 | """
0011 | 
0012 | from typing import Optional
0013 | 
0014 | 
0015 | class PromptManager:
0016 |     """Centralized prompt management"""
0017 |     
0018 |     def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
0019 |         """
0020 |         Get system prompt for vulnerability triage
0021 |         
0022 |         Args:
0023 |             language: Programming language (optional)
0024 |         
0025 |         Returns:
0026 |             Formatted system prompt
0027 |         """
0028 |         model_name = "meta-llama/llama-3-3-70b-instruct"
0029 |         
0030 |         return f"""You are a cybersecurity expert specializing in vulnerability analysis.
0031 | 
0032 | TASK: Analyze vulnerabilities and classify each as:
0033 | - "confirmed": Real security vulnerability requiring fixing
0034 | - "false_positive": Scanner false alarm, not a real issue  
0035 | - "needs_manual_review": Uncertain, needs human expert review
0036 | 
0037 | CONTEXT: Language/Technology: {language or 'Unknown'}
0038 | 
0039 | OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
0040 | {{
0041 |   "decisions": [
0042 |     {{
0043 |       "vulnerability_id": "vuln_id_here",
0044 |       "decision": "confirmed|false_positive|needs_manual_review",
0045 |       "confidence_score": 0.0-1.0,
0046 |       "reasoning": "Brief technical explanation",
0047 |       "llm_model_used": "{model_name}"
0048 |     }}
0049 |   ],
0050 |   "analysis_summary": "Overall analysis summary",
0051 |   "llm_analysis_time_seconds": 1.5
0052 | }}
0053 | 
0054 | GUIDELINES:
0055 | - Be conservative: when uncertain, choose "needs_manual_review"
0056 | - Consider code context, severity, and vulnerability type
0057 | - Provide clear, technical reasoning
0058 | - Focus on actual exploitability, not theoretical risks"""
0059 |     
0060 |     def get_remediation_system_prompt(
0061 |         self,
0062 |         vuln_type: str,
0063 |         language: Optional[str] = None,
0064 |         severity: str = "HIGH"
0065 |     ) -> str:
0066 |         """
0067 |         Get system prompt for remediation plan generation
0068 |         
0069 |         Args:
0070 |             vuln_type: Vulnerability type
0071 |             language: Programming language (optional)
0072 |             severity: Severity level
0073 |         
0074 |         Returns:
0075 |             Formatted system prompt
0076 |         """
0077 |         lang_guide = self._get_language_guide(language)
0078 |         model_name = "meta-llama/llama-3-3-70b-instruct"
0079 |         
0080 |         return f"""You are a senior security engineer creating DETAILED remediation plans.
0081 | 
0082 | # CONTEXT
0083 | - Vulnerability: {vuln_type}
0084 | - Language: {language or 'Generic'}
0085 | - Severity: {severity}
0086 | - Target: Mid-level developers (3-5 years experience)
0087 | 
0088 | # REQUIREMENTS
0089 | 
0090 | Each step MUST include:
0091 | 
0092 | 1. **Specific Title**: Action-oriented (verb + specific action)
0093 |    ❌ BAD: "Implement security fix"
0094 |    ✅ GOOD: "Replace string concatenation with parameterized queries"
0095 | 
0096 | 2. **Detailed Description**: WHY this prevents the vulnerability (100+ words)
0097 |    - Security principle
0098 |    - How vulnerability is exploited
0099 |    - How fix prevents exploitation
0100 |    - Edge cases handled
0101 | 
0102 | 3. **Complete Code Example**: BEFORE and AFTER
0103 |    - BEFORE: Exact vulnerable code (5-10 lines)
0104 |    - AFTER: Complete working fix (10-20 lines)
0105 |    - Include error handling
0106 |    - Add inline security comments
0107 | 
0108 | 4. **Concrete Validation**: Specific test
0109 |    ❌ BAD: "Test that it works"
0110 |    ✅ GOOD: "Test with input='../../etc/passwd', verify error 'Invalid filename'"
0111 | 
0112 | # OUTPUT FORMAT (STRICT JSON)
0113 | 
0114 | {{
0115 |   "vulnerability_id": "exact_id_from_input",
0116 |   "vulnerability_type": "{vuln_type}",
0117 |   "priority_level": "immediate|high|medium|low",
0118 |   "complexity_score": 6.5,
0119 |   
0120 |   "steps": [
0121 |     {{
0122 |       "step_number": 1,
0123 |       "title": "Action title",
0124 |       "description": "Detailed explanation (min 100 words)",
0125 |       "code_example": "BEFORE:\\n...\\n\\nAFTER:\\n...",
0126 |       "estimated_minutes": 30,
0127 |       "difficulty": "easy|medium|hard",
0128 |       "tools_required": ["Tool name"]
0129 |     }}
0130 |   ],
0131 |   
0132 |   "risk_if_not_fixed": "Concrete impact with CVE example",
0133 |   "references": ["https://owasp.org/...", "https://cwe.mitre.org/..."],
0134 |   "llm_model_used": "{model_name}"
0135 | }}
0136 | 
0137 | {lang_guide}
0138 | 
0139 | # QUALITY CHECKS
0140 | 
0141 | Before responding, verify:
0142 | - [ ] Each step has BEFORE and AFTER code
0143 | - [ ] Each AFTER code is COMPLETE (copy-paste ready)
0144 | - [ ] Each description is 100+ words
0145 | - [ ] Validation tests have exact inputs/outputs
0146 | - [ ] No generic phrases like "implement security"
0147 | - [ ] Risk mentions specific CVE or real breach
0148 | - [ ] All code includes error handling
0149 | 
0150 | Now generate the remediation plan:"""
0151 |     
0152 |     def _get_language_guide(self, language: Optional[str]) -> str:
0153 |         """Get language-specific remediation guidance"""
0154 |         if not language:
0155 |             return ""
0156 |         
0157 |         lang = language.lower()
0158 |         
0159 |         guides = {
0160 |             'abap': """
0161 | ## ABAP-SPECIFIC PATTERNS
0162 | 
0163 | ### Directory Traversal Prevention:
0164 | 1. Use logical filenames (transaction FILE)
0165 | 2. Validate with FILE_VALIDATE_NAME and FILE_GET_NAME
0166 | 3. Character validation: `IF filename CA '/..\\\\':\\x00'. "Block"`
0167 | 4. Authorization: AUTHORITY-CHECK OBJECT 'S_DATASET'
0168 | 5. Logging: Use BAL_LOG_CREATE and BAL_LOG_MSG_ADD
0169 | 
0170 | ### SQL Injection Prevention:
0171 | 1. NEVER use dynamic WHERE with concatenation
0172 | 2. Use host variables: SELECT * WHERE username = @lv_username
0173 | 3. Use SELECT-OPTIONS for dynamic queries
0174 | 
0175 | ### Best Practices:
0176 | - Always check sy-subrc after function calls
0177 | - Use MESSAGE TYPE 'E' for security failures
0178 | - Log security events to application log (BAL)
0179 | - Run Code Vulnerability Analyzer (CVA)
0180 | """,
0181 |             
0182 |             'python': """
0183 | ## PYTHON-SPECIFIC PATTERNS
0184 | 
0185 | ### Path Traversal Prevention:
0186 | 1. Use pathlib.Path.resolve() with is_relative_to()
0187 | 2. Use secure_filename() from werkzeug
0188 | 3. Validate: `^[a-zA-Z0-9_-]+\\.[a-z]{2,4}$`
0189 | 
0190 | ### SQL Injection Prevention:
0191 | 1. Django ORM: Use .filter(), never .raw() with f-strings
0192 | 2. SQLAlchemy: Use bound parameters with text()
0193 | 3. Always use parameterized queries
0194 | 
0195 | ### Best Practices:
0196 | - Use framework auto-escaping for XSS
0197 | - Validate inputs with Pydantic
0198 | - Use environment variables for secrets
0199 | """,
0200 |             
0201 |             'java': """
0202 | ## JAVA-SPECIFIC PATTERNS
0203 | 
0204 | ### SQL Injection Prevention:
0205 | 1. Always use PreparedStatement (never Statement)
0206 | 2. JPA: Use named parameters (:name syntax)
0207 | 3. Hibernate: Avoid native queries with concatenation
0208 | 
0209 | ### Path Traversal Prevention:
0210 | 1. Use Path.resolve() with startsWith() check
0211 | 2. Normalize paths before validation
0212 | 3. Check canonical path stays within base directory
0213 | 
0214 | ### Best Practices:
0215 | - Disable XXE with DocumentBuilderFactory
0216 | - Use @PreAuthorize for method-level security
0217 | - Enable CSRF protection in Spring Security
0218 | """
0219 |         }
0220 |         
0221 |         return guides.get(lang, "")
```

---

### infrastructure\llm\response_parser.py

**Ruta:** `infrastructure\llm\response_parser.py`

```py
0001 | # infrastructure/llm/response_parser.py
0002 | """
0003 | LLM Response Parser - Simplified
0004 | ================================
0005 | 
0006 | Responsibilities:
0007 | - Clean JSON responses
0008 | - Extract valid JSON from noisy text
0009 | - Parse to domain models
0010 | - Validate structure
0011 | """
0012 | 
0013 | import json
0014 | import re
0015 | import logging
0016 | from typing import Optional, List, Any, Dict
0017 | 
0018 | from core.models import TriageResult, RemediationPlan, VulnerabilityType
0019 | from core.exceptions import LLMError
0020 | 
0021 | logger = logging.getLogger(__name__)
0022 | 
0023 | 
0024 | class LLMResponseParser:
0025 |     """Simplified response parser with strategy pattern"""
0026 |     
0027 |     def __init__(self, debug_enabled: bool = False):
0028 |         self.debug_enabled = debug_enabled
0029 |     
0030 |     # ════════════════════════════════════════════════════════════════
0031 |     # PUBLIC API
0032 |     # ════════════════════════════════════════════════════════════════
0033 |     
0034 |     def parse_triage_response(
0035 |         self,
0036 |         llm_response: str,
0037 |         original_data: str = None
0038 |     ) -> TriageResult:
0039 |         """Parse triage response to TriageResult"""
0040 |         logger.info(f"Parsing triage response ({len(llm_response):,} chars)")
0041 |         
0042 |         # Clean and extract JSON
0043 |         cleaned = self._clean_and_extract(llm_response, required_fields=['decisions'])
0044 |         
0045 |         # Parse JSON
0046 |         try:
0047 |             data = json.loads(cleaned)
0048 |         except json.JSONDecodeError as e:
0049 |             raise LLMError(f"Invalid JSON in triage response: {e}")
0050 |         
0051 |         # Validate fields
0052 |         self._validate_fields(data, ['decisions'], 'triage')
0053 |         
0054 |         # Create model (Pydantic validates)
0055 |         try:
0056 |             result = TriageResult(**data)
0057 |             logger.info(f"✅ Triage parsed: {result.total_analyzed} decisions")
0058 |             return result
0059 |         except Exception as e:
0060 |             raise LLMError(f"Invalid triage data: {e}")
0061 |     
0062 |     def parse_remediation_response(
0063 |         self,
0064 |         llm_response: str,
0065 |         vuln_type: str = None,
0066 |         language: str = None
0067 |     ) -> RemediationPlan:
0068 |         """Parse remediation response to RemediationPlan"""
0069 |         logger.info(f"Parsing remediation response ({len(llm_response):,} chars)")
0070 |         
0071 |         # Clean and extract JSON
0072 |         cleaned = self._clean_and_extract(
0073 |             llm_response,
0074 |             required_fields=['vulnerability_type', 'priority_level', 'steps']
0075 |         )
0076 |         
0077 |         # Parse JSON
0078 |         try:
0079 |             data = json.loads(cleaned)
0080 |         except json.JSONDecodeError as e:
0081 |             raise LLMError(f"Invalid JSON in remediation response: {e}")
0082 |         
0083 |         # Validate fields
0084 |         self._validate_fields(
0085 |             data,
0086 |             ['vulnerability_type', 'priority_level', 'steps'],
0087 |             'remediation'
0088 |         )
0089 |         
0090 |         # Normalize data
0091 |         data = self._normalize_remediation(data, vuln_type)
0092 |         
0093 |         # Create model
0094 |         try:
0095 |             result = RemediationPlan(**data)
0096 |             logger.info(f"✅ Remediation parsed: {len(result.steps)} steps")
0097 |             return result
0098 |         except Exception as e:
0099 |             raise LLMError(f"Invalid remediation data: {e}")
0100 |     
0101 |     # ════════════════════════════════════════════════════════════════
0102 |     # CLEANING & EXTRACTION
0103 |     # ════════════════════════════════════════════════════════════════
0104 |     
0105 |     def _clean_and_extract(
0106 |         self,
0107 |         response: str,
0108 |         required_fields: List[str] = None
0109 |     ) -> str:
0110 |         """
0111 |         Clean and extract valid JSON
0112 |         
0113 |         Strategy:
0114 |         1. Try cleaning markdown wrappers
0115 |         2. If valid, return
0116 |         3. If not, try aggressive extraction
0117 |         """
0118 |         # Clean markdown wrappers
0119 |         cleaned = self._remove_markdown(response)
0120 |         
0121 |         # Validate structure
0122 |         if self._is_valid_json_structure(cleaned):
0123 |             return cleaned
0124 |         
0125 |         # Try extraction strategies
0126 |         logger.warning("JSON structure invalid, trying extraction")
0127 |         extracted = self._extract_json(cleaned, required_fields)
0128 |         
0129 |         if not extracted:
0130 |             raise LLMError("Could not extract valid JSON from response")
0131 |         
0132 |         return extracted
0133 |     
0134 |     def _remove_markdown(self, text: str) -> str:
0135 |         """Remove markdown code blocks and prefixes"""
0136 |         text = text.strip()
0137 |         
0138 |         # Remove ```json ... ``` wrapper
0139 |         pattern = r'^```(?:json)?\s*\n(.+?)\n```$'
0140 |         match = re.match(pattern, text, re.DOTALL)
0141 |         if match:
0142 |             text = match.group(1).strip()
0143 |         
0144 |         # Remove standalone ``` markers
0145 |         text = re.sub(r'^```(?:json)?\s*\n', '', text)
0146 |         text = re.sub(r'\n```\s*$', '', text)
0147 |         
0148 |         # Remove anomalous prefixes
0149 |         prefixes = ['L3##json\n', 'L3##', 'json\n']
0150 |         for prefix in prefixes:
0151 |             if text.startswith(prefix):
0152 |                 text = text[len(prefix):].lstrip()
0153 |         
0154 |         return text.strip()
0155 |     
0156 |     def _is_valid_json_structure(self, text: str) -> bool:
0157 |         """Quick validation of JSON structure"""
0158 |         if not text:
0159 |             return False
0160 |         
0161 |         # Check delimiters
0162 |         open_braces = text.count('{')
0163 |         close_braces = text.count('}')
0164 |         open_brackets = text.count('[')
0165 |         close_brackets = text.count(']')
0166 |         
0167 |         if open_braces != close_braces or open_brackets != close_brackets:
0168 |             return False
0169 |         
0170 |         # Check starts and ends correctly
0171 |         if not text.startswith(('{', '[')):
0172 |             return False
0173 |         
0174 |         if not text.endswith(('}', ']')):
0175 |             return False
0176 |         
0177 |         return True
0178 |     
0179 |     def _extract_json(
0180 |         self,
0181 |         text: str,
0182 |         required_fields: List[str] = None
0183 |     ) -> Optional[str]:
0184 |         """
0185 |         Extract JSON using multiple strategies
0186 |         
0187 |         Strategies (in order):
0188 |         1. Balance delimiters
0189 |         2. Stack-based extraction
0190 |         3. Simple first/last
0191 |         """
0192 |         strategies = [
0193 |             self._extract_balanced,
0194 |             self._extract_with_stack,
0195 |             self._extract_simple
0196 |         ]
0197 |         
0198 |         for strategy in strategies:
0199 |             try:
0200 |                 result = strategy(text, required_fields)
0201 |                 if result:
0202 |                     return result
0203 |             except Exception as e:
0204 |                 logger.debug(f"Strategy {strategy.__name__} failed: {e}")
0205 |         
0206 |         return None
0207 |     
0208 |     def _extract_balanced(
0209 |         self,
0210 |         text: str,
0211 |         required_fields: List[str]
0212 |     ) -> Optional[str]:
0213 |         """Auto-balance unbalanced JSON"""
0214 |         open_braces = text.count('{')
0215 |         close_braces = text.count('}')
0216 |         open_brackets = text.count('[')
0217 |         close_brackets = text.count(']')
0218 |         
0219 |         # Already balanced
0220 |         if open_braces == close_braces and open_brackets == close_brackets:
0221 |             return None
0222 |         
0223 |         balanced = text.strip()
0224 |         
0225 |         # Add missing closing brackets
0226 |         if open_brackets > close_brackets:
0227 |             missing = open_brackets - close_brackets
0228 |             balanced += ']' * missing
0229 |         
0230 |         # Add missing closing braces
0231 |         if open_braces > close_braces:
0232 |             missing = open_braces - close_braces
0233 |             balanced += '}' * missing
0234 |         
0235 |         # Validate
0236 |         try:
0237 |             parsed = json.loads(balanced)
0238 |             if self._has_fields(parsed, required_fields):
0239 |                 return balanced
0240 |         except json.JSONDecodeError:
0241 |             pass
0242 |         
0243 |         return None
0244 |     
0245 |     def _extract_with_stack(
0246 |         self,
0247 |         text: str,
0248 |         required_fields: List[str]
0249 |     ) -> Optional[str]:
0250 |         """Extract using stack-based bracket matching"""
0251 |         candidates = []
0252 |         
0253 |         i = 0
0254 |         while i < len(text):
0255 |             if text[i] == '{':
0256 |                 stack = ['{']
0257 |                 start = i
0258 |                 j = i + 1
0259 |                 
0260 |                 while j < len(text) and stack:
0261 |                     if text[j] == '{':
0262 |                         stack.append('{')
0263 |                     elif text[j] == '}':
0264 |                         stack.pop()
0265 |                         if not stack:  # Complete object found
0266 |                             candidate = text[start:j+1]
0267 |                             try:
0268 |                                 parsed = json.loads(candidate)
0269 |                                 if self._has_fields(parsed, required_fields):
0270 |                                     candidates.append((len(candidate), candidate))
0271 |                             except json.JSONDecodeError:
0272 |                                 pass
0273 |                             break
0274 |                     j += 1
0275 |             i += 1
0276 |         
0277 |         # Return longest valid candidate
0278 |         if candidates:
0279 |             candidates.sort(reverse=True)
0280 |             return candidates[0][1]
0281 |         
0282 |         return None
0283 |     
0284 |     def _extract_simple(
0285 |         self,
0286 |         text: str,
0287 |         required_fields: List[str]
0288 |     ) -> Optional[str]:
0289 |         """Simple first/last delimiter extraction"""
0290 |         first = text.find('{')
0291 |         last = text.rfind('}')
0292 |         
0293 |         if first >= 0 and last > first:
0294 |             candidate = text[first:last+1]
0295 |             try:
0296 |                 parsed = json.loads(candidate)
0297 |                 if self._has_fields(parsed, required_fields):
0298 |                     return candidate
0299 |             except json.JSONDecodeError:
0300 |                 pass
0301 |         
0302 |         return None
0303 |     
0304 |     # ════════════════════════════════════════════════════════════════
0305 |     # VALIDATION & NORMALIZATION
0306 |     # ════════════════════════════════════════════════════════════════
0307 |     
0308 |     def _validate_fields(
0309 |         self,
0310 |          Dict,
0311 |         required: List[str],
0312 |         response_type: str
0313 |     ) -> None:
0314 |         """Validate required fields are present"""
0315 |         if not isinstance(data, dict):
0316 |             raise LLMError(f"{response_type} response is not a dict")
0317 |         
0318 |         missing = [f for f in required if f not in data]
0319 |         
0320 |         if missing:
0321 |             available = list(data.keys())
0322 |             raise LLMError(
0323 |                 f"{response_type} missing fields: {missing}. "
0324 |                 f"Available: {available}"
0325 |             )
0326 |     
0327 |     def _has_fields(self,  Any, required: List[str]) -> bool:
0328 |         """Check if data has required fields"""
0329 |         if not required:
0330 |             return True
0331 |         
0332 |         if not isinstance(data, dict):
0333 |             return False
0334 |         
0335 |         return all(field in data for field in required)
0336 |     
0337 |     def _normalize_remediation(
0338 |         self,
0339 |         data: Dict,
0340 |         vuln_type: str
0341 |     ) -> Dict:
0342 |         """Normalize remediation data"""
0343 |         # Add missing vulnerability_id
0344 |         if 'vulnerability_id' not in data: 
0345 |             data['vulnerability_id'] = f"{vuln_type or 'unknown'}-{int(time.time())}"
0346 |         
0347 |         # Add missing llm_model_used
0348 |         if 'llm_model_used' not in data:
0349 |             data['llm_model_used'] = 'meta-llama/llama-3-3-70b-instruct'
0350 |         
0351 |         # Validate steps
0352 |         if not data.get('steps') or len(data['steps']) < 1:
0353 |             raise LLMError("No remediation steps in response")
0354 |         
0355 |         return data
```

---

### infrastructure\llm\__init__.py

**Ruta:** `infrastructure\llm\__init__.py`

```py
```

---

### shared\constants.py

**Ruta:** `shared\constants.py`

```py
0001 | # shared/constants.py
0002 | """
0003 | Global Constants - Single Source of Truth
0004 | =========================================
0005 | 
0006 | All constants used across the application.
0007 | """
0008 | 
0009 | from core.models import SeverityLevel, VulnerabilityType
0010 | 
0011 | # ════════════════════════════════════════════════════════════════════
0012 | # SEVERITY MAPPINGS
0013 | # ════════════════════════════════════════════════════════════════════
0014 | 
0015 | SEVERITY_MAPPINGS = {
0016 |     'CRITICAL': SeverityLevel.CRITICAL,
0017 |     'CRÍTICA': SeverityLevel.CRITICAL,
0018 |     'BLOCKER': SeverityLevel.CRITICAL,
0019 |     'HIGH': SeverityLevel.HIGH,
0020 |     'ALTA': SeverityLevel.HIGH,
0021 |     'MAJOR': SeverityLevel.HIGH,
0022 |     'MEDIUM': SeverityLevel.MEDIUM,
0023 |     'MEDIA': SeverityLevel.MEDIUM,
0024 |     'LOW': SeverityLevel.LOW,
0025 |     'BAJA': SeverityLevel.LOW,
0026 |     'MINOR': SeverityLevel.MEDIUM,
0027 |     'INFO': SeverityLevel.INFO,
0028 | }
0029 | 
0030 | SEVERITY_WEIGHTS = {
0031 |     'CRÍTICA': 10.0,
0032 |     'ALTA': 7.0,
0033 |     'MEDIA': 4.0,
0034 |     'BAJA': 2.0,
0035 |     'INFO': 0.5
0036 | }
0037 | 
0038 | SEVERITY_ICONS = {
0039 |     'CRÍTICA': '🔥',
0040 |     'ALTA': '⚡',
0041 |     'MEDIA': '⚠️',
0042 |     'BAJA': '📝',
0043 |     'INFO': 'ℹ️'
0044 | }
0045 | 
0046 | # ════════════════════════════════════════════════════════════════════
0047 | # VULNERABILITY TYPE PATTERNS
0048 | # ════════════════════════════════════════════════════════════════════
0049 | 
0050 | VULNERABILITY_TYPE_PATTERNS = {
0051 |     'sql injection': VulnerabilityType.SQL_INJECTION,
0052 |     'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
0053 |     'path traversal': VulnerabilityType.PATH_TRAVERSAL,
0054 |     'code injection': VulnerabilityType.CODE_INJECTION,
0055 |     'cross-site scripting': VulnerabilityType.XSS,
0056 |     'xss': VulnerabilityType.XSS,
0057 |     'authentication': VulnerabilityType.AUTH_BYPASS,
0058 |     'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
0059 |     'crypto': VulnerabilityType.INSECURE_CRYPTO,
0060 | }
0061 | 
0062 | # ════════════════════════════════════════════════════════════════════
0063 | # FILE VALIDATION
0064 | # ════════════════════════════════════════════════════════════════════
0065 | 
0066 | ALLOWED_FILE_EXTENSIONS = ['.json']
0067 | MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
0068 | MAX_VULNERABILITIES = 10000
0069 | 
0070 | # ════════════════════════════════════════════════════════════════════
0071 | # LLM DEFAULTS
0072 | # ════════════════════════════════════════════════════════════════════
0073 | 
0074 | DEFAULT_TEMPERATURE = 0.1
0075 | DEFAULT_MAX_TOKENS = 2048
0076 | DEFAULT_TIMEOUT = 180
0077 | 
0078 | # ════════════════════════════════════════════════════════════════════
0079 | # CHUNKING DEFAULTS
0080 | # ════════════════════════════════════════════════════════════════════
0081 | 
0082 | DEFAULT_CHUNK_SIZE = 5
0083 | DEFAULT_CHUNK_OVERLAP = 1
0084 | DEFAULT_MIN_CHUNK_SIZE = 3
0085 | DEFAULT_MAX_CHUNK_BYTES = 8000
0086 | 
0087 | # ════════════════════════════════════════════════════════════════════
0088 | # CACHE DEFAULTS
0089 | # ════════════════════════════════════════════════════════════════════
0090 | 
0091 | DEFAULT_CACHE_TTL_HOURS = 24
0092 | DEFAULT_CACHE_DIR = ".security_cache"
0093 | 
0094 | # ════════════════════════════════════════════════════════════════════
0095 | # DEDUPLICATION
0096 | # ════════════════════════════════════════════════════════════════════
0097 | 
0098 | DEDUP_STRATEGIES = ['strict', 'moderate', 'loose']
0099 | DEFAULT_DEDUP_STRATEGY = 'moderate'
0100 | 
0101 | # Similarity thresholds
0102 | DEDUP_THRESHOLD_STRICT = 1.0   # Exact match
0103 | DEDUP_THRESHOLD_MODERATE = 0.8  # 80% similar
0104 | DEDUP_THRESHOLD_LOOSE = 0.7     # 70% similar
0105 | 
0106 | # Line proximity for moderate strategy
0107 | DEDUP_LINE_PROXIMITY = 5  # ±5 lines
```

---

### shared\formatters.py

**Ruta:** `shared\formatters.py`

```py
0001 | # shared/formatters.py
0002 | """
0003 | Reusable Formatters
0004 | ==================
0005 | 
0006 | Common formatting functions for display and logging.
0007 | """
0008 | 
0009 | from datetime import datetime, timedelta
0010 | from typing import Any, Optional
0011 | 
0012 | 
0013 | def format_bytes(size_bytes: int) -> str:
0014 |     """
0015 |     Format bytes to human-readable format
0016 |     
0017 |     Args:
0018 |         size_bytes: Size in bytes
0019 |     
0020 |     Returns:
0021 |         Formatted string (e.g., "1.5 MB")
0022 |     """
0023 |     if size_bytes < 1024:
0024 |         return f"{size_bytes} B"
0025 |     elif size_bytes < 1024 * 1024:
0026 |         return f"{size_bytes / 1024:.2f} KB"
0027 |     elif size_bytes < 1024 * 1024 * 1024:
0028 |         return f"{size_bytes / (1024 * 1024):.2f} MB"
0029 |     else:
0030 |         return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
0031 | 
0032 | 
0033 | def format_duration(seconds: float) -> str:
0034 |     """
0035 |     Format duration to human-readable format
0036 |     
0037 |     Args:
0038 |         seconds: Duration in seconds
0039 |     
0040 |     Returns:
0041 |         Formatted string (e.g., "1m 30s")
0042 |     """
0043 |     if seconds < 60:
0044 |         return f"{seconds:.2f}s"
0045 |     elif seconds < 3600:
0046 |         minutes = int(seconds // 60)
0047 |         remaining = seconds % 60
0048 |         return f"{minutes}m {remaining:.1f}s"
0049 |     else:
0050 |         hours = int(seconds // 3600)
0051 |         remaining_seconds = seconds % 3600
0052 |         minutes = int(remaining_seconds // 60)
0053 |         return f"{hours}h {minutes}m"
0054 | 
0055 | 
0056 | def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
0057 |     """
0058 |     Format datetime to string
0059 |     
0060 |     Args:
0061 |         dt: Datetime object (default: now)
0062 |         fmt: Format string
0063 |     
0064 |     Returns:
0065 |         Formatted datetime string
0066 |     """
0067 |     if dt is None:
0068 |         dt = datetime.now()
0069 |     
0070 |     return dt.strftime(fmt)
0071 | 
0072 | 
0073 | def format_percentage(value: float, decimals: int = 1) -> str:
0074 |     """
0075 |     Format float as percentage
0076 |     
0077 |     Args:
0078 |         value: Value (0.0-1.0)
0079 |         decimals: Decimal places
0080 |     
0081 |     Returns:
0082 |         Formatted percentage (e.g., "75.5%")
0083 |     """
0084 |     return f"{value * 100:.{decimals}f}%"
0085 | 
0086 | 
0087 | def format_number(value: int, separator: str = ",") -> str:
0088 |     """
0089 |     Format number with thousands separator
0090 |     
0091 |     Args:
0092 |         value: Number to format
0093 |         separator: Thousands separator
0094 |     
0095 |     Returns:
0096 |         Formatted number (e.g., "1,234,567")
0097 |     """
0098 |     return f"{value:,}".replace(",", separator)
0099 | 
0100 | 
0101 | def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
0102 |     """
0103 |     Truncate text to maximum length
0104 |     
0105 |     Args:
0106 |         text: Text to truncate
0107 |         max_length: Maximum length
0108 |         suffix: Suffix to add when truncated
0109 |     
0110 |     Returns:
0111 |         Truncated text
0112 |     """
0113 |     if not text or len(text) <= max_length:
0114 |         return text
0115 |     
0116 |     return text[:max_length - len(suffix)] + suffix
0117 | 
0118 | 
0119 | def format_severity_icon(severity: str) -> str:
0120 |     """
0121 |     Get emoji icon for severity
0122 |     
0123 |     Args:
0124 |         severity: Severity level
0125 |     
0126 |     Returns:
0127 |         Emoji icon
0128 |     """
0129 |     from shared.constants import SEVERITY_ICONS
0130 |     return SEVERITY_ICONS.get(severity.upper(), "•")
0131 | 
0132 | 
0133 | def format_list(items: list, separator: str = ", ", last_separator: str = " and ") -> str:
0134 |     """
0135 |     Format list to human-readable string
0136 |     
0137 |     Args:
0138 |         items: List of items
0139 |         separator: Separator between items
0140 |         last_separator: Separator before last item
0141 |     
0142 |     Returns:
0143 |         Formatted string (e.g., "a, b and c")
0144 |     """
0145 |     if not items:
0146 |         return ""
0147 |     
0148 |     if len(items) == 1:
0149 |         return str(items[0])
0150 |     
0151 |     if len(items) == 2:
0152 |         return f"{items[0]}{last_separator}{items[1]}"
0153 |     
0154 |     return separator.join(str(i) for i in items[:-1]) + f"{last_separator}{items[-1]}"
```

---

### shared\logger.py

**Ruta:** `shared\logger.py`

```py
0001 | # shared/logger.py
0002 | """
0003 | Logger Setup - Simplified
0004 | =========================
0005 | 
0006 | Responsibilities:
0007 | - Configure logging system
0008 | - Provide formatters (JSON, Colored)
0009 | - Setup file rotation
0010 | """
0011 | 
0012 | import logging
0013 | import logging.handlers
0014 | import sys
0015 | from pathlib import Path
0016 | from datetime import datetime
0017 | from typing import Optional
0018 | import json
0019 | 
0020 | 
0021 | # ════════════════════════════════════════════════════════════════════
0022 | # FORMATTERS
0023 | # ════════════════════════════════════════════════════════════════════
0024 | 
0025 | class JSONFormatter(logging.Formatter):
0026 |     """JSON formatter for structured logging"""
0027 |     
0028 |     def format(self, record: logging.LogRecord) -> str:
0029 |         """Format record as JSON"""
0030 |         log_data = {
0031 |             "timestamp": datetime.fromtimestamp(record.created).isoformat(),
0032 |             "level": record.levelname,
0033 |             "logger": record.name,
0034 |             "message": record.getMessage(),
0035 |             "module": record.module,
0036 |             "function": record.funcName,
0037 |             "line": record.lineno
0038 |         }
0039 |         
0040 |         if record.exc_info:
0041 |             log_data["exception"] = self.formatException(record.exc_info)
0042 |         
0043 |         return json.dumps(log_data, ensure_ascii=False)
0044 | 
0045 | 
0046 | class ColoredFormatter(logging.Formatter):
0047 |     """Colored formatter for console output"""
0048 |     
0049 |     COLORS = {
0050 |         'DEBUG': '\033[36m',     # Cyan
0051 |         'INFO': '\033[32m',      # Green
0052 |         'WARNING': '\033[33m',   # Yellow
0053 |         'ERROR': '\033[31m',     # Red
0054 |         'CRITICAL': '\033[35m',  # Magenta
0055 |         'RESET': '\033[0m'       # Reset
0056 |     }
0057 |     
0058 |     def format(self, record: logging.LogRecord) -> str:
0059 |         """Format record with colors"""
0060 |         color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
0061 |         reset = self.COLORS['RESET']
0062 |         
0063 |         timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
0064 |         
0065 |         return (
0066 |             f"{color}[{timestamp}] {record.levelname:<8}{reset} - "
0067 |             f"{record.module}.{record.funcName}:{record.lineno} - "
0068 |             f"{record.getMessage()}"
0069 |         )
0070 | 
0071 | 
0072 | # ════════════════════════════════════════════════════════════════════
0073 | # SETUP FUNCTION
0074 | # ════════════════════════════════════════════════════════════════════
0075 | 
0076 | def setup_logging(
0077 |     log_level: str = "INFO",
0078 |     log_file: Optional[str] = None,
0079 |     structured: bool = False
0080 | ) -> None:
0081 |     """
0082 |     Setup logging system
0083 |     
0084 |     Args:
0085 |         log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
0086 |         log_file: Optional file path for file logging
0087 |         structured: Use JSON formatter (for structured logging)
0088 |     """
0089 |     level = getattr(logging, log_level.upper(), logging.INFO)
0090 |     
0091 |     # Clear existing handlers
0092 |     root_logger = logging.getLogger()
0093 |     root_logger.handlers.clear()
0094 |     root_logger.setLevel(level)
0095 |     
0096 |     # Console handler
0097 |     console_handler = logging.StreamHandler(sys.stdout)
0098 |     console_handler.setLevel(level)
0099 |     
0100 |     if structured:
0101 |         console_formatter = JSONFormatter()
0102 |     else:
0103 |         console_formatter = ColoredFormatter()
0104 |     
0105 |     console_handler.setFormatter(console_formatter)
0106 |     root_logger.addHandler(console_handler)
0107 |     
0108 |     # File handler (optional)
0109 |     if log_file:
0110 |         log_path = Path(log_file)
0111 |         log_path.parent.mkdir(parents=True, exist_ok=True)
0112 |         
0113 |         file_handler = logging.handlers.RotatingFileHandler(
0114 |             log_file,
0115 |             maxBytes=10 * 1024 * 1024,  # 10 MB
0116 |             backupCount=5,
0117 |             encoding='utf-8'
0118 |         )
0119 |         file_handler.setLevel(logging.DEBUG)
0120 |         file_handler.setFormatter(JSONFormatter())
0121 |         root_logger.addHandler(file_handler)
0122 |     
0123 |     # Suppress noisy loggers
0124 |     for noisy_logger in ['urllib3', 'requests', 'openai', 'httpx']:
0125 |         logging.getLogger(noisy_logger).setLevel(logging.WARNING)
0126 |     
0127 |     # Log initialization
0128 |     logger = logging.getLogger(__name__)
0129 |     logger.info(f"📝 Logging configured: {log_level}")
0130 |     if log_file:
0131 |         logger.info(f"   File logging: {log_file}")
```

---

### shared\metrics.py

**Ruta:** `shared\metrics.py`

```py
0001 | # shared/metrics.py
0002 | """
0003 | Metrics Collector - Simplified
0004 | ==============================
0005 | 
0006 | Responsibilities:
0007 | - Collect performance metrics
0008 | - Calculate statistics
0009 | - Export metrics data
0010 | """
0011 | 
0012 | import time
0013 | import logging
0014 | import json
0015 | from typing import Dict, Any, Optional, List
0016 | from dataclasses import dataclass, field, asdict
0017 | from datetime import datetime
0018 | from collections import defaultdict
0019 | 
0020 | logger = logging.getLogger(__name__)
0021 | 
0022 | 
0023 | # ════════════════════════════════════════════════════════════════════
0024 | # DATA CLASSES
0025 | # ════════════════════════════════════════════════════════════════════
0026 | 
0027 | @dataclass
0028 | class Metric:
0029 |     """Single metric entry"""
0030 |     operation: str
0031 |     start_time: float
0032 |     end_time: Optional[float] = None
0033 |     success: bool = True
0034 |     error: Optional[str] = None
0035 |     metadata: Dict[str, Any] = field(default_factory=dict)
0036 |     
0037 |     @property
0038 |     def duration(self) -> float:
0039 |         """Calculate duration"""
0040 |         if self.end_time:
0041 |             return self.end_time - self.start_time
0042 |         return 0.0
0043 | 
0044 | 
0045 | # ════════════════════════════════════════════════════════════════════
0046 | # METRICS COLLECTOR
0047 | # ════════════════════════════════════════════════════════════════════
0048 | 
0049 | class MetricsCollector:
0050 |     """Simplified metrics collector"""
0051 |     
0052 |     def __init__(self):
0053 |         self.metrics: List[Metric] = []
0054 |         self.counters: Dict[str, int] = defaultdict(int)
0055 |         self.session_start = time.time()
0056 |     
0057 |     # ════════════════════════════════════════════════════════════════
0058 |     # RECORDING METHODS
0059 |     # ════════════════════════════════════════════════════════════════
0060 |     
0061 |     def record_complete_analysis(
0062 |         self,
0063 |         file_path: str,
0064 |         vulnerability_count: int = 0,
0065 |         confirmed_count: int = 0,
0066 |         total_time: float = 0.0,
0067 |         chunking_used: bool = False,
0068 |         language: Optional[str] = None,
0069 |         success: bool = True,
0070 |         error: Optional[str] = None
0071 |     ):
0072 |         """Record complete analysis"""
0073 |         metric = Metric(
0074 |             operation="complete_analysis",
0075 |             start_time=time.time() - total_time,
0076 |             end_time=time.time(),
0077 |             success=success,
0078 |             error=error,
0079 |             metadata={
0080 |                 "file_path": file_path,
0081 |                 "vulnerability_count": vulnerability_count,
0082 |                 "confirmed_count": confirmed_count,
0083 |                 "chunking_used": chunking_used,
0084 |                 "language": language
0085 |             }
0086 |         )
0087 |         
0088 |         self.metrics.append(metric)
0089 |         self.counters["analyses_total"] += 1
0090 |         if success:
0091 |             self.counters["analyses_successful"] += 1
0092 |     
0093 |     def record_triage_analysis(
0094 |         self,
0095 |         vulnerability_count: int,
0096 |         analysis_time: float,
0097 |         success: bool,
0098 |         chunk_id: Optional[int] = None,
0099 |         error: Optional[str] = None
0100 |     ):
0101 |         """Record triage analysis"""
0102 |         metric = Metric(
0103 |             operation="triage_analysis",
0104 |             start_time=time.time() - analysis_time,
0105 |             end_time=time.time(),
0106 |             success=success,
0107 |             error=error,
0108 |             metadata={
0109 |                 "vulnerability_count": vulnerability_count,
0110 |                 "chunk_id": chunk_id,
0111 |                 "throughput": vulnerability_count / analysis_time if analysis_time > 0 else 0
0112 |             }
0113 |         )
0114 |         
0115 |         self.metrics.append(metric)
0116 |         self.counters["triage_calls"] += 1
0117 |     
0118 |     def record_remediation_generation(
0119 |         self,
0120 |         vulnerability_type: str,
0121 |         count: int,
0122 |         generation_time: float,
0123 |         success: bool,
0124 |         error: Optional[str] = None
0125 |     ):
0126 |         """Record remediation generation"""
0127 |         metric = Metric(
0128 |             operation="remediation_generation",
0129 |             start_time=time.time() - generation_time,
0130 |             end_time=time.time(),
0131 |             success=success,
0132 |             error=error,
0133 |             metadata={
0134 |                 "vulnerability_type": vulnerability_type,
0135 |                 "count": count
0136 |             }
0137 |         )
0138 |         
0139 |         self.metrics.append(metric)
0140 |         self.counters["remediation_calls"] += 1
0141 |     
0142 |     def record_report_generation(
0143 |         self,
0144 |         report_type: str,
0145 |         file_size: int = 0,
0146 |         vulnerability_count: int = 0,
0147 |         success: bool = True,
0148 |         error: Optional[str] = None
0149 |     ):
0150 |         """Record report generation"""
0151 |         metric = Metric(
0152 |             operation="report_generation",
0153 |             start_time=time.time(),
0154 |             end_time=time.time(),
0155 |             success=success,
0156 |             error=error,
0157 |             metadata={
0158 |                 "report_type": report_type,
0159 |                 "file_size": file_size,
0160 |                 "vulnerability_count": vulnerability_count
0161 |             }
0162 |         )
0163 |         
0164 |         self.metrics.append(metric)
0165 |         self.counters["reports_generated"] += 1
0166 |     
0167 |     # ════════════════════════════════════════════════════════════════
0168 |     # STATISTICS
0169 |     # ════════════════════════════════════════════════════════════════
0170 |     
0171 |     def get_summary(self) -> Dict[str, Any]:
0172 |         """Get metrics summary"""
0173 |         total_analyses = self.counters.get("analyses_total", 0)
0174 |         successful_analyses = self.counters.get("analyses_successful", 0)
0175 |         
0176 |         if total_analyses == 0:
0177 |             return {"message": "No metrics recorded"}
0178 |         
0179 |         # Calculate averages
0180 |         analysis_metrics = [
0181 |             m for m in self.metrics if m.operation == "complete_analysis"
0182 |         ]
0183 |         
0184 |         avg_time = 0.0
0185 |         if analysis_metrics:
0186 |             avg_time = sum(m.duration for m in analysis_metrics) / len(analysis_metrics)
0187 |         
0188 |         session_duration = time.time() - self.session_start
0189 |         
0190 |         return {
0191 |             "session_duration_seconds": session_duration,
0192 |             "total_analyses": total_analyses,
0193 |             "successful_analyses": successful_analyses,
0194 |             "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
0195 |             "average_analysis_time": avg_time,
0196 |             "triage_calls": self.counters.get("triage_calls", 0),
0197 |             "remediation_calls": self.counters.get("remediation_calls", 0),
0198 |             "reports_generated": self.counters.get("reports_generated", 0)
0199 |         }
0200 |     
0201 |     def export_metrics(self, output_file: Optional[str] = None) -> str:
0202 |         """Export all metrics to JSON"""
0203 |         export_data = {
0204 |             "export_timestamp": datetime.now().isoformat(),
0205 |             "session_start": datetime.fromtimestamp(self.session_start).isoformat(),
0206 |             "summary": self.get_summary(),
0207 |             "detailed_metrics": [
0208 |                 {
0209 |                     "operation": m.operation,
0210 |                     "duration_seconds": m.duration,
0211 |                     "success": m.success,
0212 |                     "error": m.error,
0213 |                     "metadata": m.metadata
0214 |                 }
0215 |                 for m in self.metrics
0216 |             ],
0217 |             "counters": dict(self.counters)
0218 |         }
0219 |         
0220 |         json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
0221 |         
0222 |         if output_file:
0223 |             with open(output_file, 'w', encoding='utf-8') as f:
0224 |                 f.write(json_data)
0225 |             logger.info(f"📊 Metrics exported to {output_file}")
0226 |         
0227 |         return json_data
```

---

### shared\validators.py

**Ruta:** `shared\validators.py`

```py
0001 | # shared/validators.py
0002 | """
0003 | Reusable Validators
0004 | ==================
0005 | 
0006 | Common validation functions used across the application.
0007 | """
0008 | 
0009 | import re
0010 | from pathlib import Path
0011 | from typing import Optional, List, Any
0012 | 
0013 | from core.exceptions import ValidationError
0014 | from shared.constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES
0015 | 
0016 | 
0017 | def validate_file_path(file_path: str) -> Path:
0018 |     """
0019 |     Validate file path
0020 |     
0021 |     Args:
0022 |         file_path: Path to validate
0023 |     
0024 |     Returns:
0025 |         Validated Path object
0026 |     
0027 |     Raises:
0028 |         ValidationError: If validation fails
0029 |     """
0030 |     path = Path(file_path)
0031 |     
0032 |     # Check exists
0033 |     if not path.exists():
0034 |         raise ValidationError(f"File not found: {file_path}")
0035 |     
0036 |     # Check is file
0037 |     if not path.is_file():
0038 |         raise ValidationError(f"Not a file: {file_path}")
0039 |     
0040 |     # Check extension
0041 |     if path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
0042 |         raise ValidationError(
0043 |             f"Unsupported file type: {path.suffix}. "
0044 |             f"Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
0045 |         )
0046 |     
0047 |     # Check size
0048 |     size = path.stat().st_size
0049 |     if size > MAX_FILE_SIZE_BYTES:
0050 |         size_mb = size / 1024 / 1024
0051 |         max_mb = MAX_FILE_SIZE_BYTES / 1024 / 1024
0052 |         raise ValidationError(f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)")
0053 |     
0054 |     return path
0055 | 
0056 | 
0057 | def validate_cwe_id(cwe: Optional[str]) -> Optional[str]:
0058 |     """
0059 |     Validate and normalize CWE ID
0060 |     
0061 |     Args:
0062 |         cwe: CWE ID string
0063 |     
0064 |     Returns:
0065 |         Normalized CWE ID or None
0066 |     """
0067 |     if not cwe:
0068 |         return None
0069 |     
0070 |     cwe_str = str(cwe).strip()
0071 |     
0072 |     # Already in correct format
0073 |     if re.match(r'^CWE-\d+$', cwe_str):
0074 |         return cwe_str
0075 |     
0076 |     # Just a number
0077 |     if cwe_str.isdigit():
0078 |         return f"CWE-{cwe_str}"
0079 |     
0080 |     return None
0081 | 
0082 | 
0083 | def validate_cvss_score(score: Any) -> Optional[float]:
0084 |     """
0085 |     Validate CVSS score
0086 |     
0087 |     Args:
0088 |         score: CVSS score (any type)
0089 |     
0090 |     Returns:
0091 |         Valid score (0.0-10.0) or None
0092 |     """
0093 |     if score is None:
0094 |         return None
0095 |     
0096 |     try:
0097 |         score_float = float(score)
0098 |         if 0.0 <= score_float <= 10.0:
0099 |             return score_float
0100 |     except (ValueError, TypeError):
0101 |         pass
0102 |     
0103 |     return None
0104 | 
0105 | 
0106 | def validate_confidence(confidence: Any) -> Optional[float]:
0107 |     """
0108 |     Validate confidence level
0109 |     
0110 |     Args:
0111 |         confidence: Confidence value (any type)
0112 |     
0113 |     Returns:
0114 |         Valid confidence (0.0-1.0) or None
0115 |     """
0116 |     if confidence is None:
0117 |         return None
0118 |     
0119 |     try:
0120 |         # Handle percentage strings
0121 |         if isinstance(confidence, str) and '%' in confidence:
0122 |             value = float(confidence.replace('%', ''))
0123 |             return value / 100.0
0124 |         
0125 |         # Handle numeric values
0126 |         conf_float = float(confidence)
0127 |         
0128 |         # If already 0-1, return as is
0129 |         if 0.0 <= conf_float <= 1.0:
0130 |             return conf_float
0131 |         
0132 |         # If 0-100, convert to 0-1
0133 |         if 0.0 <= conf_float <= 100.0:
0134 |             return conf_float / 100.0
0135 |         
0136 |     except (ValueError, TypeError):
0137 |         pass
0138 |     
0139 |     return None
0140 | 
0141 | 
0142 | def validate_temperature(temperature: float) -> float:
0143 |     """
0144 |     Validate LLM temperature
0145 |     
0146 |     Args:
0147 |         temperature: Temperature value
0148 |     
0149 |     Returns:
0150 |         Valid temperature
0151 |     
0152 |     Raises:
0153 |         ValidationError: If invalid
0154 |     """
0155 |     if not isinstance(temperature, (int, float)):
0156 |         raise ValidationError(f"Temperature must be numeric, got {type(temperature)}")
0157 |     
0158 |     if not (0.0 <= temperature <= 2.0):
0159 |         raise ValidationError(f"Temperature must be 0.0-2.0, got {temperature}")
0160 |     
0161 |     return float(temperature)
0162 | 
0163 | 
0164 | def validate_provider(provider: str) -> str:
0165 |     """
0166 |     Validate LLM provider
0167 |     
0168 |     Args:
0169 |         provider: Provider name
0170 |     
0171 |     Returns:
0172 |         Normalized provider name
0173 |     
0174 |     Raises:
0175 |         ValidationError: If invalid
0176 |     """
0177 |     if not provider:
0178 |         raise ValidationError("Provider cannot be empty")
0179 |     
0180 |     provider_lower = provider.lower()
0181 |     
0182 |     valid_providers = ['openai', 'watsonx']
0183 |     if provider_lower not in valid_providers:
0184 |         raise ValidationError(
0185 |             f"Invalid provider: {provider}. "
0186 |             f"Valid: {', '.join(valid_providers)}"
0187 |         )
0188 |     
0189 |     return provider_lower
0190 | 
0191 | 
0192 | def validate_json_fields(
0193 |     data: dict,
0194 |     required_fields: List[str],
0195 |     optional_fields: List[str] = None
0196 | ) -> None:
0197 |     """
0198 |     Validate JSON data has required fields
0199 |     
0200 |     Args:
0201 |          JSON data dict
0202 |         required_fields: List of required field names
0203 |         optional_fields: List of optional field names
0204 |     
0205 |     Raises:
0206 |         ValidationError: If validation fails
0207 |     """
0208 |     if not isinstance(data, dict):
0209 |         raise ValidationError(f"Data must be dict, got {type(data)}")
0210 |     
0211 |     missing = [f for f in required_fields if f not in data]
0212 |     
0213 |     if missing:
0214 |         available = list(data.keys())
0215 |         raise ValidationError(
0216 |             f"Missing required fields: {missing}. "
0217 |             f"Available: {available}"
0218 |         )
```

---

### shared\__init__.py

**Ruta:** `shared\__init__.py`

```py
0001 | # shared/__init__.py
0002 | """
0003 | Shared utilities package
0004 | """
0005 | 
0006 | from .logger import setup_logging
0007 | from .metrics import MetricsCollector
0008 | 
0009 | __all__ = ['setup_logging', 'MetricsCollector']
```

---

## Resumen del Análisis

- **Total de archivos en el proyecto:** 277
- **Archivos procesados:** 36
- **Archivos excluidos:** 241
- **Total de líneas de código:** 8,068
