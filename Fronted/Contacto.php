<!DOCTYPE html>
<html lang="es">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Quesería Andina — Contacto</title>
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
    <li><a href="catalogo.php">Catálogo</a></li>
    <li><a href="Ofertas.php">Ofertas</a></li>
    <li><a href="Locales.php">Locales</a></li>
    <li class="active"><a href="Contacto.php">Contacto</a></li>
    <li class="nav-right">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
      <span>Carrito</span>
      <span class="cart-count"></span>
    </li>
  </ul>
</nav>

<main class="container my-5">
  <div class="mb-5">
    <h2 class="fw-bold fs-4 mb-2">Contáctanos</h2>
    <p class="mb-1 text-secondary">Dirección: Av. Los Conquistadores 1234, Providencia</p>
    <p class="mb-0 text-secondary">Número de Teléfono: +56 9 1234 5678</p>
  </div>

  <div>
    <h3 class="fw-bold fs-4 mb-4">Mándanos un mensaje</h3>
    
    <form action="#" method="POST">
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <input type="email" class="form-control rounded-pill border-dark py-2 px-3 text-center" placeholder="EMAIL" required>
        </div>
        <div class="col-md-3">
          <input type="text" class="form-control rounded-pill border-dark py-2 px-3 text-center" placeholder="Nombre" required>
        </div>
        <div class="col-md-3">
          <input type="tel" class="form-control rounded-pill border-dark py-2 px-3 text-center" placeholder="Teléfono">
        </div>
      </div>

      <div class="col-md-9 mb-4">
        <textarea class="form-control border-dark p-3" rows="6" placeholder="Mensaje" required></textarea>
      </div>

      <button type="submit" class="btn btn-dark px-4 py-2 rounded-pill">Enviar mensaje</button>
    </form>
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