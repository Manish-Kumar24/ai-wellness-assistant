const API_BASE = "http://127.0.0.1:8000";

function selectRole(role) {
  document.getElementById("role-selection").style.display = "none";
  document.getElementById("auth-box").style.display = "block";
  document.getElementById("role-display").innerText = `Selected Role: ${role.charAt(0).toUpperCase() + role.slice(1)}`;
  document.getElementById("signup-role").value = role;
  document.getElementById("login-role").value = role;
}

// Signup: only registers user — does NOT log in
async function signup(email, password, role) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, role })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  return data;
}

// ✅ User Login + Role-Based Redirect
async function login(email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    
    // Save token
    localStorage.setItem("token", data.access_token);
    
    // 👇 PASTE THE ROLE-BASED LOGIC HERE 👇
    // Decode JWT to get role
    const payload = JSON.parse(atob(data.access_token.split('.')[1]));
    const role = payload.role || "patient"; // Default to patient if no role
    
    // Show success message
    document.getElementById("auth-result").innerHTML = 
      `<p style="color:green;">✅ Logged in as ${role}. Loading your dashboard...</p>`;
    
    // Load role-specific data
    if (role === "doctor") {
        loadAllPatients(); // Doctor sees all patients
    } else {
        loadOwnPatient(); // Patient sees only their own data
    }
    // 👆 END OF PASTE 👆
    
  } catch (error) {
    document.getElementById("auth-result").innerHTML = 
      `<p style="color:red;">❌ Login error: ${error.message}</p>`;
  }
}

function showDashboard(role) {
  document.getElementById("auth-box").style.display = "none";
  if (role === "doctor") {
    document.getElementById("doctor-dashboard").style.display = "block";
    loadPatients();
  } else {
    document.getElementById("patient-dashboard").style.display = "block";
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    document.getElementById("status-message").innerText = `Status: ${data.message} ✅`;
  } catch (error) {
    document.getElementById("status-message").innerText = "Status: Backend not reachable ❌";
  }
}

