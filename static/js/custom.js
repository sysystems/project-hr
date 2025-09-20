$(document).ready(function() {
    // 메뉴 토글 버튼 (오른쪽 상단에 추가)
    $('#content-area').prepend('<button id="sidebar-toggle" class="btn btn-primary mb-3">메뉴 토글</button>');

    // 토글 클릭 이벤트
    $('#sidebar-toggle').click(function() {
        $('.sidebar').toggleClass('collapsed');
    });

    // 메뉴 항목 클릭 이벤트 (실시간 업데이트)
    $('.menu-item').click(function(e) {
        e.preventDefault();
        var action = $(this).data('action');
        $.ajax({
            url: '/api/org/action/' + action + '/',  // Django API URL
            method: 'GET',
            success: function(data) {
                $('#content-area').html(data.html);  // 오른쪽 업데이트
                // OrgChart.js가 필요 시 여기서 재초기화
            },
            error: function() {
                alert('오류가 발생했습니다. 서버를 확인하세요.');
            }
        });
    });
});