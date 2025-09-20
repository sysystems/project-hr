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

        // Find the closest department element to append the employee to
        let targetDepartment = event.target;
        while (targetDepartment && !targetDepartment.classList.contains('department')) {
            targetDepartment = targetDepartment.parentElement;
        }

        if (targetDepartment) {
            targetDepartment.appendChild(employee);
            console.log(`Employee ${data} dropped into department ${targetDepartment.id}`);
        } else {
            console.error(`Could not find department to drop employee ${data} into.`);
        }
    }
});
