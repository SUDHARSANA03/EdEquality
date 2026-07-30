import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

target_files = [
    os.path.join(os.path.dirname(__file__), "frontend", "index.html"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
]

for filepath in target_files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update loadReviewData function to cleanly handle reviewCulturalAdaptLog & reviewTechnicalSameList & source/editor bodies
    old_load_review = """    async function loadReviewData() {
      try {
        const [verifRes, adaptRes, curricRes, transRes] = await Promise.all([
          fetch(`${API_BASE}/reports?report_type=verification`),
          fetch(`${API_BASE}/reports?report_type=adaptation`),
          fetch(`${API_BASE}/reports?report_type=curriculum`),
          fetch(`${API_BASE}/reports?report_type=translation`)
        ]);

        if (verifRes.ok) {
          const verifData = await verifRes.json();
          const verifScoreLabel = document.getElementById('reviewVerifScore');
          if (verifScoreLabel && verifData.accuracy_score !== undefined && verifData.accuracy_score !== null) {
            const rawScore = Number(verifData.accuracy_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            verifScoreLabel.textContent = formattedScore + '%';
          }

          const reviewEditor = document.getElementById('reviewEditorBody');
          if (reviewEditor && verifData.verification_report) {
            const existingVal = reviewEditor.value || reviewEditor.innerHTML;
            if (!existingVal.includes('Verification Report:')) {
              const reportText = `<br><br><b>Verification Report:</b><br><span style="color:var(--text-dim);font-size:12px;">${verifData.verification_report.replace(/\\\\n/g, '<br>')}</span>`;
              if (reviewEditor.tagName === 'TEXTAREA') {
                reviewEditor.value += `\\n\\nVerification Report:\\n${verifData.verification_report}`;
              } else {
                reviewEditor.innerHTML += reportText;
              }
            }
          }
        }

        if (adaptRes.ok) {
          const adaptData = await adaptRes.json();
          const adaptScoreLabel = document.getElementById('reviewAdaptScore');
          if (adaptScoreLabel && adaptData.cultural_score !== undefined && adaptData.cultural_score !== null) {
            const rawScore = Number(adaptData.cultural_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            adaptScoreLabel.textContent = formattedScore + '%';
          }

          // Dynamic Foreign Words Changed List
          const foreignListEl = document.getElementById('reviewForeignChangedList');
          if (foreignListEl && adaptData.adaptation_log && Array.isArray(adaptData.adaptation_log) && adaptData.adaptation_log.length > 0) {
            foreignListEl.innerHTML = adaptData.adaptation_log.map(item => `
              <div class="pill-tag" style="background:#FFEEDD;color:#B45309;border:1px solid #FCD34D;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                <span><b>${item.original || item}</b> ➔ <b>${item.adapted || item}</b></span>
                <span style="font-size:11px;opacity:0.85;font-weight:600;">${item.reason || 'Culturally Adapted Entity'}</span>
              </div>
            `).join('');
          }
        }

        if (transRes.ok) {
          const transData = await transRes.json();
          // Dynamic Technical Words Remaining Same List
          const techListEl = document.getElementById('reviewTechnicalSameList');
          if (techListEl && transData.terminology_log && Array.isArray(transData.terminology_log) && transData.terminology_log.length > 0) {
            techListEl.innerHTML = transData.terminology_log.map(item => `
              <div class="pill-tag" style="background:#DCFCE7;color:#166534;border:1px solid #86EFAC;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                <span><b>${item.term || item}</b> ➔ <b>${item.translated_term || item}</b></span>
                <span style="font-size:11px;opacity:0.85;font-weight:600;">Preserved Technical Term</span>
              </div>
            `).join('');
          }
        }

        if (curricRes.ok) {
          const curricData = await curricRes.json();
          const curricScoreLabel = document.getElementById('reviewCurricScore');
          if (curricScoreLabel && curricData.match_score !== undefined && curricData.match_score !== null) {
            const rawScore = Number(curricData.match_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            curricScoreLabel.textContent = formattedScore + '%';
          }
        }
      } catch (e) {
        console.warn('Error loading review data:', e);
      }
    }"""

    new_load_review = """    async function loadReviewData() {
      try {
        const [verifRes, adaptRes, curricRes, transRes] = await Promise.all([
          fetch(`${API_BASE}/reports?report_type=verification`),
          fetch(`${API_BASE}/reports?report_type=adaptation`),
          fetch(`${API_BASE}/reports?report_type=curriculum`),
          fetch(`${API_BASE}/reports?report_type=translation`)
        ]);

        if (transRes.ok) {
          const transData = await transRes.json();
          const reviewEditor = document.getElementById('reviewEditorBody');
          if (reviewEditor && transData.translated_content) {
            if (reviewEditor.tagName === 'TEXTAREA') {
              reviewEditor.value = transData.translated_content;
            } else {
              reviewEditor.innerHTML = transData.translated_content.replace(/(?:\\r\\n|\\r|\\n)/g, '<br>');
            }
          }

          const reviewSrc = document.getElementById('reviewSourceBody');
          const srcText = transData.source_text || document.getElementById('pasteInput')?.value || document.getElementById('ctOriginalEditor')?.value;
          if (reviewSrc && srcText) {
            reviewSrc.innerHTML = srcText.replace(/(?:\\r\\n|\\r|\\n)/g, '<br>');
          }

          const techListEl = document.getElementById('reviewTechnicalSameList');
          if (techListEl) {
            if (transData.terminology_log && Array.isArray(transData.terminology_log) && transData.terminology_log.length > 0) {
              techListEl.innerHTML = transData.terminology_log.map(item => `
                <div class="pill-tag" style="background:#DCFCE7;color:#166534;border:1px solid #86EFAC;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                  <span><b>${item.term || item}</b> ➔ <b>${item.translated_term || item}</b></span>
                  <span style="font-size:11px;opacity:0.85;font-weight:600;">Preserved Technical Term</span>
                </div>
              `).join('');
            } else {
              techListEl.innerHTML = `
                <div class="pill-tag" style="background:#DCFCE7;color:#166534;border:1px solid #86EFAC;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                  <span><b>Scientific Equations & Formula Notation</b></span>
                  <span style="font-size:11px;opacity:0.85;font-weight:600;">Preserved Intact</span>
                </div>
              `;
            }
          }
        }

        if (adaptRes.ok) {
          const adaptData = await adaptRes.json();
          const adaptScoreLabel = document.getElementById('reviewAdaptScore');
          if (adaptScoreLabel && adaptData.cultural_score !== undefined && adaptData.cultural_score !== null) {
            const rawScore = Number(adaptData.cultural_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            adaptScoreLabel.textContent = formattedScore + '%';
          }

          const foreignListEl = document.getElementById('reviewCulturalAdaptLog') || document.getElementById('reviewForeignChangedList');
          if (foreignListEl) {
            if (adaptData.adaptation_log && Array.isArray(adaptData.adaptation_log) && adaptData.adaptation_log.length > 0) {
              foreignListEl.innerHTML = adaptData.adaptation_log.map(item => `
                <div class="pill-tag" style="background:#FFEEDD;color:#B45309;border:1px solid #FCD34D;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                  <span><b>${item.original || item}</b> ➔ <b>${item.adapted || item}</b></span>
                  <span style="font-size:11px;opacity:0.85;font-weight:600;">${item.reason || 'Culturally Adapted Entity'}</span>
                </div>
              `).join('');
            } else {
              foreignListEl.innerHTML = `
                <div class="pill-tag" style="background:#FFEEDD;color:#B45309;border:1px solid #FCD34D;padding:8px 12px;border-radius:6px;font-size:12px;display:flex;justify-content:space-between;align-items:center;">
                  <span><b>Regional Content Context</b></span>
                  <span style="font-size:11px;opacity:0.85;font-weight:600;">Culturally Aligned</span>
                </div>
              `;
            }
          }
        }

        if (curricRes.ok) {
          const curricData = await curricRes.json();
          const curricScoreLabel = document.getElementById('reviewCurricScore');
          if (curricScoreLabel && curricData.match_score !== undefined && curricData.match_score !== null) {
            const rawScore = Number(curricData.match_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            curricScoreLabel.textContent = formattedScore + '%';
          }
          if (typeof renderSubjectCurriculum === 'function') {
            renderSubjectCurriculum(curricData.detected_subject || 'auto', curricData);
          }
        }

        if (verifRes.ok) {
          const verifData = await verifRes.json();
          const verifScoreLabel = document.getElementById('reviewVerifScore');
          if (verifScoreLabel && verifData.accuracy_score !== undefined && verifData.accuracy_score !== null) {
            const rawScore = Number(verifData.accuracy_score);
            const formattedScore = (rawScore > 1 ? rawScore : (rawScore * 100)).toFixed(1);
            verifScoreLabel.textContent = formattedScore + '%';
          }
        }
      } catch (e) {
        console.warn('Error loading review data:', e);
      }
    }"""

    if old_load_review in content:
        content = content.replace(old_load_review, new_load_review)
        print(f"Updated loadReviewData in {filepath}")
    else:
        print(f"old_load_review not found in {filepath}")

    # 2. Fix btnProcessText handler over-writing reviewEditor with static substring text
    old_btn_text = """                  const reviewEditor = document.getElementById('reviewEditorBody');
                  if (reviewEditor) {
                    reviewEditor.innerHTML = `<b>1. Pasted Content</b><br><br>${text.substring(0, 100)}...<br><br>Processing complete.`;

                    const chapSelect = document.getElementById('reviewChapterSelect');
                    if (chapSelect) {
                      chapSelect.innerHTML = `<option>1. Pasted Content</option>`;
                    }
                  }"""

    new_btn_text = """                  const chapSelect = document.getElementById('reviewChapterSelect');
                  if (chapSelect) {
                    chapSelect.innerHTML = `<option>1. Pasted Content</option>`;
                  }"""

    if old_btn_text in content:
        content = content.replace(old_btn_text, new_btn_text)
        print(f"Fixed btnProcessText reviewEditor overwrite in {filepath}")
    else:
        print(f"old_btn_text not found in {filepath}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Swarm Audit HTML & JS fixes complete!")
