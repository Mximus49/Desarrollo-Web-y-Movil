<!DOCTYPE html>
<html lang="es">
<head>
        <title>Proyectos | Ingeniería Civil Informatica</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>        
</head>
<body class="bg-light">

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php">Desarrollo Web y Movil Semana 2</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="caracteristicas.php">Características</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="contacto.php">Contacto</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Encabezado de la página -->
    <header class="container mt-5 mb-4 border-bottom pb-3">
        <h1 class="display-5 fw-bold text-center">Proyectos y Áreas de Estudio</h1>
        <p class="lead text-center text-muted">Un vistazo a las tecnologías, scripts y algoritmos con los que trabajo.</p>
    </header>

    <!-- Contenido Principal (Lista de Características) -->
    <main class="container mb-5">
        
        <!-- Característica 1 -->
        <div class="row align-items-center mb-5 mt-5">
            <div class="col-md-7">
                <h2 class="fw-bold">Procesamiento Paralelo y HPC</h2>
                <p class="lead">Experiencia trabajando con librerías como MPI y OpenMP para distribuir la carga de trabajo en el cálculo pesado de matrices y procesamiento de datos de sensores. El enfoque principal es reducir los tiempos de ejecución mediante la concurrencia.</p>
            </div>
            <div class="col-md-3">
                <img src="imagenes/cuda.png" alt="Imagen de NVIDIA CUDA" class="img-fluid rounded">
            </div>
        </div>

        <hr class="text-muted">

        <!-- Característica 2 (Alternada) -->
        <div class="row align-items-center mb-5 mt-5 flex-md-row-reverse">
            <div class="col-md-7">
                <h2 class="fw-bold">Complejidad y Backtracking Eficiente</h2>
                <p class="lead">Resolución de problemas clásicos evaluando su complejidad temporal. Especial atención en la optimización de memoria en algoritmos de backtracking, reestructurando el pseudocódigo para gestionar el flujo utilizando una sola variable de estado en lugar de múltiples variables independientes.</p>
            </div>
            <div class="col-md-5">
                <img src="imagenes/backtracking.png" alt="Imagen de Backtracking" class="img-fluid rounded">
            </div>
        </div>

        <hr class="text-muted">

        <!-- Característica 3 -->
        <div class="row align-items-center mb-5 mt-5">
            <div class="col-md-7">
                <h2 class="fw-bold">Python y Configuración de Entornos</h2>
                <p class="lead">Creación de aplicaciones útiles, como bots de música y scripts para forzar el modo ventana sin bordes en diferentes interfaces. Además, experiencia en el despliegue de entornos web, configurando servidores Apache2 con VirtualHosts en Ubuntu.</p>
            </div>
            <div class="col-md-2">
                    <img src="imagenes/pythonlogo.png" alt="Imagen de Python y Configuración" class="img-fluid rounded">
                </div>
            </div>
        </div>

    </main>

    <!-- Pie de Página -->
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">&copy; 2026 Semana 2. Desarrollo Web y Movil. Maximo Perez.</p>
        </div>
    </footer>
    
</body>
</html>