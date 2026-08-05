// Global Application Data Store
let appData = {
    last_sync: "Never",
    students: [],
    attendance: []
};

// Simulated Seed Data in case live json is missing
const simulatedData = {
    last_sync: new Date().toISOString().replace('T', ' ').substring(0, 19),
    students: [
        { roll_number: "CSE-001", name: "Aarav Sharma", department: "Computer Science", semester: "VIII" },
        { roll_number: "CSE-002", name: "Ananya Iyer", department: "Computer Science", semester: "VIII" },
        { roll_number: "CSE-003", name: "Rohan Varma", department: "Computer Science", semester: "VIII" },
        { roll_number: "CSE-004", name: "Ishaan Gupta", department: "Computer Science", semester: "VIII" },
        { roll_number: "CSE-005", name: "Priya Nair", department: "Computer Science", semester: "VIII" },
        { roll_number: "CSE-006", name: "Kabir Mehta", department: "Computer Science", semester: "VIII" },
        { roll_number: "ECE-012", name: "Vikram Sen", department: "Electronics & Comm", semester: "VIII" },
        { roll_number: "ECE-015", name: "Siddharth Rao", department: "Electronics & Comm", semester: "VIII" }
    ],
    attendance: [
        { attendance_id: 1, roll_number: "CSE-001", student_name: "Aarav Sharma", date: "2026-08-05", time: "09:05:12", subject: "AI_Lab", status: "Present" },
        { attendance_id: 2, roll_number: "CSE-002", student_name: "Ananya Iyer", date: "2026-08-05", time: "09:04:45", subject: "AI_Lab", status: "Present" },
        { attendance_id: 3, roll_number: "CSE-003", student_name: "Rohan Varma", date: "2026-08-05", time: "09:06:01", subject: "AI_Lab", status: "Present" },
        { attendance_id: 4, roll_number: "CSE-004", student_name: "Ishaan Gupta", date: "2026-08-05", time: "09:12:30", subject: "AI_Lab", status: "Present" },
        { attendance_id: 5, roll_number: "CSE-005", student_name: "Priya Nair", date: "2026-08-05", time: "09:03:15", subject: "AI_Lab", status: "Present" },
        { attendance_id: 6, roll_number: "CSE-006", student_name: "Kabir Mehta", date: "2026-08-05", time: "10:15:00", subject: "AI_Lab", status: "Absent" },
        { attendance_id: 7, roll_number: "ECE-012", student_name: "Vikram Sen", date: "2026-08-05", time: "09:07:22", subject: "AI_Lab", status: "Present" },
        { attendance_id: 8, roll_number: "ECE-015", student_name: "Siddharth Rao", date: "2026-08-05", time: "10:15:00", subject: "AI_Lab", status: "Absent" },
        
        { attendance_id: 9, roll_number: "CSE-001", student_name: "Aarav Sharma", date: "2026-08-04", time: "10:35:10", subject: "Computer_Vision", status: "Present" },
        { attendance_id: 10, roll_number: "CSE-002", student_name: "Ananya Iyer", date: "2026-08-04", time: "10:33:55", subject: "Computer_Vision", status: "Present" },
        { attendance_id: 11, roll_number: "CSE-003", student_name: "Rohan Varma", date: "2026-08-04", time: "10:34:20", subject: "Computer_Vision", status: "Present" },
        { attendance_id: 12, roll_number: "CSE-004", student_name: "Ishaan Gupta", date: "2026-08-04", time: "11:45:00", subject: "Computer_Vision", status: "Absent" },
        { attendance_id: 13, roll_number: "CSE-005", student_name: "Priya Nair", date: "2026-08-04", time: "10:36:12", subject: "Computer_Vision", status: "Present" },
        { attendance_id: 14, roll_number: "CSE-006", student_name: "Kabir Mehta", date: "2026-08-04", time: "10:38:00", subject: "Computer_Vision", status: "Present" },
        { attendance_id: 15, roll_number: "ECE-012", student_name: "Vikram Sen", date: "2026-08-04", time: "11:45:00", subject: "Computer_Vision", status: "Absent" },
        { attendance_id: 16, roll_number: "ECE-015", student_name: "Siddharth Rao", date: "2026-08-04", time: "10:40:11", subject: "Computer_Vision", status: "Present" }
    ]
};

