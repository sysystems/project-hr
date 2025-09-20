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
