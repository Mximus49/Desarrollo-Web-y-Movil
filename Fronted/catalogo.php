<!DOCTYPE html>
<html lang="es">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<title>Quesería Andina — Catalogo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="index.css" rel="stylesheet">
<body>

<header class="topbar">
  <div class="logo">Quesería Andina <span>desde 1978</span></div>
  <div class="search">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" placeholder="Buscar quesos, quesillos, tablas…">
  </div>
  <a href="#" class="account">
    <span>Ingresar</span>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
  </a>
</header>

<nav class="mainnav">
  <ul>
    <li><a href="index.php">Inicio</a></li>
    <li class="active"><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li><a href="Locales.php">Locales</a></li>
    <li><a href="Contacto.php">Contacto</a></li>
    <li class="nav-right">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      <span>Carrito</span>
      <span class="cart-count"></span>
    </li>
  </ul>
</nav>
<main class="container-fluid my-4">
    <div class="row">
        
        <!-- COLUMNA IZQUIERDA: Filtros (ocupa 3 columnas) -->
        <aside class="col-md-3 col-lg-2 mb-4">
            <div class="p-3 bg-light rounded shadow-sm border">
                <h4 class="mb-3 fs-5 text-danger fw-bold">Filtros</h4>
                
                <div class="mb-3">
                    <label class="form-label fw-semibold small">Tipo de queso</label>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="quesoMadurado">
                        <label class="form-check-label small" for="quesoMadurado">Madurados</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="quesoFresco">
                        <label class="form-check-label small" for="quesoFresco">Frescos</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="quesoEspeciales">
                        <label class="form-check-label small" for="quesoEspeciales">Especiales</label>
                    </div>
                </div>

                <button type="button" class="btn btn-danger btn-sm w-100">Aplicar filtros</button>
            </div>
        </aside>

        <!-- COLUMNA DERECHA: Productos repartidos en la pantalla (ocupa el resto) -->
        <section class="col-md-9">
            <!-- row-cols define cuántas tarjetas entran por fila según la pantalla -->
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-xl-4 g-4">
                
                <!-- Producto 1 -->
                <div class="col">
                    <div class="card h-100 shadow-sm text-center p-3 border-0">
                        <img src="https://media.vogue.es/photos/609d3714fae5608e730970ed/2:3/w_2560%2Cc_limit/Billie-Eilish-Happier-Than-Ever.jpeg" class="card-img-top mx-auto" style="width: 140px; height: 140px; object-fit: contain;" alt="Queso">
                        <div class="card-body d-flex flex-column px-0 pb-0">
                            <h5 class="card-title fs-6 fw-bold">Queso Mantecoso</h5>
                            <p class="card-text text-muted mb-2">$6.990</p>
                            <a href="#" class="btn btn-outline-danger mt-auto btn-sm">Agregar al carro</a>
                        </div>
                    </div>
                </div>

                <!-- Producto 2 -->
                <div class="col">
                    <div class="card h-100 shadow-sm text-center p-3 border-0">
                        <img src="https://i.ytimg.com/vi/MAjQ9XdYeqE/maxresdefault.jpg" class="card-img-top mx-auto" style="width: 140px; height: 140px; object-fit: contain;" alt="Queso">
                        <div class="card-body d-flex flex-column px-0 pb-0">
                            <h5 class="card-title fs-6 fw-bold">Queso Especiado</h5>
                            <p class="card-text text-muted mb-2">$8.500</p>
                            <a href="#" class="btn btn-outline-danger mt-auto btn-sm">Agregar al carro</a>
                        </div>
                    </div>
                </div>

                <!-- Producto 3 -->
                <div class="col">
                    <div class="card h-100 shadow-sm text-center p-3 border-0">
                        <img src="https://via.placeholder.com/150" class="card-img-top mx-auto" style="width: 140px; height: 140px; object-fit: contain;" alt="Queso">
                        <div class="card-body d-flex flex-column px-0 pb-0">
                            <h5 class="card-title fs-6 fw-bold">Queso Chanco</h5>
                            <p class="card-text text-muted mb-2">$5.400</p>
                            <a href="#" class="btn btn-outline-danger mt-auto btn-sm">Agregar al carro</a>
                        </div>
                    </div>
                </div>

                <!-- Producto 4 -->
                <div class="col">
                    <div class="card h-100 shadow-sm text-center p-3 border-0">
                        <img src="https://via.placeholder.com/150" class="card-img-top mx-auto" style="width: 140px; height: 140px; object-fit: contain;" alt="Queso">
                        <div class="card-body d-flex flex-column px-0 pb-0">
                            <h5 class="card-title fs-6 fw-bold">Queso de Fundo</h5>
                            <p class="card-text text-muted mb-2">$7.200</p>
                            <a href="#" class="btn btn-outline-danger mt-auto btn-sm">Agregar al carro</a>
                        </div>
                    </div>
                </div>

            </div>
        </section>

    </div>
</main>


<footer>
  <div>
    <h3>Quesería Andina</h3>
    <p class="desc">Afinamos y distribuimos quesos artesanales del sur de Chile desde 1978, directo de la cava a tu mesa.</p>
  </div>
  <div>
    <h3>Contacto</h3>
    <ul>
      <li><a href="#">contacto@queseriaandina.cl</a></li>
      <li><a href="#">+56 9 1234 5678</a></li>
      <li><a href="#">Nuestros locales</a></li>
    </ul>
  </div>
  <div>
    <h3>Nosotros</h3>
    <ul>
      <li><a href="#">Nuestra historia</a></li>
      <li><a href="#">Productores</a></li>
      <li><a href="#">Trabaja con nosotros</a></li>
    </ul>
  </div>
  <div class="foot-bottom">© 2026 Quesería Andina. Todos los derechos reservados.</div>
</footer>

</body>
</html>