// Chart instances
let subjectChart = null;
let statusChart = null;

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadDashboardData();
    
    // Bind search and filter events
    document.getElementById("search-students-input").addEventListener("input", filterStudentsTable);
    document.getElementById("search-logs-input").addEventListener("input", filterLogsTable);
    document.getElementById("filter-status-select").addEventListener("change", filterLogsTable);
});

// Navigation Handling
function initNavigation() {
    const menuItems = document.querySelectorAll(".menu-item");
    const sections = document.querySelectorAll(".content-section");
    const pageHeading = document.getElementById("page-heading");

    menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            
            // Remove active status
            menuItems.forEach(i => i.classList.remove("active"));
            sections.forEach(s => s.classList.remove("active-section"));

            // Set active
            item.classList.add("active");
            const targetSectionId = item.getAttribute("href").substring(1) + "-section";
            const targetSection = document.getElementById(targetSectionId);
            if (targetSection) {
                targetSection.classList.add("active-section");
            }

            // Update Header Name
            if (item.innerText.includes("Dashboard")) {
                pageHeading.innerText = "Classroom Analytics Dashboard";
            } else if (item.innerText.includes("Student Registry")) {
                pageHeading.innerText = "Registered Student Registry";
            } else if (item.innerText.includes("Attendance Logs")) {
                pageHeading.innerText = "Attendance Logs Logbook";
            }
        });
    });

    // View All Logs shortcut link
    document.querySelector(".view-all-btn").addEventListener("click", (e) => {
        e.preventDefault();
        document.querySelector('a[href="#logs"]').click();
    });
}

// Fetch or Load Data
function loadDashboardData() {
    // Try to load attendance_data.json
    fetch("attendance_data.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Local data file not found");
            }
            return response.json();
        })
        .then(data => {
            appData = data;
            updateDashboardUI();
        })
        .catch(err => {
            console.log("[INFO] Using simulated seed data inside dashboard. Error: ", err.message);
            appData = simulatedData;
            updateDashboardUI();
            
            // Show alert modal that simulated data is active
            document.getElementById("no-data-modal").style.display = "flex";
        });
}

function closeModal() {
    document.getElementById("no-data-modal").style.display = "none";
}

// Core UI Updating
function updateDashboardUI() {
    // 1. Sync Time
    document.getElementById("last-sync-time").innerText = appData.last_sync;

    // 2. Compute Statistics Metrics
    const totalStudents = appData.students.length;
    const totalLogs = appData.attendance.length;
    
    const presents = appData.attendance.filter(r => r.status === "Present").length;
    const absents = appData.attendance.filter(r => r.status === "Absent").length;
    
    // Attendance rate
    const rate = totalLogs > 0 ? Math.round((presents / totalLogs) * 100) : 0;

    document.getElementById("stat-total-students").innerText = totalStudents;
    document.getElementById("stat-total-records").innerText = totalLogs;
    document.getElementById("stat-attendance-rate").innerText = `${rate}%`;
    document.getElementById("stat-absent-alerts").innerText = absents; // Notifications sent

    // 3. Render Registry Table
    renderRegistryTable(appData.students);

    // 4. Render Logs Tables
    renderLogsTable(appData.attendance);
    renderRecentLogs(appData.attendance.slice(0, 5));

    // 5. Render Analytics Visualizations
    renderCharts(appData.attendance);
}

// Render student registry
function renderRegistryTable(students) {
    const tbody = document.getElementById("students-tbody");
    tbody.innerHTML = "";

    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-table">No registered students found.</td></tr>`;
        return;
    }

    students.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${s.roll_number}</strong></td>
            <td>${s.name}</td>
            <td>${s.department}</td>
            <td>${s.semester}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Filter Student Registry
function filterStudentsTable() {
    const query = document.getElementById("search-students-input").value.toLowerCase().trim();
    if (!query) {
        renderRegistryTable(appData.students);
        return;
    }

    const filtered = appData.students.filter(s => 
        s.name.toLowerCase().includes(query) ||
        s.roll_number.toLowerCase().includes(query) ||
        s.department.toLowerCase().includes(query)
    );

    renderRegistryTable(filtered);
}

