
// ---------- Navigation ----------
const navLinks = document.querySelectorAll('#navList a');
const views = document.querySelectorAll('.view');
const crumbTitle = document.getElementById('crumbTitle');
const titles = {
  dashboard:'Dashboard', upload:'Textbook Ingestion', adaptation:'Cultural Adaptation Studio',
  translation:'Dialect Translation', curriculum:'Curriculum Alignment', review:'Review & Approval',
  agents:'Agent Monitoring', analytics:'Analytics Dashboard', knowledge:'Knowledge Base', settings:'Settings'
};
navLinks.forEach(link=>{
  link.addEventListener('click', e=>{
    e.preventDefault();
    const target = link.dataset.view;
    navLinks.forEach(l=>l.classList.remove('active'));
    link.classList.add('active');
    views.forEach(v=>v.classList.remove('active'));
    document.getElementById('view-'+target).classList.add('active');
    crumbTitle.textContent = titles[target];
    window.scrollTo({top:0,behavior:'smooth'});
  });
});

// ---------- Chart.js defaults ----------
Chart.defaults.font.family = "'Segoe UI', Arial, sans-serif";
Chart.defaults.color = '#8A7B67';

// Translation Progress (line)
new Chart(document.getElementById('chartTranslationProgress'), {
  type:'line',
  data:{
    labels:['May 1','May 8','May 15','May 22','May 29'],
    datasets:[
      {label:'Completed', data:[20,55,80,110,150], borderColor:'#2FA463', backgroundColor:'#2FA46322', tension:.4, fill:true, pointRadius:3},
      {label:'In Progress', data:[10,30,45,60,75], borderColor:'#E0972B', backgroundColor:'#E0972B22', tension:.4, fill:true, pointRadius:3},
      {label:'Pending', data:[60,45,35,25,15], borderColor:'#B7A98F', backgroundColor:'#B7A98F22', tension:.4, fill:true, pointRadius:3},
    ]
  },
  options:{plugins:{legend:{display:false}}, scales:{y:{grid:{color:'#F0EAD9'}},x:{grid:{display:false}}}}
});

// Language Distribution (donut)
new Chart(document.getElementById('chartLangDist'), {
  type:'doughnut',
  data:{
    labels:['Tamil','Telugu','Hindi','Kannada','Malayalam'],
    datasets:[{data:[35,20,18,15,12], backgroundColor:['#2FA463','#3E7CB8','#E0972B','#DD5145','#8B6FC7'], borderWidth:2, borderColor:'#fff'}]
  },
  options:{cutout:'68%', plugins:{legend:{display:false}}}
});

// Gauge helper (half-donut style but full ring with track)
function makeGauge(id, value){
  new Chart(document.getElementById(id), {
    type:'doughnut',
    data:{datasets:[{data:[value,100-value], backgroundColor:['#2FA463','#EFE7D6'], borderWidth:0}]},
    options:{cutout:'78%', plugins:{legend:{display:false},tooltip:{enabled:false}}, rotation:-90, circumference:360}
  });
}
makeGauge('gaugeAlignment', 93);
makeGauge('gaugeCurriculum', 95);

// Localized Books Over Time
new Chart(document.getElementById('chartLocalizedOverTime'), {
  type:'line',
  data:{
    labels:['May 1','May 8','May 15','May 22','May 29'],
    datasets:[{data:[10,35,55,80,100], borderColor:'#E0972B', backgroundColor:'#E0972B22', tension:.4, fill:true, pointRadius:3}]
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { grid: { color: '#F0EAD9' } }, x: { grid: { display: false } } }
  }
});

// Books by Language
new Chart(document.getElementById('chartBooksByLang'), {
  type: 'doughnut',
  data: {
    labels: ['Tamil', 'Telugu', 'Hindi', 'Others'],
    datasets: [{
      data: [35, 20, 18, 27],
      backgroundColor: ['#2FA463', '#3E7CB8', '#E0972B', '#8B6FC7'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  },
  options: { cutout: '68%', plugins: { legend: { display: false } } }
});

// Cost Reduction Over Time
new Chart(document.getElementById('chartCostReduction'), {
  type: 'bar',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Cost per Book (₹)',
      data: [65, 58, 52, 47, 42.5],
      backgroundColor: '#DD5145',
      borderRadius: 4
    }]
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { grid: { color: '#F0EAD9' } }, x: { grid: { display: false } } }
  }
});

// --- Backend API Integration ---
const API_BASE = 'http://localhost:8000';

async function fetchDashboardData() {
  try {
    const res = await fetch(`${API_BASE}/dashboard`);
    if (res.ok) {
      const data = await res.json();
      document.getElementById('val-total-books').textContent = data.total_books_processed;
      document.getElementById('val-avg-accuracy').textContent = data.average_accuracy + '%';
    }
  } catch (err) {
    console.warn('Backend not reachable:', err);
  }
}
// Initial fetch
fetchDashboardData();

// Upload Logic
let current_thread_id = null;

const btnUpload = document.getElementById('btnUpload');
const btnBrowseFiles = document.getElementById('btnBrowseFiles');
const uploadDropArea = document.getElementById('uploadDropArea');
const uploadInput = document.getElementById('uploadInput');

