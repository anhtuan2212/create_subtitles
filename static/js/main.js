document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("uploadForm");
    const taskTable = document.getElementById("taskTable");
  
    // 👉 Tạo phần loading
    const loadingIndicator = document.createElement("div");
    loadingIndicator.innerHTML = `
      <div class="text-center my-2" id="uploadLoading" style="display: none;">
        <div class="spinner-border text-primary" role="status"></div>
        <div>Đang tải lên file...</div>
      </div>
    `;
    form.appendChild(loadingIndicator);
  
    function renderStatus(status) {
      switch (status) {
        case 'pending':
          return 'Chờ xử lý';
        case 'processing':
          return `<span class="spinner-border spinner-border-sm text-primary me-1" role="status" aria-hidden="true"></span>Đang xử lý`;
        case 'done':
          return 'Hoàn thành';
        case 'error':
          return 'Lỗi';
        default:
          return 'Không rõ';
      }
    }
  
    function fetchTasks() {
      fetch("/tasks")
        .then((res) => res.json())
        .then((tasks) => {
          taskTable.innerHTML = "";
          tasks.forEach((task) => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${task.task_id}</td>
              <td>${renderStatus(task.status)}</td>
              <td><small>${task.srt || 'Chưa có'}</small></td>
              <td>
                ${task.status === 'done' ? `<a class='btn btn-sm btn-success' href='/download/${task.task_id}'>Tải xuống</a>` : ""}
                ${task.status === 'done' ? `<button class='btn btn-sm btn-outline-danger ms-1' onclick='deleteTask("${task.task_id}")'>Xoá</button>` : ""}
                ${['pending', 'processing'].includes(task.status) ? `<button class='btn btn-sm btn-warning' onclick='cancelTask("${task.task_id}")'>Huỷ</button>` : ""}
              </td>
            `;
            taskTable.appendChild(row);
          });
        });
    }
  
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);
      
        // 👉 Hiện overlay loading
        document.getElementById("uploadOverlay").style.display = "flex";
      
        fetch("/submit", {
          method: "POST",
          body: formData,
        })
          .then((res) => res.json())
          .then(() => {
            form.reset();
            setTimeout(fetchTasks, 1000);
          })
          .finally(() => {
            // 👉 Ẩn overlay khi xong
            document.getElementById("uploadOverlay").style.display = "none";
          });
      });
      
    window.cancelTask = function (id) {
      fetch(`/cancel/${id}`, { method: "POST" }).then(fetchTasks);
    };
  
    window.deleteTask = function (id) {
      fetch(`/delete/${id}`, { method: "POST" }).then(fetchTasks);
    };
  
    setInterval(fetchTasks, 2000);
    fetchTasks();
  });