<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tổng quan</title>

    <!-- Google Font: Source Sans Pro -->
    <link rel="stylesheet"
        href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
    {% load static %}
    <!-- Font Awesome -->

    <link rel="stylesheet" href="{% static 'assets/css/Admin/admin/assets/plugins/fontawesome-free/css/all.min.css' %}">
    <!-- Ionicons -->
    <link rel="stylesheet" href="https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css">
    <!-- Tempusdominus Bootstrap 4 -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'assets/css/Admin/admin/assets/plugins/fontawesome-free/css/all.min.css' %}">
    {% load static %}
    <link rel="stylesheet" href="{% static 'assets/css/singin.css' %}">
    {% load static %}
    <link rel="stylesheet"
        href="{% static 'assets/css/Admin/admin/assets/plugins/tempusdominus-bootstrap-4/css/tempusdominus-bootstrap-4.min.css' %}">
    {% load static %}
    <link rel="stylesheet"
        href="{% static 'assets/css/Admin/admin/assets/plugins/icheck-bootstrap/icheck-bootstrap.min.css' %}">
    {% load static %}
    <link rel="stylesheet" href="{% static 'assets/css/Admin/admin/assets/plugins/jqvmap/jqvmap.min.css' %}">
    {% load static %}
    <link rel="stylesheet" href="{% static 'assets/css/Admin/admin/assets/css/adminlte.min.css' %}">
    {% load static %}
    <link rel="stylesheet"
        href="{% static 'assets/css/Admin/admin/assets/plugins/overlayScrollbars/css/OverlayScrollbars.min.css' %}">
    {% load static %}
    <link rel="stylesheet" href="{% static 'assets/css/singin.css' %}">
    {% load static %}
    <link rel="stylesheet"
        href="{% static 'assets/css/Admin/admin/assets/plugins/daterangepicker/daterangepicker.css' %}">
    {% load static %}
    <link rel="stylesheet"
        href="{% static 'assets/css/Admin/admin/assets/plugins/summernote/summernote-bs4.min.css' %}">
    <link rel="stylesheet" href="{% static 'assets/css/style.css' %}">
    <link rel="stylesheet" href="{% static 'assets/css/main.css' %}">
    <style>
    .main-sidebar {
        background-color: #223771;
    }

    .m-0 {
        color: #223771;
    }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>