if (uploadDropArea) {
  uploadDropArea.addEventListener('dragenter', (e) => {
    e.preventDefault();
  });
  uploadDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadDropArea.style.borderColor = 'var(--green)';
  });
  uploadDropArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadDropArea.style.borderColor = ''; // reset to css default
  });
  uploadDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadDropArea.style.borderColor = '';
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadInput.files = e.dataTransfer.files;
      uploadInput.dispatchEvent(new Event('change'));
    }
  });
  // Make the whole area clickable
  uploadDropArea.addEventListener('click', (e) => {
    if (e.target.closest('#btnBrowseFiles')) return;
    uploadInput.click();
  });
}

if (btnBrowseFiles) {
  btnBrowseFiles.addEventListener('click', (e) => {
    e.stopPropagation();
    uploadInput.click();
  });
}
if (btnUpload) {
  btnUpload.addEventListener('click', (e) => {
    e.stopPropagation();
    uploadInput.click();
  });
}

if (uploadInput) {
  uploadInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (btnUpload) btnUpload.textContent = 'Uploading...';
    if (btnUpload) btnUpload.disabled = true;
    if (btnBrowseFiles) btnBrowseFiles.textContent = 'Uploading...';
    if (btnBrowseFiles) btnBrowseFiles.disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const uploadRes = await fetch(`${API_BASE}/upload-pdf`, {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();
      
      if (btnUpload) btnUpload.textContent = 'Processing Agents...';
      if (btnBrowseFiles) btnBrowseFiles.textContent = 'Processing Agents...';
      
      const processRes = await fetch(`${API_BASE}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pdf_path: uploadData.file_path, target_language: 'tam_Taml' })
      });
      const processData = await processRes.json();
      
      if (processRes.ok) {
        current_thread_id = processData.thread_id;
        if (btnUpload) btnUpload.textContent = 'Awaiting Review...';
        if (btnBrowseFiles) btnBrowseFiles.textContent = 'Awaiting Review...';
        
        // Poll for status
        const interval = setInterval(async () => {
            try {
                const statRes = await fetch(`${API_BASE}/status?thread_id=${current_thread_id}`);
                const statData = await statRes.json();
                
                if (statData.next && statData.next.includes("workbook_generation")) {
                    clearInterval(interval);
                    alert('Workflow paused for Human Review! Please go to the Review Center to approve.');
                    if (btnUpload) btnUpload.textContent = 'Pending Approval';
                    if (btnBrowseFiles) btnBrowseFiles.textContent = 'Pending Approval';
                } else if (!statData.next || statData.next.length === 0) {
                    clearInterval(interval);
                    if (btnUpload) btnUpload.textContent = 'Completed';
                    if (btnBrowseFiles) btnBrowseFiles.textContent = 'Completed';
                }
            } catch(e) {}
        }, 2000);
        
      } else {
        alert('Error processing document');
      }
    } catch (err) {
      alert('Network error connecting to backend.');
    } finally {
      uploadInput.value = '';
      if (btnUpload) btnUpload.disabled = false;
      if (btnBrowseFiles) {
          btnBrowseFiles.textContent = 'Browse Files';
          btnBrowseFiles.disabled = false;
      }
    }
  });
}

// Approve Logic
const btnApprove = document.getElementById('btnApprove');
if (btnApprove) {
    btnApprove.addEventListener('click', async () => {
        if (!current_thread_id) {
            alert('No active workflow to approve.');
            return;
        }
        btnApprove.textContent = 'Approving...';
        btnApprove.disabled = true;
        try {
            const res = await fetch(`${API_BASE}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: current_thread_id })
            });
            if (res.ok) {
                alert('Approved! Workbook is now generating.');
                btnUpload.textContent = 'Completed!';
                btnApprove.textContent = 'Approved';
            }
        } catch(e) {
            console.warn(e);
            btnApprove.textContent = 'Approve';
            btnApprove.disabled = false;
        }
    });
}

// Translation Preview Logic
const btnPreviewTranslation = document.getElementById('btnPreviewTranslation');
if (btnPreviewTranslation) {
  btnPreviewTranslation.addEventListener('click', async () => {
    btnPreviewTranslation.textContent = 'Translating...';
    btnPreviewTranslation.disabled = true;
    try {
      const res = await fetch(`${API_BASE}/translate?content=Photosynthesis%20is%20important&target_language=tam_Taml`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert('Translated content snippet: \n' + data.translated_content);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      btnPreviewTranslation.textContent = 'Preview Full Chapter';
      btnPreviewTranslation.disabled = false;
    }
  });
}

// Curriculum Alignment Logic
const btnCheckAlignment = document.getElementById('btnCheckAlignment');
if (btnCheckAlignment) {
  btnCheckAlignment.addEventListener('click', async () => {
    btnCheckAlignment.textContent = 'Checking...';
    btnCheckAlignment.disabled = true;
    try {
      const res = await fetch(`${API_BASE}/verify?content=Test%20Content`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert(`Alignment Score: ${data.accuracy_score}\nReport: ${data.verification_report}`);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      btnCheckAlignment.textContent = 'Check Alignment';
      btnCheckAlignment.disabled = false;
    }
  });
}
