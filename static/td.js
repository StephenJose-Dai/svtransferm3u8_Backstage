document.querySelectorAll('.resizer').forEach((resizer) => {
    resizer.addEventListener('mousedown', (e) => {
        const th = resizer.parentElement; // 获取当前 th
        const startX = e.clientX; // 鼠标起始位置
        const startWidth = th.offsetWidth; // 当前列的初始宽度

        const mouseMoveHandler = (e) => {
            const newWidth = startWidth + (e.clientX - startX); // 新宽度计算
            if (newWidth > 30) { // 设置最小宽度为 30px
                th.style.width = `${newWidth}px`; // 更新当前单元格宽度
                updateContainerWidth(); // 更新容器宽度
            }
        };

        const mouseUpHandler = () => {
            document.removeEventListener('mousemove', mouseMoveHandler);
            document.removeEventListener('mouseup', mouseUpHandler);
        };

        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
    });
});

// 更新容器宽度，保持自动适应表格宽度
function updateContainerWidth() {
    const table = document.querySelector('table');
    const dashboardContainer = document.querySelector('.dashboard-container');
    dashboardContainer.style.width = `${table.scrollWidth}px`;
}
