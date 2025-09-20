// 조직도 데이터 (임시)
const orgChartData = {
    departments: [
        { id: 1, name: 'Department 1', employees: [1, 2] },
        { id: 2, name: 'Department 2', employees: [3] }
    ],
    employees: [
        { id: 1, name: 'Employee 1', title: 'Manager', photo: '', department: 1, details: { phone: '123-456-7890', email: 'employee1@example.com' } },
        { id: 2, name: 'Employee 2', title: 'Developer', photo: '', department: 1, details: { phone: '987-654-3210', email: 'employee2@example.com' } },
        { id: 3, name: 'Employee 3', title: 'Designer', photo: '', department: 2, details: { phone: '555-123-4567', email: 'employee3@example.com' } }
    ]
};

function handleMenuClick(action) {
    // alert('Clicked: ' + action);
    // 여기에 선택된 메뉴 항목에 대한 동작을 구현합니다.
    // 예시: 조직도 영역의 내용을 변경
    const contentArea = document.querySelector('.content');
    switch (action) {
        case 'create_department':
            contentArea.innerHTML = `
                <h2>Create Department</h2>
                <form>
                    <label for="department_name">Name:</label><br>
                    <input type="text" id="department_name" name="department_name"><br>
                    <label for="creation_date">Creation Date:</label><br>
                    <input type="date" id="creation_date" name="creation_date"><br>
                    <label for="parent_department">Parent Department:</label><br>
                    <select id="parent_department" name="parent_department">
                        <option value="">-- Select --</option>
                        <!-- 여기에 상위 조직 목록을 동적으로 채워야 합니다. -->
                    </select><br><br>
                    <button type="button" onclick="createDepartment()">Create</button>
                </form>
            `;
            break;
        case 'move_department':
            contentArea.innerHTML = '<h2>Move Department</h2><p>Moving a department...</p>';
            break;
        case 'delete_department':
            contentArea.innerHTML = '<h2>Delete Department</h2><p>Deleting a department...</p>';
            break;
        case 'hire_employee':
            contentArea.innerHTML = '<h2>Hire Employee</h2><p>Hiring a new employee...</p>';
            break;
        case 'assign_employee':
            contentArea.innerHTML = '<h2>Assign Employee</h2><p>Assigning an employee...</p>';
            break;
        case 'move_employee':
            contentArea.innerHTML = '<h2>Move Employee</h2><p>Moving an employee...</p>';
            break;
        case 'terminate_employee':
            contentArea.innerHTML = '<h2>Terminate Employee</h2><p>Terminating an employee...</p>';
            break;
        default:
            contentArea.innerHTML = '<h1>Organization Chart</h1><p>Drag and drop employees to move them between departments.</p>';
    }
}

function createDepartment() {
    const departmentName = document.getElementById('department_name').value;
    const creationDate = document.getElementById('creation_date').value;
    const parentDepartment = document.getElementById('parent_department').value;

    console.log('Department Name:', departmentName);
    console.log('Creation Date:', creationDate);
    console.log('Parent Department:', parentDepartment);

    // 여기에 조직 생성 API 호출 코드를 추가합니다.
    // fetch('/api/departments/', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify({
    //         name: departmentName,
    //         creation_date: creationDate,
    //         parent: parentDepartment
    //     })
    // })
    // .then(response => {
    //     if (response.ok) {
    //         alert('Department created successfully!');
    //         // 여기에 조직도 데이터를 업데이트하는 코드를 추가합니다.
    //     } else {
    //         alert('Failed to create department.');
    //     }
    // })
    // .catch(error => {
    //     alert('An error occurred.');
    //     console.error(error);
    // });

    alert('Department created successfully!');
    // 임시로 조직도 영역을 업데이트합니다.
    const contentArea = document.querySelector('.content');
    contentArea.innerHTML += `<p>Created department: ${departmentName}</p>`;
}

// 조직도 데이터 (임시)
// const orgChartData = {
//     departments: [
//         { id: 1, name: 'Department 1', employees: [1, 2] },
//         { id: 2, name: 'Department 2', employees: [3] }
//     ],
//     employees: [
//         { id: 1, name: 'Employee 1', title: 'Manager', photo: '', department: 1, details: { phone: '123-456-7890', email: 'employee1@example.com' } },
//         { id: 2, name: 'Employee 2', title: 'Developer', photo: '', department: 1, details: { phone: '987-654-3210', email: 'employee2@example.com' } },
//         { id: 3, name: 'Employee 3', title: 'Designer', photo: '', department: 2, details: { phone: '555-123-4567', email: 'employee3@example.com' } }
//     ]
// };

function renderOrgChart() {
    const container = document.getElementById('org-chart-container');
    container.innerHTML = ''; // 기존 내용 삭제

    orgChartData.departments.forEach(department => {
        const departmentDiv = document.createElement('div');
        departmentDiv.classList.add('department', 'rounded-box');
        departmentDiv.innerHTML = `<h3>${department.name}</h3>`;
        container.appendChild(departmentDiv);

        department.employees.forEach(employeeId => {
            const employee = orgChartData.employees.find(e => e.id === employeeId);
            if (employee) {
                const employeeDiv = document.createElement('div');
                employeeDiv.classList.add('employee', 'rounded-box');
                employeeDiv.innerHTML = `
                    <img src="${employee.photo}" alt="${employee.name}" style="width: 50px; height: 50px; border-radius: 50%;">
                    <p>${employee.name}</p>
                    <p>${employee.title}</p>
                `;
                employeeDiv.addEventListener('click', () => showEmployeeDetails(employee));
                departmentDiv.appendChild(employeeDiv);
            }
        });
    });
}

function showEmployeeDetails(employee) {
    alert(`
        Name: ${employee.name}
        Title: ${employee.title}
        Phone: ${employee.details.phone}
        Email: ${employee.details.email}
    `);
}

// 페이지 로드 시 조직도 렌더링
document.addEventListener('DOMContentLoaded', () => {
    renderOrgChart();
});