<body class="hold-transition sidebar-mini layout-fixed">
    <div class="wrapper">


        <!-- Sidebar Container -->
        <aside class="main-sidebar sidebar-dark-primary elevation-4">
            <!-- Brand Logo -->
            <a href="#" class="brand-link">
                <img src="{%static 'assets/images/AdminLTELogo.png' %}" alt="AdminLTE Logo"
                    class="brand-image img-circle elevation-3" style="opacity: .8">
                <span class="brand-text font-weight-light">Teacher</span>
            </a>

            <!-- Sidebar -->
            <div class="sidebar">
                <!-- Sidebar user panel (optional) -->
                <div class="user-panel mt-3 pb-3 mb-3 d-flex">
                    <div class="info">
                        <a href="#" class="d-block">{{ request.user.first_name }} {{ request.user.last_name }}</a>
                    </div>
                </div>

                <!-- Sidebar Menu -->
                <nav class="mt-2">
                    <ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu"
                        data-accordion="false">
                        <li class="nav-item ">
                            <a href="#" class="nav-link active">
                                <i class="nav-icon fas fa-tachometer-alt"></i>
                                <p>
                                    Tổng quan
                                </p>
                            </a>
                        </li>
                        <li class="nav-item ">
                            <a href="/classroom_list" class="nav-link ">
                                <i class="nav-icon fas fa-user"></i>
                                <p>
                                    Lớp học
                                </p>
                            </a>
                        </li>
                        <li class="nav-item ">
                            <a href="/classroom_list_attendance" class="nav-link ">
                                <i class="nav-icon fas fa-book"></i>
                                <p>
                                    Điểm danh
                                </p>
                            </a>
                        </li>
                        <li class="nav-item mt-5">
                            <a style="margin-top: 320px;" href="/signout" class="nav-link">
                                <i class="fas fa-sign-out-alt"></i>
                                <p>Đăng xuất</p>
                            </a>
                        </li>

                    </ul>
                </nav>
                <!-- /.sidebar-menu -->
            </div>
            <!-- /.sidebar -->
        </aside>

        <!-- Content -->
        <div class="content-wrapper">
            <!-- Content Header (Page header) -->
            <div class="content-header">
                <div class="container-fluid">
                    <div class="row mb-2">
                        <div class="col-sm-6">
                            <h1 class="m-0">Tổng quan</h1>
                        </div><!-- /.col -->

                    </div><!-- /.row -->
                </div><!-- /.container-fluid -->
            </div>
            <!-- /.content-header -->

            <!-- Main content -->
            <section class="content">
                <div class="container-fluid">
                    <!-- Small boxes (Stat box) -->
                    <div class="row">
                        <div class="col-lg-3 col-6">
                            <!-- small box -->
                            <div class="small-box bg-info">
                                <div class="inner">
                                    <h3>{{ total_students }}</h3>

                                    <p>Students</p>
                                </div>
                                <div class="icon">
                                    <i class="nav-icon fas fa-table"></i>
                                </div>
                                <a href="" class="small-box-footer">More info <i
                                        class="fas fa-arrow-circle-right"></i></a>
                            </div>
                        </div>
                        <!-- ./col -->
                        <div class="col-lg-3 col-6">
                            <!-- small box -->
                            <div class="small-box bg-success">
                                <div class="inner">
                                    <h3>{{ total_class }}</h3>

                                    <p>Class</p>
                                </div>
                                <div class="icon">
                                    <i class="ion ion-stats-bars"></i>
                                </div>
                                <a href="classroom_list" class="small-box-footer">More info <i
                                        class="fas fa-arrow-circle-right"></i></a>
                            </div>
                        </div>
                        <!-- ./col -->
                        <div class="col-lg-3 col-6">
                            <!-- small box -->
                            <div class="small-box bg-warning">
                                <div class="inner">
                                    <h3>{{ total_teachers }}</h3>

                                    <p>Teacher</p>
                                </div>
                                <div class="icon">
                                    <i class="ion ion-person-add"></i>
                                </div>
                                <a href="#" class="small-box-footer">More info <i
                                        class="fas fa-arrow-circle-right"></i></a>
                            </div>
                        </div>
                        <!-- ./col -->
                        <div class="col-lg-3 col-6">

                            <div class="small-box bg-danger">
                                <div class="inner">
                                    <h3>10</h3>

                                    <p>More</p>
                                </div>
                                <div class="icon">
                                    <i class="ion ion-pie-graph"></i>
                                </div>
                                <a href="#" class="small-box-footer">More info <i
                                        class="fas fa-arrow-circle-right"></i></a>
                            </div>
                        </div>
                        <!-- ./col -->
                    </div>
                    <!-- /.row -->
                    <!-- Main row -->

                    <!-- /.row (main row) -->
                </div><!-- /.container-fluid -->

                <div class="row">
                    <div class="col-lg-6">
                        <label for="classSelect">Tiến trình của các lớp học</label>
                        <select id="classSelect" onchange="updateChart()">
                            <option value="">Chọn lớp</option>
                            {% for classroom in teacher_classes %}
                                <option value="{{ classroom.class_id }}">{{ classroom.class_name }}</option>
                            {% endfor %}
                        </select>
                    
                        <canvas id="myChart" width="400" height="400"></canvas>
                    </div>
                
                    <div class="col-lg-6">
                        <label for="absenceClassSelect">Chọn lớp để xem % vắng mặt:</label>
                        <select id="absenceClassSelect" onchange="updateAbsenceChart()">
                            <option value="">Chọn lớp</option>
                            {% for classroom in teacher_classes %}
                                <option value="{{ classroom.class_id }}">{{ classroom.class_name }}</option>
                            {% endfor %}
                        </select>
                        <canvas id="absenceChart" width="400" height="400"></canvas>
                        <h3>{{ absent_data }}</h3>
                    </div>
                </div>
                

                
                
            </section>
            <!-- /.content -->
        </div>


    </div>
    <!-- ./wrapper -->

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        var attendanceData = {
            {% for classroom in teacher_classes %}
                "{{ classroom.class_id }}": {
                    labels: ["Đã học", "Tổng"],
                    datasets: [
                        {
                            label: "Đã học",
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',  // Màu xanh cho buổi đã học
                            borderColor: 'rgba(75, 192, 192, 1)',
                            data: [{{ classroom.attended_sessions }}, 0]   // Dữ liệu cho cột đã học
                        },
                        {
                            label: "Tổng",
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',  // Màu đỏ cho tổng buổi học
                            borderColor: 'rgba(255, 99, 132, 1)',
                            data: [0, {{ classroom.total_sessions }}]      // Dữ liệu cho cột tổng số buổi
                        }
                    ]
                },
            {% endfor %}
        };
    
        var ctx = document.getElementById('myChart').getContext('2d');
        var myChart;
    
        function updateChart() {
            var selectedClass = document.getElementById("classSelect").value;
    
            // Xóa biểu đồ nếu đã tồn tại
            if (myChart) {
                myChart.destroy();
            }
    
            if (selectedClass && attendanceData[selectedClass]) {
                myChart = new Chart(ctx, {
                    type: 'bar',
                    data: attendanceData[selectedClass],
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        }
    
        var absentData = {
            labels: [
                {% for data in classroom.absent_data %}
                    "{{ data.student_name }}",
                {% endfor %}
            ],
            datasets: [{
                label: "Vắng (%)",
                backgroundColor: [
                    {% for data in classroom.absent_data %}
                        {% if data.absent_rate > 20 %}
                            "rgba(255, 99, 132, 0.5)",  // Màu đỏ nếu vắng hơn 20%
                        {% else %}
                            "rgba(75, 192, 192, 0.5)",  // Màu xanh nếu vắng dưới 20%
                        {% endif %}
                    {% endfor %}
                ],
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                data: [
                    {% for data in classroom.absent_data %}
                        {{ data.absent_rate }},
                    {% endfor %}
                ]
            }]
        };
    
        var ctx2 = document.getElementById('absenceChart').getContext('2d');
        var absenceChart;
    
        function updateAbsenceChart() {
            var selectedClass = document.getElementById("absenceClassSelect").value;
    
            // Xóa biểu đồ nếu đã tồn tại
            if (absenceChart) {
                absenceChart.destroy();
            }
    
            // Reset dữ liệu
            absentData.labels = [];
            absentData.datasets[0].data = [];
            absentData.datasets[0].backgroundColor = [];
    
            {% for classroom in teacher_classes %}
                if (selectedClass === "{{ classroom.class_id }}") {
                    {% for data in classroom.absent_data %}
                        absentData.labels.push("{{ data.student_name }}");
                        absentData.datasets[0].data.push({{ data.absent_rate }});
                        // Thiết lập màu sắc dựa trên tỷ lệ vắng mặt
                        {% if data.absent_rate > 20 %}
                            absentData.datasets[0].backgroundColor.push("rgba(255, 99, 132, 0.2)"); // Màu đỏ nếu vắng hơn 20%
                        {% else %}
                            absentData.datasets[0].backgroundColor.push("rgba(75, 192, 192, 0.5)"); // Màu xanh nếu vắng dưới 20%
                        {% endif %}
                    {% endfor %}
                }
            {% endfor %}
    
            // Tạo biểu đồ mới chỉ khi có dữ liệu
            if (selectedClass) {
                absenceChart = new Chart(ctx2, {
                    type: 'bar',
                    data: absentData,
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
        }
    
        // Kiểm tra và hủy biểu đồ khi tải trang
        window.onload = function() {
            if (myChart) {
                myChart.destroy();
            }
            if (absenceChart) {
                absenceChart.destroy();
            }
        };
    </script>
</body>

</html>