// Render full logs
function renderLogsTable(logs) {
    const tbody = document.getElementById("logs-tbody");
    tbody.innerHTML = "";

    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-table">No logs recorded yet.</td></tr>`;
        return;
    }

    logs.forEach(l => {
        const tr = document.createElement("tr");
        const statusClass = l.status.toLowerCase() === "present" ? "present" : "absent";
        tr.innerHTML = `
            <td>#${l.attendance_id}</td>
            <td><strong>${l.roll_number}</strong></td>
            <td>${l.student_name}</td>
            <td>${l.subject}</td>
            <td>${l.date}</td>
            <td>${l.time}</td>
            <td><span class="status-pill ${statusClass}">${l.status}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// Filter Logs table (Search & Status Selector)
function filterLogsTable() {
    const query = document.getElementById("search-logs-input").value.toLowerCase().trim();
    const statusFilter = document.getElementById("filter-status-select").value;

    let filtered = appData.attendance;

    if (query) {
        filtered = filtered.filter(l => 
            l.student_name.toLowerCase().includes(query) ||
            l.roll_number.toLowerCase().includes(query) ||
            l.subject.toLowerCase().includes(query) ||
            l.date.includes(query)
        );
    }

    if (statusFilter !== "ALL") {
        filtered = filtered.filter(l => l.status === statusFilter);
    }

    renderLogsTable(filtered);
}

// Render Recent 5 Logs
function renderRecentLogs(logs) {
    const tbody = document.getElementById("recent-logs-tbody");
    tbody.innerHTML = "";

    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-table">No recent logs recorded.</td></tr>`;
        return;
    }

    logs.forEach(l => {
        const tr = document.createElement("tr");
        const statusClass = l.status.toLowerCase() === "present" ? "present" : "absent";
        tr.innerHTML = `
            <td><strong>${l.roll_number}</strong></td>
            <td>${l.student_name}</td>
            <td>${l.subject}</td>
            <td>${l.date}</td>
            <td>${l.time}</td>
            <td><span class="status-pill ${statusClass}">${l.status}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// Chart.js Graphs Rendition
function renderCharts(logs) {
    // Destroy existing charts to reload fresh states
    if (subjectChart) subjectChart.destroy();
    if (statusChart) statusChart.destroy();

    // 1. Group status counts (Present vs Absent)
    const statusCounts = { Present: 0, Absent: 0 };
    logs.forEach(l => {
        if (l.status === "Present") statusCounts.Present++;
        if (l.status === "Absent") statusCounts.Absent++;
    });

    // 2. Group details by subject
    const subjectStats = {}; // { subject_name: { present: X, absent: Y } }
    logs.forEach(l => {
        if (!subjectStats[l.subject]) {
            subjectStats[l.subject] = { present: 0, absent: 0 };
        }
        if (l.status === "Present") subjectStats[l.subject].present++;
        if (l.status === "Absent") subjectStats[l.subject].absent++;
    });

    const subjects = Object.keys(subjectStats);
    const presentData = subjects.map(s => subjectStats[s].present);
    const absentData = subjects.map(s => subjectStats[s].absent);

    // Render Pie/Doughnut Chart
    const ctxStatus = document.getElementById("statusChart").getContext("2d");
    statusChart = new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
            labels: ['Present', 'Absent'],
            datasets: [{
                data: [statusCounts.Present, statusCounts.Absent],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 1,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { family: 'Inter' } }
                }
            }
        }
    });

    // Render Bar Chart (Present vs Absent per subject)
    const ctxSub = document.getElementById("subjectChart").getContext("2d");
    subjectChart = new Chart(ctxSub, {
        type: 'bar',
        data: {
            labels: subjects,
            datasets: [
                {
                    label: 'Present',
                    data: presentData,
                    backgroundColor: '#0ea5e9',
                    borderRadius: 4
                },
                {
                    label: 'Absent',
                    data: absentData,
                    backgroundColor: '#f59e0b',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8', stepSize: 1 }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Inter' } }
                }
            }
        }
    });
}
