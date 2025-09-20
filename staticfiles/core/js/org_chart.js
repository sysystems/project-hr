document.addEventListener('DOMContentLoaded', function() {
    const employees = document.querySelectorAll('.employee');
    const departments = document.querySelectorAll('.department');

    employees.forEach(employee => {
        employee.addEventListener('dragstart', dragStart);
    });

    departments.forEach(department => {
        department.addEventListener('dragover', dragOver);
        department.addEventListener('drop', drop);
    });

    function dragStart(event) {
        event.dataTransfer.setData('text', event.target.id);
    }

    function dragOver(event) {
        event.preventDefault();
    }

    function drop(event) {
        event.preventDefault();
        const data = event.dataTransfer.getData('text');
        const employee = document.getElementById(data);
        event.target.appendChild(employee);
    }
});