async function submitSymptom(symptom) {
  const token = localStorage.getItem("token");
  if (!token) { alert("Please log in first!"); return; }
  try {
    const res = await fetch(`${API_BASE}/symptoms/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ symptoms: symptom })
    });
    const data = await res.json();
    document.getElementById("symptom-result").innerText = `Prediction: ${data.prediction}`;
  } catch (error) {
    document.getElementById("symptom-result").innerText = `Error: ${error.message}`;
  }
}

async function submitReport(file, patientId = null) {
  const token = localStorage.getItem("token");
  if (!token) { alert("Please log in first!"); return; }
  const formData = new FormData();
  formData.append("file", file);
  const url = patientId 
    ? `${API_BASE}/cv/clean_and_analyze?patient_id=${patientId}`
    : `${API_BASE}/cv/clean_and_analyze`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    const structured = JSON.stringify(data.structured_output, null, 2);
    const analysis = JSON.stringify(data.analysis, null, 2);
    document.getElementById("report-result").innerHTML = `
      <h3>✅ Analysis Complete (Log ID: ${data.log_id})</h3>
      ${data.patient_id ? `<p><strong>Linked to Patient ID:</strong> ${data.patient_id}</p>` : ''}
      <div><strong>📄 Raw Text:</strong><pre>${data.raw_text}</pre></div>
      <div><strong>🧹 Cleaned Text:</strong><pre>${data.cleaned_text}</pre></div>
      <div><strong>📊 Structured Output:</strong><pre>${structured}</pre></div>
      <div><strong>🔍 Analysis:</strong><pre>${analysis}</pre></div>
    `;
  } catch (error) {
    document.getElementById("report-result").innerHTML = `<p style="color:red;">❌ Error: ${error.message}</p>`;
  }
}

async function addPatient(name, age, gender, contact = "") {
  const token = localStorage.getItem("token");
  if (!token) { alert("Please log in first!"); return; }
  try {
    const res = await fetch(`${API_BASE}/cv/add_patient`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ name, age, gender, contact })
    });
    const data = await res.json();
    if (!res.ok) throw new Error("Failed to add patient");
    document.getElementById("add-patient-result").innerHTML = 
      `<p style="color:green;">✅ Patient added: ${data.name} (ID: ${data.id})</p>`;
    loadPatients();
  } catch (error) {
    document.getElementById("add-patient-result").innerHTML = 
      `<p style="color:red;">❌ Error: ${error.message}</p>`;
  }
}

async function loadPatients() {
  const token = localStorage.getItem("token");
  if (!token) return;
  try {
    const res = await fetch(`${API_BASE}/cv/get_patients`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const patients = await res.json();
    if (!res.ok) throw new Error("Failed to load patients");
    const listDiv = document.getElementById("patient-list");
    if (patients.length === 0) {
      listDiv.innerHTML = "<p>No patients found.</p>";
      return;
    }
    let html = `<div style="display: grid; gap: 10px;">`;
    patients.forEach(p => {
      html += `
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; background: #f9f9f9;">
          <strong>${p.name}</strong> | Age: ${p.age} | ${p.gender}
          ${p.contact ? `| ${p.contact}` : ''}
          <br><small>ID: ${p.id}</small>
        </div>
      `;
    });
    html += `</div>`;
    listDiv.innerHTML = html;
  } catch (error) {
    document.getElementById("patient-list").innerHTML = 
      `<p style="color:red;">❌ Error: ${error.message}</p>`;
  }
}

async function sendChatMessage(message) {
  const token = localStorage.getItem("token");
  if (!token) { alert("Please log in first!"); return; }
  try {
    const res = await fetch(`${API_BASE}/chat/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ message, patient_id: window.selectedPatientId || null })
    });
    const data = await res.json();
    const messagesDiv = document.getElementById("chat-messages");
    messagesDiv.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
    messagesDiv.innerHTML += `<div style="color: #2c3e50; background: #e8f4fc; padding: 5px; margin: 5px 0; border-radius: 5px;">
      <strong>AI Assistant:</strong> ${data.response}
    </div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  } catch (error) {
    document.getElementById("chat-messages").innerHTML += 
      `<div style="color: red;">❌ Error: ${error.message}</div>`;
  }
}

// --- Form Listeners ---
document.getElementById("signupForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const role = document.getElementById("signup-role").value;
  signup(email, password, role)
    .then(() => {
      document.getElementById("auth-result").innerHTML = 
        `<p style="color:green;">✅ Account created! Please log in.</p>`;
    })
    .catch(error => {
      document.getElementById("auth-result").innerHTML = 
        `<p style="color:red;">❌ ${error.message}</p>`;
    });
});

document.getElementById("loginForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  const role = document.getElementById("login-role").value;
  login(email, password, role)
    .then(() => showDashboard(role))
    .catch(error => {
      document.getElementById("auth-result").innerHTML = 
        `<p style="color:red;">❌ ${error.message}</p>`;
    });
});

document.getElementById("symptomForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const symptom = document.getElementById("symptom-input").value.trim();
  if (symptom) submitSymptom(symptom);
});

document.getElementById("reportForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const file = document.getElementById("report-input").files[0];
  if (!file) { alert("Please select a file."); return; }
  submitReport(file, window.selectedPatientId || null);
});

document.getElementById("addPatientForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const name = document.getElementById("patient-name").value.trim();
  const age = parseInt(document.getElementById("patient-age").value);
  const gender = document.getElementById("patient-gender").value;
  const contact = document.getElementById("patient-contact").value.trim();
  if (!name || !age || !gender) {
    alert("Please fill all required fields.");
    return;
  }
  addPatient(name, age, gender, contact);
});

document.getElementById("chatForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = document.getElementById("chat-input").value.trim();
  if (message) {
    sendChatMessage(message);
    document.getElementById("chat-input").value = "";
  }
});

// ✅ CRITICAL: Always start at role selection — no auto-login ever
window.onload = () => {
  document.getElementById("role-selection").style.display = "block";
  document.getElementById("auth-box").style.display = "none";
  document.getElementById("patient-dashboard").style.display = "none";
  document.getElementById("doctor-dashboard").style.display = "none";
};

// Load only the current patient (for patients)
async function loadOwnPatient() {
  const token = localStorage.getItem("token");
  if (!token) return;
  
  try {
    const res = await fetch(`${API_BASE}/cv/get_patients`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const patients = await res.json();
    // Assuming patients[0] is the current user's patient profile
    const patientListDiv = document.getElementById("patient-list");
    if (patients.length > 0) {
      patientListDiv.innerHTML = `
        <div style="border:1px solid #ddd; padding:10px; margin-top:10px;">
          <strong>Your Profile</strong><br>
          Name: ${patients[0].name} | Age: ${patients[0].age} | ${patients[0].gender}
        </div>
      `;
    } else {
      patientListDiv.innerHTML = "<p>No patient profile found. Create one!</p>";
    }
  } catch (error) {
    console.error("Error loading own patient:", error);
  }
}

// Load all patients (for doctors)
async function loadAllPatients() {
  const token = localStorage.getItem("token");
  if (!token) return;
  
  try {
    const res = await fetch(`${API_BASE}/doctor/patients`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const patients = await res.json();
    
    let html = `<div style="display: grid; gap: 10px; margin-top: 10px;">`;
    patients.forEach(p => {
      html += `
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; background: #f9f9f9;">
          <strong>${p.name}</strong> | Age: ${p.age} | ${p.gender}
          ${p.contact ? `| ${p.contact}` : ''}
          <br><small>ID: ${p.id}</small>
          <button onclick="selectPatient(${p.id}, '${p.name}')" style="margin-top: 5px; font-size: 0.8em;">Use for Report</button>
        </div>
      `;
    });
    html += `</div>`;
    document.getElementById("patient-list").innerHTML = html;
  } catch (error) {
    console.error("Error loading all patients:", error);
    document.getElementById("patient-list").innerHTML = "<p>Failed to load patients.</p>";
  }
}